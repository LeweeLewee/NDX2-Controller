import XCTest
@testable import StillWater

@MainActor final class PreviewTests: XCTestCase {
    func testPreviewBuildAndBundledMetadataAgree() {
        let declared = Bundle.main.object(forInfoDictionaryKey:"StillWaterBuildMode") as? String
        XCTAssertEqual(RuntimeMode.demoOnly, declared != "STILL_WATER_LIVE_BETA")
        if RuntimeMode.demoOnly { XCTAssertTrue(RuntimeMode.fixture) }
    }
    func testLiveBetaDoesNotEnableSpeechCapture() {
        XCTAssertFalse(RuntimeMode.speechEnabled)
    }
    #if STILL_WATER_LIVE_BETA
    func testLiveTransportRequiresEnrollmentBeforeNetwork() async {
        XCTAssertFalse(RuntimeMode.demoOnly)
        let record = Enrollment(origin:URL(string:"https://127.0.0.1:1")!,anchors:[],state:"pending")
        let client = BridgeClient(record, persistRevocation:false)
        do { _ = try await client.send(BridgeRequest("snapshot")); XCTFail("Unpaired transport opened a connection") }
        catch { XCTAssertEqual(error as? BridgeFailure,.notConfigured) }
        XCTAssertThrowsError(try Enrollment.origin("http://127.0.0.1"))
        XCTAssertThrowsError(try Enrollment.origin("https://user:secret@localhost"))
        XCTAssertThrowsError(try Enrollment.certificates(Data()))
    }
    #endif
    #if STILL_WATER_PREVIEW
    func testPreviewRejectsLiveTransportAndEnrollmentBeforeIO() async {
        let record = Enrollment(origin:URL(string:"https://127.0.0.1:1")!,anchors:[],state:"paired")
        let client = BridgeClient(record)
        do { _ = try await client.post("v1/request",body:Data(),authenticated:false); XCTFail("Preview opened live transport") }
        catch { XCTAssertEqual(error as? BridgeFailure,.notConfigured) }
        do { _ = try await BridgeClient.pair(origin:"invalid",certificate:Data(),code:""); XCTFail("Preview attempted enrollment") }
        catch { XCTAssertEqual(error as? BridgeFailure,.notConfigured) }
        do { _ = try await BridgeClient.replaceTrust(Data()); XCTFail("Preview attempted trust replacement") }
        catch { XCTAssertEqual(error as? BridgeFailure,.notConfigured) }
        XCTAssertThrowsError(try SecureEnrollment.load())
        XCTAssertThrowsError(try SecureEnrollment.save(record))
        XCTAssertThrowsError(try SecureEnrollment.forget())
        let model = ControllerModel(transport:FixtureTransport(),restore:false)
        model.replaceTransport(client)
        XCTAssertTrue(model.fixture); XCTAssertFalse(model.active)
    }
    #endif
}
