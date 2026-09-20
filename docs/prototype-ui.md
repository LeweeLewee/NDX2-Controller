# Prototype UI

The first computer-side prototype follows the selected Waveshare 800 × 480 landscape canvas. It is a browser interface with a small Python bridge; it is not ESP32 firmware.

## Run the demo

From the repository root, with Python 3.9+:

```sh
python tools/prototype_ui.py
```

Open [the local prototype](http://127.0.0.1:8990). The server listens on loopback only. Stop it with Ctrl+C. No dependencies, credentials or NDX connection are needed for the demo. Queue and demo state live in the page and reset on reload.

Try Find music → Albums → Mezzanine → Play now; then Next, Pause and Queue. Search the small Massive Attack sample catalogue, browse Collection, open tracks, and use Play next or Add to queue. Album contents are deliberately abbreviated sample fixtures. All demo playback is silent and explicitly labelled.

## Configure live services

```sh
python tools/prototype_ui.py --tidal --country GB
python tools/prototype_ui.py --ndx NDX_IP --tidal --country GB
```

The first mode uses live TIDAL catalogue metadata with a simulated player. The second enables native controls against the private NDX address you supply. Run it at home with authorization to change playback. Credentials are prompted locally without echo, or read from TIDAL_CLIENT_ID and TIDAL_CLIENT_SECRET environment variables. Keep them out of command arguments, source files and chat. They are retained only by the Python process, never sent to the browser.

Without --tidal, search is a demo fixture even if an NDX is configured; its candidate IDs still require native resolution. Collection and Queue use the NDX when --ndx is configured.

The bridge resolves selected candidates through native Naim browse. Play buttons require a matching returned native reference and TIDAL object class. Each mutation reads player state first and is sent once; a timeout does not trigger automatic retry. Acknowledgement is labelled as a request, and the Now playing screen polls actual player state every five seconds while visible. The search-to-native-track-play path has now passed through this UI on the home network.

The bridge validates Host and Origin, accepts only JSON at its fixed API route, and exposes no arbitrary proxy, audio URL, volume or device-configuration operation. It is a local development service, not a network-accessible Pi deployment.

## Scope and remaining work

Cover art currently previews a tonal treatment: charcoal shadows, sage midtones and warm sand highlights matching the controls. An SVG luminance filter applies at render time in both artwork views; the cached original JPEG remains unchanged. This is a browser design trial, not yet an embedded rendering implementation.

| Available in this prototype | Remaining |
| --- | --- |
| Ranked search, type filters and catalogue next-page requests | Broader album/playlist and failure-recovery UI trials |
| Native favourites and item drill-down | Large collections and back-navigation edge cases on real responses |
| Play now, play next and append requests | Confirm native queue mutations and app coexistence through the UI |
| Now playing, pause/resume, next/previous and stop | Real disconnect/reconnect and asynchronous transition validation |
| Queue listing and refresh | Queue removal/reordering controls |
| Player-supplied cover art in Now Playing and native detail views, with bounded caching and fallback | Broader artwork coverage across sources |
| Browser input field and responsive layout | Embedded on-screen keyboard, physical touch sizing and LVGL implementation |

Amplifier volume remains excluded pending a successful System Automation test. Artwork, duration and playback state in demo mode are illustrations, not device observations. The browser does not measure display power, standby, wake latency or physical usability.

## Verification

36 offline tests pass, including native-resolution gating, artwork registration and album-name mapping, rejection of unsupported volume, demo isolation and HTTP Host/Origin enforcement. The loopback HTTP test needs an environment that permits local sockets. Browser checks covered rendered now-playing layout, search filtering, album and track detail, demo play, next, pause, queue listing/addition and return navigation. After returning home, live TIDAL search → native Teardrop playback and AI suggestion → TIDAL → native artist browsing also passed. Live Now Playing artwork loaded at 640 × 640 and was visually verified without changing playback. The user confirmed that microphone input returned the correct transcript. See [voice and AI discovery](voice-discovery.md) for setup.
