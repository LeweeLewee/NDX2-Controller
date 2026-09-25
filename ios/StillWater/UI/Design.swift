import SwiftUI
import UIKit

struct RGB: Equatable {
    var r: Double, g: Double, b: Double
    init(_ hex: UInt32) { r = Double((hex >> 16) & 255)/255; g = Double((hex >> 8) & 255)/255; b = Double(hex & 255)/255 }
    init(_ r: Double, _ g: Double, _ b: Double) { self.r = r; self.g = g; self.b = b }
    func scale(_ f: Double) -> Self { Self(r*f, g*f, b*f) }
    func mix(_ other: Self, _ fraction: Double) -> Self {
        Self(r*(1-fraction)+other.r*fraction, g*(1-fraction)+other.g*fraction, b*(1-fraction)+other.b*fraction)
    }
    var luminance: Double {
        func c(_ v: Double) -> Double { v <= 0.04045 ? v/12.92 : pow((v+0.055)/1.055, 2.4) }
        return c(r)*0.2126+c(g)*0.7152+c(b)*0.0722
    }
    var color: Color { Color(.sRGB, red: r, green: g, blue: b, opacity: 1) }
    func quiet(_ f: Double) -> Self { mix(Self((r+g+b)/3, (r+g+b)/3, (r+g+b)/3), f) }
    func distance(_ v: Self) -> Double { pow(r-v.r,2)+pow(g-v.g,2)+pow(b-v.b,2) }
}

struct FieldPalette: Equatable {
    var mid: RGB, dark: RGB, light: RGB, shade = 1.0
    static func fallback(_ name: String) -> Self {
        let p: Self
        switch name {
        case "sand": p = Self(mid: RGB(0x7A6858), dark: RGB(0x231A16), light: RGB(0xE2CFAF))
        case "slate": p = Self(mid: RGB(0x4E5B66), dark: RGB(0x161C21), light: RGB(0xC8D2D8))
        default: p = Self(mid: RGB(0x5A6360), dark: RGB(0x141A19), light: RGB(0xCFD3C4))
        }
        return p.contrasted()
    }
    func pixel(x: Double, y: Double) -> RGB {
        let top = mid.scale(0.62*shade), center = dark.scale(0.55*shade), bottom = RGB(0x070808)
        var p = y <= 288 ? top.mix(center, y/288) : center.mix(bottom, (y-288)/192)
        p = p.mix(light.scale(shade), 0.22*max(0, 1-hypot(x-180,y-220)/380))
        return p.mix(mid.scale(shade), 0.55*max(0, 1-hypot(x-928,y-48)/420))
    }
    func contrasted() -> Self {
        var p = self
        // Evaluate the complete field, including both glows; 0.12 alone does not guarantee 7:1.
        for _ in 0..<40 {
            var pass = true
            for y in stride(from: 0.0, through: 480.0, by: 16) {
                for x in stride(from: 0.0, through: 1048.0, by: 16) {
                    let bg = p.pixel(x: x, y: y), ink = RGB(0xF1EBDF)
                    if (ink.luminance+0.05)/(bg.luminance+0.05) < 7.2 ||
                        (bg.mix(ink,0.7).luminance+0.05)/(bg.luminance+0.05) < 4.7 { pass = false }
                }
            }
            if pass { return p }; p.shade *= 0.92
        }
        return p
    }
    static func extract(_ preview: Preview, fallback: String) -> Self {
        let base = Self.fallback(fallback), bytes = [UInt8](preview.pixels)
        guard preview.side >= 80, bytes.count == preview.side*preview.side*2 else { return base }
        var samples: [RGB] = []
        for y in 4..<76 { for x in 4..<76 {
            let i = ((y*preview.side/80)*preview.side + x*preview.side/80)*2
            let v = UInt16(bytes[i]) << 8 | UInt16(bytes[i+1])
            samples.append(RGB(Double((v>>11)&31)/31, Double((v>>5)&63)/63, Double(v&31)/31))
        } }
        var centers = [RGB(0x101010),RGB(0x606060),RGB(0xA0A0A0),RGB(0xEEEEEE)]
        var counts = [Int](repeating: 0, count: 4)
        for _ in 0..<6 {
            var sums = [RGB](repeating: RGB(0), count: 4); counts = [Int](repeating: 0, count: 4)
            for c in samples {
                let index = centers.indices.min { c.distance(centers[$0]) < c.distance(centers[$1]) }!
                sums[index] = RGB(sums[index].r+c.r,sums[index].g+c.g,sums[index].b+c.b); counts[index] += 1
            }
            for i in centers.indices where counts[i] > 0 { centers[i] = sums[i].scale(1/Double(counts[i])) }
        }
        let eligible = centers.indices.filter { Double(counts[$0])/Double(samples.count) > 0.05 }
        guard eligible.count >= 3, let darkest = eligible.min(by: { centers[$0].luminance < centers[$1].luminance }),
              let lightest = eligible.max(by: { centers[$0].luminance < centers[$1].luminance }),
              let middle = eligible.filter({ $0 != darkest && $0 != lightest }).max(by: { counts[$0] < counts[$1] }) else { return base }
        return Self(mid: centers[middle].quiet(0.2), dark: centers[darkest], light: centers[lightest].quiet(0.1)).contrasted()
    }
}

enum Design {
    static let width: CGFloat = 1048, height: CGFloat = 480, scale: CGFloat = 0.7206
    static let windowWidth: CGFloat = 755, windowHeight: CGFloat = 346
    static let ink = RGB(0xF1EBDF).color, accent = RGB(0xF1C98D).color
    static func name(serif: Bool = false, italic: Bool = false, caps: Bool = false) -> String {
        serif ? (italic ? "InstrumentSerif-Italic" : "InstrumentSerif-Regular") : (caps ? "Geist-Medium" : "Geist-Regular")
    }
    static func font(_ units: CGFloat, serif: Bool = false, italic: Bool = false, caps: Bool = false) -> Font {
        // Render in design units then scale the entire canvas once.
        return .custom(name(serif:serif,italic:italic,caps:caps), fixedSize: (units * scale * 2).rounded() / (2 * scale))
    }
}

struct MusicField: View {
    let palette: FieldPalette
    var intensity = 1.0
    var body: some View {
        ZStack {
            Color(red: 5/255, green: 7/255, blue: 7/255)
            ZStack {
                LinearGradient(stops: [.init(color: palette.mid.scale(0.62*palette.shade).color, location: 0),
                    .init(color: palette.dark.scale(0.55*palette.shade).color, location: 0.6),
                    .init(color: RGB(0x070808).color, location: 1)], startPoint: .top, endPoint: .bottom)
                RadialGradient(colors: [palette.light.scale(palette.shade).color.opacity(0.22), .clear],
                    center: UnitPoint(x: 180/1048, y: 220/480), startRadius: 0, endRadius: 380)
                RadialGradient(colors: [palette.mid.scale(palette.shade).color.opacity(0.55), .clear],
                    center: UnitPoint(x: 928/1048, y: 48/480), startRadius: 0, endRadius: 420)
            }.opacity(intensity)
        }.allowsHitTesting(false)
    }
}

// UILabel supplies the explicit paragraph line height that SwiftUI Text does not expose.
// In particular, Instrument Serif's native metrics are 1.3 em; the brief calls for 1.02.
struct DesignText: UIViewRepresentable {
    var value: String
    var units: CGFloat
    var serif = false, italic = false, caps = false
    var lines = 1
    var alignment: NSTextAlignment = .left
    static func attributes(units: CGFloat, serif: Bool, italic: Bool, caps: Bool,
                           alignment: NSTextAlignment = .left) -> [NSAttributedString.Key:Any] {
        let size = (units * Design.scale * 2).rounded() / (2 * Design.scale)
        let font = UIFont(name:Design.name(serif:serif,italic:italic,caps:caps),size:size) ?? UIFont.systemFont(ofSize:size)
        let paragraph = NSMutableParagraphStyle()
        paragraph.minimumLineHeight = size * (serif ? 1.02 : 1.3)
        paragraph.maximumLineHeight = paragraph.minimumLineHeight
        paragraph.alignment = alignment; paragraph.lineBreakMode = .byTruncatingTail
        return [.font:font,.paragraphStyle:paragraph,.kern:caps ? units*0.18 : 0,
                .foregroundColor:UIColor(red:241/255,green:235/255,blue:223/255,alpha:1)]
    }
    func makeUIView(context: Context) -> UILabel {
        let label = UILabel(); label.backgroundColor = .clear; label.isUserInteractionEnabled = false
        label.setContentCompressionResistancePriority(.defaultLow,for:.horizontal)
        return label
    }
    func updateUIView(_ view: UILabel,context: Context) {
        view.numberOfLines = lines
        view.attributedText = NSAttributedString(string:caps ? value.uppercased() : value,
            attributes:Self.attributes(units:units,serif:serif,italic:italic,caps:caps,alignment:alignment))
        view.accessibilityLabel = value
    }
    func sizeThatFits(_ proposal: ProposedViewSize,uiView: UILabel,context: Context) -> CGSize? {
        let width = proposal.width ?? Design.width
        let fit = uiView.sizeThatFits(CGSize(width:width,height:.greatestFiniteMagnitude))
        return CGSize(width:width,height:fit.height)
    }
}

enum Mark { case play, pause, previous, next, mic, search, plus, minus, back, check, question, heart }
struct OutlineMark: Shape {
    var mark: Mark
    func path(in rect: CGRect) -> Path {
        var p = Path()
        func line(_ points: [(CGFloat,CGFloat)]) {
            guard let first = points.first else { return }; p.move(to: CGPoint(x:first.0,y:first.1))
            for pt in points.dropFirst() { p.addLine(to: CGPoint(x:pt.0,y:pt.1)) }
        }
        switch mark {
        case .play: line([(7,4),(20,12),(7,20),(7,4)])
        case .pause: line([(8,5),(8,19)]); line([(16,5),(16,19)])
        case .previous: line([(19,5),(8,12),(19,19),(19,5)]); line([(5,5),(5,19)])
        case .next: line([(5,5),(16,12),(5,19),(5,5)]); line([(19,5),(19,19)])
        case .mic:
            p.addRoundedRect(in: CGRect(x:9,y:2,width:6,height:13), cornerSize: CGSize(width:3,height:3))
            p.move(to: CGPoint(x:5,y:10)); p.addCurve(to: CGPoint(x:19,y:10), control1: CGPoint(x:5,y:23), control2: CGPoint(x:19,y:23))
            line([(12,19),(12,23)])
        case .search: p.addEllipse(in: CGRect(x:3,y:3,width:13,height:13)); line([(15,15),(22,22)])
        case .plus: line([(5,12),(19,12)]); line([(12,5),(12,19)])
        case .minus: line([(5,12),(19,12)])
        case .back: line([(15,5),(8,12),(15,19)])
        case .check: line([(4,12),(10,18),(21,6)])
        case .question:
            p.addEllipse(in: CGRect(x:2,y:2,width:20,height:20)); line([(9,7),(14,7),(16,10),(12,13),(12,15)]); line([(12,18),(12,18.4)])
        case .heart:
            p.move(to: CGPoint(x:12,y:21)); p.addCurve(to: CGPoint(x:12,y:5), control1: CGPoint(x:-6,y:10), control2: CGPoint(x:5,y:-2))
            p.addCurve(to: CGPoint(x:12,y:21), control1: CGPoint(x:19,y:-2), control2: CGPoint(x:30,y:10))
        }
        return p.applying(CGAffineTransform(scaleX: rect.width/24, y: rect.height/24))
    }
}

extension Preview {
    var uiImage: UIImage? {
        let input = [UInt8](pixels)
        guard input.count == side*side*2 else { return nil }
        var rgb = Data(capacity: side*side*4)
        for i in stride(from: 0, to: input.count, by: 2) {
            let v = UInt16(input[i])<<8 | UInt16(input[i+1])
            rgb.append(UInt8(((v>>11)&31)*255/31)); rgb.append(UInt8(((v>>5)&63)*255/63)); rgb.append(UInt8((v&31)*255/31)); rgb.append(255)
        }
        guard let provider = CGDataProvider(data: rgb as CFData), let image = CGImage(width: side, height: side,
            bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: side*4, space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.noneSkipLast.rawValue), provider: provider,
            decode: nil, shouldInterpolate: true, intent: .defaultIntent) else { return nil }
        return UIImage(cgImage: image)
    }
}
