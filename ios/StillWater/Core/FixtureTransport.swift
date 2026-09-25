import Foundation

@MainActor final class FixtureTransport: BridgeTransport {
    private var samples: [String: JSONValue] = [:]
    var state = "playing", saved = "unsaved", track = 0
    private var memberships: [String:String] = [:]
    var mutations: [String] = []
    var fail = false
    var clock: () -> Double = { ProcessInfo.processInfo.systemUptime }
    private var battery: (level: Int, charging: Bool, received: Double)?
    init() {
        if let url = Bundle.main.url(forResource:"BridgeFixtures",withExtension:"json"),
           let raw = try? Data(contentsOf:url), let samples = try? JSONDecoder().decode([String:JSONValue].self,from:raw) { self.samples = samples }
    }
    func cancel() {}
    func sample(_ name: String) -> JSONValue { samples[name]?["reply"] ?? .null }
    func send(_ request: BridgeRequest) async throws -> BridgeReply {
        guard !fail else { throw BridgeFailure.unavailable }
        var name: String
        switch request.action {
        case "snapshot": name = "snapshot-" + state
        case "search": name = request.args["offset"]?.number == 12 ? "search-more" : "search-" + (request.args["kind"]?.text ?? "albums")
        case "library_page": name = "library-" + (request.args["kind"]?.text ?? "albums")
        case "browse": name = "browse-" + ((request.args["reference"]?.text ?? "").split(separator:"/").dropFirst(2).first.map(String.init) ?? "albums")
        case "queue": name = "queue"
        case "library_state": name = "membership-" + (memberships[request.args["reference"]?.text ?? ""] ?? saved)
        case "artwork": name = request.args["side"]?.number == 320 ? "artwork-" + String(request.args["pixel_offset"]?.number ?? 0) : "artwork-80"
        case "voice_review": name = "voice"
        case "battery_report":
            guard let level = request.args["level"]?.number, (0...100).contains(level),
                  let charging = request.args["charging"]?.flag else { throw BridgeFailure.invalidResponse }
            battery = (level,charging,clock()); name = "battery"
        case "charge?": name = "charge-none"
        case "transport", "play", "amplifier", "library_save":
            mutations.append(request.action)
            if request.action == "library_save", let ref = request.args["reference"]?.text { memberships[ref] = request.args["saved"]?.flag == true ? "saved" : "unsaved" }
            if request.action == "play" { state = "playing" }
            if request.action == "transport" {
                switch request.args["command"]?.text {
                case "pause": state = "paused"
                case "resume": state = "playing"
                case "stop": state = "stopped"
                case "next": track = (track + 1) % 3
                case "prev": track = (track + 2) % 3
                default: break
                }
            }
            return BridgeReply(version:1,request_id:request.request_id,boot_id:String(repeating:"1",count:32),outcome:"submitted",fixture:true,data:.object([:]),error:.null)
        default: throw BridgeFailure.invalidResponse
        }
        guard case .object(var r) = sample(name) else { throw BridgeFailure.invalidResponse }
        r["request_id"] = .string(request.request_id)
        if request.action == "library_page", case .object(var data) = r["data"] {
            let kind = request.args["kind"]?.text ?? "albums"
            var catalog = sample("search-"+kind)["data"]["items"].values
            catalog += sample("search-more")["data"]["items"].values.filter { $0["kind"].text == kind }
            if kind == "tracks" {
                for index in 0..<3 {
                    if case .object(var current) = sample("snapshot-playing")["data"]["current_item"] {
                        current["reference"] = .string("inputs/tidal/tracks/\(101+index)")
                        current["title"] = .string(["A Still Morning","Soft Light","Quiet Hours"][index])
                        catalog.append(.object(current))
                    }
                }
            }
            let selected = catalog.filter { memberships[$0["reference"].text ?? ""] == "saved" }
            let offset = request.args["offset"]?.number ?? 0
            data["items"] = .array(Array(selected.dropFirst(max(0,offset)).prefix(12)))
            data["next_offset"] = offset + 12 < selected.count ? .int(offset + 12) : .null
            data["cursor"] = .null
            r["data"] = .object(data)
        }
        if case .object(var data) = r["data"], case .array(let items) = data["items"] {
            data["items"] = .array(items.map { item in
                guard case .object(var fields) = item, let ref = fields["reference"]?.text else { return item }
                // Keep deliberately unknown fixture rows unavailable; known rows reflect per-item writes.
                if let state = memberships[ref] { fields["saved"] = .string(state) }
                else if fields["saved"]?.text != "unknown" { fields["saved"] = .string(saved) }
                return .object(fields)
            })
            r["data"] = .object(data)
        }
        if request.action == "charge?" {
            let fresh = battery.map { clock() >= $0.received && clock() - $0.received < 3600 } ?? false
            let charge = fresh && (battery!.level < 35 || (battery!.level < 75 && battery!.charging))
            r["data"] = .object(["charge":.string(charge ? "yes" : "no"),"reason":.string(battery == nil ? "none" : fresh ? "window" : "stale")])
        }
        if request.action == "browse", let ref = request.args["reference"], case .object(var d) = r["data"], case .object(var item) = d["item"] {
            item["reference"] = ref; d["item"] = .object(item); r["data"] = .object(d)
        }
        if request.action == "snapshot", case .object(var d) = r["data"], case .object(var p) = d["player"] {
            if state == "playing" || state == "paused" { p["title"] = .string(["A Still Morning","Soft Light","Quiet Hours"][track]) }
            d["player"] = .object(p)
            if case .object(var current) = d["current_item"] {
                current["title"] = p["title"]; current["reference"] = .string("inputs/tidal/tracks/\(101+track)"); d["current_item"] = .object(current)
            }
            r["data"] = .object(d)
        }
        let raw = try JSONEncoder().encode(JSONValue.object(r))
        return try BridgeReply.decode(raw,for:request)
    }
}
