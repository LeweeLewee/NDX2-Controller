import XCTest
@testable import StillWater

@MainActor final class PreviewTests: XCTestCase {
    func testPreviewBuildAndBundledMetadataAgree() {
        let declared = Bundle.main.object(forInfoDictionaryKey:"StillWaterBuildMode") as? String
        XCTAssertEqual(RuntimeMode.demoOnly, declared == "STILL_WATER_PREVIEW")
        if RuntimeMode.demoOnly { XCTAssertTrue(RuntimeMode.fixture) }
    }
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
