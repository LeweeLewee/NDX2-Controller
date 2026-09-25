import SwiftUI
import UniformTypeIdentifiers

struct AuditElement: Equatable {
    var id: String, frame: CGRect, fontSize: CGFloat, opacity: Double, tap: Bool, pill: Bool
    var scrollClipped = false, truncates = false
    var text = "", fontName = "Geist-Regular", maxLines = 1, tracking: CGFloat = 0
}
struct AuditKey: PreferenceKey {
    static var defaultValue: [AuditElement] = []
    static func reduce(value: inout [AuditElement], nextValue: () -> [AuditElement]) { value += nextValue() }
}
extension View {
    func audit(_ id: String, font: CGFloat = 0, opacity: Double = 1, tap: Bool = false,
               pill: Bool = false, scroll: Bool = false, truncates: Bool = false,
               text: String = "", fontName: String = "Geist-Regular", lines: Int = 1, tracking: CGFloat = 0) -> some View {
        background(GeometryReader { g in
            Color.clear.preference(key: AuditKey.self, value: [AuditElement(id: id, frame: g.frame(in: .named("canvas")),
                fontSize: font, opacity: opacity, tap: tap, pill: pill, scrollClipped: scroll, truncates: truncates,
                text:text,fontName:fontName,maxLines:lines,tracking:tracking)])
        })
    }
}

struct StillWaterView: View {
    @ObservedObject var model: ControllerModel
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var palette = FieldPalette.fallback("sage")
    @State private var cover: UIImage?
    @State private var pressingSettings = false
    @State private var wakeMask: CGFloat = 1
    @State private var paletteKey: String?
    @FocusState private var queryFocused: Bool
    var auditSink: (([AuditElement]) -> Void)?
    var snapshot = false
    var body: some View {
        ZStack(alignment: .topLeading) {
            MusicField(palette: isUtility ? .fallback(model.preferences.palette) : palette, intensity: intensity)
            switch model.context.screen {
            case .now: now
            case .find: find
            case .library: library
            case .detail: detail
            case .queue: upNext
            case .ask: ask
            case .settings, .display, .connection, .device, .wifi, .pairing: utility
            }
            if model.fixture {
                label("Silent demo", id: "fixture", x: 48, y: model.context.screen == .now ? 24 : 6,
                      w: 220, h: 18, size: 15, alpha: 0.35, caps: true)
            }
            if !snapshot && (model.consumeContact || (model.context.screen == .now && model.rest != .touched)) {
                Color.clear.contentShape(Rectangle()).frame(width:1048,height:480)
                    .gesture(DragGesture(minimumDistance: 0).onEnded { _ in model.contactEnded() })
                    .accessibilityLabel("Wake and reveal controls").accessibilityAddTraits(.isButton)
                    .accessibilityAction { model.contactEnded() }
            }
        }
        .frame(width: 1048, height: 480).coordinateSpace(name: "canvas").clipped()
        .foregroundStyle(Design.ink).preferredColorScheme(.dark)
        .onPreferenceChange(AuditKey.self) { auditSink?($0) }
        .simultaneousGesture(DragGesture(minimumDistance: 0).onChanged { _ in model.noteContact() })
        .onAppear { updateArt(); animateWake() }
        .onChange(of: model.rest) { _, value in if value == .waking { animateWake() } }
        .onChange(of: model.artwork?.deadline) { _, _ in updateArt() }
        .onChange(of: model.colorPreview?.deadline) { _, _ in updateArt() }
        .onChange(of: model.preferences.palette) { _, _ in updateArt() }
        .onChange(of: model.context.screen) { _, _ in queryFocused = false }
        .onChange(of: queryFocused) { _, v in model.keyboardVisible = v }
    }
    private var isUtility: Bool { [.settings,.display,.connection,.device,.wifi,.pairing].contains(model.context.screen) }
    private var intensity: Double { model.context.screen == .ask ? 0.28 : model.context.screen == .queue ? 0.6 : [.find,.library,.detail].contains(model.context.screen) ? 0.35 : 1 }
    private func animateWake() {
        wakeMask = 1
        guard model.rest == .waking, !snapshot else { return }
        withAnimation(reduceMotion ? nil : .easeOut(duration:0.4)) { wakeMask = 0 }
    }
    private func updateArt() {
        cover = model.artwork?.uiImage
        let key = (model.colorPreview?.reference ?? "fallback") + ":" + model.preferences.palette
        guard key != paletteKey else { return }
        paletteKey = key
        let p = model.colorPreview.map { FieldPalette.extract($0, fallback: model.preferences.palette) } ?? .fallback(model.preferences.palette)
        withAnimation(reduceMotion || snapshot ? nil : .easeInOut(duration:0.6)) { palette = p }
    }
    private func label(_ value: String, id: String, x: CGFloat, y: CGFloat, w: CGFloat, h: CGFloat,
                       size: CGFloat, alpha: Double = 1, serif: Bool = false, italic: Bool = false,
                       caps: Bool = false, lines: Int = 1, align: Alignment = .leading) -> some View {
        DesignText(value:value,units:size,serif:serif,italic:italic,caps:caps,lines:lines,
                   alignment:align == .center ? .center : align == .trailing ? .right : .left)
            .frame(width:w,height:h,alignment:align).opacity(alpha)
            .audit(id,font:size,opacity:alpha,truncates:lines > 1,text:caps ? value.uppercased() : value,
                   fontName:Design.name(serif:serif,italic:italic,caps:caps),lines:lines,tracking:caps ? size*0.18 : 0)
            .position(x:x+w/2,y:y+h/2)
    }
    private func button(_ title: String, id: String, x: CGFloat, y: CGFloat, w: CGFloat = 140, h: CGFloat = 56,
                        enabled: Bool = true, filled: Bool = false, border: Bool = true,
                        size: CGFloat = 22, indicator: Bool = false,
                        action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title).font(Design.font(size)).lineLimit(1).frame(width:w,height:h)
                .foregroundStyle(filled ? RGB(0x141614).color : Design.ink)
                .background(filled ? Design.ink : .clear, in: Capsule())
                .overlay(Capsule().stroke(Design.ink.opacity(border ? 0.18 : 0),lineWidth:1))
                .overlay(alignment:.bottom) { if indicator { Rectangle().fill(Design.ink).frame(width:24,height:1).padding(.bottom,8) } }
        }.buttonStyle(.plain).disabled(!enabled).opacity(enabled ? 1 : 0.35)
            .accessibilityIdentifier(id).audit(id,font:size,tap:true,pill:true,text:title)
            .position(x:x+w/2,y:y+h/2)
    }
    private func icon(_ mark: Mark, id: String, label: String, x: CGFloat, y: CGFloat, w: CGFloat = 72, h: CGFloat = 64,
                      ring: Bool = false, accent: Bool = false, enabled: Bool = true, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            OutlineMark(mark: mark).stroke(accent ? Design.accent : Design.ink, style: StrokeStyle(lineWidth:ring ? 2.2 : 1.6,lineCap:.round,lineJoin:.round))
                .frame(width:30,height:30).frame(width:w,height:h)
                .background((accent ? Design.accent : Design.ink).opacity(ring ? 0.12 : 0),in:Circle())
                .overlay(Circle().stroke((accent ? Design.accent : Design.ink).opacity(ring ? 0.7 : 0),lineWidth:1.5))
                .overlay { if model.pendingAction != nil && model.pendingTarget == id { Circle().stroke(Design.ink,lineWidth:1) } }
        }.buttonStyle(.plain).disabled(!enabled).opacity(enabled ? 1 : 0.35)
            .accessibilityLabel(label).accessibilityIdentifier(id).audit(id,tap:true).position(x:x+w/2,y:y+h/2)
    }
    private func sleeve(x: CGFloat,y: CGFloat,size: CGFloat, hidden: Bool = false) -> some View {
        Group {
            if hidden { Color.clear }
            else if let cover { Image(uiImage:cover).resizable().interpolation(.high) }
            else {
                palette.dark.scale(0.8).color.overlay(Text("Artwork unavailable").font(Design.font(18)).foregroundStyle(Design.ink.opacity(0.35)))
            }
        }.frame(width:size,height:size).clipShape(RoundedRectangle(cornerRadius:3))
            .audit("cover")
            .shadow(color:.black.opacity(0.45),radius:20,x:0,y:18).position(x:x+size/2,y:y+size/2)
    }
    private var now: some View {
        let touched = model.touched, stopped = model.player.state == "stopped" || model.player.title.isEmpty
        let x: CGFloat = touched ? 336 : 368, width: CGFloat = touched ? 664 : 632
        let size: CGFloat = model.player.title.count > 18 ? 44 : 56
        let title = stopped ? "Nothing playing" : model.player.title
        let artist = !model.online ? "RECONNECTING" : stopped ? model.player.source :
            (model.player.state == "paused" ? "PAUSED · " : "") + model.player.artist
        return ZStack(alignment:.topLeading) {
            sleeve(x:48,y:touched ? 56 : 72,size:touched ? 248 : 272,hidden:stopped)
            VStack(alignment:.leading,spacing:14) {
                Text(artist.uppercased()).font(Design.font(15,caps:true)).tracking(2.7).lineLimit(1)
                    .opacity(model.online ? 0.55 : 0.7)
                    .overlay(alignment:.bottom) { if pressingSettings { Rectangle().frame(height:1) } }
                    .audit("artist",font:15,opacity:0.55,truncates:true,text:artist.uppercased(),fontName:Design.name(caps:true),tracking:2.7)
                    .overlay(alignment:.topLeading) {
                        Color.clear.frame(width:width,height:64).contentShape(Rectangle())
                            .onLongPressGesture(minimumDuration:0.7,pressing:{ pressingSettings = $0 },perform:{ model.navigate(.settings) })
                            .accessibilityIdentifier("settings-hold").audit("settings-hold",tap:true)
                    }
                DesignText(value:title,units:stopped ? 32 : size,serif:true,lines:2)
                    .opacity(model.online && !stopped ? 1 : 0.7).audit("track-title",font:stopped ? 32 : size,opacity:model.online && !stopped ? 1 : 0.7,truncates:true,text:title,fontName:Design.name(serif:true),lines:2)
                if !stopped {
                    DesignText(value:model.player.album,units:26,serif:true,italic:true).opacity(0.7)
                        .audit("album",font:26,opacity:0.7,truncates:true,text:model.player.album,fontName:Design.name(serif:true,italic:true))
                }
            }.frame(width:width,height:touched ? 190 : 272,alignment:touched ? .topLeading : .leading)
                .audit("now-text-block")
                .position(x:x+width/2,y:touched ? 151 : 208)
            if touched {
                icon(.previous,id:"previous",label:"Previous track",x:460,y:282,enabled:model.controlsAvailable) { model.mutate("transport",["command":.string("prev")],target:"previous") }
                icon(model.player.state == "playing" ? .pause : .play,id:"play-pause",label:model.player.state == "playing" ? "Pause" : "Resume",x:552,y:274,w:80,h:80,ring:true,enabled:model.controlsAvailable) { model.mutate("transport",["command":.string(model.player.state == "playing" ? "pause" : "resume")],target:"play-pause") }
                icon(.next,id:"next",label:"Next track",x:640,y:282,enabled:model.controlsAvailable) { model.mutate("transport",["command":.string("next")],target:"next") }
                label("AMP",id:"amp-label",x:848,y:256,w:152,h:20,size:15,alpha:0.55,caps:true,align:.center)
                Capsule().stroke(Design.ink.opacity(0.18),style:StrokeStyle(lineWidth:1,dash:model.unknownAction == "amplifier" ? [3,3] : []))
                    .frame(width:152,height:64).position(x:924,y:314).allowsHitTesting(false)
                icon(.minus,id:"amp-down",label:"Amplifier down",x:848,y:282,enabled:model.controlsAvailable && model.unknownAction != "amplifier") { model.mutate("amplifier",["direction":.string("down")],target:"amp-down") }
                icon(.plus,id:"amp-up",label:"Amplifier up",x:928,y:282,enabled:model.controlsAvailable && model.unknownAction != "amplifier") { model.mutate("amplifier",["direction":.string("up")],target:"amp-up") }
                if model.unknownAction != nil {
                    label(model.unknownAction == "amplifier" ? "Volume outcome unknown" : "Command outcome unknown",id:"unknown",x:740,y:351,w:260,h:35,size:18,alpha:0.7,lines:2)
                }
                Button { model.navigate(.queue) } label: {
                    VStack(alignment:.leading,spacing:3) {
                        Text("UP NEXT").font(Design.font(15,caps:true)).tracking(2.7).opacity(0.55)
                        Text(model.queue.dropFirst().first?.title ?? "Up next").font(Design.font(26,serif:true)).lineLimit(1)
                    }.frame(width:260,height:56,alignment:.leading)
                }.buttonStyle(.plain).audit("up-next",tap:true,pill:true).position(x:178,y:416)
                icon(.mic,id:"ask",label:"Ask for music",x:488,y:376,w:72,h:72,ring:true,accent:true) { model.navigate(.ask) }
                button("Find",id:"find",x:800,y:392,w:96,border:false) { model.navigate(.find) }
                button("Library",id:"library",x:904,y:392,w:96,border:false) { model.navigate(.library) }
                if let p = model.player.position { label(time(p),id:"elapsed",x:48,y:444,w:100,h:24,size:18,alpha:0.7) }
                if let d = model.player.duration, let p = model.player.position { label("−"+time(max(0,d-p)),id:"remaining",x:900,y:444,w:100,h:24,size:18,alpha:0.7,align:.trailing) }
            }
            if !stopped {
                Rectangle().fill(Design.ink.opacity(0.18)).frame(width:1048,height:1).audit("waterline").position(x:524,y:472.5)
                let fraction = min(1,max(0,Double(model.player.position ?? 0)/Double(max(1,model.player.duration ?? 1))))
                Rectangle().fill(Design.ink.opacity(model.player.state == "paused" ? 0.4 : 0.75)).frame(width:1048*fraction,height:2).position(x:524*fraction,y:473)
            }
            if model.rest == .waking {
                let height: CGFloat = snapshot ? 240 : 480 * wakeMask
                Color.black.frame(width:1048,height:height).position(x:524,y:height/2).allowsHitTesting(false)
            }
        }.animation(reduceMotion || snapshot ? nil : .easeInOut(duration:touched ? 0.25 : 0.4),value:model.rest)
    }
    private func time(_ milliseconds: Int) -> String { String(format:"%d:%02d",milliseconds/60000,(milliseconds/1000)%60) }
    private func header(_ title: String) -> some View {
        ZStack {
            label(title,id:"screen-title",x:48,y:30,w:560,h:42,size:32,serif:true)
            if model.history.count > 1 { button("Back",id:"back",x:704,y:24,w:140) { model.back() } }
            button("Back to now",id:"back-now",x:860,y:24,w:140) { model.back(toNow:true) }
        }
    }
    private func connectionLine() -> some View {
        Group { if !model.online { label("Reconnecting to the bridge",id:"offline",x:48,y:190,w:650,h:30,size:26,alpha:0.7,serif:true,italic:true) } }
    }
    private func filters(y: CGFloat) -> some View {
        ForEach(Array(["albums","tracks","artists","playlists"].enumerated()),id:\.offset) { i,kind in
            button(kind.capitalized,id:"filter-"+kind,x:48+CGFloat(i)*128,y:y,w:120,border:false,size:18,indicator:model.context.kind == kind) { model.filter(kind) }
                .opacity(model.context.kind == kind ? 1 : 0.55)
        }
    }
    private var find: some View {
        ZStack(alignment:.topLeading) {
            header("Find")
            TextField("Artist, album or a kind of music",text:$model.context.query)
                .font(Design.font(26,serif:true)).focused($queryFocused).submitLabel(.search).autocorrectionDisabled()
                .onSubmit { queryFocused = false; model.search() }
                .frame(width:784,height:64).audit("query",font:26,tap:true).position(x:440,y:120)
            Rectangle().fill(Design.ink.opacity(queryFocused ? 0.75 : 0.18)).frame(width:784,height:1).position(x:440,y:152)
            icon(.search,id:"search",label:"Search",x:848,y:88) { queryFocused = false; model.search() }
            icon(.mic,id:"search-voice",label:"Search by voice",x:928,y:88,accent:true) { model.navigate(.ask) }
            if !queryFocused && !model.keyboardVisible { filters(y:160); rows(y:224,height:256) }
            connectionLine()
        }
    }
    private var library: some View {
        ZStack(alignment:.topLeading) {
            header("Library"); filters(y:88)
            if model.account == "disconnected" {
                label("Connect your collection on the bridge computer",id:"collection-connect",x:48,y:152,w:952,h:72,size:26,alpha:0.7,serif:true,italic:true,lines:2)
            } else { rows(y:148,height:332) }
        }
    }
    private func rows(y: CGFloat,height: CGFloat) -> some View {
        ScrollViewReader { proxy in
            ScrollView {
                VStack(spacing:0) {
                    ForEach(model.context.items) { item in
                        HStack(spacing:8) {
                            Button { model.details(item) } label: {
                                VStack(alignment:.leading,spacing:4) {
                                    Text(item.title).font(Design.font(26,serif:true)).lineLimit(1)
                                        .audit("row-title-"+item.id,font:26,scroll:true,truncates:true)
                                    Text(item.artist + " / " + item.kind).font(Design.font(18)).lineLimit(1).opacity(0.7)
                                }.frame(maxWidth:.infinity,minHeight:64,alignment:.leading).contentShape(Rectangle())
                            }.buttonStyle(.plain).audit("row-"+item.id,tap:true,scroll:true)
                            OutlineMark(mark:item.saved == "saved" ? .check : item.saved == "unsaved" ? .plus : .question)
                                .stroke(Design.ink.opacity(0.7),lineWidth:1.6).frame(width:24,height:24).frame(width:72,height:64)
                                .accessibilityLabel("Library status " + item.saved)
                        }.frame(height:72).overlay(alignment:.bottom) { Rectangle().fill(Design.ink.opacity(0.18)).frame(height:1) }.id(item.id)
                    }
                    if model.context.nextOffset != nil || model.context.cursor != nil {
                        Button("More") { if model.context.screen == .detail { model.moreChildren() } else { model.loadPage(more:true) } }
                            .font(Design.font(22)).frame(width:140,height:56).audit("more",font:22,tap:true,pill:true,scroll:true).padding(.top,4)
                    }
                    if model.context.items.isEmpty {
                        Text(model.loading ? "Looking…" : model.context.query.isEmpty ? "" : "Nothing found for “\(model.context.query)”")
                            .font(Design.font(26,serif:true,italic:true)).opacity(0.7).frame(maxWidth:.infinity,alignment:.leading)
                    }
                }.scrollTargetLayout()
            }.scrollPosition(id:$model.context.scrollID,anchor:.top).scrollTargetBehavior(.viewAligned)
                .onAppear { if let id = model.context.scrollID { proxy.scrollTo(id,anchor:.top) } }
        }.frame(width:952,height:height).position(x:524,y:y+height/2)
    }
    private var detail: some View {
        let item = model.context.selected, x: CGFloat = item.kind == "artists" ? 48 : 280
        return ZStack(alignment:.topLeading) {
            header(item.kind == "artists" ? "Artist" : item.kind == "tracks" ? "Track" : "Album")
            if item.kind != "artists" { sleeve(x:48,y:96,size:200) }
            label(item.kind+" · TIDAL",id:"detail-kind",x:x,y:100,w:1000-x,h:20,size:15,alpha:0.55,caps:true)
            label(item.title,id:"detail-title",x:x,y:122,w:1000-x,h:76,size:32,serif:true,lines:2)
            if let ref = item.artistReference {
                button(item.artist,id:"artist-link",x:x,y:206,w:500,border:false) { model.details(MusicItem(.object(["reference":.string(ref)]))) }
            } else { label(item.artist,id:"detail-artist",x:x,y:202,w:1000-x,h:29,size:22,alpha:0.7) }
            label(membershipText,id:"membership",x:x,y:270,w:1000-x,h:26,size:18,alpha:0.7)
            if model.context.playable {
                button("Play",id:"play-detail",x:x,y:300,enabled:model.controlsAvailable,filled:true) { model.mutate("play",["reference":.string(item.reference)]) }
            }
            button(model.pendingAction == "library_save" ? "Saving…" : item.kind == "artists" ? "Follow" : "Library",id:"membership-write",x:x+152,y:300,w:150,
                   enabled:model.controlsAvailable && model.context.membership != "unknown") {
                model.mutate("library_save",["reference":.string(item.reference),"saved":.bool(model.context.membership != "saved")])
            }
            if let albumRef = item.albumReference {
                button("Album",id:"album-link",x:x+314,y:300,w:120,border:false) { model.details(MusicItem(.object(["reference":.string(albumRef)]))) }
            }
            rows(y:376,height:104)
        }
    }
    private var membershipText: String {
        let artist = model.context.selected.kind == "artists"
        switch model.context.membership {
        case "saved": return artist ? "Following" : "In your library"
        case "unsaved": return artist ? "Not following" : "Not in your library"
        default: return artist ? "Follow status unknown" : "Library status unknown"
        }
    }
    private var upNext: some View {
        let items = model.context.items.isEmpty ? model.queue : model.context.items
        let sizes: [CGFloat] = [200,150,124,104,90,78,68]
        let alphas = [1.0,0.92,0.78,0.62,0.48,0.34,0.24]
        let selected = items.indices.contains(model.context.queueSelection) ? items[model.context.queueSelection] : items.first
        return ZStack(alignment:.topLeading) {
            header("Up next")
            Rectangle().fill(Design.ink.opacity(0.18)).frame(width:1048,height:1).position(x:524,y:300)
            ScrollView(.horizontal) {
                HStack(alignment:.top,spacing:22) {
                    ForEach(Array(items.enumerated()),id:\.offset) { i,item in
                        let side = sizes[min(i,6)]
                        let image = model.queueArtwork[item.reference]?.uiImage
                        ZStack(alignment:.topLeading) {
                            Button { model.context.queueSelection = i; model.noteContact() } label: {
                                ZStack {
                                    palette.dark.color
                                    if let image { Image(uiImage:image).resizable() }
                                    else { Text(item.title).font(Design.font(18,serif:true)).lineLimit(2).padding(8) }
                                }.frame(width:side,height:side).opacity(alphas[min(i,6)])
                                    .overlay { if model.context.queueSelection == i { Rectangle().stroke(Design.ink.opacity(0.8),lineWidth:1.5).padding(-4) } }
                            }.buttonStyle(.plain).frame(width:max(72,side),height:side).contentShape(Rectangle())
                                .audit("queue-\(i)",tap:true,scroll:true).position(x:max(72,side)/2,y:204-side/2)
                            if let image {
                                Image(uiImage:image).resizable().frame(width:side,height:side).scaleEffect(x:1,y:-1)
                                    .frame(width:side,height:side*0.4,alignment:.top).clipped()
                                    .mask(LinearGradient(colors:[.black,.clear],startPoint:.top,endPoint:.bottom))
                                    .opacity(0.22*alphas[min(i,6)]).position(x:max(72,side)/2,y:204+side*0.2)
                                    .allowsHitTesting(false)
                            }
                        }.frame(width:max(72,side),height:284)
                    }
                }.padding(.horizontal,4)
            }.frame(width:960,height:284).position(x:524,y:238)
            label(selected?.reference == model.player.current.reference ? "PLAYING NOW" : "UP NEXT",id:"queue-timing",x:48,y:392,w:952,h:20,size:15,alpha:0.55,caps:true)
            label(selected?.title ?? "Queue unavailable",id:"queue-title",x:48,y:412,w:700,h:42,size:32,serif:true)
            if model.context.nextOffset != nil { button("More",id:"queue-more",x:860,y:388) { model.loadPage(more:true) } }
        }
    }
    private var ask: some View {
        ZStack(alignment:.topLeading) {
            label(model.voiceState == "recording" ? "LISTENING · 0:\(String(format:"%02d",model.voiceSeconds)) OF 0:30" : model.voiceState == "unavailable" ? "MICROPHONE UNAVAILABLE" : "RECORDING STOPPED",
                  id:"voice-state",x:124,y:40,w:800,h:24,size:15,alpha:0.7,caps:true,align:.center)
            if model.voiceState == "recording" { Ripples(reduce:reduceMotion || snapshot).frame(width:600,height:600).position(x:524,y:270).allowsHitTesting(false) }
            label(model.transcript.isEmpty ? "Say an artist, an album or the kind of music you want" : "“\(model.transcript)”",id:"transcript",x:204,y:126,w:640,h:124,size:model.transcript.isEmpty ? 32 : 56,
                  alpha:model.transcript.isEmpty ? 0.7 : 1,serif:true,italic:true,lines:2,align:.center)
            OutlineMark(mark:.mic).stroke(Design.accent,lineWidth:1.6).frame(width:30,height:30).frame(width:72,height:72)
                .background(Design.accent.opacity(0.12),in:Circle()).overlay(Circle().stroke(Design.accent.opacity(0.8),lineWidth:1.5)).position(x:524,y:294)
            button("Cancel",id:"voice-cancel",x:244,y:388,w:152) { model.back() }
            button("Restart",id:"voice-restart",x:452,y:388,w:160) { model.startVoice() }
            button("Stop & search",id:"voice-search",x:634,y:388,w:192,enabled:!model.transcript.isEmpty,filled:true) { model.submitVoice() }
            if model.fixture { label("Microphone fixture: no audio captured. Search only.",id:"voice-fixture",x:124,y:456,w:800,h:24,size:18,alpha:0.35,align:.center) }
        }
    }
    private var utility: some View {
        ZStack(alignment:.topLeading) {
            header(model.context.screen.rawValue.capitalized)
            switch model.context.screen {
            case .settings:
                settingRow("Display",value:"Palette, brightness and idle time",index:0) { model.navigate(.display) }
                settingRow("Connection",value:model.online ? "Connected to bridge" : "Connection unavailable",index:1) { model.navigate(.connection) }
                settingRow("Device",value:"Battery and local state",index:2) { model.navigate(.device) }
                settingRow("Wi-Fi",value:"Configure in iOS Settings",index:3) { model.navigate(.wifi) }
            case .display:
                label("Palette",id:"palette-label",x:48,y:96,w:300,h:28,size:22)
                ForEach(Array(["sage","sand","slate"].enumerated()),id:\.offset) { i,name in
                    button(name.capitalized,id:"palette-"+name,x:48+CGFloat(i)*128,y:128,w:120,border:false) { model.preferences.palette = name; model.preferences.save() }
                }
                label("Brightness",id:"brightness-label",x:48,y:210,w:300,h:28,size:22)
                Slider(value:$model.preferences.brightness,in:0.1...1).tint(Design.ink)
                    .onChange(of:model.preferences.brightness) { _,v in UIScreen.main.brightness = v; model.preferences.save() }
                    .frame(width:952,height:64).audit("brightness",tap:true).position(x:524,y:266)
                label("Release idle timer after",id:"timeout-label",x:48,y:320,w:500,h:30,size:22)
                Menu {
                    ForEach([30,60,120,300],id:\.self) { seconds in Button("\(seconds) seconds") { model.preferences.timeout = seconds; model.preferences.save() } }
                } label: { Text("\(model.preferences.timeout) seconds⌄").font(Design.font(22)).frame(width:240,height:56).overlay(Capsule().stroke(Design.ink.opacity(0.18))) }
                    .audit("timeout",font:22,tap:true,pill:true).position(x:168,y:388)
            case .connection:
                settingRow("Bridge",value:model.online ? "Connected with provisioned trust" : model.status,index:0) { Task { await model.refresh() } }
                settingRow("Pairing",value:"Private enrollment and trust",index:1) { model.navigate(.pairing) }
                if model.unknownAction != nil { settingRow("Acknowledge uncertain command",value:"Clears the notice; sends no command",index:2) { model.acknowledgeUnknown() } }
            case .device:
                let level = UIDevice.current.batteryLevel
                label(level < 0 ? "Battery unavailable" : "Battery \(Int(level*100))%",id:"battery",x:48,y:112,w:952,h:40,size:22)
                label("Still Water · iPhone display client",id:"device",x:48,y:192,w:952,h:40,size:22)
                label("Charging is managed by iOS and the power bank",id:"power",x:48,y:272,w:952,h:60,size:18,alpha:0.7,lines:2)
            case .wifi:
                label("Configure Wi-Fi in iOS Settings, then return here. No Wi-Fi credentials are stored by Still Water.",id:"wifi",x:48,y:112,w:952,h:150,size:22,alpha:0.7,lines:3)
            case .pairing:
                PairingView(model:model).frame(width:952,height:360).position(x:524,y:278)
            default: EmptyView()
            }
        }
    }
    private func settingRow(_ title: String,value: String,index: Int,action: @escaping () -> Void) -> some View {
        Button(action:action) {
            VStack(alignment:.leading,spacing:6) {
                Text(title).font(Design.font(22))
                Text(value).font(Design.font(18)).opacity(0.7).lineLimit(1)
            }.frame(width:952,height:72,alignment:.leading).overlay(alignment:.trailing) { Text("›").font(Design.font(22)).opacity(0.45) }
                .overlay(alignment:.bottom) { Rectangle().fill(Design.ink.opacity(0.18)).frame(height:1) }
        }.buttonStyle(.plain).audit("settings-\(index)",font:22,tap:true).position(x:524,y:136+CGFloat(index)*80)
    }
}

struct Ripples: View {
    var reduce: Bool
    @State private var expand = false
    var body: some View {
        ZStack {
            ForEach(0..<3) { i in
                Circle().stroke(Design.accent.opacity(reduce ? 0.2 : expand ? 0 : 0.55),lineWidth:1)
                    .scaleEffect(reduce ? 0.5 : expand ? 1 : 0.15)
                    .animation(reduce ? nil : .linear(duration:3.6).repeatForever(autoreverses:false).delay(Double(i)*1.2),value:expand)
            }
        }.onAppear { expand = true }
    }
}
