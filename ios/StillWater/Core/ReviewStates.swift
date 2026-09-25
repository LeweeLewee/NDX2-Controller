import Foundation

@MainActor enum ReviewStates {
    static let all = ["still-fallback", "still-artwork", "touched", "paused", "stopped", "longtitle", "noart", "offline", "pending", "unknown", "wake", "queue", "find", "keyboard", "detail", "library", "artist-following", "track-liked", "album-saved", "ask-idle", "ask-typing", "ask-unavailable", "ask-recording", "ask-stopped", "settings", "display", "connection", "device", "wifi", "pairing"]
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
        model.rest = ["touched","paused","offline","pending","unknown"].contains(state) ? .touched : .still
        switch state {
        case "paused": model.player.state = "paused"
        case "stopped": model.player.state = "stopped"; model.player.title = ""; model.artwork = nil
        case "longtitle": model.player.title = "An Exceptionally Long Track Title for the Seated Listening Trial"
        case "noart": model.artwork = nil; model.colorPreview = nil
        case "offline": model.online = false; model.artwork = nil; model.colorPreview = nil
        case "pending": model.pendingAction = "transport"; model.pendingTarget = "play-pause"
        case "unknown": model.unknownAction = "amplifier"
        case "wake": model.rest = .waking
        case "queue":
            model.context.screen = .queue; model.context.items = model.queue
            for _ in 0..<7 { await model.loadQueueArtwork() }
        case "find","keyboard","library","detail":
            let fixture = FixtureTransport()
            model.context.items = fixture.sample("search-albums")["data"]["items"].values.map(MusicItem.init)
            if state == "detail" {
                let d = fixture.sample("browse-albums")["data"]
                model.context.screen = .detail; model.context.selected = MusicItem(d["item"])
                model.context.items = d["items"].values.map(MusicItem.init); model.context.playable = true
            } else { model.context.screen = state == "library" ? .library : .find }
            model.context.query = "Evening listening"
            if state == "keyboard" { model.context.screen = .ask; model.context.typing = true; model.keyboardVisible = true }
        case "artist-following","track-liked","album-saved":
            let fixture = FixtureTransport()
            let kind = state == "artist-following" ? "artists" : state == "track-liked" ? "tracks" : "albums"
            let d = fixture.sample("browse-"+kind)["data"]
            model.context.screen = .detail; model.context.selected = MusicItem(d["item"])
            model.context.items = d["items"].values.map(MusicItem.init)
            model.context.playable = d["playable"].flag == true; model.context.membership = "saved"
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
