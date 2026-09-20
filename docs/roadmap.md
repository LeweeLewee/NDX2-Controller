# Roadmap

## M0 — Concept and native playback feasibility

- [x] Agree compact form, battery operation, weight and bespoke UI direction.
- [x] Record native Naim TIDAL as a hard constraint.
- [x] Reach the actual NDX 2 and browse native TIDAL content.
- [x] Launch one native track and observe playback.
- [x] Establish a local repository and evidence record.

## M1 — Complete software control loop (next)

- [x] Verify public catalogue search and pagination using the project's own TIDAL app (artists, tracks, albums and playlists).
- [ ] Verify search-result IDs through native Naim browse and playback on the home network.
- [x] Retrieve artwork with bounded caching and no credential leakage (native TIDAL JPEG).
- [x] Launch albums and playlists using native Naim semantics.
- [x] Verify queue listing, add/remove/reorder and next/previous behaviour.
- [ ] Identify and test actual amplifier System Automation volume control.
- [x] Verify high-resolution playback where the service and recording support it (24-bit/44.1 kHz observed).
- [ ] Check gapless transitions, native app coexistence and recovery after reconnect.

Automatic track advancement and a new controller connection during playback passed. Audible gaplessness, app concurrency and actual network outage recovery remain open. Switching the Naim app from High to Max changed the native API setting to losslessHd and enabled 24-bit playback through the same native command. Higher sample rates remain untested.
- [ ] Build a small computer-side UI covering search → select → native play → now playing.

**Exit criterion:** all core interactions work on the actual NDX 2, preserve native playback and have recorded evidence. An acknowledged request alone is insufficient.

## M2 — Touch display and power prototype

- [ ] Select a small display plus matching touch hardware.
- [ ] Demonstrate browse/search input and now-playing on e-paper.
- [ ] Measure full-board sleep, connected idle, browsing and refresh consumption.
- [ ] Implement wake/reconnect and stale-state handling.
- [ ] Decide direct ESP32 control versus optional Pi bridge.
- [ ] Select battery and charging electronics based on measured load and packaging.

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
