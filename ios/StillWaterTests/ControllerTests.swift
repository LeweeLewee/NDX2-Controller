import XCTest
@testable import StillWater

@MainActor final class ControllerTests: XCTestCase {
    final class FaultTransport: BridgeTransport {
        let fixture = FixtureTransport()
        var loseMutation = false
        var afterReply: ((BridgeRequest) -> Void)?
        func cancel() {}
        func send(_ request: BridgeRequest) async throws -> BridgeReply {
            let reply = try await fixture.send(request)
            afterReply?(request)
            if loseMutation && request.isMutation { throw BridgeFailure.unavailable }
            return reply
        }
    }
    func settle() async { for _ in 0..<30 { await Task.yield() } }
    func testWakeConsumesTouchAndSnapshotExpires() async {
        var time = 100.0
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{time},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh()
        m.mutate("amplifier",["direction":.string("up")]); await settle()
        XCTAssertEqual(t.mutations,[])
        m.contactEnded(); XCTAssertTrue(m.controlsAvailable)
        time += 5; m.tick(); XCTAssertFalse(m.controlsAvailable)
        m.deactivate()
    }
    func testLostReplyRemainsUnknownAndIsNeverReplayed() async {
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        t.loseMutation = true
        m.mutate("amplifier",["direction":.string("up")]); await settle()
        XCTAssertEqual(t.fixture.mutations,["amplifier"]); XCTAssertEqual(m.unknownAction,"amplifier")
        await m.refresh(); m.contactEnded(); m.mutate("amplifier",["direction":.string("up")]); await settle()
        XCTAssertEqual(t.fixture.mutations,["amplifier"])
        m.deactivate(); m.acknowledgeUnknown()
    }
    func testHistoryRetainsQueryFilterAndScrollWithBoundFour() {
        let m = ControllerModel(transport:FixtureTransport(),restore:false)
        m.context = BrowseContext(screen:.find,query:"quiet",kind:"tracks",scrollID:"track-5")
        m.navigate(.settings); m.back()
        XCTAssertEqual(m.context.query,"quiet"); XCTAssertEqual(m.context.scrollID,"track-5")
        for _ in 0..<7 { m.navigate(.display) }
        XCTAssertEqual(m.history.count,4)
    }
    func testVoiceTimeoutAndCancelCannotSubmit() async {
        var time = 100.0
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{time},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.navigate(.ask); XCTAssertEqual(m.voiceState,"recording")
        time += 30; await m.refresh(); m.tick()
        XCTAssertEqual(m.voiceState,"stopped"); XCTAssertEqual(t.mutations,[])
        m.startVoice(); m.back(); XCTAssertEqual(m.voiceState,"idle"); XCTAssertEqual(m.transcript,"")
        m.deactivate()
    }
    func testOnDeviceSearchNeverPlays() async {
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.navigate(.ask); m.transcript = "quiet instrumental"; m.submitVoice(); await settle()
        XCTAssertEqual(m.context.screen,.find); XCTAssertEqual(m.context.query,"quiet instrumental")
        XCTAssertEqual(t.mutations,[]); m.deactivate()
    }
    func testLateMutationReplyIsUnknownWithoutReplay() async {
        var time = 100.0
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{time},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        t.afterReply = { if $0.isMutation { time += 8 } }
        m.mutate("transport",["command":.string("next")]); await settle()
        XCTAssertEqual(m.unknownAction,"transport"); XCTAssertEqual(t.fixture.mutations,["transport"])
        m.deactivate(); m.acknowledgeUnknown()
    }
    func testDeactivationDiscardsVoiceAndReleasesIdleTimer() async {
        let m = ControllerModel(transport:FixtureTransport(),restore:false)
        var idleHeld = true
        m.applyIdlePolicy = { idleHeld = $0 }
        m.activate(); await settle(); await m.refresh(); m.contactEnded(); m.navigate(.ask)
        m.transcript = "discard this"; m.deactivate()
        XCTAssertFalse(m.active); XCTAssertFalse(m.online); XCTAssertFalse(idleHeld)
        XCTAssertNil(m.artwork); XCTAssertEqual(m.transcript,""); XCTAssertEqual(m.voiceState,"idle")
    }
    func testFixtureBatteryLastReportAndOneHourBoundary() async throws {
        var time = 100.0
        let t = FixtureTransport(); t.clock = { time }
        var reply = try await t.send(BridgeRequest("charge?"))
        XCTAssertEqual(reply.data["reason"].text,"none")
        _ = try await t.send(BridgeRequest("battery_report",["level":.int(34),"charging":.bool(false),"client_id":.string("test")]))
        reply = try await t.send(BridgeRequest("charge?")); XCTAssertEqual(reply.data["charge"].text,"yes")
        time += 3600
        reply = try await t.send(BridgeRequest("charge?")); XCTAssertEqual(reply.data["reason"].text,"stale"); XCTAssertEqual(reply.data["charge"].text,"no")
        _ = try await t.send(BridgeRequest("battery_report",["level":.int(75),"charging":.bool(true),"client_id":.string("test")]))
        reply = try await t.send(BridgeRequest("charge?")); XCTAssertEqual(reply.data["reason"].text,"window"); XCTAssertEqual(reply.data["charge"].text,"no")
    }
}
