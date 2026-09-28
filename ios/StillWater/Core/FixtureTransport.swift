import Foundation

@MainActor final class FixtureTransport: BridgeTransport {
    private var samples: [String: JSONValue] = [:]
    var state = "playing", saved = "unsaved", track = 0
    private var memberships: [String:String] = [:]
    var mutations: [String] = []
    var fail = false
    var clock: () -> Double = { ProcessInfo.processInfo.systemUptime }
    private var battery: (level: Int, charging: Bool, received: Double)?
    init(seedCollection: Bool = false) {
        if let url = Bundle.main.url(forResource:"BridgeFixtures",withExtension:"json"),
           let raw = try? Data(contentsOf:url), let samples = try? JSONDecoder().decode([String:JSONValue].self,from:raw) { self.samples = samples }
        if seedCollection {
            for kind in ["albums","tracks","artists","playlists"] {
                for index in 201...212 { memberships["inputs/tidal/"+kind+"/"+String(index)] = "saved" }
            }
        }
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
        case "artwork":
            let variant = (0..<6).first { sample("sleeve-\($0)-80")["data"]["reference"].text == request.args["reference"]?.text }
            let portrait = request.args["reference"]?.text == sample("artist-bio")["data"]["artwork"].text
            name = request.args["side"]?.number == 320 ? (portrait ? "portrait-" : "artwork-") + String(request.args["pixel_offset"]?.number ?? 0) : (portrait ? "portrait-80" : "artwork-80")
                    if let variant { name = "sleeve-\(variant)-" + (request.args["side"]?.number == 320 ? String(request.args["pixel_offset"]?.number ?? 0) : "80") }
            if request.args["encoding"]?.text == "jpeg-base64", request.args["side"]?.number == 320 {
                name = variant.map { "sleeve-\($0)-jpeg" } ?? (portrait ? "portrait-jpeg" : "artwork-jpeg")
            }
        case "artist_bio": name = "artist-bio"
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
            let known = Set(catalog.compactMap { $0["reference"].text })
            for ref in memberships.keys.sorted() where memberships[ref] == "saved" && !known.contains(ref) && ref.contains("/"+kind+"/") {
                let detail = try await send(BridgeRequest("browse",["reference":.string(ref)]))
                catalog.append(detail.data["item"])
            }
            let selected = catalog.filter { memberships[$0["reference"].text ?? ""] == "saved" }
            let offset = request.args["offset"]?.number ?? 0
            data["items"] = .array(Array(selected.dropFirst(max(0,offset)).prefix(12)))
            data["next_offset"] = offset + 12 < selected.count ? .int(offset + 12) : .null
            data["cursor"] = .null
            r["data"] = .object(data)
        }
        if request.action == "browse", case .object(var data) = r["data"], let ref = request.args["reference"]?.text {
            let kind = ref.split(separator:"/").dropFirst(2).first.map(String.init) ?? "albums"
            let index = Int(ref.split(separator:"/").last ?? "1") ?? 1
            let titles = ["Listening Studies, Vol. 01", "Estuary", "Slow Rooms", "Northern Shelf"]
            func art(_ variant: Int) -> JSONValue { sample("sleeve-\(variant)-80")["data"]["reference"] }
            func album(_ number: Int) -> JSONValue {
                .object(["reference":.string("inputs/tidal/albums/\(number)"),"title":.string(titles[(number-1)%4]),"artist":.string("River Stone Ensemble"),"kind":.string("albums"),"artwork":art([0,3,4,5][(number-1)%4]),"year":.int(2026-number+1),"track_count":.int(6),"duration":.int(1620000),"saved":.string("unsaved"),"artist_reference":.string("inputs/tidal/artists/1")])
            }
            func trackItem(_ number: Int, albumID: Int) -> JSONValue {
                .object(["reference":.string("inputs/tidal/tracks/\(number)"),"title":.string(["A Still Morning","Soft Light","Quiet Hours","On the Water","After Rain","Evening Study"][(number-101)%6]),"artist":.string("River Stone Ensemble"),"album":.string(titles[(albumID-1)%4]),"kind":.string("tracks"),"artwork":art((number-101)%6),"duration":.int(210000+(number-101)%6*24000),"saved":.string("unsaved"),"artist_reference":.string("inputs/tidal/artists/1"),"album_reference":.string("inputs/tidal/albums/\(albumID)")])
            }
            if kind == "artists" {
                data["item"] = .object(["reference":.string(ref),"title":.string("River Stone Ensemble"),"kind":.string("artists"),"artwork":sample("artist-bio")["data"]["artwork"],"biography":.string("A fictional ensemble for this silent preview. Piano, strings and soft electronic textures trace the changing light of a quiet room. Explore four imagined albums and six tracks.")])
                data["items"] = .array((1...4).map(album) + (101...106).map { trackItem($0,albumID:1) })
                data["playable"] = .bool(false)
            } else if kind == "albums" {
                data["item"] = album(max(1,index)); data["items"] = .array((101...106).map { trackItem($0,albumID:max(1,index)) })
            } else if kind == "playlists" {
                data["item"] = .object(["reference":.string(ref),"title":.string(["Evening Listening","Quiet Piano","After Rain","Acoustic Rooms"][(max(1,index)-1)%4]),"artist":.string("Silent collection"),"kind":.string("playlists"),"artwork":art((max(1,index)-1)%6)])
                data["items"] = .array((101...106).map { trackItem($0,albumID:1) })
            } else if kind == "tracks" {
                data["item"] = trackItem(max(101,index),albumID:1); data["items"] = .array([])
            }
            data["next_offset"] = .null; r["data"] = .object(data)
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
        if request.action == "artist_bio", case .object(var data) = r["data"] {
            data["reference"] = request.args["reference"]
            if request.args["reference"]?.text == "inputs/tidal/artists/203" { data["artwork"] = .null }
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
