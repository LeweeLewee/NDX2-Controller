import Foundation

enum BridgeFailure: Error, Equatable {
    case invalidResponse, oversized, unauthenticated, unavailable, expired, busy, notConfigured
}

enum JSONValue: Codable, Equatable {
    case string(String), int(Int), bool(Bool), object([String: JSONValue]), array([JSONValue]), null
    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if c.decodeNil() { self = .null }
        else if let v = try? c.decode(Bool.self) { self = .bool(v) }
        else if let v = try? c.decode(Int.self) { self = .int(v) }
        else if let v = try? c.decode(String.self) { self = .string(v) }
        else if let v = try? c.decode([String: JSONValue].self) { self = .object(v) }
        else { self = .array(try c.decode([JSONValue].self)) }
    }
    func encode(to encoder: Encoder) throws {
        var c = encoder.singleValueContainer()
        switch self {
        case .string(let v): try c.encode(v)
        case .int(let v): try c.encode(v)
        case .bool(let v): try c.encode(v)
        case .object(let v): try c.encode(v)
        case .array(let v): try c.encode(v)
        case .null: try c.encodeNil()
        }
    }
    subscript(_ key: String) -> JSONValue { if case .object(let d) = self { return d[key] ?? .null }; return .null }
    var text: String? { if case .string(let v) = self { return v }; return nil }
    var number: Int? { if case .int(let v) = self { return v }; return nil }
    var flag: Bool? { if case .bool(let v) = self { return v }; return nil }
    var values: [JSONValue] { if case .array(let v) = self { return v }; return [] }
    func bounded(depth: Int = 0, key: String = "") throws {
        guard depth < 12 else { throw BridgeFailure.invalidResponse }
        switch self {
        case .string(let s):
            let limit = key == "pixels" ? 25_600 : key == "cursor" ? 4_096 : key == "biography" ? 8_000 : 256
            guard s.utf8.count <= limit, key != "biography" || s.unicodeScalars.count <= 2000 else { throw BridgeFailure.oversized }
        case .array(let a):
            guard a.count <= 12 else { throw BridgeFailure.oversized }
            for v in a { try v.bounded(depth: depth + 1) }
        case .object(let o):
            guard o.count <= 40 else { throw BridgeFailure.oversized }
            for (k, v) in o { try v.bounded(depth: depth + 1, key: k) }
        default: break
        }
    }
}

struct BridgeRequest: Codable {
    let version = 1
    let request_id: String
    let action: String
    let args: [String: JSONValue]
    static let mutations: Set<String> = ["play", "transport", "amplifier", "library_save"]
    var isMutation: Bool { Self.mutations.contains(action) }
    init(_ action: String, _ args: [String: JSONValue] = [:], id: String = UUID().uuidString) {
        self.action = action; self.args = args; self.request_id = id
    }
    func encoded() throws -> Data {
        guard request_id.range(of: "^[A-Za-z0-9_-]{16,64}$", options: .regularExpression) != nil else {
            throw BridgeFailure.invalidResponse
        }
        try JSONValue.object(args).bounded()
        let data = try JSONEncoder().encode(self)
        guard data.count <= 8192 else { throw BridgeFailure.oversized }
        return data
    }
}

struct BridgeReply: Codable {
    let version: Int
    let request_id: String
    let boot_id: String
    let outcome: String
    let fixture: Bool
    let data: JSONValue
    let error: JSONValue
    static func decode(_ raw: Data, for request: BridgeRequest) throws -> Self {
        guard raw.count <= 32768 else { throw BridgeFailure.oversized }
        guard let object = try JSONSerialization.jsonObject(with: raw) as? [String: Any] else { throw BridgeFailure.invalidResponse }
        let keys = Set(object.keys)
        guard keys == Set(["version", "request_id", "boot_id", "outcome", "fixture", "data", "error"]) else {
            throw BridgeFailure.invalidResponse
        }
        let r = try JSONDecoder().decode(Self.self, from: raw)
        guard r.version == 1, r.request_id == request.request_id,
              r.boot_id.range(of: "^[0-9a-f]{32}$", options: .regularExpression) != nil,
              ["observed", "submitted", "unknown", "rejected"].contains(r.outcome),
              request.isMutation || ["observed", "rejected"].contains(r.outcome) else { throw BridgeFailure.invalidResponse }
        try r.data.bounded(); try r.error.bounded()
        return r
    }
}

@MainActor protocol BridgeTransport: AnyObject {
    func send(_ request: BridgeRequest) async throws -> BridgeReply
    func cancel()
}

struct MusicItem: Equatable, Identifiable {
    var reference = "", title = "", artist = "", album = "", kind = "tracks"
    var artwork: String?, artistReference: String?, albumReference: String?
    var biography: String?
    var year: Int?, duration: Int?, trackCount: Int?
    var saved = "unknown"
    var id: String { reference }
    init(_ value: JSONValue = .null) {
        reference = value["reference"].text ?? ""
        title = value["title"].text ?? ""
        artist = value["artist"].text ?? ""
        album = value["album"].text ?? ""
        kind = value["kind"].text ?? "tracks"
        biography = value["biography"].text.map { String(String.UnicodeScalarView($0.unicodeScalars.prefix(2000))) }
        year = value["year"].number.flatMap { (1900...2100).contains($0) ? $0 : nil }
        trackCount = value["track_count"].number.flatMap { (1...10000).contains($0) ? $0 : nil }
        duration = value["duration"].number.flatMap { $0 > 0 ? $0 : nil }
        artwork = value["artwork"].text
        artistReference = value["artist_reference"].text
        albumReference = value["album_reference"].text
        let membership = value["saved"].text ?? value["saved"].flag.map { $0 ? "saved" : "unsaved" } ?? "unknown"
        saved = ["saved","unsaved","unknown"].contains(membership) ? membership : "unknown"
    }
}

struct Player: Equatable {
    var title = "", artist = "", album = "", state = "unknown", source = ""
    var artwork: String?
    var current = MusicItem()
    var position: Int?, duration: Int?
    init(_ value: JSONValue = .null) {
        title = value["title"].text ?? ""; artist = value["artist"].text ?? value["artistName"].text ?? ""
        album = value["album"].text ?? ""
        let observed = value["state"].text ?? "unknown"
        state = ["playing","paused","stopped"].contains(observed) ? observed : "unknown"
        source = value["sourceDetail"].text ?? ""; artwork = value["artwork"].text
        position = value["transportPosition"].number.flatMap { $0 >= 0 ? $0 : nil }
        duration = value["duration"].number.flatMap { $0 > 0 ? $0 : nil }
    }
}

struct ArtworkAssembly {
    let reference: String, side: Int
    private(set) var offset = 0, bytes = Data()
    private(set) var deadline = Double.infinity
    private var imageID: String?, bootID: String?
    init(reference: String, side: Int) {
        self.reference = reference
        self.side = side
    }
    var complete: Bool { offset == side * side }
    mutating func append(_ reply: BridgeReply, started: Double, now: Double) throws {
        let d = reply.data
        guard reply.outcome == "observed", d["available"].flag == true,
              d["reference"].text == reference, d["width"].number == side, d["height"].number == side,
              d["format"].text == "rgb565be-hex", let valid = d["valid_for_ms"].number,
              (1...60000).contains(valid), now < started + Double(valid) / 1000,
              side >= 1, side <= 320, !complete else { throw BridgeFailure.expired }
        if side != 80 {
            guard d["offset"].number == offset, d["total_pixels"].number == side * side,
                  let id = d["image_id"].text, id.range(of: "^[0-9a-f]{64}$", options: .regularExpression) != nil,
                  imageID == nil || imageID == id else { throw BridgeFailure.invalidResponse }
            imageID = id
        }
        guard bootID == nil || bootID == reply.boot_id else { throw BridgeFailure.expired }
        bootID = reply.boot_id
        let count = min(6400, side * side - offset)
        guard let pixels = d["pixels"].text, pixels.utf8.count == count * 4,
              pixels.range(of: "^[0-9a-f]+$", options: .regularExpression) != nil else { throw BridgeFailure.invalidResponse }
        let next = offset + count
        if side != 80 {
            guard next == side * side ? d["next_offset"] == .null : d["next_offset"].number == next else {
                throw BridgeFailure.invalidResponse
            }
        }
        let chars = Array(pixels.utf8)
        func nibble(_ c: UInt8) -> UInt8 { c <= 57 ? c - 48 : c - 87 }
        for i in stride(from: 0, to: chars.count, by: 2) { bytes.append(nibble(chars[i]) * 16 + nibble(chars[i + 1])) }
        offset = next; deadline = min(deadline, started + Double(valid) / 1000)
        guard now < deadline else { throw BridgeFailure.expired }
    }
}
