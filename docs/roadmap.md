# Roadmap

## M0 — Concept and native playback feasibility

- [x] Agree compact form, battery operation, weight and bespoke UI direction.
- [x] Record native Naim TIDAL as a hard constraint.
- [x] Reach the actual NDX 2 and browse native TIDAL content.
- [x] Launch one native track and observe playback.
- [x] Establish a local repository and evidence record.

## M1 — Complete software control loop (next)

- [x] Verify public catalogue search and pagination using the project's own TIDAL app (artists, tracks, albums and playlists).
- [x] Verify search-result IDs through native Naim browse and playback on the home network (Teardrop through the UI).
- [x] Retrieve artwork with bounded caching and no credential leakage (native TIDAL JPEG).
- [x] Launch albums and playlists using native Naim semantics.
- [x] Verify queue listing, add/remove/reorder and next/previous behaviour.
- [x] Identify System Automation commands and audibly verify volume down/up; add bounded UI controls.
- [x] Verify high-resolution playback where the service and recording support it (24-bit/44.1 kHz observed).
- [ ] Check gapless transitions, native app coexistence and recovery after reconnect.

Automatic track advancement and a new controller connection during playback passed. Audible gaplessness, app concurrency and actual network outage recovery remain open. Switching the Naim app from High to Max changed the native API setting to losslessHd and enabled 24-bit playback through the same native command. Higher sample rates remain untested.
- [x] Build the first 800 × 480 computer-side UI and check demo search, selection, transport and queue interactions.
- [x] Verify search → select → native play → now playing through the UI on the home network.
- [x] Add AI discovery/refinement and verify suggestion → live TIDAL search → native artist browsing.
- [x] Validate browser microphone capture and transcription (user confirmed correct transcript).
- [x] Connect cached native artwork to the UI and verify live Now Playing display.
- [ ] Complete queue-edit controls.
- [x] Implement TIDAL collection hearts, album saves, artist/playlist saves and OAuth account connection; verify all four save/remove round trips live.
- [x] Provide Back from discovery, nested browsing and main sections with restored browsing context.
- [ ] Add playlist creation/editing, related album/artist links and shuffle/repeat/seek UI.

**Exit criterion:** all core interactions work on the actual NDX 2, preserve native playback and have recorded evidence. An acknowledged request alone is insufficient.

## M2 — Touch display and power prototype

- [x] Record hardware design baseline and initial parts BOM ([hardware](hardware/README.md)); Waveshare ESP32-S3-Touch-LCD-4.3B is preferred.
- [ ] Validate and finalize the display/touch selection.
- [ ] Demonstrate browse/search input and now-playing on the preferred LCD; evaluate e-paper fallback only if needed.
- [ ] Measure full-board sleep, connected idle, browsing and refresh consumption.
- [ ] Implement wake/reconnect and stale-state handling.
- [ ] Decide direct ESP32 control versus optional Pi bridge.
- [ ] Resolve onboard versus external power path, then select the large base battery and charging electronics from measured load and packaging.
- [ ] Resolve wiring, charging access, low-battery handling and service isolation; track open choices in the hardware research register.

**Exit criterion:** usable interaction, reliable wake and a measured energy budget supporting the agreed usage profile. Confirm the desired daily interaction time and listening hours before promising runtime.

## M3 — Physical prototype

- [ ] Finalize dimensions around measured components.
- [ ] Print fit prototype; evaluate tilt, weight, touch stability and screen protection.
- [ ] Integrate serviceable battery and charging access.
- [ ] Iterate finish and assembly.

## M4 — Daily-use validation

- [ ] Repeated reconnects, Wi-Fi outages and service authentication renewal.
- [ ] Sustained album playback and interaction from multiple controllers.
- [ ] Real battery-life trial and charging behaviour.
- [ ] Build/assembly documentation and reproducible firmware process.
- [ ] Evaluate additional native music sources.
