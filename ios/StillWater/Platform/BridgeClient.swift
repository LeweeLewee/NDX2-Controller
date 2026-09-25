import Foundation
import Security
import CryptoKit

struct Enrollment: Codable {
    var origin: URL
    var anchors: [Data]
    var state: String
    var device: String?
    var credential: String?
    var trustDigest: String {
        SHA256.hash(data: anchors.reduce(into: Data()) { $0.append($1) }).map { String(format: "%02x", $0) }.joined()
    }
    static func origin(_ text: String) throws -> URL {
        guard let c = URLComponents(string: text), c.scheme == "https", c.host != nil,
              c.user == nil, c.password == nil, c.query == nil, c.fragment == nil,
              c.path.isEmpty || c.path == "/", let url = c.url else { throw BridgeFailure.notConfigured }
        return url
    }
    static func certificates(_ raw: Data) throws -> [Data] {
        guard raw.count <= 65536 else { throw BridgeFailure.oversized }
        if SecCertificateCreateWithData(nil, raw as CFData) != nil { return [raw] }
        let pem = String(decoding: raw, as: UTF8.self)
        let result = pem.components(separatedBy: "-----BEGIN CERTIFICATE-----").dropFirst().compactMap { part -> Data? in
            guard let body = part.components(separatedBy: "-----END CERTIFICATE-----").first,
                  let data = Data(base64Encoded: body.filter { !$0.isWhitespace }),
                  SecCertificateCreateWithData(nil, data as CFData) != nil else { return nil }
            return data
        }
        guard !result.isEmpty, result.count <= 8 else { throw BridgeFailure.notConfigured }
        return result
    }
}

enum SecureEnrollment {
    private static let query: [String: Any] = [kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "StillWater.bridge", kSecAttrAccount as String: "enrollment-v1"]
    static func load() throws -> Enrollment? {
        guard !RuntimeMode.demoOnly else { throw BridgeFailure.notConfigured }
        var q = query; q[kSecReturnData as String] = true
        var item: CFTypeRef?
        let status = SecItemCopyMatching(q as CFDictionary, &item)
        if status == errSecItemNotFound { return nil }
        guard status == errSecSuccess, let data = item as? Data, data.count <= 100000 else { throw BridgeFailure.notConfigured }
        let record = try JSONDecoder().decode(Enrollment.self, from: data)
        guard try Enrollment.origin(record.origin.absoluteString).host == record.origin.host,
              !record.anchors.isEmpty, record.anchors.count <= 8,
              record.anchors.allSatisfy({ SecCertificateCreateWithData(nil, $0 as CFData) != nil }),
              ["pending", "paired", "revoked"].contains(record.state) else { throw BridgeFailure.notConfigured }
        return record
    }
    static func save(_ value: Enrollment) throws {
        guard !RuntimeMode.demoOnly else { throw BridgeFailure.notConfigured }
        let data = try JSONEncoder().encode(value)
        let attrs: [String: Any] = [kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly]
        let status = SecItemUpdate(query as CFDictionary, attrs as CFDictionary)
        if status == errSecItemNotFound {
            var q = query; attrs.forEach { q[$0.key] = $0.value }
            guard SecItemAdd(q as CFDictionary, nil) == errSecSuccess else { throw BridgeFailure.notConfigured }
        } else if status != errSecSuccess { throw BridgeFailure.notConfigured }
    }
    static func forget() throws {
        guard !RuntimeMode.demoOnly else { throw BridgeFailure.notConfigured }
        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else { throw BridgeFailure.notConfigured }
    }
}

final class PinnedTrust: NSObject, URLSessionDelegate, URLSessionTaskDelegate {
    let record: Enrollment
    init(_ record: Enrollment) { self.record = record }
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              challenge.protectionSpace.host.lowercased() == record.origin.host?.lowercased(),
              let trust = challenge.protectionSpace.serverTrust else { completionHandler(.cancelAuthenticationChallenge, nil); return }
        let certificates = record.anchors.compactMap { SecCertificateCreateWithData(nil, $0 as CFData) }
        let policy = SecPolicyCreateSSL(true, challenge.protectionSpace.host as CFString)
        guard certificates.count == record.anchors.count,
              SecTrustSetPolicies(trust, policy) == errSecSuccess,
              SecTrustSetAnchorCertificates(trust, certificates as CFArray) == errSecSuccess,
              SecTrustSetAnchorCertificatesOnly(trust, true) == errSecSuccess,
              SecTrustSetNetworkFetchAllowed(trust, false) == errSecSuccess,
              SecTrustEvaluateWithError(trust, nil) else { completionHandler(.cancelAuthenticationChallenge, nil); return }
        completionHandler(.useCredential, URLCredential(trust: trust))
    }
    func urlSession(_ session: URLSession, task: URLSessionTask, willPerformHTTPRedirection response: HTTPURLResponse,
                    newRequest request: URLRequest, completionHandler: @escaping (URLRequest?) -> Void) { completionHandler(nil) }
}

@MainActor final class BridgeClient: BridgeTransport {
    private var record: Enrollment
    private let trust: PinnedTrust
    private let session: URLSession
    private let persistRevocation: Bool
    private var operation: (id: UUID, task: Task<Data,Error>)?
    init(_ record: Enrollment, persistRevocation: Bool = true) {
        self.record = record; self.persistRevocation = persistRevocation; trust = PinnedTrust(record)
        let config = URLSessionConfiguration.ephemeral
        config.urlCache = nil; config.httpCookieStorage = nil; config.urlCredentialStorage = nil
        config.httpShouldSetCookies = false; config.requestCachePolicy = .reloadIgnoringLocalCacheData
        config.timeoutIntervalForRequest = 7; config.timeoutIntervalForResource = 8
        config.waitsForConnectivity = false; config.httpMaximumConnectionsPerHost = 1
        config.tlsMinimumSupportedProtocolVersion = .TLSv12
        session = URLSession(configuration: config, delegate: trust, delegateQueue: nil)
    }
    func cancel() { operation?.task.cancel(); operation = nil }
    func post(_ path: String, body: Data, authenticated: Bool) async throws -> Data {
        guard !RuntimeMode.demoOnly else { throw BridgeFailure.notConfigured }
        guard operation == nil else { throw BridgeFailure.busy }
        guard body.count <= 8192, ["v1/request", "v1/pair"].contains(path) else { throw BridgeFailure.oversized }
        if authenticated {
            guard record.state == "paired", let token = record.credential,
                  token.range(of: "^[A-Za-z0-9_-]{32,128}$", options: .regularExpression) != nil else { throw BridgeFailure.notConfigured }
        }
        var req = URLRequest(url: record.origin.appendingPathComponent(path))
        req.httpMethod = "POST"; req.httpBody = body
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if authenticated { req.setValue("Bearer " + (record.credential ?? ""), forHTTPHeaderField: "Authorization") }
        let id = UUID()
        let task = Task { try await self.receive(req,authenticated:authenticated) }
        operation = (id,task)
        defer { if operation?.id == id { operation = nil } }
        return try await withTaskCancellationHandler(operation:{ try await task.value },onCancel:{ task.cancel() })
    }
    private func receive(_ req: URLRequest, authenticated: Bool) async throws -> Data {
        try Task.checkCancellation()
        let (bytes, response) = try await session.bytes(for: req)
        try Task.checkCancellation()
        guard let http = response as? HTTPURLResponse else { throw BridgeFailure.invalidResponse }
        if http.statusCode == 401 {
            if authenticated && persistRevocation { record.state = "revoked"; record.credential = nil; try SecureEnrollment.save(record) }
            throw BridgeFailure.unauthenticated
        }
        guard http.statusCode == 200, http.expectedContentLength <= 32768,
              http.mimeType == "application/json" else { throw BridgeFailure.invalidResponse }
        var raw = Data()
        for try await byte in bytes {
            try Task.checkCancellation()
            guard raw.count < 32768 else { cancel(); throw BridgeFailure.oversized }
            raw.append(byte)
        }
        return raw
    }
    func send(_ request: BridgeRequest) async throws -> BridgeReply {
        let raw = try await post("v1/request", body: request.encoded(), authenticated: true)
        return try BridgeReply.decode(raw, for: request)
    }
    static func pair(origin: String, certificate: Data, code: String) async throws -> Enrollment {
        guard !RuntimeMode.demoOnly else { throw BridgeFailure.notConfigured }
        guard try SecureEnrollment.load() == nil, !code.isEmpty, code.utf8.count <= 256 else { throw BridgeFailure.notConfigured }
        var pending = Enrollment(origin: try Enrollment.origin(origin), anchors: try Enrollment.certificates(certificate), state: "pending")
        try SecureEnrollment.save(pending) // durable before the one-use code is sent; never automatically re-pair
        let client = BridgeClient(pending)
        let raw = try await client.post("v1/pair", body: JSONEncoder().encode(["code": code]), authenticated: false)
        struct Paired: Decodable { let device: String; let credential: String }
        let reply = try JSONDecoder().decode(Paired.self, from: raw)
        guard reply.device.range(of: "^[0-9a-f]{24}$", options: .regularExpression) != nil,
              reply.credential.range(of: "^[A-Za-z0-9_-]{32,128}$", options: .regularExpression) != nil else { throw BridgeFailure.invalidResponse }
        pending.state = "paired"; pending.device = reply.device; pending.credential = reply.credential
        try SecureEnrollment.save(pending)
        return pending
    }
    static func replaceTrust(_ certificate: Data) async throws -> Enrollment {
        guard !RuntimeMode.demoOnly else { throw BridgeFailure.notConfigured }
        guard var candidate = try SecureEnrollment.load(), candidate.state == "paired" else { throw BridgeFailure.notConfigured }
        candidate.anchors = try Enrollment.certificates(certificate)
        let probe = BridgeClient(candidate, persistRevocation: false), started = ProcessInfo.processInfo.systemUptime
        let r = try await probe.send(BridgeRequest("snapshot"))
        guard r.outcome == "observed", let valid = r.data["valid_for_ms"].number, (1...5000).contains(valid),
              let age = r.data["age_ms"].number, age >= 0, age + valid <= 5000,
              ProcessInfo.processInfo.systemUptime < started + Double(valid) / 1000 else { throw BridgeFailure.expired }
        try SecureEnrollment.save(candidate)
        return candidate
    }
}
