import XCTest
@testable import StillWater

@MainActor final class ControllerTests: XCTestCase {
    final class FaultTransport: BridgeTransport {
        let fixture = FixtureTransport()
        var requests: [String] = []
        var artworkSides: [Int] = []
        var loseMutation = false
        var holdNextAction: String?
        var held: CheckedContinuation<Void, Never>?
        func release() { let continuation = held; held = nil; continuation?.resume() }
        var afterReply: ((BridgeRequest) -> Void)?
        func cancel() {}
        func send(_ request: BridgeRequest) async throws -> BridgeReply {
            requests.append(request.action)
            if request.action == "artwork" { artworkSides.append(request.args["side"]?.number ?? 80) }
            let reply = try await fixture.send(request)
            if holdNextAction == request.action {
                holdNextAction = nil
                await withCheckedContinuation { held = $0 }
            }
            afterReply?(request)
            if loseMutation && request.isMutation { throw BridgeFailure.unavailable }
            return reply
        }
    }
    func testControlsPreemptSlowReadsAndReserveOneMutationBeforeTaskStarts() async throws {
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{100},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        t.holdNextAction = "library_state"
        let oldRead = Task { await m.currentMembership() }
        await settle()
        XCTAssertNotNil(t.held); XCTAssertNotNil(m.inFlight)
        XCTAssertTrue(m.controlsAvailable, "Optional reads must not flash or block fresh controls")
        t.holdNextAction = "transport"
        m.mutate("transport",["command":.string("pause")])
        XCTAssertFalse(m.controlsAvailable)
        m.mutate("transport",["command":.string("pause")])
        // Release the cancelled read late, while a new command owns the flight.
        t.release()
        await oldRead.value; await settle()
        XCTAssertEqual(t.fixture.mutations,["transport"])
        XCTAssertFalse(m.controlsAvailable)
        XCTAssertEqual(m.pendingAction,"transport")
        m.mutate("transport",["command":.string("resume")])
        t.release(); await settle()
        XCTAssertEqual(t.fixture.mutations,["transport"])
        XCTAssertNil(m.unknownAction)
        XCTAssertTrue(m.controlsAvailable)
        m.deactivate()
    }
    func testSlowReadDoesNotPermitControlAfterSnapshotExpires() async {
        var now = 100.0
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{now},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        t.holdNextAction = "queue"
        let read = Task { await m.perform(BridgeRequest("queue")) }
        await settle(); XCTAssertTrue(m.controlsAvailable)
        now += 5
        XCTAssertFalse(m.controlsAvailable)
        m.mutate("transport",["command":.string("pause")])
        XCTAssertTrue(t.fixture.mutations.isEmpty)
        t.release(); _ = await read.value
        m.deactivate()
    }
    func testCompletedArtworkSurvivesNavigationWithoutRenewingExpiry() async throws {
        var now = 100.0
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{now},restore:false)
        m.active = true; m.snapshotMode = true
        await m.refresh(); await m.loadArtwork()
        let original = try XCTUnwrap(m.artwork)
        let field = try XCTUnwrap(m.colorPreview)
        m.navigate(.settings); m.back()
        XCTAssertEqual(m.artwork?.pixels, original.pixels)
        XCTAssertEqual(m.artwork?.deadline, original.deadline)
        XCTAssertEqual(m.colorPreview?.deadline, field.deadline)
        // A different detail must never borrow NOW's cover.
        m.navigate(.detail)
        m.context.selected = MusicItem(.object(["reference":.string("inputs/tidal/albums/2")]))
        XCTAssertNil(m.artwork)
        m.back(); XCTAssertEqual(m.artwork?.reference, original.reference)
        m.navigate(.settings)
        now = original.deadline
        await m.refresh() // Fresh player state does not extend an old image's deadline.
        m.back(); XCTAssertNil(m.artwork)
        XCTAssertNil(m.colorPreview)
        m.deactivate()
    }
    func testArtworkReuseIsClearedOnDisconnect() async throws {
        let m = ControllerModel(transport:FixtureTransport(),clock:{100},restore:false)
        m.active = true; m.snapshotMode = true
        await m.refresh(); await m.loadArtwork()
        XCTAssertNotNil(m.artwork)
        m.navigate(.settings); m.invalidate()
        await m.refresh(); m.back()
        XCTAssertNil(m.artwork)
        XCTAssertNil(m.colorPreview)
        m.deactivate()
    }
    func testQueueArtworkUsesRegisteredCoverWithoutBrowsingQueueIdentity() async throws {
        let transport = FaultTransport()
        let model = ControllerModel(transport:transport,clock:{100},restore:false)
        model.active = true; model.snapshotMode = true
        await model.refresh()
        let ref = try XCTUnwrap(model.player.artwork)
        model.context.screen = .queue
        let item = MusicItem(.object(["reference":.string("inputs/playqueue/145"),
                                     "artwork":.string(ref),"kind":.string("tracks")]))
        model.context.items = [item]
        transport.requests = []
        await model.loadQueueArtwork()
        XCTAssertEqual(model.queueArtwork[item.reference]?.reference, ref)
        XCTAssertEqual(model.queueArtwork[item.reference]?.side, 320)
        XCTAssertFalse(transport.requests.contains("browse"))
        XCTAssertTrue(transport.artworkSides.allSatisfy { $0 == 320 })
        model.deactivate()
    }
    func testBackToGridKeepsValidCoversWithoutRefetching() async throws {
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{100},restore:false)
        m.replaceTransport(t); await settle(); m.snapshotMode = true; await m.refresh()
        m.context.screen = .library
        m.context.items = [1,2].map { MusicItem(.object(["reference":.string("inputs/tidal/albums/\($0)"),"kind":.string("albums")])) }
        for _ in 0..<2 { await m.loadQueueArtwork() }
        let original = m.queueArtwork
        m.navigate(.detail)
        m.context.items = [MusicItem(.object(["reference":.string("inputs/tidal/albums/3"),"kind":.string("albums")]))]
        await m.loadQueueArtwork()
        m.back(); t.requests = []
        await m.loadQueueArtwork()
        for (ref,preview) in original {
            XCTAssertEqual(m.queueArtwork[ref]?.renderID,preview.renderID)
            XCTAssertEqual(m.queueArtwork[ref]?.deadline,preview.deadline)
        }
        XCTAssertTrue(t.requests.isEmpty, "Back reuses completed grid covers until their original deadline")
        m.deactivate()
    }
    func testArtworkCacheStaysBoundedAcrossDifferentPages() async throws {
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{100},restore:false)
        m.replaceTransport(t); await settle(); m.snapshotMode = true; await m.refresh()
        m.context.screen = .library
        for i in 1...30 {
            m.context.items = [MusicItem(.object(["reference":.string("inputs/tidal/albums/\(i)"),"kind":.string("albums")]))]
            await m.loadQueueArtwork()
            XCTAssertLessThanOrEqual(m.queueArtwork.count,24)
            XCTAssertNotNil(m.queueArtwork[m.context.items[0].reference])
        }
        m.deactivate()
    }
    func testPlayLabelRequiresFreshMatchingPlayerObservation() async throws {
        var now = 100.0
        let m = ControllerModel(transport:FixtureTransport(),clock:{now},restore:false)
        m.active = true; m.snapshotMode = true; await m.refresh()
        m.context.selected = m.player.current
        XCTAssertEqual(m.detailPlayLabel,"Playing")
        m.pendingAction = "play"; XCTAssertEqual(m.detailPlayLabel,"Starting…")
        m.pendingAction = nil; m.unknownAction = "play"; XCTAssertEqual(m.detailPlayLabel,"Check player")
        m.unknownAction = nil; now = 106; XCTAssertFalse(m.selectedIsPlaying)
        XCTAssertEqual(m.detailPlayLabel,"Play")
        m.deactivate()
    }
    func testDisconnectedLibraryIsNotReportedAsEmptyCollection() {
        let m = ControllerModel(transport:FixtureTransport(),restore:false)
        m.online = true; m.account = "disconnected"
        XCTAssertEqual(m.libraryEmptyMessage,"Connect TIDAL My Collection")
        m.account = "connected"; m.pageError = "Library unavailable"
        XCTAssertEqual(m.libraryEmptyMessage,"Library unavailable")
        m.pageError = nil
        XCTAssertEqual(m.libraryEmptyMessage,"Nothing saved here yet")
        m.online = false
        XCTAssertNotEqual(m.libraryEmptyMessage,"Nothing saved here yet")
    }
    func testSharedQueueCoverIsLoadedOnceAndKeepsOriginalExpiry() async throws {
        let t = FaultTransport()
        let m = ControllerModel(transport:t,clock:{100},restore:false)
        m.active = true; m.snapshotMode = true; await m.refresh()
        let ref = try XCTUnwrap(m.player.artwork)
        m.context.screen = .queue
        m.context.items = (0..<12).map { MusicItem(.object(["reference":.string("inputs/playqueue/\($0)"),"artwork":.string(ref)])) }
        t.requests = []
        await m.loadQueueArtwork()
        XCTAssertEqual(m.queueArtwork.count,12)
        let requests = t.requests.filter { $0 == "artwork" }.count
        XCTAssertEqual(requests,1)
        await m.loadQueueArtwork()
        XCTAssertEqual(t.requests.filter { $0 == "artwork" }.count,requests)
        XCTAssertEqual(Set(m.queueArtwork.values.map(\.renderID)).count,1)
        XCTAssertEqual(Set(m.queueArtwork.values.map(\.deadline)).count,1)
        m.deactivate()
    }
    func testCollectionCoverRenewalReadsMetadataAndPreservesDeadlineUntilReply() async throws {
        var now = 100.0
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{now},restore:false)
        m.replaceTransport(t); await settle(); m.snapshotMode = true; await m.refresh()
        m.context.screen = .library
        let item = MusicItem(.object(["reference":.string("inputs/tidal/albums/1"),"kind":.string("albums")]))
        m.context.items = [item]
        await m.loadQueueArtwork()
        let first = try XCTUnwrap(m.queueArtwork[item.reference])
        now = 155; await m.refresh(); t.requests = []
        await m.loadQueueArtwork()
        XCTAssertTrue(t.requests.contains("browse"))
        XCTAssertGreaterThan(try XCTUnwrap(m.queueArtwork[item.reference]).deadline,first.deadline)
        m.deactivate()
    }
    func testCollectionArtworkUses320AndPaletteFollowsSettledItem() async throws {
        var now = 100.0
        let transport = FaultTransport()
        let model = ControllerModel(transport:transport,clock:{now},restore:false)
        model.active = true; model.snapshotMode = true
        await model.refresh()
        model.context.screen = .library
        model.context.items = [1,2].map { MusicItem(.object(["reference":.string("inputs/tidal/albums/\($0)"),"kind":.string("albums")])) }
        for _ in 0..<2 { await model.loadQueueArtwork() }
        XCTAssertEqual(model.queueArtwork.count,2)
        XCTAssertFalse(transport.artworkSides.isEmpty)
        XCTAssertTrue(transport.artworkSides.allSatisfy { $0 == 320 })
        let first = try XCTUnwrap(model.queueArtwork[model.context.items[0].reference])
        let second = try XCTUnwrap(model.queueArtwork[model.context.items[1].reference])
        XCTAssertEqual(model.fieldPreview?.reference,first.reference)
        model.settleLibrary(firstIndex:1)
        XCTAssertEqual(model.fieldPreview?.reference,second.reference)
        model.queueArtwork[model.context.items[1].reference] = nil
        XCTAssertEqual(model.fieldPreview?.reference,first.reference,"Use loaded cover before fallback")
        now = first.deadline
        XCTAssertNil(model.fieldPreview,"Never tint with an expired preview")
        XCTAssertFalse(transport.requests.contains("play"))
        XCTAssertFalse(transport.requests.contains("library_save"))
    }
    func testSilentPreviewCollectionSupportsEveryLibraryLayout() async throws {
        let fixture = FixtureTransport(seedCollection:true)
        for kind in ["albums","tracks","artists","playlists"] {
            let page = try await fixture.send(BridgeRequest("library_page",["kind":.string(kind)]))
            let items = page.data["items"].values.map(MusicItem.init)
            XCTAssertEqual(items.count,12)
            XCTAssertTrue(items.allSatisfy { $0.kind == kind && $0.saved == "saved" })
        }
        let missing = try await fixture.send(BridgeRequest("artist_bio",["reference":.string("inputs/tidal/artists/203")]))
        XCTAssertNil(missing.data["artwork"].text)
        XCTAssertTrue(fixture.mutations.isEmpty)
    }
    func settle() async { for _ in 0..<30 { await Task.yield() } }
    func testNowRelationshipsLikeAndIndependentAlbumArtistMembership() async throws {
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{100},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        let track = m.player.current.reference
        let album = try XCTUnwrap(m.player.current.albumReference)
        let artist = try XCTUnwrap(m.player.current.artistReference)
        XCTAssertFalse(track.isEmpty)
        XCTAssertEqual(m.player.current.saved,"unsaved")
        m.toggleCurrentLike(); await settle()
        XCTAssertEqual(m.player.current.saved,"saved")
        let liked = try await t.send(BridgeRequest("library_page",["kind":.string("tracks")]))
        XCTAssertTrue(liked.data["items"].values.map(MusicItem.init).contains { $0.reference == track })
        m.details(MusicItem(.object(["reference":.string(album)]))); await settle()
        XCTAssertEqual(m.context.selected.kind,"albums"); XCTAssertEqual(m.membershipAction,"Add to library")
        m.mutate("library_save",["reference":.string(album),"saved":.bool(true)]); await settle()
        XCTAssertEqual(m.membershipAction,"Remove from library")
        m.details(MusicItem(.object(["reference":.string(artist)]))); await settle()
        XCTAssertEqual(m.context.selected.kind,"artists"); XCTAssertEqual(m.membershipAction,"Follow")
        m.mutate("library_save",["reference":.string(artist),"saved":.bool(true)]); await settle()
        XCTAssertEqual(m.membershipAction,"Unfollow")
        m.mutate("library_save",["reference":.string(artist),"saved":.bool(false)]); await settle()
        XCTAssertEqual(m.membershipAction,"Follow")
        m.back(); XCTAssertEqual(m.context.selected.reference,album)
        m.back(toNow:true); await m.refresh()
        XCTAssertEqual(m.player.current.saved,"saved")
        m.toggleCurrentLike(); await settle(); XCTAssertEqual(m.player.current.saved,"unsaved")
        m.deactivate()
    }
    func testResultMembershipTargetsRowAndPreservesBrowsingContext() async throws {
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{100},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.navigate(.find); m.context.query = "quiet"; m.context.kind = "albums"
        m.context.items = t.sample("search-albums")["data"]["items"].values.map(MusicItem.init)
        let row = m.context.items[1], other = m.context.items[0]
        m.context.scrollID = row.id
        m.mutate("library_save",["reference":.string(row.reference),"saved":.bool(true)]); await settle()
        XCTAssertEqual(m.context.screen,.find); XCTAssertEqual(m.context.query,"quiet"); XCTAssertEqual(m.context.scrollID,row.id)
        XCTAssertEqual(m.context.items[1].saved,"saved"); XCTAssertEqual(m.context.items[0],other)
        await m.currentMembership()
        XCTAssertEqual(m.player.current.saved,"unsaved")
        let page = try await t.send(BridgeRequest("library_page",["kind":.string("albums")]))
        XCTAssertEqual(page.data["items"].values.map(MusicItem.init).first { $0.reference == row.reference }?.saved,"saved")
        m.mutate("library_save",["reference":.string(row.reference),"saved":.bool(false)]); await settle()
        let removed = try await t.send(BridgeRequest("library_page",["kind":.string("albums")]))
        XCTAssertFalse(removed.data["items"].values.map(MusicItem.init).contains { $0.reference == row.reference })
        m.deactivate()
    }
    func testUnknownMembershipCannotWriteAndUnrelatedReadCannotResolveUncertainty() async {
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{100},restore:false)
        t.saved = "unknown"
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.toggleCurrentLike(); await settle(); XCTAssertTrue(t.mutations.isEmpty)
        m.unknownAction = "library_save"
        m.details(MusicItem(.object(["reference":.string("inputs/tidal/artists/1")]))); await settle()
        XCTAssertEqual(m.unknownAction,"library_save")
        m.deactivate(); m.acknowledgeUnknown()
    }
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
    func testFindEntryModesAndExplicitSearch() async {
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{100},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.fixture = false // Exercise the callback with a harmless test closure.
        var starts = 0
        m.voiceStart = { starts += 1 }
        t.requests.removeAll()
        m.navigate(.ask)
        XCTAssertEqual(m.voiceState,"idle"); XCTAssertFalse(m.context.typing)
        XCTAssertEqual(starts,0); XCTAssertFalse(t.requests.contains("search"))
        m.stopVoice(); m.submitVoice(); XCTAssertEqual(m.context.screen,.ask)
        m.startVoice(); XCTAssertEqual(starts,1)
        m.transcript = "discard me"; m.setTyping(true)
        XCTAssertEqual(m.voiceState,"idle"); XCTAssertEqual(m.transcript,"")
        m.startVoice(); XCTAssertEqual(starts,1)
        m.context.query = "   "; m.submitTypedSearch(); XCTAssertEqual(m.context.screen,.ask)
        m.context.query = String(repeating:"x",count:257); m.submitTypedSearch(); XCTAssertEqual(m.context.screen,.ask)
        XCTAssertFalse(t.requests.contains("search"))
        m.context.query = "  Evening listening  "; m.submitTypedSearch(); await settle()
        XCTAssertEqual(m.context.screen,.find); XCTAssertEqual(m.context.query,"Evening listening")
        XCTAssertTrue(t.requests.contains("search")); XCTAssertEqual(t.fixture.mutations,[])
        m.back(); XCTAssertEqual(m.context.screen,.ask); XCTAssertFalse(m.context.typing)
        XCTAssertEqual(m.context.query,""); XCTAssertEqual(starts,1)
        m.setTyping(false); XCTAssertEqual(m.voiceState,"idle"); XCTAssertEqual(starts,1)
        m.fixture = false
        m.startVoice(); m.transcript = "quiet piano"; m.stopVoice(); m.submitVoice(); await settle()
        XCTAssertEqual(m.context.screen,.find); XCTAssertEqual(m.context.query,"quiet piano")
        m.editSearch(); XCTAssertEqual(m.context.screen,.ask); XCTAssertFalse(m.context.typing)
        XCTAssertEqual(m.voiceState,"idle"); XCTAssertEqual(starts,2)
        m.startVoice(); m.back(); XCTAssertEqual(m.context.screen,.find)
        XCTAssertEqual(m.voiceState,"idle"); XCTAssertEqual(m.transcript,"")
        XCTAssertEqual(t.fixture.mutations,[]); m.deactivate()
    }
    func testFixtureTranscriptProgressRestartAndArtistHistory() async throws {
        var time = 100.0
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{time},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.navigate(.ask); m.startVoice(); XCTAssertEqual(m.transcript,"")
        time += 0.7; m.tick(); XCTAssertEqual(m.transcript,"Find")
        time += 0.7; m.tick(); XCTAssertEqual(m.transcript,"Find quiet")
        m.startVoice(); XCTAssertEqual(m.transcript,""); XCTAssertEqual(m.voiceSession,2)
        time += 2.7; await m.refresh(); m.tick(); XCTAssertEqual(m.transcript,"Find quiet instrumental albums")
        XCTAssertEqual(m.context.screen,.ask); XCTAssertTrue(t.mutations.isEmpty)
        m.stopVoice(); m.submitVoice(); await settle(); XCTAssertEqual(m.context.screen,.find)
        m.details(MusicItem(.object(["reference":.string("inputs/tidal/artists/1")]))); await settle()
        XCTAssertEqual(m.context.items.filter { $0.kind == "albums" }.count,4)
        XCTAssertNotNil(m.context.selected.biography)
        m.selectArtistTab("tracks")
        let track = try XCTUnwrap(m.context.items.first { $0.kind == "tracks" })
        XCTAssertNotNil(track.duration)
        m.context.scrollID = track.id; m.selectArtistTab("albums"); m.selectArtistTab("tracks")
        XCTAssertEqual(m.context.scrollID,track.id)
        m.details(track); await settle(); m.back()
        XCTAssertEqual(m.context.artistTab,"tracks"); XCTAssertEqual(m.context.scrollID,track.id)
        XCTAssertTrue(t.mutations.isEmpty); m.deactivate()
    }
    func testVoiceTimeoutAndCancelCannotSubmit() async {
        var time = 100.0
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),clock:{time},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.navigate(.ask); XCTAssertEqual(m.voiceState,"idle"); m.startVoice(); XCTAssertEqual(m.voiceState,"recording")
        time += 30; await m.refresh(); m.tick()
        XCTAssertEqual(m.voiceState,"stopped"); XCTAssertEqual(t.mutations,[])
        m.startVoice(); m.back(); XCTAssertEqual(m.voiceState,"idle"); XCTAssertEqual(m.transcript,"")
        m.deactivate()
    }
    func testOnDeviceSearchNeverPlays() async {
        let t = FixtureTransport(), m = ControllerModel(transport:FixtureTransport(),restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.navigate(.ask); m.startVoice(); m.transcript = "quiet instrumental"; m.stopVoice(); m.submitVoice(); await settle()
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
    func testSilenceStopsOnlyAfterActivityAndNeverSubmits() async {
        var time = 100.0
        let t = FaultTransport(), m = ControllerModel(transport:FaultTransport(),clock:{time},restore:false)
        m.replaceTransport(t); await settle(); await m.refresh(); m.contactEnded()
        m.fixture = false; m.stopOnSilence = true; m.navigate(.ask); m.startVoice()
        time += 3; await m.refresh(); m.fixture = false; m.tick()
        XCTAssertEqual(m.voiceState,"recording")
        m.transcript = "quiet piano"; m.noteSpeechActivity()
        time += 1.5; await m.refresh(); m.fixture = false; m.tick(); XCTAssertEqual(m.voiceState,"recording")
        time += 0.5; m.tick(); XCTAssertEqual(m.voiceState,"stopped")
        XCTAssertFalse(t.requests.contains("search"))
        m.startVoice(); XCTAssertEqual(m.transcript,"")
        m.stopOnSilence = false; m.noteSpeechActivity(); time += 3
        await m.refresh(); m.fixture = false; m.tick(); XCTAssertEqual(m.voiceState,"recording")
        m.stopOnSilence = true; m.deactivate()
    }

}
