import XCTest

final class InteractionTests: XCTestCase {
    func testPhoneLayoutAndRestoredMusicActions() {
        let app = XCUIApplication(); app.launchArguments = ["--fixture"]
        XCUIDevice.shared.orientation = .landscapeLeft; app.launch()
        XCTAssertTrue(app.buttons["wake-contact"].waitForExistence(timeout:5)); app.buttons["wake-contact"].tap()
        let play = app.buttons["play-pause"]
        XCTAssertTrue(play.waitForExistence(timeout:10))
        XCTAssertGreaterThanOrEqual(play.frame.width,80)
        XCTAssertGreaterThanOrEqual(app.buttons["previous"].frame.width,72)
        XCTAssertGreaterThanOrEqual(app.buttons["next"].frame.width,72)
        XCTAssertEqual(app.buttons["amp-down"].label,"Volume down")
        XCTAssertFalse(app.staticTexts["AMP"].exists)
        let screen = app.windows.firstMatch.frame
        XCTAssertLessThan(app.buttons["library"].frame.maxX,screen.maxX - 8)
        XCTAssertGreaterThan(app.buttons["library"].frame.maxX,screen.maxX - 70)
        let like = app.buttons["now-like"]
        XCTAssertTrue(like.isEnabled); like.tap()
        expectLabel(like,"♥  Liked")
        like.tap(); expectLabel(like,"♡  Like")
        app.buttons["now-artist"].tap()
        let membership = app.buttons["membership-write"]
        XCTAssertTrue(membership.waitForExistence(timeout:5)); expectLabel(membership,"Follow")
        membership.tap(); expectLabel(membership,"Unfollow")
        membership.tap(); expectLabel(membership,"Follow")
        app.buttons["back-now"].tap()
        app.buttons["now-album"].tap()
        XCTAssertTrue(membership.waitForExistence(timeout:5)); expectLabel(membership,"Add to library")
        membership.tap(); expectLabel(membership,"Remove from library")
        membership.tap(); expectLabel(membership,"Add to library")
        let detail = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); detail.name = "Remediation-album-actions"; detail.lifetime = .keepAlways; add(detail)
        app.buttons["back-now"].tap()
        let image = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); image.name = "Remediation-full-phone"; image.lifetime = .keepAlways; add(image)
    }
    private func expectLabel(_ element: XCUIElement,_ label: String) {
        let changed = XCTNSPredicateExpectation(predicate:NSPredicate(format:"label == %@",label),object:element)
        XCTAssertEqual(XCTWaiter.wait(for:[changed],timeout:5),.completed)
    }
    func testSystemKeyboardAndLandscapeMask() {
        let app = XCUIApplication()
        app.launchArguments = ["--fixture","--review-state","find"]
        // Device orientation is opposite the matching interface orientation.
        XCUIDevice.shared.orientation = .landscapeLeft
        app.launch()
        let field = app.textFields.firstMatch
        XCTAssertTrue(field.waitForExistence(timeout:10)); field.tap(); field.typeText("Evening listening")
        XCTAssertTrue(app.keyboards.firstMatch.waitForExistence(timeout:5))
        let image = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); image.name = "Find-system-keyboard"; image.lifetime = .keepAlways; add(image)
        // Label-based matching also finds the system keyboard's Search key.
        let search = app.buttons.matching(NSPredicate(format:"identifier == %@","search")).element
        XCTAssertTrue(search.exists)
        // Exercise the declared target outside the small outline glyph itself.
        search.coordinate(withNormalizedOffset:CGVector(dx:0.1,dy:0.5)).tap()
        assertKeyboardDismissed(app)
        XCTAssertTrue(app.buttons["filter-albums"].exists)
        field.tap(); field.typeText("\n")
        assertKeyboardDismissed(app)
        let result = XCTAttachment(screenshot:XCUIScreen.main.screenshot()); result.name = "Find-after-search"; result.lifetime = .keepAlways; add(result)
        XCTAssertEqual(app.statusBars.count,0)
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
        XCTAssertTrue(app.textFields.firstMatch.waitForExistence(timeout:5))
    }
    private func assertKeyboardDismissed(_ app: XCUIApplication) {
        let hidden = XCTNSPredicateExpectation(predicate:NSPredicate(format:"exists == false"),object:app.keyboards.firstMatch)
        XCTAssertEqual(XCTWaiter.wait(for:[hidden],timeout:5),.completed)
    }
}
