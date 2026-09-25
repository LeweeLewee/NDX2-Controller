import XCTest

final class InteractionTests: XCTestCase {
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
        search.tap()
        XCTAssertFalse(app.keyboards.firstMatch.exists)
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
    }
}
