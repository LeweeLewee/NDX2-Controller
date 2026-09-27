import XCTest
@testable import StillWater

@MainActor final class TrustTests: XCTestCase {
    func testTLSFailureReportsOnlyAllowlistedDiagnosticFields() {
        let diagnostic = TLSFailure(networkCode:-1200,trustStep:"certificate evaluation",trustCode:-67818)
        let text = PairingFailure(stage:.connect,cause:diagnostic).message
        XCTAssertTrue(text.contains("URL -1200"))
        XCTAssertTrue(text.contains("certificate evaluation -67818"))
        let record = Enrollment(origin:URL(string:"https://127.0.0.1")!,anchors:[],state:"pending")
        let trust = PinnedTrust(record)
        let error = URLError(.secureConnectionFailed,userInfo:[NSLocalizedDescriptionKey:"secret"])
        XCTAssertTrue(trust.failure(error).message.contains("trust callback not reached"))
        XCTAssertFalse(trust.failure(error).message.contains("secret"))
    }

    #if STILL_WATER_LIVE_BETA
    private func fixture() throws -> [String:Any] {
        let url = try XCTUnwrap(Bundle(for:Self.self).url(forResource:"TLSProbe",withExtension:"json"))
        let values = try XCTUnwrap(JSONSerialization.jsonObject(with:Data(contentsOf:url)) as? [String:Any])
        guard values["available"] as? Bool == true else { throw XCTSkip("Loopback TLS peer is started by CI") }
        return values
    }
    private func client(_ values: [String:Any], peer: String = "valid", anchor: String = "root") throws -> BridgeClient {
        let origin = try Enrollment.origin(XCTUnwrap(values[peer] as? String))
        XCTAssertEqual(origin.host,"127.0.0.1")
        let der = try XCTUnwrap(Data(base64Encoded:XCTUnwrap(values[anchor] as? String)))
        return BridgeClient(Enrollment(origin:origin,anchors:[der],state:"pending"),persistRevocation:false)
    }
    func testURLSessionAcceptsOnlyImportedCAAndValidHost() async throws {
        let connection = try client(fixture())
        let reply = try await connection.post("v1/pair",body:Data("{\"code\":\"synthetic\"}".utf8),authenticated:false)
        XCTAssertEqual(String(decoding:reply,as:UTF8.self),"{\"synthetic_tls_probe\":true}")
    }
    func testURLSessionRejectsUnrelatedAnchor() async throws {
        let connection = try client(fixture(),anchor:"unrelated")
        do {
            _ = try await connection.post("v1/pair",body:Data("{}".utf8),authenticated:false)
            XCTFail("Accepted an unrelated root")
        } catch {
            let failure = try XCTUnwrap(error as? TLSFailure)
            XCTAssertEqual(failure.trustStep,"certificate evaluation")
            XCTAssertNotNil(failure.trustCode)
        }
    }
    func testURLSessionRejectsWrongHostEvenWithImportedCA() async throws {
        let connection = try client(fixture(),peer:"wrong-host")
        do {
            _ = try await connection.post("v1/pair",body:Data("{}".utf8),authenticated:false)
            XCTFail("Accepted a certificate for the wrong host")
        } catch {
            let failure = try XCTUnwrap(error as? TLSFailure)
            XCTAssertEqual(failure.trustStep,"certificate evaluation")
            XCTAssertNotNil(failure.trustCode)
        }
    }
    #endif
}
