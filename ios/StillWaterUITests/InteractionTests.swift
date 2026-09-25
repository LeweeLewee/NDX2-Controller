import XCTest

final class InteractionTests: XCTestCase {
    func testSystemKeyboardAndLandscapeMask() {
        let app = XCUIApplication()
        app.launchArguments = ["--fixture","--review-state","find"]
        XCUIDevice.shared.orientation = .landscapeRight
        app.launch()
        let field = app.textFields.firstMatch
        XCTAssertTrue(field.waitForExistence(timeout:10)); field.tap(); field.typeText("Evening listening")
        XCTAssertTrue(app.keyboards.firstMatch.waitForExistence(timeout:5))
        let image = XCTAttachment(screenshot:app.screenshot()); image.name = "Find-system-keyboard"; image.lifetime = .keepAlways; add(image)
        XCTAssertTrue(app.buttons["search"].exists)
        app.buttons["search"].tap()
        XCTAssertFalse(app.keyboards.firstMatch.exists)
        XCTAssertEqual(app.statusBars.count,0)
    }
    func testFirstContactRevealsWithoutTransportCommand() {
        let app = XCUIApplication(); app.launchArguments = ["--fixture"]; app.launch()
        let wake = app.otherElements["Wake and reveal controls"]
        if wake.waitForExistence(timeout:5) { wake.tap() }
        else { app.tap() }
        XCTAssertTrue(app.buttons["play-pause"].waitForExistence(timeout:5))
        XCTAssertTrue(app.staticTexts["A Still Morning"].exists)
    }
}
