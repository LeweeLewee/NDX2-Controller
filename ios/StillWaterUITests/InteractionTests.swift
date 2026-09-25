import XCTest

final class InteractionTests: XCTestCase {
    func testPhoneLayoutAndRestoredMusicActions() {
        let app = XCUIApplication(); app.launchArguments = ["--fixture"]
        XCUIDevice.shared.orientation = .landscapeLeft; app.launch()
        XCTAssertTrue(app.buttons["wake-contact"].waitForExistence(timeout:5)); app.buttons["wake-contact"].tap()
        let play = app.buttons["play-pause"]
        XCTAssertTrue(play.waitForExistence(timeout:10))
        XCTAssertGreaterThanOrEqual(play.frame.width,76)
        XCTAssertGreaterThanOrEqual(app.buttons["previous"].frame.width,72)
        XCTAssertGreaterThanOrEqual(app.buttons["next"].frame.width,72)
        XCTAssertEqual(app.buttons["amp-down"].label,"Volume down")
        XCTAssertFalse(app.staticTexts["AMP"].exists)
        let screen = app.windows.firstMatch.frame
        XCTAssertLessThan(app.buttons["library"].frame.maxX,screen.maxX - 8)
        XCTAssertGreaterThan(app.buttons["library"].frame.maxX,screen.maxX - 110)
        // iPhone 11 landscape safe area: 44 pt at each side, 21 pt below.
        for id in ["previous","play-pause","next","now-artist","now-album","now-like","up-next","settings","find","library"] {
            let frame = app.buttons[id].frame
            XCTAssertGreaterThanOrEqual(frame.minX,screen.minX + 52,id)
            XCTAssertLessThanOrEqual(frame.maxX,screen.maxX - 52,id)
            XCTAssertLessThanOrEqual(frame.maxY,screen.maxY - 29,id)
        }
        let like = app.buttons["now-like"]
        XCTAssertTrue(like.isEnabled); like.tap()
        expectLabel(like,"Unlike track")
        like.tap(); expectLabel(like,"Like track")
        app.buttons["now-artist"].tap()
        let membership = app.buttons["membership-write"]
        XCTAssertTrue(membership.waitForExistence(timeout:5)); expectLabel(membership,"Follow")
        membership.tap(); expectLabel(membership,"Unfollow")
        membership.tap(); expectLabel(membership,"Follow")
        app.buttons["back"].tap()
        app.buttons["settings"].tap()
        XCTAssertTrue(app.buttons["back"].waitForExistence(timeout:5))
        XCTAssertFalse(app.buttons["back-now"].exists)
        app.buttons["back"].tap()
        app.buttons["now-album"].tap()
        XCTAssertTrue(membership.waitForExistence(timeout:5)); expectLabel(membership,"Add to library")
        membership.tap(); expectLabel(membership,"Remove from library")
        membership.tap(); expectLabel(membership,"Add to library")
        let detail = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); detail.name = "Remediation-album-actions"; detail.lifetime = .keepAlways; add(detail)
        app.buttons["back"].tap()
        let image = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); image.name = "Remediation-full-phone"; image.lifetime = .keepAlways; add(image)
    }
    private func expectLabel(_ element: XCUIElement,_ label: String) {
        let changed = XCTNSPredicateExpectation(predicate:NSPredicate(format:"label == %@",label),object:element)
        XCTAssertEqual(XCTWaiter.wait(for:[changed],timeout:5),.completed)
    }
    func testSystemKeyboardAndLandscapeMask() {
        let app = XCUIApplication()
        app.launchArguments = ["--fixture","--review-state","ask-idle"]
        XCUIDevice.shared.orientation = .landscapeLeft; app.launch()
        let record = app.buttons["voice-record"]
        XCTAssertTrue(record.waitForExistence(timeout:10)); expectLabel(record,"Start recording")
        XCTAssertFalse(app.keyboards.firstMatch.exists)
        let idle = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); idle.name = "Find-idle"; idle.lifetime = .keepAlways; add(idle)
        app.buttons["type-instead"].tap()
        let field = app.textFields["typed-query"]
        XCTAssertTrue(field.waitForExistence(timeout:5)); field.tap(); field.typeText("Evening listening")
        XCTAssertTrue(app.keyboards.firstMatch.waitForExistence(timeout:5))
        let image = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); image.name = "Find-system-keyboard"; image.lifetime = .keepAlways; add(image)
        let search = app.buttons.matching(NSPredicate(format:"identifier == %@","search")).element
        XCTAssertTrue(search.exists)
        search.coordinate(withNormalizedOffset:CGVector(dx:0.1,dy:0.5)).tap()
        assertKeyboardDismissed(app)
        XCTAssertTrue(app.buttons["filter-albums"].waitForExistence(timeout:5))
        app.buttons["edit-search"].tap()
        expectLabel(record,"Start recording")
        app.buttons["type-instead"].tap()
        XCTAssertTrue(field.waitForExistence(timeout:5)); field.tap(); field.typeText("\n")
        assertKeyboardDismissed(app)
        let result = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); result.name = "Find-after-search"; result.lifetime = .keepAlways; add(result)
        XCTAssertEqual(app.statusBars.count,0)
    }
    func testVoiceStartsOnlyOnTapAndUsesSharedResults() {
        let app = XCUIApplication(); app.launchArguments = ["--fixture","--review-state","ask-idle"]
        XCUIDevice.shared.orientation = .landscapeLeft; app.launch()
        let record = app.buttons["voice-record"]
        XCTAssertTrue(record.waitForExistence(timeout:5)); expectLabel(record,"Start recording")
        record.tap(); expectLabel(record,"Stop recording")
        app.buttons["type-instead"].tap()
        XCTAssertTrue(app.textFields["typed-query"].waitForExistence(timeout:5))
        // The top typing-mode switch remains reachable above the landscape keyboard.
        app.buttons["use-voice"].tap(); expectLabel(record,"Start recording")
        record.tap(); expectLabel(record,"Stop recording")
        app.buttons["voice-search"].tap()
        XCTAssertTrue(app.buttons["filter-albums"].waitForExistence(timeout:5))
        app.buttons["back"].tap(); expectLabel(record,"Start recording")
        XCTAssertFalse(app.buttons["voice-search"].exists)
    }
    func testFirstContactRevealsWithoutTransportCommand() {
        let app = XCUIApplication(); app.launchArguments = ["--fixture"]
        XCUIDevice.shared.orientation = .landscapeLeft
        app.launch()
        let wake = app.buttons["wake-contact"]
        XCTAssertTrue(wake.waitForExistence(timeout:5)); wake.tap()
        XCTAssertTrue(app.buttons["play-pause"].waitForExistence(timeout:5))
        XCTAssertTrue(app.staticTexts["A Still Morning"].exists)
        XCTAssertEqual(app.buttons["play-pause"].label,"Pause")
        XCTAssertGreaterThan(app.windows.firstMatch.frame.width,app.windows.firstMatch.frame.height)
        let image = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); image.name = "First-contact-touched"; image.lifetime = .keepAlways; add(image)
        app.buttons["find"].tap()
        XCTAssertTrue(app.buttons["voice-record"].waitForExistence(timeout:5))
        expectLabel(app.buttons["voice-record"],"Start recording")
        XCTAssertFalse(app.buttons["ask"].exists)
    }
    private func assertKeyboardDismissed(_ app: XCUIApplication) {
        let hidden = XCTNSPredicateExpectation(predicate:NSPredicate(format:"exists == false"),object:app.keyboards.firstMatch)
        XCTAssertEqual(XCTWaiter.wait(for:[hidden],timeout:5),.completed)
    }
}
