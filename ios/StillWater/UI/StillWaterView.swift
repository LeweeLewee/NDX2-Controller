import SwiftUI
import UniformTypeIdentifiers

struct AuditElement: Equatable {
    var id: String, frame: CGRect, fontSize: CGFloat, opacity: Double, tap: Bool, pill: Bool
    var scrollClipped = false, truncates = false
    var text = "", fontName = "ArialMT", maxLines = 1, tracking: CGFloat = 0
}
struct CollectionOffsetKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) { value = nextValue() }
}
struct AuditKey: PreferenceKey {
    static var defaultValue: [AuditElement] = []
    static func reduce(value: inout [AuditElement], nextValue: () -> [AuditElement]) { value += nextValue() }
}
extension View {
    func audit(_ id: String, font: CGFloat = 0, opacity: Double = 1, tap: Bool = false,
               pill: Bool = false, scroll: Bool = false, truncates: Bool = false,
               text: String = "", fontName: String = "ArialMT", lines: Int = 1, tracking: CGFloat = 0) -> some View {
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
    @State private var collectionOffset: CGFloat = 0
    @FocusState private var queryFocused: Bool
    var auditSink: (([AuditElement]) -> Void)?
    var snapshot = false
    var drawsBackground = true
    var body: some View {
        ZStack(alignment: .topLeading) {
            if drawsBackground { MusicField(palette: isUtility ? .fallback(model.preferences.palette) : palette, intensity: intensity) }
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
                label("Silent demo", id: "fixture", x: 48, y: 24,
                      w: 220, h: 22, size: 15, alpha: 0.35, caps: true)
            }
            if !snapshot && (model.consumeContact || (model.context.screen == .now && model.rest != .touched)) {
                Color.clear.contentShape(Rectangle()).frame(width:1048,height:480)
                    .gesture(DragGesture(minimumDistance: 0).onEnded { _ in model.contactEnded() })
                    .accessibilityIdentifier("wake-contact")
                    .accessibilityLabel("Wake and reveal controls").accessibilityAddTraits(.isButton)
                    .accessibilityAction { model.contactEnded() }
            }
        }
        .frame(width: 1048, height: 480).coordinateSpace(name: "canvas").clipped()
        .foregroundStyle(Design.ink).preferredColorScheme(.dark)
        .onPreferenceChange(AuditKey.self) { auditSink?($0) }
        // A zero-distance drag at the page level cancels native Button taps.
        // Observe taps separately; real drags still refresh the idle timer.
        .simultaneousGesture(TapGesture().onEnded { model.noteContact() })
        .simultaneousGesture(DragGesture(minimumDistance: 10).onChanged { _ in model.noteContact() })
        .onAppear { updateArt(); animateWake() }
        .onChange(of: model.rest) { _, value in if value == .waking { animateWake() } }
        .onChange(of: model.artwork?.deadline) { _, _ in updateArt() }
        .onChange(of: model.fieldPreview?.reference) { _, _ in updateArt() }
        .onChange(of: model.preferences.palette) { _, _ in updateArt() }
        .onChange(of: model.context.screen) { _, _ in queryFocused = false; updateArt() }
        .onPreferenceChange(CollectionOffsetKey.self) { collectionOffset = $0 }
        .task(id: collectionOffset) {
            do { try await Task.sleep(nanoseconds:250_000_000) } catch { return }
            guard model.context.screen == .library else { return }
            let stride: CGFloat = model.context.kind == "tracks" ? 72 : 156
            let columns = model.context.kind == "tracks" ? 1 : 6
            let offset = max(0,-collectionOffset)
            let row = Int(floor(offset/stride))
            let coverBottom: CGFloat = model.context.kind == "tracks" ? 64 : 104
            let first = row + (offset.truncatingRemainder(dividingBy:stride) >= coverBottom ? 1 : 0)
            model.settleLibrary(firstIndex:first*columns)
        }
        .onChange(of: queryFocused) { _, v in model.keyboardVisible = v }
    }
    private var isUtility: Bool { [.settings,.display,.connection,.device,.wifi,.pairing].contains(model.context.screen) }
    private var intensity: Double { model.context.screen == .ask ? 0.28 : model.context.screen == .queue ? 0.6 : model.context.screen == .detail ? 0.5 : [.find,.library].contains(model.context.screen) ? 0.35 : [.settings,.display,.connection,.device,.wifi,.pairing].contains(model.context.screen) ? 0.6 : 1 }
    private func animateWake() {
        wakeMask = 1
        guard model.rest == .waking, !snapshot else { return }
        withAnimation(reduceMotion ? nil : .easeOut(duration:0.4)) { wakeMask = 0 }
    }
    private func updateArt() {
        cover = model.artwork?.uiImage(palette:model.preferences.palette)
        let key = (model.fieldPreview?.reference ?? "fallback") + ":" + model.preferences.palette
        guard key != paletteKey else { return }
        paletteKey = key
        let p = model.fieldPreview.map { FieldPalette.extract($0, fallback: model.preferences.palette) } ?? .fallback(model.preferences.palette)
        withAnimation(reduceMotion || snapshot ? nil : .easeInOut(duration:0.6)) { palette = p }
    }
    private func label(_ value: String, id: String, x: CGFloat, y: CGFloat, w: CGFloat, h: CGFloat,
                       size: CGFloat, alpha: Double = 1, serif: Bool = false, italic: Bool = false,
                       caps: Bool = false, lines: Int = 1, accent: Bool = false, align: Alignment = .leading) -> some View {
        DesignText(value:value,units:size,serif:serif,italic:italic,caps:caps,lines:lines,
                   alignment:align == .center ? .center : align == .trailing ? .right : .left,accent:accent)
            .frame(width:w,height:h,alignment:Alignment(horizontal:align.horizontal,vertical:.top)).opacity(alpha)
            .audit(id,font:size,opacity:alpha,truncates:lines > 1,text:caps ? value.uppercased() : value,
                   fontName:Design.name(serif:serif,italic:italic,caps:caps),lines:lines,tracking:caps ? size*0.18 : 0)
            .position(x:x+w/2,y:y+h/2)
    }
    private func button(_ title: String, id: String, x: CGFloat, y: CGFloat, w: CGFloat = 140, h: CGFloat = 56,
                        enabled: Bool = true, filled: Bool = false, border: Bool = true,
                        size: CGFloat = 22, alignment: Alignment = .center, indicator: Bool = false,
                        action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Text(title).font(Design.font(size)).lineLimit(1).frame(width:w,height:h,alignment:alignment)
                .foregroundStyle(filled ? RGB(0x141614).color : Design.ink)
                .background(filled ? Design.ink : .clear, in: Capsule())
                .overlay(Capsule().stroke(Design.ink.opacity(border ? 0.18 : 0),lineWidth:1))
                .overlay(alignment:alignment == .leading ? .bottomLeading : .bottom) { if indicator { Rectangle().fill(Design.ink).frame(width:24,height:1).padding(.leading,alignment == .leading ? 18 : 0).padding(.bottom,8) } }
                .contentShape(Rectangle())
        }.buttonStyle(.plain).disabled(!enabled).opacity(enabled ? 1 : 0.35)
            .accessibilityIdentifier(id).audit(id,font:size,tap:true,pill:true,text:title)
            .position(x:x+w/2,y:y+h/2)
    }
    private func icon(_ mark: Mark, id: String, label: String, x: CGFloat, y: CGFloat, w: CGFloat = 72, h: CGFloat = 64,
                      ring: Bool = false, accent: Bool = false, enabled: Bool = true, glyph: CGFloat = 30, selected: Bool = false, ringSize: CGFloat? = nil, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            OutlineMark(mark: mark).stroke(accent ? Design.accent : Design.ink, style: StrokeStyle(lineWidth:ring ? 2.2 : 1.6,lineCap:.round,lineJoin:.round))
                .background { if selected || mark == .stop { OutlineMark(mark:mark).fill(mark == .stop ? Design.accent : Design.ink) } }
                .frame(width:glyph,height:glyph).frame(width:w,height:h)
                .background { if ring { Circle().fill((accent ? Design.accent : Design.ink).opacity(accent && mark == .mic ? 0 : 0.12)).frame(width:ringSize ?? min(w,h),height:ringSize ?? min(w,h)) } }
                .overlay { if ring { Circle().stroke((accent ? Design.accent : Design.ink).opacity(0.7),lineWidth:1.5).frame(width:ringSize ?? min(w,h),height:ringSize ?? min(w,h)) } }
                .overlay { if model.pendingAction != nil && model.pendingAction != "amplifier" && model.pendingTarget == id { Circle().stroke(Design.ink,lineWidth:1) } }
                .contentShape(Rectangle())
        }.buttonStyle(.plain).disabled(!enabled)
            .opacity(model.pendingAction == "amplifier" && id.hasPrefix("amp-") ? 0.35 : enabled || (model.pendingAction != nil && model.pendingTarget == id) ? 1 : 0.35)
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
        let x: CGFloat = touched ? 344 : 392, width: CGFloat = touched ? 656 : 608
        let size: CGFloat = model.player.title.count > 18 ? 44 : 56
        let title = stopped ? "Nothing playing" : model.player.title
        let artist = !model.online ? "RECONNECTING" : stopped ? model.player.source :
            (model.player.state == "paused" ? "PAUSED · " : "") + model.player.artist
        return ZStack(alignment:.topLeading) {
            if touched {
                Color.clear.contentShape(Rectangle()).frame(width:1048,height:480)
                    .onLongPressGesture(minimumDuration:0.7) { model.navigate(.settings) }
                    .accessibilityIdentifier("settings-surface").accessibilityLabel("Hold background for Settings")
                    .accessibilityAction(named:Text("Settings")) { model.navigate(.settings) }
            }
            sleeve(x:48,y:touched ? 56 : 60,size:touched ? 256 : 296,hidden:stopped)
            let titleHeight = DesignText.height(title, units:stopped ? 32 : size, width:width, serif:true, lines:2)
            let blockHeight = 20 + 14 + titleHeight + (stopped ? 0 : 14 + 34)
            let top: CGFloat = touched ? 56 : 208 - blockHeight/2
            ZStack(alignment:.topLeading) {
                label(artist,id:"artist",x:0,y:0,w:width,h:22,size:15,alpha:0.55,caps:true)
                label(title,id:"track-title",x:0,y:34,w:width,h:titleHeight,size:stopped ? 32 : size,alpha:stopped || !model.online ? 0.7 : 1,serif:true,lines:2)
                if !stopped { label(model.player.album,id:"album",x:0,y:48+titleHeight,w:width,h:36,size:26,alpha:0.7,serif:true,italic:true) }
            }.frame(width:width,height:blockHeight,alignment:.topLeading).audit("now-text-block")
                .position(x:x+width/2,y:top+blockHeight/2)
            if touched {
                if let ref = model.player.current.artistReference, !ref.isEmpty {
                    Button { model.details(MusicItem(.object(["reference":.string(ref)]))) } label: { Color.clear.frame(width:width,height:64).contentShape(Rectangle()) }
                        .buttonStyle(.plain).accessibilityIdentifier("now-artist").accessibilityLabel(artist).audit("now-artist",tap:true).position(x:x+width/2,y:64)
                }
                if !stopped, let ref = model.player.current.albumReference, !ref.isEmpty {
                    Button { model.details(MusicItem(.object(["reference":.string(ref)]))) } label: { Color.clear.frame(width:width,height:64).contentShape(Rectangle()) }
                        .buttonStyle(.plain).accessibilityIdentifier("now-album").accessibilityLabel(model.player.album).audit("now-album",tap:true).position(x:x+width/2,y:min(224,top+titleHeight+66))
                }
            }
            if touched {
                icon(.previous,id:"previous",label:"Previous track",x:363,y:268,w:98,h:96,enabled:model.controlsAvailable,glyph:36) { model.mutate("transport",["command":.string("prev")],target:"previous") }
                icon(model.player.state == "playing" ? .pause : .play,id:"play-pause",label:model.player.state == "playing" ? "Pause" : "Resume",x:472,y:264,w:104,h:104,ring:true,enabled:model.controlsAvailable,glyph:40) { model.mutate("transport",["command":.string(model.player.state == "playing" ? "pause" : "resume")],target:"play-pause") }
                icon(.next,id:"next",label:"Next track",x:587,y:268,w:98,h:96,enabled:model.controlsAvailable,glyph:36) { model.mutate("transport",["command":.string("next")],target:"next") }
                icon(.volumeDown,id:"amp-down",label:"Volume down",x:816,y:276,w:80,h:80,enabled:model.controlsAvailable && model.unknownAction != "amplifier",glyph:32) { model.mutate("amplifier",["direction":.string("down")],target:"amp-down") }
                icon(.volumeUp,id:"amp-up",label:"Volume up",x:920,y:276,w:80,h:80,enabled:model.controlsAvailable && model.unknownAction != "amplifier",glyph:32) { model.mutate("amplifier",["direction":.string("up")],target:"amp-up") }
                Button { model.navigate(.queue) } label: {
                    VStack(alignment:.leading,spacing:2) {
                        Text("UP NEXT").font(Design.font(15,caps:true)).tracking(2.7).opacity(0.55)
                        Text(model.queue.dropFirst().first?.title ?? "Queue").font(Design.font(26,serif:true)).lineLimit(1)
                    }.frame(width:248,height:64,alignment:.leading).contentShape(Rectangle())
                }.buttonStyle(.plain).accessibilityIdentifier("up-next").audit("up-next",font:26,tap:true).position(x:172,y:420)
                icon(.mic,id:"ask",label:"Find music",x:488,y:376,w:72,h:72,ring:true,accent:true,glyph:28) { model.navigate(.ask) }
                icon(.library,id:"library",label:"Library",x:920,y:384,w:80,h:64,glyph:30) { model.navigate(.library) }
                if model.unknownAction == "amplifier" {
                    RoundedRectangle(cornerRadius:32).stroke(Design.ink.opacity(0.55),style:StrokeStyle(lineWidth:1,dash:[4,4]))
                        .frame(width:184,height:80).position(x:908,y:316).allowsHitTesting(false)
                    label("Volume outcome unknown",id:"unknown",x:760,y:360,w:288,h:24,size:15,alpha:0.7,align:.center)
                } else if model.unknownAction != nil {
                    label("Outcome unknown",id:"unknown",x:48,y:320,w:280,h:24,size:18,alpha:0.7)
                }
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
            label(title,id:"screen-title",x:48,y:56,w:560,h:42,size:32,serif:true)
            button("‹ Back",id:"back",x:888,y:24,w:112,border:false,size:22) { model.back() }
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
            TextField("Search",text:$model.context.query).font(Design.font(26,serif:true))
                .focused($queryFocused).submitLabel(.search).onSubmit { queryFocused = false; model.search() }
                .accessibilityIdentifier("results-query").frame(width:744,height:64).audit("results-query",font:26,tap:true).position(x:420,y:146)
            icon(.search,id:"edit-search",label:"Search",x:816,y:114) { queryFocused = false; model.search() }
            icon(.mic,id:"results-mic",label:"Start voice search",x:928,y:114,accent:true) { model.navigate(.ask); model.startVoice() }
            Rectangle().fill(Design.ink.opacity(0.35)).frame(width:744,height:1).position(x:420,y:178)
            filters(y:186); rows(y:250,height:230,width:704)
            connectionLine()
        }
    }
    private var library: some View {
        ZStack(alignment:.topLeading) {
            header("Library"); filters(y:112)
            if model.account == "disconnected" {
                label("Connect your collection on the bridge computer",id:"collection-connect",x:48,y:180,w:952,h:72,size:26,alpha:0.7,serif:true,italic:true,lines:2)
            } else if model.context.kind == "tracks" { rows(y:180,height:300,width:704) }
            else { libraryGrid }
        }
    }
    private var libraryGrid: some View {
        ScrollView {
            LazyVGrid(columns:Array(repeating:GridItem(.fixed(104),spacing:16),count:6),alignment:.leading,spacing:16) {
                ForEach(model.context.items) { item in
                    VStack(alignment:.leading,spacing:10) {
                        Button { model.details(item) } label: {
                            ZStack {
                                if model.context.kind == "playlists" {
                                    collectionCover(item).opacity(0.5).offset(x:6,y:-6)
                                }
                                collectionCover(item)
                            }.frame(width:104,height:104).contentShape(Rectangle())
                        }.buttonStyle(.plain).accessibilityIdentifier("library-cover-"+item.id).accessibilityLabel(item.title)
                            .audit("library-cover-"+item.id,tap:true,scroll:true)
                        Text(item.title).font(Design.font(15)).opacity(0.7).lineLimit(1).truncationMode(.tail)
                            .frame(width:104,height:26,alignment:.topLeading)
                    }.frame(width:104,height:140,alignment:.topLeading).id(item.id)
                }
                if model.context.nextOffset != nil || model.context.cursor != nil {
                    Button("More") { model.loadPage(more:true) }.font(Design.font(18))
                        .frame(width:104,height:104).audit("more",font:18,tap:true,scroll:true)
                }
            }.scrollTargetLayout().padding(.top,model.context.kind == "playlists" ? 6 : 0)
                .background(GeometryReader { g in
                    Color.clear.preference(key:CollectionOffsetKey.self,value:g.frame(in:.named("collection")).minY)
                })
            if model.context.items.isEmpty {
                Text(model.libraryEmptyMessage).font(Design.font(26,serif:true,italic:true))
                    .opacity(0.7).frame(maxWidth:.infinity,alignment:.leading)
            }
        }.coordinateSpace(name:"collection").scrollPosition(id:$model.context.scrollID,anchor:.top)
            .frame(width:710,height:300,alignment:.leading).clipped()
            .mask(LinearGradient(stops:[.init(color:.black,location:0),.init(color:.black,location:260.0/300),.init(color:.clear,location:1)],startPoint:.top,endPoint:.bottom))
            .position(x:403,y:330)
    }
    @ViewBuilder private func collectionCover(_ item: MusicItem) -> some View {
        let image = model.queueArtwork[item.reference]?.uiImage(palette:model.preferences.palette)
        if model.context.kind == "artists" {
            if let image {
                Image(uiImage:image).resizable().interpolation(.high).scaledToFill()
                    .frame(width:104,height:104).clipShape(Circle())
            } else {
                Circle().stroke(Design.ink.opacity(0.35),lineWidth:1).frame(width:104,height:104)
                    .overlay(Text(String(item.title.prefix(1))).font(Design.font(32,serif:true)).opacity(0.62))
            }
        } else {
            if let image {
                Image(uiImage:image).resizable().interpolation(.high).scaledToFill()
                    .frame(width:104,height:104).clipShape(RoundedRectangle(cornerRadius:3))
            } else {
                RoundedRectangle(cornerRadius:3).stroke(Design.ink.opacity(0.18),lineWidth:1).frame(width:104,height:104)
            }
        }
    }
    private func rows(y: CGFloat,height: CGFloat, items: [MusicItem]? = nil, tracks: Bool = false, width: CGFloat = 952, left: CGFloat = 48) -> some View {
        let contents = items ?? model.context.items
        return
        ScrollViewReader { proxy in
            ScrollView {
                VStack(spacing:0) {
                    ForEach(Array(contents.enumerated()),id: \.element.id) { index,item in
                        HStack(spacing:8) {
                            Button { model.details(item) } label: {
                                HStack(spacing:16) {
                                    if !tracks, let image = model.queueArtwork[item.reference]?.uiImage(palette:model.preferences.palette) {
                                        Image(uiImage:image).resizable().interpolation(.high).scaledToFill()
                                            .frame(width:56,height:56).clipShape(RoundedRectangle(cornerRadius:3))
                                    } else if !tracks && item.artwork != nil {
                                        Color.clear.frame(width:56,height:56)
                                    }
                                    if tracks { Text(String(index+1)).font(Design.font(18)).opacity(0.55).frame(width:28) }
                                    VStack(alignment:.leading,spacing:4) {
                                    Text(item.title).font(Design.font(26,serif:true)).lineLimit(1)
                                        .audit("row-title-"+item.id,font:26,scroll:true,truncates:true)
                                    if !tracks { Text(rowSubtitle(item)).font(Design.font(18)).lineLimit(1).opacity(0.55) }
                                    }.frame(maxWidth:.infinity,alignment:.leading)
                                    if tracks, let duration = item.duration { Text(time(duration)).font(Design.font(18)).opacity(0.55) }
                                }.frame(maxWidth:.infinity,alignment:.leading).frame(height:64).contentShape(Rectangle())
                            }.buttonStyle(.plain).audit("row-"+item.id,tap:true,scroll:true)
                            Button {
                                model.mutate("library_save",["reference":.string(item.reference),"saved":.bool(item.saved != "saved")],target:"row-membership-"+item.id)
                            } label: {
                                OutlineMark(mark:item.saved == "unknown" ? .question : item.kind == "tracks" ? .heart : item.saved == "saved" ? .check : .plus)
                                    .stroke(Design.ink.opacity(item.saved == "saved" ? 1 : 0.7),lineWidth:2)
                                    .background { if item.kind == "tracks" && item.saved == "saved" { OutlineMark(mark:.heart).fill(Design.ink) } }
                                    .frame(width:32,height:32).frame(width:72,height:64).contentShape(Rectangle())
                            }.buttonStyle(.plain)
                                .disabled(!model.controlsAvailable || model.unknownAction == "library_save" || !["saved","unsaved"].contains(item.saved))
                                .accessibilityIdentifier("row-membership-"+item.id)
                                .accessibilityLabel(item.saved == "unknown" ? "Membership unavailable" : item.kind == "artists" ? (item.saved == "saved" ? "Unfollow artist" : "Follow artist") : item.kind == "tracks" ? (item.saved == "saved" ? "Unlike track" : "Like track") : (item.saved == "saved" ? "Remove from library" : "Add to library"))
                                .audit("row-membership-"+item.id,tap:true,scroll:true)
                        }.frame(height:72).overlay(alignment:.bottom) { Rectangle().fill(Design.ink.opacity(0.18)).frame(height:1) }.id(item.id)
                    }
                    if model.context.nextOffset != nil || model.context.cursor != nil {
                        Button("More") { if model.context.screen == .detail { model.moreChildren() } else { model.loadPage(more:true) } }
                            .font(Design.font(22)).frame(width:140,height:56).audit("more",font:22,tap:true,pill:true,scroll:true).padding(.top,4)
                    }
                    if contents.isEmpty {
                        Text(model.loading ? "Looking…" : model.context.screen == .library ? model.libraryEmptyMessage : model.context.screen == .detail && tracks ? "No tracks available yet" : model.context.query.isEmpty ? "" : "Nothing found for “\(model.context.query)”")
                            .font(Design.font(26,serif:true,italic:true)).opacity(0.7).frame(maxWidth:.infinity,alignment:.leading)
                    }
                }.scrollTargetLayout()
                    .background(GeometryReader { g in
                        Color.clear.preference(key:CollectionOffsetKey.self,value:g.frame(in:.named("collection")).minY)
                    })
            }.coordinateSpace(name:"collection").scrollPosition(id:$model.context.scrollID,anchor:.top).scrollTargetBehavior(.viewAligned)
                .onAppear { if let id = model.context.scrollID { proxy.scrollTo(id,anchor:.top) } }
        }.frame(width:width,height:height).clipped()
            .mask(LinearGradient(stops:[.init(color:.black,location:0),.init(color:.black,location:max(0,(height-40)/height)),.init(color:.clear,location:1)],startPoint:.top,endPoint:.bottom))
            .position(x:left+width/2,y:y+height/2)
    }
    private func rowSubtitle(_ item: MusicItem) -> String {
        let suffix = model.context.screen == .library && item.kind == "tracks"
            ? item.duration.map(time) ?? ""
            : ["albums":"album","tracks":"track","artists":"artist","playlists":"playlist"][item.kind] ?? item.kind
        return [item.artist,suffix].filter { !$0.isEmpty }.joined(separator:" · ")
    }
    private var detail: some View {
        Group { if model.context.selected.kind == "artists" { artistDetail } else { albumDetail } }
    }
    private var membershipEnabled: Bool {
        model.controlsAvailable && model.unknownAction != "library_save" && ["saved","unsaved"].contains(model.context.membership)
    }
    private func toggleMembership() {
        model.mutate("library_save",["reference":.string(model.context.selected.reference),"saved":.bool(model.context.membership != "saved")])
    }
    private var detailMembershipLabel: String {
        if model.pendingAction == "library_save" { return "Saving…" }
        if model.unknownAction == "library_save" || model.context.membership == "unknown" { return model.context.selected.kind == "artists" ? "Follow ?" : "Library ?" }
        if model.context.selected.kind == "artists" { return model.context.membership == "saved" ? "✓ Following" : "Follow" }
        return model.context.membership == "saved" ? "✓ In your library" : "Add to library"
    }
    private var albumDetail: some View {
        let item = model.context.selected
        let facts = ([item.kind == "albums" ? "Album" : item.kind == "tracks" ? "Track" : "Playlist"] + [item.year.map(String.init), item.trackCount.map { "\($0) tracks" }, item.duration.map { "\($0/60000) min" }].compactMap { $0 }).joined(separator:" · ")
        return ZStack(alignment:.topLeading) {
            header(""); sleeve(x:48,y:56,size:248)
            if let ref = item.artistReference {
                Button { model.details(MusicItem(.object(["reference":.string(ref)]))) } label: {
                    Text(item.artist.uppercased()).font(Design.font(15,caps:true)).tracking(2.7).opacity(0.55).lineLimit(1)
                        .frame(width:488,height:64,alignment:.leading).contentShape(Rectangle())
                }.buttonStyle(.plain).accessibilityIdentifier("artist-link").audit("artist-link",font:15,tap:true,truncates:true).position(x:580,y:64)
            } else { label(item.artist,id:"detail-artist",x:336,y:56,w:488,h:24,size:15,alpha:0.55,caps:true) }
            label(item.title,id:"detail-title",x:336,y:88,w:664,h:72,size:32,serif:true,lines:2)
            label(facts,id:"detail-facts",x:336,y:168,w:664,h:28,size:18,alpha:0.55)
            if model.context.playable {
                button(model.detailPlayLabel,id:"play-detail",x:336,y:212,w:140,enabled:model.controlsAvailable && !model.selectedIsPlaying && model.unknownAction != "play",filled:true) { model.mutate("play",["reference":.string(item.reference)],target:"play-detail") }
            }
            if item.kind == "tracks" {
                icon(.heart,id:"membership-write",label:model.membershipAction,x:488,y:212,w:80,h:64,enabled:membershipEnabled,glyph:40,selected:model.context.membership == "saved") { toggleMembership() }
            } else { button(detailMembershipLabel,id:"membership-write",x:488,y:212,w:232,enabled:membershipEnabled) { toggleMembership() }.accessibilityLabel(model.membershipAction) }
            if let albumRef = item.albumReference {
                button("Album ›",id:"album-link",x:760,y:212,w:144,border:false) { model.details(MusicItem(.object(["reference":.string(albumRef)]))) }
            }
            if item.kind != "tracks" {
                rows(y:328,height:152,tracks:true)
                LinearGradient(colors:[.clear,palette.dark.scale(0.3).color],startPoint:.top,endPoint:.bottom).frame(width:952,height:32).position(x:524,y:464).allowsHitTesting(false)
            }
        }
    }
    private var artistDetail: some View {
        let item = model.context.selected, hasPortrait = cover != nil
        let left: CGFloat = hasPortrait ? 336 : 48, width: CGFloat = hasPortrait ? 664 : 776
        let nameSize: CGFloat = hasPortrait ? 44 : 56
        let nameHeight = DesignText.height(item.title,units:nameSize,width:width,serif:true,lines:2)
        let bioTop = max(148,84 + nameHeight + 12)
        let bioHeight: CGFloat = min(100,254-bioTop)
        let albums = model.context.items.filter { $0.kind == "albums" }, tracks = model.context.items.filter { $0.kind == "tracks" }
        return ZStack(alignment:.topLeading) {
            header("")
            if let cover {
                Image(uiImage:cover).resizable().interpolation(.high).scaledToFill().frame(width:360,height:448).clipped()
                    .mask(LinearGradient(stops:[.init(color:.clear,location:0),.init(color:.black,location:0.08),.init(color:.black,location:0.55),.init(color:.clear,location:1)],startPoint:.leading,endPoint:.trailing))
                    .mask(LinearGradient(stops:[.init(color:.clear,location:0),.init(color:.black,location:0.06),.init(color:.black,location:0.7),.init(color:.clear,location:1)],startPoint:.top,endPoint:.bottom))
                    .position(x:228,y:248).allowsHitTesting(false)
            }
            label("ARTIST · TIDAL",id:"artist-kind",x:left,y:60,w:664,h:24,size:15,alpha:0.55,caps:true)
            label(item.title,id:"detail-title",x:left,y:84,w:width,h:nameHeight,size:nameSize,serif:true,lines:2)
            if let biography = item.biography, !biography.isEmpty {
                if model.context.biographyExpanded || model.context.artistTab == "about" {
                    ScrollView { Text(biography).font(Design.font(18)).lineSpacing(5).opacity(0.7).frame(maxWidth:.infinity,alignment:.leading) }
                        .frame(width:width,height:380-bioTop).position(x:left+width/2,y:(380+bioTop)/2)
                    button("Close biography",id:"artist-read-less",x:left,y:400,w:224,border:false) { model.context.biographyExpanded = false; model.context.artistTab = "albums" }
                } else {
                    Button { model.context.biographyExpanded = true } label: {
                        Text(biography).font(Design.font(18)).lineSpacing(5).lineLimit(max(2,Int(bioHeight/25))).opacity(0.7).frame(width:width,height:max(64,bioHeight),alignment:.topLeading).contentShape(Rectangle())
                    }.buttonStyle(.plain).accessibilityIdentifier("artist-read-more").accessibilityLabel("Read artist biography").audit("artist-summary",font:18,tap:true,truncates:true).position(x:left+width/2,y:bioTop+max(64,bioHeight)/2)
                }
            }
            if !model.context.biographyExpanded && model.context.artistTab != "about" {
                button(detailMembershipLabel,id:"membership-write",x:item.biography == nil ? left : 816,y:item.biography == nil ? max(148,84+nameHeight+12) : 262,w:184,enabled:membershipEnabled) { toggleMembership() }.accessibilityLabel(model.membershipAction)
                if !albums.isEmpty { button("Albums",id:"artist-tab-albums",x:left,y:312,w:120,border:false,size:18,alignment:.leading,indicator:model.context.artistTab == "albums") { model.selectArtistTab("albums") } }
                if !tracks.isEmpty { button("Tracks",id:"artist-tab-tracks",x:left+136,y:312,w:120,border:false,size:18,alignment:.leading,indicator:model.context.artistTab == "tracks") { model.selectArtistTab("tracks") } }
                if model.context.artistTab == "tracks" { rows(y:384,height:88,items:tracks,tracks:true,width:1000-left,left:left) }
                else if !albums.isEmpty {
                    ScrollView(.horizontal) {
                        HStack(spacing:16) {
                            ForEach(albums) { album in
                                Button { model.details(album) } label: {
                                    Group {
                                        if let image = model.queueArtwork[album.reference]?.uiImage(palette:model.preferences.palette) { Image(uiImage:image).resizable().interpolation(.high) }
                                        else { Text(album.title).font(Design.font(18,serif:true)).lineLimit(3) }
                                    }.frame(width:96,height:96).clipped().contentShape(Rectangle())
                                }.buttonStyle(.plain).accessibilityIdentifier("artist-album-"+album.id).accessibilityLabel(album.title).audit("artist-album-"+album.id,tap:true,scroll:true).id(album.id)
                            }
                            if model.context.nextOffset != nil { Button("More albums") { model.moreChildren() }.font(Design.font(18)).frame(width:144,height:64).audit("artist-more",font:18,tap:true,scroll:true) }
                        }.scrollTargetLayout()
                    }.scrollPosition(id:$model.context.scrollID,anchor:.leading).frame(width:1000-left,height:96).position(x:left+(1000-left)/2,y:424)
                }
            }
        }
    }
    private var upNext: some View {
        let items = model.context.items.isEmpty ? model.queue : model.context.items
        let sizes: [CGFloat] = [200,150,124,104,90,78,68]
        let alphas = [1.0,0.92,0.78,0.62,0.48,0.34,0.24]
        let selected = items.indices.contains(model.context.queueSelection) ? items[model.context.queueSelection] : items.first
        return ZStack(alignment:.topLeading) {
            header("Up next")
            Rectangle().fill(Design.ink.opacity(0.18)).frame(width:1048,height:1).position(x:524,y:316)
            ScrollView(.horizontal) {
                HStack(alignment:.top,spacing:22) {
                    ForEach(Array(items.enumerated()),id:\.offset) { i,item in
                        let side = sizes[min(i,6)]
                        let image = model.queueArtwork[item.reference]?.uiImage(palette:model.preferences.palette)
                        ZStack(alignment:.topLeading) {
                            Button { model.context.queueSelection = i; model.noteContact() } label: {
                                ZStack {
                                    palette.dark.color
                                    if let image { Image(uiImage:image).resizable().interpolation(.high) }
                                    else { Text(item.title).font(Design.font(18,serif:true)).lineLimit(2).padding(8) }
                                }.frame(width:side,height:side).opacity(alphas[min(i,6)])
                                    .overlay { if model.context.queueSelection == i { Rectangle().stroke(Design.ink.opacity(0.8),lineWidth:1.5).padding(-4) } }
                                    .frame(width:max(72,side),height:side).contentShape(Rectangle())
                            }.buttonStyle(.plain).frame(width:max(72,side),height:side).contentShape(Rectangle())
                                .audit("queue-\(i)",tap:true,scroll:true).position(x:max(72,side)/2,y:204-side/2)
                            if let image {
                                Image(uiImage:image).resizable().interpolation(.high).frame(width:side,height:side).scaleEffect(x:1,y:-1)
                                    .frame(width:side,height:20,alignment:.top).clipped()
                                    .mask(LinearGradient(colors:[.black,.clear],startPoint:.top,endPoint:.bottom))
                                    .opacity(0.22*alphas[min(i,6)]).position(x:max(72,side)/2,y:214)
                                    .allowsHitTesting(false)
                            }
                            DesignText(value:item.title,units:15,lines:2)
                                .frame(width:max(72,side),height:44,alignment:.topLeading)
                                .foregroundStyle(Design.ink).opacity(0.7)
                                .audit("queue-track-title-\(i)",font:15,opacity:0.7,scroll:true,truncates:true,text:item.title,lines:2)
                                .position(x:max(72,side)/2,y:255)
                        }.frame(width:max(72,side),height:284)
                    }
                }.padding(.horizontal,4)
            }.frame(width:960,height:284).position(x:524,y:254)
            label(selected?.reference == model.player.current.reference ? "PLAYING NOW" : "UP NEXT",id:"queue-timing",x:48,y:392,w:952,h:20,size:15,alpha:0.55,caps:true)
            label(selected?.title ?? "Queue unavailable",id:"queue-title",x:48,y:412,w:700,h:42,size:32,serif:true)
            if model.context.nextOffset != nil { button("More",id:"queue-more",x:860,y:388) { model.loadPage(more:true) } }
        }
    }
    private var ask: some View {
        let recording = model.voiceState == "recording", ready = model.voiceState == "stopped"
        let seconds = String(format:"%d:%02d",model.voiceSeconds/60,model.voiceSeconds%60)
        return ZStack(alignment:.topLeading) {
            header(recording || ready ? "" : "Find")
            if recording || ready || model.voiceState == "unavailable" {
                label(recording ? "LISTENING · \(seconds) OF 0:30" : ready ? (model.transcript.isEmpty ? "NOTHING HEARD" : "STOPPED · \(seconds)") : "MICROPHONE UNAVAILABLE",id:"voice-state",x:204,y:40,w:632,h:24,size:15,alpha:0.7,caps:true,accent:true,align:.center)
            }
            if recording { Ripples(reduce:reduceMotion || snapshot).frame(width:520,height:520).position(x:524,y:336).id(model.voiceSession).allowsHitTesting(false) }
            if !queryFocused && ((!recording && !ready) || !model.transcript.isEmpty) {
                label(model.transcript.isEmpty ? "Say an artist, an album or\nthe kind of music you want" : "“\(model.transcript)”",id:"transcript",x:184,y:124,w:680,h:116,size:model.transcript.isEmpty ? 32 : 44,alpha:model.transcript.isEmpty ? 0.7 : 1,serif:true,italic:true,lines:2,align:.center)
            }
            if !queryFocused { icon(recording ? .stop : ready ? .submit : .mic,id:ready ? "voice-search" : "voice-record",label:recording ? "Stop recording" : ready ? "Search transcript" : "Start recording",x:488,y:recording || ready ? 300 : 232,w:72,h:72,ring:true,accent:true,enabled:!ready || !model.transcript.isEmpty,glyph:28) {
                queryFocused = false; model.context.typing = false
                if recording { model.stopVoice() } else if ready { model.submitVoice() } else { model.startVoice() }
            }
            }
            if ready { icon(.reset,id:"voice-reset",label:"Discard and record again",x:376,y:304,w:72,h:64,ring:true,glyph:26,ringSize:56) { model.startVoice() } }
            if !recording && !ready {
                TextField("Or type here",text:$model.context.query).font(Design.font(26,serif:true,italic:true)).focused($queryFocused).submitLabel(.search).autocorrectionDisabled()
                    .accessibilityIdentifier("typed-query").onSubmit { queryFocused = false; model.submitTypedSearch() }
                    .frame(width:864,height:64).audit("query",font:26,tap:true).position(x:480,y:queryFocused ? 146 : 412)
                Rectangle().fill(Design.ink.opacity(0.35)).frame(width:864,height:1).position(x:480,y:queryFocused ? 178 : 444)
                icon(.search,id:"search",label:"Search",x:928,y:queryFocused ? 114 : 380,enabled:!model.context.query.trimmingCharacters(in:.whitespacesAndNewlines).isEmpty && model.context.query.utf8.count <= 256) { queryFocused = false; model.submitTypedSearch() }
            }
        }
    }
    private var utility: some View {
        ZStack(alignment:.topLeading) {
            header(model.context.screen == .wifi ? "Wi-Fi" : model.context.screen.rawValue.capitalized)
            switch model.context.screen {
            case .settings:
                settingRow("Display",value:"Palette, brightness and idle time",index:0) { model.navigate(.display) }
                settingRow("Connection",value:model.online ? "Connected to bridge" : "Connection unavailable",index:1) { model.navigate(.connection) }
                settingRow("Device",value:"Battery and local state",index:2) { model.navigate(.device) }
                settingRow("Wi-Fi",value:"Configure in iOS Settings",index:3) { model.navigate(.wifi) }
            case .display:
                label("Palette",id:"palette-label",x:48,y:112,w:300,h:28,size:22)
                ForEach(Array(["sage","sand","slate"].enumerated()),id:\.offset) { i,name in
                    button(name.capitalized,id:"palette-"+name,x:48+CGFloat(i)*128,y:144,w:120,border:false,
                           indicator:model.preferences.palette == name) { model.preferences.palette = name; model.preferences.save() }
                        .opacity(model.preferences.palette == name ? 1 : 0.55)
                }
                label("Brightness",id:"brightness-label",x:48,y:210,w:300,h:28,size:22)
                HairlineSlider(value:$model.preferences.brightness)
                    .onChange(of:model.preferences.brightness) { _,v in UIScreen.main.brightness = v; model.preferences.save() }
                    .frame(width:952,height:64).audit("brightness",tap:true).position(x:524,y:266)
                label("Turn screen off after",id:"timeout-label",x:48,y:312,w:500,h:30,size:22)
                Menu {
                    ForEach([30,60,120,300],id:\.self) { seconds in Button("\(seconds) seconds") { model.preferences.timeout = seconds; model.preferences.save() } }
                } label: { Text("\(model.preferences.timeout/60 > 0 ? String(model.preferences.timeout/60) + (model.preferences.timeout == 60 ? " minute" : " minutes") : "30 seconds")⌄").font(Design.font(22)).frame(width:240,height:56).overlay(Capsule().stroke(Design.ink.opacity(0.18))).contentShape(Rectangle()) }
                    .audit("timeout",font:22,tap:true,pill:true).position(x:168,y:372)
                label("Saved on this iPhone",id:"preference-feedback",x:48,y:432,w:952,h:28,size:18,alpha:0.55)
            case .connection:
                settingRow("Bridge",value:model.online ? "Connected with provisioned trust" : model.status,index:0) { Task { await model.refresh() } }
                settingRow("Pairing",value:"Private enrollment and trust",index:1) { model.navigate(.pairing) }
                if model.unknownAction != nil { settingRow("Acknowledge uncertain command",value:"Clears the notice; sends no command",index:2) { model.acknowledgeUnknown() } }
            case .device:
                Toggle("Stop on silence",isOn:$model.stopOnSilence).font(Design.font(22)).tint(Design.accent)
                    .accessibilityIdentifier("stop-on-silence").frame(width:952,height:64).audit("stop-on-silence",font:22,tap:true).position(x:524,y:392)
                let level = UIDevice.current.batteryLevel
                label(level < 0 ? "Battery unavailable" : "Battery \(Int(level*100))%",id:"battery",x:48,y:112,w:952,h:40,size:22)
                label("Still Water · iPhone display client",id:"device",x:48,y:192,w:952,h:40,size:22)
                label("Charging is managed by iOS and the power bank",id:"power",x:48,y:272,w:952,h:60,size:18,alpha:0.7,lines:2)
            case .wifi:
                label("Configure Wi-Fi in iOS Settings, then return here. No Wi-Fi credentials are stored by Still Water.",id:"wifi",x:48,y:112,w:952,h:150,size:22,alpha:0.7,lines:3)
            case .pairing:
                PairingView(model:model).frame(width:952,height:344).position(x:524,y:296)
            default: EmptyView()
            }
        }
    }
    private func settingRow(_ title: String,value: String,index: Int,action: @escaping () -> Void) -> some View {
        Button(action:action) {
            VStack(alignment:.leading,spacing:6) {
                Text(title).font(Design.font(22))
                Text(value).font(Design.font(18)).opacity(0.55).lineLimit(1)
            }.frame(width:952,height:72,alignment:.leading).overlay(alignment:.trailing) { Text("›").font(Design.font(22)).opacity(0.45) }
                .overlay(alignment:.bottom) { Rectangle().fill(Design.ink.opacity(0.18)).frame(height:1) }
                .contentShape(Rectangle())
        }.buttonStyle(.plain).audit("settings-\(index)",font:22,tap:true).position(x:524,y:152+CGFloat(index)*80)
    }
}

struct Ripples: View {
    var reduce: Bool
    @State private var expand = false
    var body: some View {
        ZStack {
            ForEach(0..<3) { i in
                Circle().stroke(Design.accent.opacity(reduce ? 0.2 : expand ? 0 : 0.55),lineWidth:1)
                    .scaleEffect(reduce ? 0.5 : expand ? 1 : 45.0/260.0)
                    .animation(reduce ? nil : .linear(duration:3.6).repeatForever(autoreverses:false).delay(Double(i)*1.2),value:expand)
            }
        }.onAppear { expand = true }
    }
}
