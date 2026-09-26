import Foundation

@MainActor enum ReviewStates {
    static let all = ["still-fallback", "still-artwork", "touched", "now-liked", "paused", "stopped", "longtitle", "noart", "offline", "pending", "unknown", "wake", "queue", "find", "keyboard", "detail", "library", "library-albums", "library-tracks", "library-artists", "library-playlists", "artist-following", "artist-tracks", "artist-about", "artist-missing", "artist-no-bio", "artist-no-portrait", "artist-no-albums", "artist-long-name", "track-liked", "album-saved", "ask-idle", "ask-typing", "ask-unavailable", "ask-recording", "ask-stopped", "ask-empty", "volume-pending", "settings", "display", "connection", "device", "wifi", "pairing"]
    static func make(_ state: String) async -> ControllerModel {
        let transport = FixtureTransport()
        if ["paused","stopped","longtitle","noart"].contains(state) { transport.state = state }
        let model = ControllerModel(transport:transport,clock:{100},restore:false)
        model.snapshotMode = true; model.active = true
        await apply(state,to:model)
        return model
    }
    static func apply(_ state: String, to model: ControllerModel) async {
        guard all.contains(state) else { return }
        await model.refresh(); model.consumeContact = false
        if !["still-fallback","noart","stopped"].contains(state) { await model.loadArtwork() }
        model.rest = ["touched","now-liked","paused","offline","pending","unknown"].contains(state) ? .touched : .still
        switch state {
        case "now-liked": model.player.current.saved = "saved"
        case "paused": model.player.state = "paused"
        case "stopped": model.player.state = "stopped"; model.player.title = ""; model.artwork = nil
        case "longtitle": model.player.title = "An Exceptionally Long Track Title for the Seated Listening Trial"
        case "noart": model.artwork = nil; model.colorPreview = nil
        case "offline": model.online = false; model.artwork = nil; model.colorPreview = nil
        case "volume-pending": model.rest = .touched; model.pendingAction = "amplifier"; model.pendingTarget = "amp-down"
        case "ask-empty": model.context.screen = .ask; model.voiceState = "stopped"
        case "pending": model.pendingAction = "transport"; model.pendingTarget = "play-pause"
        case "unknown": model.unknownAction = "amplifier"
        case "wake": model.rest = .waking
        case "queue":
            model.context.screen = .queue; model.context.items = model.queue
            for _ in 0..<7 { await model.loadQueueArtwork() }
        case "find","keyboard","detail":
            let fixture = FixtureTransport()
            model.context.items = fixture.sample("search-albums")["data"]["items"].values.map(MusicItem.init)
            if state == "detail" {
                let d = (try? await fixture.send(BridgeRequest("browse",["reference":.string("inputs/tidal/albums/1")]))).map(\.data) ?? .null
                model.context.screen = .detail; model.context.selected = MusicItem(d["item"])
                model.context.items = d["items"].values.map(MusicItem.init); model.context.playable = true
                model.context.selected.title = "An exceptionally long album title for seated reading and layout trials"; model.context.membership = "unsaved"
            } else { model.context.screen = state == "library" ? .library : .find }
            model.context.query = "Evening listening"
            for _ in 0..<model.context.items.count { await model.loadQueueArtwork() }
            if state == "detail" { await model.loadArtwork() }
            if state == "keyboard" { model.context.screen = .ask; model.context.typing = true; model.keyboardVisible = true }
        case "library","library-albums","library-tracks","library-artists","library-playlists":
            let fixture = FixtureTransport()
            let kind = state == "library-tracks" ? "tracks" : state == "library-artists" ? "artists" : state == "library-playlists" ? "playlists" : "albums"
            model.context.screen = .library; model.context.kind = kind; model.account = "connected"
            model.context.items = []
            for index in 0..<12 {
                let number = kind == "tracks" ? 101+index : 1+index
                let ref = "inputs/tidal/"+kind+"/"+String(number)
                if let d = try? await fixture.send(BridgeRequest("browse",["reference":.string(ref)])) {
                    var item = MusicItem(d.data["item"]); item.reference = ref; item.kind = kind; item.saved = "saved"
                    if kind == "artists" { item.title = ["River Stone Ensemble","Maren Holt","The Alder Quartet","Oskar Lind"][index%4] }
                    model.context.items.append(item)
                }
            }
            for _ in 0..<12 { await model.loadQueueArtwork() }
            if kind == "artists", let last = model.context.items.last { model.queueArtwork[last.reference] = nil }
        case "artist-following","artist-tracks","artist-about","artist-missing", "artist-no-bio", "artist-no-portrait", "artist-no-albums", "artist-long-name","track-liked","album-saved":
            let fixture = FixtureTransport()
            let kind = state.hasPrefix("artist-") ? "artists" : state == "track-liked" ? "tracks" : "albums"
            let d = (try? await fixture.send(BridgeRequest("browse",["reference":.string("inputs/tidal/"+kind+"/1")]))).map(\.data) ?? .null
            model.context.screen = .detail; model.context.selected = MusicItem(d["item"])
            model.context.items = d["items"].values.map(MusicItem.init)
            model.context.playable = d["playable"].flag == true; model.context.membership = "saved"
            if kind == "artists" {
                model.artwork = nil
                if state != "artist-missing" { await model.loadArtwork() }
                model.context.artistTab = state == "artist-tracks" ? "tracks" : state == "artist-about" ? "about" : "albums"
                if state == "artist-missing" { model.context.selected.biography = nil; model.context.selected.artwork = nil; model.context.items = [] }
                if state == "artist-no-bio" { model.context.selected.biography = nil }
                if state == "artist-no-portrait" { model.artwork = nil; model.context.selected.artwork = nil }
                if state == "artist-no-albums" { model.context.items = [] }
                if state == "artist-long-name" { model.context.selected.title = "An Exceptionally Long Artist Ensemble Name" }
                for _ in 0..<4 { await model.loadQueueArtwork() }
            }
        case "ask-idle","ask-typing","ask-unavailable":
            model.context.screen = .ask; model.context.typing = state == "ask-typing"
            model.voiceState = state == "ask-unavailable" ? "unavailable" : "idle"
        case "ask-recording","ask-stopped":
            model.context.screen = .ask; model.voiceState = state == "ask-recording" ? "recording" : "stopped"
            model.transcript = "Something like this, but more acoustic"; model.voiceSeconds = 4
        case "settings","display","connection","device","wifi","pairing": model.context.screen = Screen(rawValue:state) ?? .settings
        default: break
        }
    }
}
