import Foundation
import Combine

enum Screen: String, CaseIterable { case now, find, detail, library, queue, ask, settings, display, connection, device, wifi, pairing }
enum Rest: String { case waking, still, touched }
struct BrowseContext {
    var screen: Screen = .now, query = "", kind = "albums", items: [MusicItem] = []
    var cursor: String?, pageCursor: String?, nextOffset: Int?, resultID: String?, scrollID: String?
    var selected = MusicItem(), playable = false, membership = "unknown", queueSelection = 1
}
struct DisplayPreferences: Codable {
    var palette = "sage", brightness = 0.35, timeout = 120
    static func load() -> Self {
        guard let raw = UserDefaults.standard.data(forKey: "display-v1"),
              let p = try? JSONDecoder().decode(Self.self, from: raw),
              ["sage", "sand", "slate"].contains(p.palette), (0.1...1).contains(p.brightness),
              [30, 60, 120, 300].contains(p.timeout) else { return Self() }
        return p
    }
    func save() { if let d = try? JSONEncoder().encode(self) { UserDefaults.standard.set(d, forKey: "display-v1") } }
}
struct Preview {
    let reference: String, pixels: Data, side: Int, deadline: Double
}

@MainActor final class ControllerModel: ObservableObject {
    @Published var context = BrowseContext(), player = Player(), queue: [MusicItem] = []
    @Published var online = false, fixture = false, active = false, consumeContact = true
    @Published var rest: Rest = .still, status = "", account = "disconnected"
    @Published var pendingAction: String?, unknownAction: String?, pendingTarget: String?
    @Published var artwork: Preview?, preferences = DisplayPreferences.load()
    @Published var colorPreview: Preview?
    @Published var queueArtwork: [String:Preview] = [:]
    @Published var voiceState = "idle", transcript = "", voiceSeconds = 0
    @Published var loading = false, keyboardVisible = false
    var voiceStart: (() -> Void)?, voiceCancel: (() -> Void)?
    var reportBattery: (() async -> Void)?
    var applyIdlePolicy: ((Bool) -> Void)?
    var snapshotMode = false
    private(set) var history: [BrowseContext] = [], freshUntil = 0.0, boot: String?
    private(set) var generation = 0
    private var transport: BridgeTransport
    private var timer: Task<Void, Never>?, readTask: Task<Void, Never>?, artTask: Task<Void, Never>?
    @Published private(set) var inFlight: UUID?
    private var flightDeadline = 0.0, flightMutation = false
    private var nextPoll = 0.0, lastTouch = 0.0, voiceDeadline = 0.0, nextBattery = 0.0, retry = 1.0
    private var revision = -1
    private var nextArtAttempt = 0.0
    private var nextQueueArtAttempt = 0.0
    let clock: () -> Double
    init(transport: BridgeTransport, clock: @escaping () -> Double = { ProcessInfo.processInfo.systemUptime }, restore: Bool = true) {
        self.transport = transport; self.clock = clock; fixture = transport is FixtureTransport
        if restore { unknownAction = UserDefaults.standard.string(forKey: "uncertain-command") }
    }
    var controlsAvailable: Bool { active && online && clock() < freshUntil && !consumeContact && pendingAction == nil && inFlight == nil }
    var touched: Bool { rest == .touched }
    var artworkReference: String? { context.screen == .detail ? context.selected.artwork : player.artwork }
    func replaceTransport(_ value: BridgeTransport) {
        deactivate(); transport = value; fixture = value is FixtureTransport; player = Player(); queue = []; boot = nil; revision = -1
        activate()
    }
    func activate() {
        guard !active, !snapshotMode else { return }
        active = true; consumeContact = true; rest = .waking; lastTouch = clock()
        nextPoll = 0; nextBattery = clock(); retry = 1
        timer = Task { [weak self] in
            while !Task.isCancelled {
                self?.tick()
                try? await Task.sleep(nanoseconds: 200_000_000)
            }
        }
    }
    func deactivate() {
        active = false; timer?.cancel(); timer = nil
        invalidate(); online = false; freshUntil = 0; applyIdlePolicy?(false)
    }
    func invalidate() {
        generation += 1; consumeContact = true
        if flightMutation { markUnknown() }
        inFlight = nil; flightMutation = false; pendingAction = nil; pendingTarget = nil
        transport.cancel(); readTask?.cancel(); artTask?.cancel(); artTask = nil
        artwork = nil; colorPreview = nil; queueArtwork = [:]; context.membership = "unknown"; context.items = context.items.map { var i = $0; i.saved = "unknown"; return i }
        for i in history.indices { history[i].membership = "unknown"; history[i].items = history[i].items.map { var v = $0; v.saved = "unknown"; return v } }
        cancelVoice()
    }
    private func markUnknown() {
        unknownAction = pendingAction ?? unknownAction
        if let action = unknownAction { UserDefaults.standard.set(action, forKey: "uncertain-command") }
    }
    func acknowledgeUnknown() {
        // Explicit local acknowledgement, never a retry or claim that the command completed.
        unknownAction = nil; UserDefaults.standard.removeObject(forKey: "uncertain-command")
    }
    func contactEnded() {
        lastTouch = clock()
        if consumeContact { consumeContact = false }
        if context.screen == .now { rest = .touched }
    }
    func noteContact() { lastTouch = clock() }
    func tick() {
        guard active, !snapshotMode else { return }
        let now = clock()
        if inFlight != nil && now >= flightDeadline { invalidate(); online = false; status = "Connection unavailable"; nextPoll = now + retry }
        if now >= freshUntil { online = false; artwork = nil; colorPreview = nil; queueArtwork = [:]; if voiceState == "recording" { cancelVoice() } }
        if let art = artwork, now >= art.deadline { artwork = nil }
        if let art = colorPreview, now >= art.deadline { colorPreview = nil }
        if queueArtwork.values.contains(where:{ now >= $0.deadline }) { queueArtwork = queueArtwork.filter { now < $0.value.deadline } }
        if rest == .waking && now - lastTouch >= 0.4 { rest = .still }
        if context.screen == .now && rest == .touched && now - lastTouch >= 8 { rest = .still }
        if voiceState == "recording" {
            voiceSeconds = min(30, max(0, Int(30 - (voiceDeadline - now))))
            if now >= voiceDeadline { stopVoice() }
        }
        // iOS owns actual lock. Releasing the idle timer cannot force a hardware sleep deadline.
        let idleHold = now - lastTouch < Double(preferences.timeout) && (rest == .touched || (context.screen == .ask && voiceState == "recording"))
        applyIdlePolicy?(idleHold)
        guard inFlight == nil else { return }
        if now >= nextPoll {
            nextPoll = now + 2
            readTask = Task { await self.refresh() }
        } else if now >= nextBattery, let reportBattery {
            nextBattery = now + 900
            readTask = Task { await reportBattery() }
        } else if artwork == nil && artTask == nil && artworkReference != nil && online && now >= nextArtAttempt {
            nextArtAttempt = now + 5
            artTask = Task { await self.loadArtwork(); self.artTask = nil }
        } else if context.screen == .queue && artTask == nil && online && now >= nextQueueArtAttempt {
            nextQueueArtAttempt = now + 5
            artTask = Task { await self.loadQueueArtwork(); self.artTask = nil }
        }
    }
    func perform(_ request: BridgeRequest) async -> BridgeReply? {
        guard active, inFlight == nil else { return nil }
        let token = UUID(), gen = generation
        inFlight = token; flightDeadline = clock() + 8; flightMutation = request.isMutation
        if request.isMutation {
            pendingAction = request.action
            UserDefaults.standard.set(request.action, forKey: "uncertain-command")
        }
        defer { if inFlight == token { inFlight = nil; flightMutation = false; pendingAction = nil; pendingTarget = nil } }
        do {
            let r = try await transport.send(request)
            guard active, generation == gen, inFlight == token else { return nil }
            guard clock() < flightDeadline, !Task.isCancelled else {
                let mutation = flightMutation
                invalidate(); online = false; freshUntil = 0; status = mutation ? "Command outcome unknown" : "Connection unavailable"
                return nil
            }
            fixture = r.fixture
            if let boot, boot != r.boot_id {
                if request.isMutation { markUnknown() }
                self.boot = r.boot_id; revision = -1; freshUntil = 0
                invalidate(); online = false; nextPoll = 0
                return nil
            }
            boot = r.boot_id
            if request.isMutation {
                if r.outcome == "unknown" { markUnknown() }
                else if unknownAction == nil { UserDefaults.standard.removeObject(forKey: "uncertain-command") }
            }
            if r.outcome == "rejected" { status = r.error["code"].text ?? "Request unavailable" }
            return r
        } catch {
            guard generation == gen, inFlight == token else { return nil }
            if request.isMutation { markUnknown() }
            invalidate(); online = false; freshUntil = 0
            status = error as? BridgeFailure == .unauthenticated ? "Pairing requires attention" : "Reconnecting to the bridge"
            nextPoll = clock() + retry + Double.random(in: 0...0.2); retry = min(30, retry * 2)
            return nil
        }
    }
    func refresh() async {
        let started = clock()
        guard let r = await perform(BridgeRequest("snapshot")), r.outcome == "observed",
              let valid = r.data["valid_for_ms"].number, (1...5000).contains(valid),
              let age = r.data["age_ms"].number, (0...5000).contains(age), age + valid <= 5000,
              let rev = r.data["revision"].number, rev >= revision,
              clock() < started + Double(valid) / 1000 else { return }
        revision = rev; freshUntil = started + Double(valid) / 1000; online = true; retry = 1; status = ""
        var p = Player(r.data["player"]); p.current = MusicItem(r.data["current_item"])
        if p.artwork != player.artwork { artwork = nil; colorPreview = nil; nextArtAttempt = 0 }
        player = p; queue = r.data["queue"].values.map(MusicItem.init)
        account = r.data["account"].text ?? "disconnected"
    }
    func navigate(_ screen: Screen) {
        noteContact(); cancelVoice(); generation += 1; transport.cancel(); inFlight = nil
        readTask?.cancel(); artTask?.cancel(); artTask = nil; artwork = nil; colorPreview = nil; nextArtAttempt = 0; loading = false
        if pendingAction != nil { markUnknown(); pendingAction = nil; flightMutation = false }
        history.append(context); if history.count > 4 { history.removeFirst() }
        context = BrowseContext(screen: screen)
        if screen == .ask { startVoice() }
        if [.library, .queue].contains(screen) { loadPage() }
    }
    func back(toNow: Bool = false) {
        cancelVoice(); generation += 1; transport.cancel(); inFlight = nil
        if pendingAction != nil { markUnknown(); pendingAction = nil; flightMutation = false }
        readTask?.cancel(); artTask?.cancel(); artTask = nil; artwork = nil; colorPreview = nil; nextArtAttempt = 0; loading = false
        context = toNow ? BrowseContext() : history.popLast() ?? BrowseContext()
        if toNow { history.removeAll() }
        noteContact()
    }
    func search() { noteContact(); keyboardVisible = false; context.cursor = nil; context.pageCursor = nil; context.nextOffset = nil; context.resultID = nil; loadPage() }
    func filter(_ kind: String) { context.kind = kind; search() }
    private func cancelReadForInteraction() -> Bool {
        guard !flightMutation else { status = "Command in progress"; return false }
        generation += 1; transport.cancel(); inFlight = nil
        readTask?.cancel(); artTask?.cancel(); artTask = nil
        return true
    }
    func loadPage(more: Bool = false) {
        guard cancelReadForInteraction() else { return }
        if context.screen == .find && context.query.utf8.count > 256 { status = "Search text too long; use fewer words."; return }
        let gen = generation, old = context
        loading = true
        readTask = Task {
            defer { if self.generation == gen { self.loading = false } }
            var args: [String: JSONValue] = [:]
            let action = old.screen == .library ? "library_page" : old.screen == .queue ? "queue" : "search"
            if action != "queue" { args["kind"] = .string(old.kind) }
            if action == "search" {
                args["query"] = .string(String(old.query.prefix(256)))
                if let id = old.resultID { args["result_id"] = .string(id) }
            }
            if more {
                if let offset = old.nextOffset {
                    args["offset"] = .int(offset)
                    if let cursor = old.pageCursor { args["cursor"] = .string(cursor) }
                }
                else if let cursor = old.cursor { args["cursor"] = .string(cursor) }
                else { return }
            }
            guard let r = await self.perform(BridgeRequest(action, args)), r.outcome == "observed", self.generation == gen else { return }
            self.context.items = r.data["items"].values.map(MusicItem.init)
            self.context.scrollID = nil
            self.context.pageCursor = args["cursor"]?.text
            self.context.nextOffset = r.data["next_offset"].number; self.context.cursor = r.data["cursor"].text
            self.context.resultID = r.data["result_id"].text
        }
    }
    func details(_ item: MusicItem) {
        guard !item.reference.isEmpty else { return }
        let old = context
        navigate(.detail); context.selected = item
        let gen = generation
        readTask = Task {
            guard let r = await self.perform(BridgeRequest("browse", ["reference": .string(item.reference)])), r.outcome == "observed", self.generation == gen else {
                if self.generation == gen { self.context = old; _ = self.history.popLast() }
                return
            }
            self.context.selected = MusicItem(r.data["item"]); self.context.playable = r.data["playable"].flag == true
            self.context.items = r.data["items"].values.map(MusicItem.init); self.context.nextOffset = r.data["next_offset"].number
            await self.membership()
        }
    }
    func moreChildren() {
        guard let offset = context.nextOffset else { return }
        guard cancelReadForInteraction() else { return }
        let ref = context.selected.reference, gen = generation
        readTask = Task {
            guard let r = await self.perform(BridgeRequest("browse", ["reference": .string(ref), "offset": .int(offset)])), r.outcome == "observed", gen == self.generation else { return }
            self.context.items = r.data["items"].values.map(MusicItem.init); self.context.nextOffset = r.data["next_offset"].number
        }
    }
    func membership() async {
        let ref = context.selected.reference, gen = generation
        guard let r = await perform(BridgeRequest("library_state", ["reference": .string(ref)])), r.outcome == "observed", gen == generation else { return }
        context.membership = r.data["saved_state"].text ?? "unknown"
        if unknownAction == "library_save" { acknowledgeUnknown() }
    }
    func mutate(_ action: String, _ args: [String: JSONValue], target: String? = nil) {
        guard controlsAvailable, inFlight == nil, unknownAction != action else { return }
        noteContact(); pendingTarget = target
        readTask = Task {
            guard let r = await self.perform(BridgeRequest(action, args)) else { return }
            if r.outcome == "submitted" { self.status = "Request sent; checking player" }
            await self.refresh()
            if action == "library_save" { await self.membership() }
        }
    }
    func loadArtwork() async {
        guard let ref = artworkReference, ref.range(of: "^/artwork/[0-9a-f]{64}\\.jpg$", options: .regularExpression) != nil else { return }
        let gen = generation
        let paletteStart = clock()
        if let reply = await perform(BridgeRequest("artwork",["reference":.string(ref)])), generation == gen {
            var small = ArtworkAssembly(reference:ref,side:80)
            if (try? small.append(reply,started:paletteStart,now:clock())) != nil, small.complete,
               active, artworkReference == ref, clock() < freshUntil {
                colorPreview = Preview(reference:ref,pixels:small.bytes,side:80,deadline:small.deadline)
            }
        }
        var image = ArtworkAssembly(reference: ref, side: 320)
        while !image.complete && active && generation == gen && artworkReference == ref && !Task.isCancelled {
            if clock() >= nextPoll { nextPoll = clock() + 2; await refresh() }
            guard online else { return }
            let start = clock()
            guard let reply = await perform(BridgeRequest("artwork", ["reference": .string(ref), "side": .int(320), "pixel_offset": .int(image.offset)])) else { return }
            do { try image.append(reply, started: start, now: clock()) } catch { return }
        }
        guard active, generation == gen, artworkReference == ref, image.complete, clock() < freshUntil, clock() < image.deadline else { return }
        artwork = Preview(reference: ref, pixels: image.bytes, side: 320, deadline: image.deadline)
    }
    func loadQueueArtwork() async {
        let items = context.items.isEmpty ? queue : context.items
        let candidates = Array(items.prefix(7))
        guard context.screen == .queue, let item = candidates.first(where:{ queueArtwork[$0.reference] == nil }) else { return }
        let gen = generation
        // Queue artwork is registered by a native read, never fetched as an arbitrary URL.
        guard let detail = await perform(BridgeRequest("browse",["reference":.string(item.reference)])),
              detail.outcome == "observed", detail.data["item"]["reference"].text == item.reference,
              let ref = detail.data["item"]["artwork"].text,
              ref.range(of:"^/artwork/[0-9a-f]{64}\\.jpg$",options:.regularExpression) != nil,
              generation == gen else { return }
        let start = clock()
        guard let reply = await perform(BridgeRequest("artwork",["reference":.string(ref)])), generation == gen else { return }
        var image = ArtworkAssembly(reference:ref,side:80)
        do { try image.append(reply,started:start,now:clock()) } catch { return }
        guard image.complete, online, clock() < freshUntil, context.screen == .queue else { return }
        let currentRefs = Set(candidates.map(\.reference))
        queueArtwork = queueArtwork.filter { currentRefs.contains($0.key) }
        queueArtwork[item.reference] = Preview(reference:ref,pixels:image.bytes,side:80,deadline:image.deadline)
        nextQueueArtAttempt = clock() + 0.2
    }
    func startVoice() {
        cancelVoice(); voiceState = "recording"; voiceDeadline = clock() + 30; voiceSeconds = 0; noteContact()
        if fixture { transcript = "Find quiet instrumental albums" } else { voiceStart?() }
    }
    func stopVoice() { guard voiceState == "recording" else { return }; voiceCancel?(); voiceState = "stopped" }
    func cancelVoice() { voiceCancel?(); voiceState = "idle"; transcript = ""; voiceSeconds = 0 }
    func submitVoice() {
        stopVoice()
        let query = transcript
        guard !query.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty, query.utf8.count <= 256 else { status = "No transcript; try typing"; return }
        navigate(.find); context.query = query; search() // search only; never resolves or plays
    }
}
