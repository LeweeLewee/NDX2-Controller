import XCTest
import SwiftUI
import UIKit
@testable import StillWater

@MainActor final class SnapshotTests: XCTestCase {
    func testEveryNativeStateGeometryFontsContrastAndCapture() async throws {
        for state in ReviewStates.all where state != "keyboard" { // real system keyboard is covered by the UI test target
            let model = await ReviewStates.make(state)
            var elements: [AuditElement] = []
            let content = StillWaterView(model:model,auditSink:{ elements = $0 },snapshot:true)
                .scaleEffect(Design.scale).frame(width:Design.windowWidth,height:Design.windowHeight).clipped()
            let controller = UIHostingController(rootView:content)
            // This test window represents only the inlay, not the phone's notched screen.
            controller.safeAreaRegions = []
            let bounds = CGRect(x:0,y:0,width:Design.windowWidth,height:Design.windowHeight)
            let scene = UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.first
            let window = scene.map { UIWindow(windowScene:$0) } ?? UIWindow(frame:bounds)
            window.frame = bounds
            window.rootViewController = controller; window.makeKeyAndVisible()
            controller.view.frame = window.bounds
            try await Task.sleep(nanoseconds:300_000_000)
            controller.view.layoutIfNeeded()
            XCTAssertFalse(elements.isEmpty,"No geometry was captured for \(state)")
            let format = UIGraphicsImageRendererFormat(); format.scale = 2
            let image = UIGraphicsImageRenderer(bounds:window.bounds,format:format).image { _ in
                controller.view.drawHierarchy(in:window.bounds,afterScreenUpdates:true)
            }
            XCTAssertEqual(image.cgImage?.width,1510); XCTAssertEqual(image.cgImage?.height,692)
            let attachment = XCTAttachment(image:image); attachment.name = "StillWater-\(state)-1510x692"; attachment.lifetime = .keepAlways; add(attachment)
            let visible = elements.filter { $0.frame.intersects(CGRect(x:0,y:0,width:1048,height:480)) }
            for e in visible {
                if e.fontSize > 0 { XCTAssertGreaterThanOrEqual(e.fontSize,15,"\(state) \(e.id)") }
                if !e.text.isEmpty { try assertTextFits(e,state:state) }
                if !e.scrollClipped {
                    XCTAssertGreaterThanOrEqual(e.frame.minX,-0.5,"\(state) \(e.id)")
                    XCTAssertGreaterThanOrEqual(e.frame.minY,-0.5,"\(state) \(e.id)")
                    XCTAssertLessThanOrEqual(e.frame.maxX,1048.5,"\(state) \(e.id)")
                    XCTAssertLessThanOrEqual(e.frame.maxY,480.5,"\(state) \(e.id)")
                }
                if e.tap {
                    XCTAssertGreaterThanOrEqual(e.frame.width,e.pill ? 96 : 72,"\(state) \(e.id)")
                    XCTAssertGreaterThanOrEqual(e.frame.height,e.pill ? 56 : 64,"\(state) \(e.id)")
                }
            }
            let taps = visible.filter { $0.tap }
            for i in taps.indices { for j in taps.indices where j > i {
                XCTAssertFalse(taps[i].frame.insetBy(dx:0.25,dy:0.25).intersects(taps[j].frame.insetBy(dx:0.25,dy:0.25)),"Overlapping \(state): \(taps[i].id) / \(taps[j].id)")
                XCTAssertFalse(taps[i].frame.insetBy(dx:-3.75,dy:-3.75).intersects(taps[j].frame.insetBy(dx:-3.75,dy:-3.75)),"Less than 8-unit target gap \(state): \(taps[i].id) / \(taps[j].id)")
            } }
            if state == "touched" {
                for (id,rect) in [("previous",CGRect(x:460,y:282,width:72,height:64)),("play-pause",CGRect(x:552,y:274,width:80,height:80)),("next",CGRect(x:640,y:282,width:72,height:64)),("amp-down",CGRect(x:848,y:282,width:72,height:64)),("amp-up",CGRect(x:928,y:282,width:72,height:64))] {
                    let actual = try XCTUnwrap(visible.first { $0.id == id }?.frame)
                    XCTAssertEqual(actual.minX,rect.minX,accuracy:4); XCTAssertEqual(actual.minY,rect.minY,accuracy:4)
                    XCTAssertEqual(actual.width,rect.width,accuracy:4); XCTAssertEqual(actual.height,rect.height,accuracy:4)
                }
            }
            let musicStates = ["still-fallback","still-artwork","touched","paused","stopped","longtitle","noart","offline","pending","unknown","wake"]
            if musicStates.contains(state) {
                let touched = ["touched","paused","offline","pending","unknown"].contains(state)
                let cover = try XCTUnwrap(visible.first { $0.id == "cover" }?.frame)
                XCTAssertEqual(cover.minX,48,accuracy:4); XCTAssertEqual(cover.minY,touched ? 56 : 72,accuracy:4)
                XCTAssertEqual(cover.width,touched ? 248 : 272,accuracy:4); XCTAssertEqual(cover.width,cover.height,accuracy:1)
                let text = try XCTUnwrap(visible.first { $0.id == "now-text-block" }?.frame)
                XCTAssertEqual(text.minX,touched ? 336 : 368,accuracy:4)
                XCTAssertEqual(text.width,touched ? 664 : 632,accuracy:4)
                if state != "stopped" {
                    let line = try XCTUnwrap(visible.first { $0.id == "waterline" }?.frame)
                    XCTAssertEqual(line.minY,472,accuracy:4); XCTAssertEqual(line.width,1048,accuracy:1)
                }
            }
            for title in visible where title.fontSize >= 26 && !title.tap && !title.scrollClipped {
                try assertContrast(image,title:title,state:state)
            }
            for name in ["InstrumentSerif-Regular","InstrumentSerif-Italic","Geist-Regular","Geist-Medium"] {
                XCTAssertNotNil(UIFont(name:name,size:20),"Missing bundled font \(name)")
            }
            window.isHidden = true
        }
    }
    private func assertTextFits(_ e: AuditElement,state: String) throws {
        let size = (e.fontSize * Design.scale * 2).rounded() / (2 * Design.scale)
        let font = try XCTUnwrap(UIFont(name:e.fontName,size:size))
        var attributes = DesignText.attributes(units:e.fontSize,serif:e.fontName.hasPrefix("Instrument"),
            italic:e.fontName.hasSuffix("Italic"),caps:e.fontName.hasSuffix("Medium"))
        attributes[.kern] = e.tracking
        let measured = (e.text as NSString).boundingRect(with:CGSize(width:e.frame.width,height:10000),
            options:[.usesLineFragmentOrigin,.usesFontLeading],attributes:attributes,context:nil)
        let line = (attributes[.paragraphStyle] as? NSParagraphStyle)?.maximumLineHeight ?? font.lineHeight
        let allowed = e.truncates ? min(measured.height,line * CGFloat(e.maxLines)) : measured.height
        XCTAssertLessThanOrEqual(allowed,e.frame.height+2,"Clipped glyphs \(state): \(e.id)")
    }
    private func assertContrast(_ image: UIImage,title: AuditElement,state: String) throws {
        let cg = try XCTUnwrap(image.cgImage), w = cg.width, h = cg.height
        var pixels = [UInt8](repeating:0,count:w*h*4)
        let ctx = try XCTUnwrap(CGContext(data:&pixels,width:w,height:h,bitsPerComponent:8,bytesPerRow:w*4,
            space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue))
        ctx.draw(cg,in:CGRect(x:0,y:0,width:w,height:h))
        let scale = Double(w)/1048
        // Match the source gate's field strip above each title, using the native rendered pixels.
        let y = max(0,min(h-1,Int((title.frame.minY-8)*scale)))
        var red = 0, green = 0, blue = 0, count = 0
        for x in stride(from:max(0,Int(title.frame.minX)),to:min(1048,Int(title.frame.maxX)),by:8) {
            let index = (y*w + min(w-1,Int(Double(x)*scale)))*4
            red += Int(pixels[index]); green += Int(pixels[index+1]); blue += Int(pixels[index+2]); count += 1
        }
        XCTAssertGreaterThan(count,0)
        guard count > 0 else { return }
        // Match still-water-gates.py: average the strip, then blend ink and measure.
        // Taking its brightest pixel mistakes the adjacent kicker's glyph for the field.
        let bg = RGB(Double(red/count)/255,Double(green/count)/255,Double(blue/count)/255)
        let fg = bg.mix(RGB(0xF1EBDF),title.opacity)
        let ratio = (fg.luminance+0.05)/(bg.luminance+0.05)
        XCTAssertGreaterThanOrEqual(ratio,title.opacity >= 0.99 ? 7 : 4.5,"\(state) contrast: \(title.id)")
    }
    func testPaletteExtractionAndFallbackContrast() async throws {
        for name in ["sage","sand","slate"] {
            let p = FieldPalette.fallback(name)
            for y in stride(from:0.0,through:480.0,by:16) { for x in stride(from:0.0,through:1048.0,by:16) {
                let bg = p.pixel(x:x,y:y), ink = RGB(0xF1EBDF)
                XCTAssertGreaterThanOrEqual((ink.luminance+0.05)/(bg.luminance+0.05),7)
                XCTAssertGreaterThanOrEqual((bg.mix(ink,0.7).luminance+0.05)/(bg.luminance+0.05),4.5)
            } }
        }
        let model = await ReviewStates.make("still-artwork")
        let preview = try XCTUnwrap(model.colorPreview)
        XCTAssertEqual(FieldPalette.extract(preview,fallback:"sage"),FieldPalette.extract(preview,fallback:"sage"))
    }
}
