import XCTest
import SwiftUI
import UIKit
@testable import StillWater

@MainActor final class SnapshotTests: XCTestCase {
    func testArtworkRenderingTimingBaseline() async throws {
        let model = await ReviewStates.make("still-artwork")
        let preview = try XCTUnwrap(model.artwork)
        let cached = try XCTUnwrap(preview.uiImage(palette:"sage"))
        XCTAssertTrue(preview.uiImage(palette:"sage") === cached)
        let start = ProcessInfo.processInfo.systemUptime
        for _ in 0..<12 { XCTAssertNotNil(preview.uiImage(palette:"sage")) }
        let elapsed = ProcessInfo.processInfo.systemUptime - start
        print("ARTWORK_RENDER_BASELINE twelve_320_palette_renders_ms=\(elapsed*1000)")
        // Diagnostic only: simulator timing is not an iPhone acceptance threshold.
    }
    func testArtworkRenderingUsesSelectedPaletteAndKeepsBrightnessDetail() throws {
        // Black, white and saturated red/green/blue RGB565 input.
        let source = Data([0,0, 255,255, 248,0, 7,224, 0,31, 0,0, 255,255, 248,0, 7,224])
        let preview = Preview(reference:"test",pixels:source,side:3,deadline:160)
        var rendered: [Data] = []
        for name in ["sage","sand","slate"] {
            let image = try XCTUnwrap(preview.uiImage(palette:name)?.cgImage)
            XCTAssertEqual(image.width,3); XCTAssertEqual(image.height,3)
            let bytes = try XCTUnwrap(image.dataProvider?.data) as Data
            rendered.append(bytes)
            let p = FieldPalette.fallback(name)
            for pixel in 0..<9 {
                for (channel,range) in [min(p.dark.r,p.mid.r,p.light.r)...max(p.dark.r,p.mid.r,p.light.r),
                                        min(p.dark.g,p.mid.g,p.light.g)...max(p.dark.g,p.mid.g,p.light.g),
                                        min(p.dark.b,p.mid.b,p.light.b)...max(p.dark.b,p.mid.b,p.light.b)].enumerated() {
                    let value = Double(bytes[pixel*4+channel])/255
                    XCTAssertGreaterThanOrEqual(value,range.lowerBound-1/255)
                    XCTAssertLessThanOrEqual(value,range.upperBound+1/255)
                }
            }
            func brightness(_ pixel: Int) -> Int { (0..<3).reduce(0) { $0 + Int(bytes[pixel*4+$1]) } }
            XCTAssertLessThan(brightness(0),brightness(4))
            XCTAssertLessThan(brightness(4),brightness(2))
            XCTAssertLessThan(brightness(2),brightness(3))
            XCTAssertLessThan(brightness(3),brightness(1))
        }
        XCTAssertNotEqual(rendered[0],rendered[1]); XCTAssertNotEqual(rendered[1],rendered[2])
        XCTAssertEqual(preview.pixels,source)
    }
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
            let fixture = try XCTUnwrap(visible.first { $0.id == "fixture" })
            XCTAssertEqual(fixture.frame.minX,48,accuracy:0.5)
            XCTAssertEqual(fixture.frame.minY,24,accuracy:0.5)
            let taps = visible.filter { $0.tap }
            for i in taps.indices { for j in taps.indices where j > i {
                XCTAssertFalse(taps[i].frame.insetBy(dx:0.25,dy:0.25).intersects(taps[j].frame.insetBy(dx:0.25,dy:0.25)),"Overlapping \(state): \(taps[i].id) / \(taps[j].id)")
                XCTAssertFalse(taps[i].frame.insetBy(dx:-3.75,dy:-3.75).intersects(taps[j].frame.insetBy(dx:-3.75,dy:-3.75)),"Less than 8-unit target gap \(state): \(taps[i].id) / \(taps[j].id)")
            } }
            if state == "library-albums" {
                let covers = visible.filter { $0.id.hasPrefix("library-cover-") }.sorted { $0.frame.minY == $1.frame.minY ? $0.frame.minX < $1.frame.minX : $0.frame.minY < $1.frame.minY }
                XCTAssertGreaterThanOrEqual(covers.count,6)
                for (index,cover) in covers.prefix(6).enumerated() {
                    XCTAssertEqual(cover.frame.minX,48+CGFloat(index)*120,accuracy:1)
                    XCTAssertEqual(cover.frame.width,104,accuracy:1)
                    XCTAssertEqual(cover.frame.height,104,accuracy:1)
                }
            }
            if state == "queue" {
                let titles = visible.filter { $0.id.hasPrefix("queue-track-title-") }
                XCTAssertFalse(titles.isEmpty)
                for title in titles {
                    XCTAssertFalse(title.text.isEmpty)
                    XCTAssertEqual(title.fontSize,15)
                    XCTAssertGreaterThanOrEqual(title.frame.minY,340)
                    XCTAssertLessThanOrEqual(title.frame.maxY,392)
                }
            }
            if state == "artist-following" {
                let tab = try XCTUnwrap(visible.first { $0.id == "artist-tab-albums" })
                let name = try XCTUnwrap(visible.first { $0.id == "detail-title" })
                XCTAssertEqual(tab.frame.minX,name.frame.minX,accuracy:1)
            }
            if state.hasPrefix("artist-"), let albums = visible.first(where: { $0.id.hasPrefix("artist-album-") }) {
                XCTAssertLessThanOrEqual(albums.frame.maxY,472.5,"Artist album row must clear the bottom edge")
            }
            if state == "touched" {
                let artist = try XCTUnwrap(visible.first { $0.id == "artist" })
                let title = try XCTUnwrap(visible.first { $0.id == "track-title" })
                let album = try XCTUnwrap(visible.first { $0.id == "album" })
                XCTAssertEqual(artist.fontSize,15)
                XCTAssertEqual(title.frame.minY-artist.frame.maxY,12,accuracy:2)
                XCTAssertEqual(album.frame.minY-title.frame.maxY,14,accuracy:2)
                let ask = try XCTUnwrap(visible.first { $0.id == "ask" })
                let play = try XCTUnwrap(visible.first { $0.id == "play-pause" })
                XCTAssertEqual(ask.frame.midX,play.frame.midX,accuracy:0.5)
                for id in ["previous","next","amp-down","amp-up"] {
                    XCTAssertEqual(try XCTUnwrap(visible.first { $0.id == id }).frame.midY,play.frame.midY,accuracy:0.5)
                }
                XCTAssertFalse(visible.contains { $0.id == "find" })
                XCTAssertLessThanOrEqual(ask.frame.maxY,448.5,"Ask ring must have breathing room above the waterline")
                for (id,rect) in [("previous",CGRect(x:363,y:268,width:98,height:96)),("play-pause",CGRect(x:472,y:264,width:104,height:104)),("next",CGRect(x:587,y:268,width:98,height:96)),("amp-down",CGRect(x:816,y:276,width:80,height:80)),("amp-up",CGRect(x:920,y:276,width:80,height:80))] {
                    let actual = try XCTUnwrap(visible.first { $0.id == id }?.frame)
                    XCTAssertEqual(actual.minX,rect.minX,accuracy:4); XCTAssertEqual(actual.minY,rect.minY,accuracy:4)
                    XCTAssertEqual(actual.width,rect.width,accuracy:4); XCTAssertEqual(actual.height,rect.height,accuracy:4)
                }
            }
            let musicStates = ["still-fallback","still-artwork","touched","paused","stopped","longtitle","noart","offline","pending","unknown","wake"]
            if musicStates.contains(state) {
                let touched = ["touched","paused","offline","pending","unknown"].contains(state)
                let cover = try XCTUnwrap(visible.first { $0.id == "cover" }?.frame)
                XCTAssertEqual(cover.minX,48,accuracy:4); XCTAssertEqual(cover.minY,touched ? 56 : 60,accuracy:4)
                XCTAssertEqual(cover.width,touched ? 256 : 296,accuracy:4); XCTAssertEqual(cover.width,cover.height,accuracy:1)
                let text = try XCTUnwrap(visible.first { $0.id == "now-text-block" }?.frame)
                XCTAssertEqual(text.minX,touched ? 344 : 392,accuracy:4)
                XCTAssertEqual(text.width,touched ? 656 : 608,accuracy:4)
                if state != "stopped" {
                    let line = try XCTUnwrap(visible.first { $0.id == "waterline" }?.frame)
                    XCTAssertEqual(line.minY,472,accuracy:4); XCTAssertEqual(line.width,1048,accuracy:1)
                }
            }
            for title in visible where title.fontSize >= 26 && !title.tap && !title.scrollClipped {
                try assertContrast(image,title:title,state:state)
            }
            for name in [Design.name(serif:true),Design.name(serif:true,italic:true),Design.name(),"InstrumentSerif-Regular","Geist-Regular"] {
                XCTAssertNotNil(UIFont(name:name,size:20),"Missing bundled font \(name)")
            }
            window.isHidden = true
        }
    }
    private func assertTextFits(_ e: AuditElement,state: String) throws {
        let size = (e.fontSize * Design.scale * 2).rounded() / (2 * Design.scale)
        let font = try XCTUnwrap(UIFont(name:e.fontName,size:size))
        var attributes = DesignText.attributes(units:e.fontSize,serif:e.fontName.hasPrefix("TimesNewRoman"),
            italic:e.fontName.contains("Italic"),caps:e.tracking > 0)
        attributes[.kern] = e.tracking
        if e.maxLines > 1, let paragraph = (attributes[.paragraphStyle] as? NSParagraphStyle)?.mutableCopy() as? NSMutableParagraphStyle {
            paragraph.lineBreakMode = .byWordWrapping
            attributes[.paragraphStyle] = paragraph
        }
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
