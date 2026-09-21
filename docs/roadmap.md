# Roadmap

## M0 — Concept and native playback feasibility

- [x] Agree compact form, battery operation, weight and bespoke UI direction.
- [x] Record native Naim TIDAL as a hard constraint.
- [x] Reach the actual NDX 2 and browse native TIDAL content.
- [x] Launch one native track and observe playback.
- [x] Establish a local repository and evidence record.

## M1 — Software feasibility (closed, 20 September 2026)

- [x] Verify public catalogue search and pagination using the project's own TIDAL app (artists, tracks, albums and playlists).
- [x] Verify search-result IDs through native Naim browse and playback on the home network (Teardrop through the UI).
- [x] Retrieve artwork with bounded caching and no credential leakage (native TIDAL JPEG).
- [x] Launch albums and playlists using native Naim semantics.
- [x] Verify queue listing, add/remove/reorder and next/previous behaviour.
- [x] Identify System Automation commands and audibly verify volume down/up; add bounded UI controls.
- [x] Verify high-resolution playback where the service and recording support it (24-bit/44.1 kHz observed).

Automatic track advancement and a new controller connection during playback passed. Audible gaplessness, app concurrency and actual network outage recovery remain open. Switching the Naim app from High to Max changed the native API setting to losslessHd and enabled 24-bit playback through the same native command. Higher sample rates remain untested.
- [x] Build the first 800 × 480 computer-side UI and check demo search, selection, transport and queue interactions.
- [x] Verify search → select → native play → now playing through the UI on the home network.
- [x] Add AI discovery/refinement and verify suggestion → live TIDAL search → native artist browsing.
- [x] Validate browser microphone capture and transcription (user confirmed correct transcript).
- [x] Connect cached native artwork to the UI and verify live Now Playing display.
- [x] Implement TIDAL collection hearts, album saves, artist/playlist saves and OAuth account connection; verify all four save/remove round trips live.
- [x] Provide Back from discovery, nested browsing and main sections with restored browsing context.
- [x] Add save/unsave hearts directly to album search results.
- [x] Add direct Now Playing album/artist shortcuts and related links on track/album details.

**Closeout:** the user accepted software feasibility as achieved. The essential control path has live evidence and native playback is preserved. This is not production readiness or full feature parity. Unfinished UI and reliability work is carried forward below; no failed or untested item is marked proven. Frozen reference: `software-feasibility-v1`; see [handover](milestone-handover.md).

## M2 — Detailed design, deployment and hardware proof (started)

- [x] Audit frozen reference and publish [phase plan](detailed-design-plan.md) with deliverables, dependencies and acceptance gates.
- [x] Resolve display choice: Waveshare selected, Android ruled out (D017, 21 September 2026).
- [x] Reconcile detailed-design records with published main; retain D015 for dedicated display and use D018 for the provisional bridge partition.
- [ ] Implement the hardware-independent software workstream: development-host bridge, fixture-backed controller contract, recovery/security tests and embedded UI/build foundation. Physical and host deployment gates remain open.
- [ ] Confirm HW-001/measurement inventory, obtain purchasing approval if required, then execute HP-01.
- [ ] Deferred B01: album-save visibility differs in laptop browser versus Codex preview; cause undocumented. Investigate only when relevant; no caching assumption or speculative fix.

- [ ] Decide where the bridge runs and specify secure credential storage and persistent sign-in.
- [ ] Validate gapless transitions, native app coexistence and disconnect/reconnect recovery.
- [ ] Define interaction flows and touch targets on the actual 4.3-inch display.
- [ ] Carry forward queue-edit controls and playlist creation/editing, shuffle/repeat/seek UI; prioritize only when required by the detailed design.

- [x] Record hardware baseline and BOM ([hardware](hardware/README.md)); Waveshare selected (D017), hardware proof pending.
- [ ] Validate the selected Waveshare display/touch hardware.
- [ ] Demonstrate browse/search input and now-playing on the preferred LCD; evaluate e-paper fallback only if needed.
- [ ] Measure full-board sleep, connected idle, browsing and refresh consumption.
- [ ] Implement wake/reconnect and stale-state handling.
- [ ] Validate provisional bridge partition (D018), select host after Pi inventory and implement Waveshare embedded UI.
- [ ] Resolve onboard versus external power path, then select the large base battery and charging electronics from measured load and packaging.
- [ ] Resolve wiring, charging access, low-battery handling and service isolation; track open choices in the hardware research register.

**Exit criterion:** usable interaction, reliable wake and a measured energy budget supporting the agreed usage profile. Confirm the desired daily interaction time and listening hours before promising runtime.

## M3 — Physical prototype

- [x] Select original River Stone as stationary table enclosure and record dimensioned packaging study ([layout](hardware/river-stone/README.md)).
- [ ] Surface the original asymmetric shell; verify real wall offsets, screen insertion, mounts, connectors, antenna and microphone space before releasing a fit print.

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
