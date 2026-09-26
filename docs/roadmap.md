# Roadmap

**Live-beta follow-up — 26 September 2026:** user authorized staged live NDX testing (D036). The 8.1.0 silent beta is preserved. Work is on `codex/still-water-live-beta`; explicit live build and pairing startup are implemented, with real speech disabled. Eleven local project/distribution checks and all 31 native tests pass. Source `1fec991` passed the live-mode device archive; signed release run 36252070759 uploaded **0.1.0 (9.1.0)**. Apple processing completed; **0.1.0 (9.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group with status **Testing**. Host provisioning, phone pairing and live observations remain pending. [Trial plan](ios-live-beta.md). Bridge host and NDX address are requested; do not invent them.

**Brief B.1 testing amendment — 26 September 2026:** the completed-testing instruction authorizes the accumulated boundary, NOW, artist and Library addendum changes. Implementation is on the isolated B1 branch; preserve the primary checkout. Common x48/y24 caption anchor, unchanged phone safe area, aligned transport/mic/volume, larger touched cover, no NOW Find icon, aligned artist children, Library grids/shared thumbnail rows, settled-cover tint and 320px displayed artwork are implemented. The sole mic entry opens Find idle as the documented implementation assumption so typing remains accessible. [Amendment report](ios-b1-amendment.md). All 150 Python tests, five navigation tests and six silent fixture stages pass. First native run passed 29 tests and archive; all 50 captures were reviewed directly or matched to prior reviewed pixels. Final source `0f9ecc6` passed all 30 native tests and archive; all 50 final captures are covered by direct review or pixel-identical comparison. Gallery: `local/ios/review-b1-amendment/review.html`. Release run 36248128881 repeated all 30 native checks and signed/uploaded **0.1.0 (8.1.0)**. Apple processed the build; it is assigned to the existing Naim NDX2 Controller TestFlight group with status **Testing**. Phone acceptance of this amendment remains open. No bridge, firmware or route changes; no live commands.

**B1 visual correction — 26 September 2026:** GitHub retry succeeded. Source `5e78b5f` on `codex/still-water-b1` passed all 28 native tests and the unsigned device archive; all 46 final captures are covered by direct review or pixel-identical comparison. [Visual audit](ios-visual-audit.md); gallery `local/ios/review-b1-visual/review.html`. [Release run 36235235938](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36235235938) repeated native validation, signed and uploaded **0.1.0 (7.1.0)**; Apple processing completed; the build is assigned to the existing Naim NDX2 Controller TestFlight group and shows **Testing**. New user feedback confirms an unresolved shared header boundary: Silent Demo is at y24 on NOW and y6 on every secondary screen. NOW is the required anchor; Up next, Find states/results, Library, detail/artist and all utility screens need a coordinated header/content refactor. This is not fixed in 7.1.0. No overall left shift occurred: the centred canvas, iPhone safe area and extra 8 pt inset remain unchanged. Preserve that left exclusion zone, the working prototype and newer primary-checkout/physical-trial work.

**B1 available in TestFlight — 26 September 2026:** isolated branch `codex/still-water-b1` (D035), tested source `85628f2`. All 150 Python tests, five navigation tests, six silent TLS stages and **28 native tests** passed, including the unsigned device archive. All changed captures in the 46-image gallery were inspected. Revised NOW, Find Idle/Listening/Ready, album/artist layouts, bounded authenticated artist bio/portrait reads and default-on silence stop are implemented. [Implementation and evidence](ios-b1.md); gallery `local/ios/review-b1/review.html`. Tag `ios-preview-2026-09-26-b1` passed [the signed workflow](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36230634817); **0.1.0 (6.1.0)** is assigned to the existing internal group and Apple shows **Testing**. The release workflow repeated all 28 native checks successfully. Preserve the primary checkout, full-bleed safe area and track access/likes. Presence is excluded; live controls, physical speech and mounted-phone acceptance remain untested.


**D034 UI amendment — 25 September 2026:** **0.1.0 (5.1.0)** has been signed and uploaded; Apple processing and existing-group assignment are pending. Album and artist pages are redesigned, NOW elapsed/total time is removed, and Find uses a keyboard icon, microphone-centered ripples, progressive fixture text, Tap to search and microphone clear/restart. Presence is explicitly excluded and not queued. All **26 native tests** and the unsigned archive passed in [run 36191105906](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36191105906), source `10313a8e417b29274112af09548c5d7546707182`. Nine local project/distribution checks also passed. Gallery: `local/ios/review-amendment/review.html` (40 captures). This remains UI-only: simulated speech, fictional artist metadata and neutral portrait fallback; no live NDX or audio. Mounted-phone/user acceptance remains open.

**D033 available in TestFlight — 25 September 2026:** **0.1.0 (4.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group and Apple shows **Testing**. Source `1fddc6ac877e36c8e072acf2acba311bebd17459`, [run 36186308393](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36186308393), passed all **25 native tests**, unsigned archive and signed upload. NOW has a larger icon-only heart, warm ivory outlined/filled states, Find and Library icons, and one Find entry. Find opens idle voice input with explicit recording and secondary typing; both search paths share Results. Still artwork is about 9% larger, with metadata shifted right. The safe-area layout and locked orientation remain. Gallery: `local/ios/review-find/review.html` (36 captures). This remains a silent fixture preview; mounted-phone/user acceptance is open.

**D032 safe-area update available — 25 September 2026:** internal TestFlight **0.1.0 (3.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group and Apple shows **Testing**. Source `6f0b9afa49da5e6953c17664bdc5987e312a9524`, [run 36178335036](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36178335036), passed all 23 native tests and archive/sign/upload checks. The background fills the screen, content respects the system safe area plus an 8 pt inactive inset in the existing locked orientation, Like is compact beside the album, and secondary screens have one plain Back control. Other review suggestions were not adopted. Gallery: `local/ios/review-safe-area/review.html`. Mounted-phone/user acceptance remains open; this is still a silent preview.

**D032 remediation available in TestFlight — 25 September 2026:** version **0.1.0 (2.1.0)** was signed and uploaded from `dbd5c379c0c57e58bdab6a360a01e214f80d65bd` in [run 36174233828](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36174233828). All **23 native tests** passed, none failed or skipped; unsigned device archive and signed internal export succeeded. The phone-fit layout, larger type/transport, volume icons, exact artist/album navigation, track likes, album library controls, artist follow controls and row-specific membership actions are implemented. Fixture Library reflects per-item additions/removals. Apple processing completed; the build is assigned to **Naim NDX2 Controller TestFlight** and shows **Testing**. The existing tester can update through TestFlight; group distribution remains manual. Read [the parity checklist](ios-remediation.md). Physical readability and user acceptance of this replacement remain open; it is still a silent fixture preview.

**Internal TestFlight ready — 25 September 2026:** version **0.1.0 (1.2.0)** was signed and uploaded from `eb72f22fe764f91687e16bff5f4a74714ba56102` in [run 36166397352, attempt 2](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36166397352). All 19 native tests passed. Apple processed the build and reports **Ready to Test**. The user-created internal group **Naim NDX2 Controller TestFlight** contains this build and only the explicitly approved tester, whose status is **Invited**. Build distribution is **Manual for Xcode Builds**. Phone installation and hands-on acceptance remain unverified. This is the compile-time silent fixture preview; live bridge, playback and speech remain disabled. This checkpoint supersedes older pending-signing/upload statements below.

**Software follow-up — Brief B / D031, 25 September 2026:** native SwiftUI source and an unsigned private GitHub Mac-runner workflow are implemented. The user authorized the cloud build from Windows. [Cloud instructions](ios-cloud-build.md) and [implementation report](ios-still-water.md) track native evidence separately from the parallel mounting work.

- [x] Create the app, fixture codec/lifecycle tests, native snapshot gate and keyboard UI tests.
- [x] Push a separate build branch based on the newer mounting commits; keep the original dirty checkout.
- [x] Native compilation and 17 simulator tests pass at `5c211f7`; inspect all 23 states plus three interaction captures ([run](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36130364216)).
- [x] Prepare a Windows gallery with unchanged native PNGs, reference comparisons and exact build/artifact identity.
- [ ] Complete user review of the native design; retain known keyboard, OS-chrome and native-control differences.
- [x] Prepare the silent internal TestFlight workflow, app icon, privacy manifest and signed-archive checks; Apple account configuration is pending.
- [x] Pass 19 native tests and unsigned iOS device archive validation under Xcode 26.3 ([run](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36134704504)); inspect changed captures.
- [x] Revalidate the registered bundle identity: 19 native tests and unsigned archive passed ([run](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36152860230)); configure the GitHub environment and app-identity variables.
- [x] Verify the Apple team and register `com.ndx2.controller` plus the NDX2 Controller iOS app record; keep Still Water as the phone display name.
- [x] Configure and verify protected certificate, exact-app profile and Developer-role upload key in the private GitHub environment.
- [x] Upload the signed internal preview and verify Apple processing. Banking details remain outside this non-commercial trial.
- [ ] Install the preview on the selected phone and complete user/device evaluation; live bridge and speech require a later trial.

> **Current scope — 25 September 2026, D030:** iPhone 11 + selected UGREEN 20,000mAh PD20W bank. Agree rear-loaded mounting and masked screen/stone interface, confirm exact bank SKU, then validate a physical aperture/cradle sample. Waveshare CAD, fit-coupon printing and display bring-up are parked fallback. Older scope/selection statements below are historical.

- [x] Preserve and mark Waveshare mechanical/slicing work as fallback.
- [x] Record iPhone/bank selection and publish [mounting proposal](hardware/river-stone/iphone-mount/README.md).
- [x] Prepare iPhone front/section/underside layout, working UGREEN bay, acoustic reservations and a 1:1 paper aperture template. Plane/box clearance checked; no fitted shell or acoustic proof.
- [ ] Agree aperture/interface details and verify physical mask, touch, sensors and voice.
- [ ] Confirm bank variant, phone/plug/camera measurements and fresh internal layout.

> **Current scope — 23 September 2026, Brief A/A.1:** Bridge additions are validated; screen selection is open and neither UI is authorized for implementation. D029 records this bounded revised-direction scope; D028 remains the design pause. Older display/visual-selection statements below are history.

> **Historical closeout — before Brief A:** Design work was paused at the user's request. The working prototype is retained, but its visual direction is not accepted. Earlier approval/gate/next-step statements below are historical and do not authorize further design work. Read [the chat closeout](chat-closeout-2026-09-23.md) and D028; resume only under the user's revised direction.

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
- [x] Implement the initial hardware-independent M2 workstream: development-host bridge, fixture-backed v1 contract, protected authentication/recovery tests, desktop HTTPS slice and native LVGL/build foundation. See [deliverables and evidence limits](m2-software.md).
- [x] Compile shared SDL/LVGL and ESP32 fixture targets with pinned tools; exercise actual LVGL pixels over authenticated TLS and add the bounded ESP32 HTTPS worker.
- [ ] Validate protected ESP32 provisioning and network transport on hardware; perform physical display/touch acceptance. Physical and host deployment gates remain open.
- [ ] Confirm HW-001/measurement inventory, obtain purchasing approval if required, then execute HP-01.
- [ ] Deferred B01: album-save visibility differs in laptop browser versus Codex preview; cause undocumented. Investigate only when relevant; no caching assumption or speculative fix.

- [x] Implement protected development-host credentials and synthetic persistent-authorization/rotation tests.
- [ ] Select deployment host after inventory and complete trusted OAuth administration, callback registration and long-running sign-in validation.
- [ ] Validate gapless transitions, native app coexistence and disconnect/reconnect recovery.
- [ ] Define interaction flows and touch targets on the actual 4.3-inch display.
- [x] Complete desktop visual design review: user approved the [UI baseline](ui-review/approval.md) on 22 September 2026.
- [x] Implement the approved core layouts/interactions in shared LVGL and exercise silent end-to-end slices; see [parity and remaining integration](m2-ui-parity.md).
- [x] Implement authenticated bounded artwork previews in shared LVGL with silent fixtures.
- [x] Persist local display preferences with native restart and storage-failure tests.
- [ ] Validate live artwork/quality, production provisioning and physical preference/touch behavior.
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
- [x] Create the first River Stone shell/cover solids and check conservative display insertion and component-envelope collisions ([study](hardware/river-stone/shell-v1/README.md)).
- [x] Model provisional removable screen retainers and fit coupons; check meshes, insertion and sampled wall/overhang geometry ([v2 study](hardware/river-stone/shell-v2/README.md)).
- [x] Reinforce rim/crown and cover-boss junctions; add a valid screen-edge bevel and rerun geometry/mesh checks ([v3 study](hardware/river-stone/shell-v3/README.md)).
- [ ] Refine the exterior and verify minimum wall thickness, screen retention, connectors, antenna, microphone, print supports and physical fit before releasing a build.

- [ ] Finalize dimensions around measured components.
- [x] Slice small mounting coupons and compare supported shell orientations on the P1S baseline ([slicing study](hardware/river-stone/slice-v1/README.md)); actual material/plate and physical checks remain pending.
- [ ] Print fit prototype; evaluate tilt, weight, touch stability and screen protection.
- [ ] Integrate serviceable battery and charging access.
- [ ] Iterate finish and assembly.

## M4 — Daily-use validation

- [ ] Repeated reconnects, Wi-Fi outages and service authentication renewal.
- [ ] Sustained album playback and interaction from multiple controllers.
- [ ] Real battery-life trial and charging behaviour.
- [ ] Build/assembly documentation and reproducible firmware process.
- [ ] Evaluate additional native music sources.

## Current continuation — 22 September 2026

Desktop UI design is approved (D020). [M2 closeout](m2-closeout.md) records delivered software, prior validation and remaining gates; [the continuation prompt](continuation-prompt.md) starts the approved shared-LVGL implementation. The subsequent [native port](m2-ui-parity.md) implements the core layouts, Settings/detail navigation and immediate-record Stop & search, with integration limits recorded explicitly. This checkpoint does not close HP-01 or physical P3/P4/P5.


## Shared approved UI implementation — 22 September 2026

The approved direction is now implemented as native C/LVGL slices: Playing layout and controls, filtered search, nested details and membership, collection/queue reads, immediate-record voice search and Settings. See the [parity inventory and actual evidence](m2-ui-parity.md) for implemented behavior and remaining integration gaps. Desktop evidence: 72 Python tests, five JavaScript tests, two CTests, five-stage TLS demo and expanded native LVGL/TLS smoke passed. HP-01 and physical P3/P4/P5 remain open; the hardware-arrival checklist is unchanged.

## M2 authenticated artwork checkpoint - 22 September 2026

Authenticated bounded artwork renders in shared LVGL Playing/detail screens using silent local JPEG fixtures. Voice Restart now cancels pending transcripts. Fresh validation: 77 Python tests, five JavaScript tests, three CTests, both TLS demos, desktop and ESP32 builds passed (`0x92c00`, 43% free). Native artwork/changed-cover pixels were inspected and asserted. See [limits and detailed evidence](m2-artwork.md). Live artwork/quality, deployment-host resource profiling, provisioning/preferences and physical HP-01/P3/P4/P5 remain open. No audio or hardware operation occurred.

## M2 local preferences - 22 September 2026

Local palette, brightness intent and timeout persist across separate native desktop launches. Bounds/checksum, atomic replacement, writer locking, corrupted storage, coalescing and save failures have native tests. Restored Settings pixels were inspected. Fresh evidence: 77 Python tests, five JavaScript tests, four CTests, both TLS demos, preference restart smoke and both builds passed. The ESP32 NVS adapter is compiled only; hardware brightness/sleep and physical durability remain open. See [details and limitations](m2-preferences.md). No live Naim or hardware operation occurred.

## M2 offline recovery - 22 September 2026

Desktop startup outages, late pipe replies and helper recovery are fixed without retrying commands. Shared LVGL detects bridge restarts, rejects expired snapshots, bounds pending state, clears stale artwork/membership and preserves browsing while consuming old gestures. Silent fault injection proves one play and one volume request despite lost replies. Fresh evidence: 80 Python tests, five JavaScript tests, four CTests, TLS/native/preference/recovery demos and both builds passed (`0x971f0`, 41% free on ESP32). The screenshot harness now flushes current LVGL pixels before capture. See [recovery scope and evidence](m2-recovery.md). No live Naim or hardware operation occurred; physical gates remain open.

## M2 enrollment and revocation foundation - 22 September 2026

The [offline provisioning slice](m2-provisioning.md) adds protected enrollment intent, origin/trust-bound controller records, durable uncertain/revoked states, local ID inventory and setup-code cancellation. The desktop helper enforces new record bindings while preserving legacy fixtures. Fresh evidence: 93 Python tests, read-only TLS enrollment/revocation/re-pairing demo, native UI/artwork smoke and outage-recovery demo passed. No C/ESP32 or UI changes; prior build evidence was not rerun. Production setup UI, physical installation and HP-01/P3/P4/P5 remain open.

## Host setup console - 22 September 2026

The [operator setup flow](m2-setup.md) adds local status, hidden-code pairing, explicit read-only verification and confirmed local forgetting. It rejects piped secret input and echo fallback, retains durable unknown outcomes and supports local recovery without a trust file. Fresh evidence: 107 Python tests, setup/TLS fixture demo and enrollment regression demo passed; zero live commands or real credential changes. Native UI/firmware are unchanged. Physical terminal echo and deployment/hardware gates remain separate.

## Certificate renewal and trust recovery - 22 September 2026

The [trust lifecycle slice](m2-trust.md) proves same-CA leaf renewal retains pairing and expired/wrong-host/unexpected certificates fail. An explicit same-origin `trust-update` verifies a snapshot before atomically replacing the saved binding; status reports the saved digest for interrupted recovery. Fresh evidence: 118 Python tests plus trust/setup/provisioning TLS demos passed, with no live commands or real certificate changes. Native UI/firmware and physical gates are unchanged. Production certificate installation and ESP32 rotation remain separate.

## Portable desktop package - 22 September 2026

The [desktop package](m2-package.md) bundles the validated native executable, SDL and isolated Python runtime with a launcher and setup entry point. Explicit client dependencies exclude bridge/provider adapters. Launch/setup enforce external pairing/trust/configuration; preferences remain per-user or explicitly external. Fresh evidence: 126 Python tests and extracted native/TLS package acceptance passed; a second clean installation retained byte-identical pairing/preferences without command replay. This is a portable development build and upgrade-layout rehearsal on the current Windows host, not a signed release, clean-OS certification or physical deployment.

## User trial: Play/Pause and visual finish - 22 September 2026

The packaged standalone fixture revealed a real gap: transport commands were acknowledged but snapshot state always said playing, so Pause never changed to Play. Both shared C and Python TLS fixtures now update paused/resumed state; starting a new track restores playing. The UI remains driven by the refreshed snapshot rather than optimistically changing the icon. Actual native pointer taps and icon pixels pass Pause -> Play -> Pause in standalone and TLS modes, with one pause and one resume only. 127 Python tests and five desktop CTests pass.

The user also identified that the native port is less polished than the approved reference. The approved design remains the target, but the functional native port is not yet a final visual match. Generic LVGL glyphs/type, spacing/control styling, the diagnostic status strip and fixture-only missing artwork need a focused visual-parity pass. Do not restart the design or change the approved baseline. Earlier functional parity/packaging evidence does not establish finished visual polish. No live Naim control or physical acceptance is claimed.

## User trial: visible Next/Previous feedback

Next/Previous had the same silent-fixture gap: commands were logged without changing track data. Both fixtures now use a three-track sequence with distinct titles/references, wrapping in either direction and resetting position to zero. Queue/current-item/detail identity stays consistent. Skipping preserves paused state; explicit Play starts the selected fixture playback state. The icons for Next/Previous intentionally stay fixed; changed metadata is their feedback. Native pointer smoke now covers pause/resume, next, previous and wrapping with one request per tap. Live Naim adapters and D011 are unchanged; this is silent simulation, not live transport validation.

## Native visual polish - 23 September 2026

[Visual-polish scope, screenshots and validation](m2-visual-polish.md) records a shared LVGL refinement of D020: consistent outline icons, clearer typography, quieter status, cohesive palettes/navigation, structured lists/settings and rounded artwork. Approved layout, hit areas and playback/recovery constraints remain. Five CTests, both builds, native TLS screen/artwork smoke, transport checks, preferences restart and recovery fault checks passed; an intermittent library-state smoke timeout passed on unchanged rerun and remains recorded. ESP32 image: `0x98210`, 41% free. Native photographic artwork quality and physical acceptance remain open.

## Object-led native design - 23 September 2026

The user clarified that the approved screens were rough prototypes and authorized expert iteration for the coffee-table ornament outcome (D027). [Design gate and evidence](m2-object-design.md) records three native iterations: 280 px artwork, quieter chrome/navigation, stronger Play/Pause emphasis, bounded long titles and larger browse text. The 13-state desktop composition gate passes; photographic artwork resolution, physical readability/touch/power and user acceptance remain separate. Six CTests, 128 Python tests, native TLS/transport/preferences/recovery checks and both builds passed; ESP32 `0x98810`, 40% free. Original demo sleeves are fixture-only and never conceal missing real covers.


## Still Water Brief A — 23 September 2026

- [x] Authenticated artwork sizes 1–320, chunked under the existing 32-KiB response and four-entry pixel-cache bounds; default 80 × 80 remains compatible.
- [x] Strictly validated, volatile last battery report; read-only `charge?` with 35–75% window and no at age >= one hour.
- [x] Silent fixtures, TLS authentication/revocation and bounded concurrency coverage; no additional HTTP/static route.
- [x] Fresh validation: 136 Python tests, five JavaScript navigation tests and all six stages of `python tools/m2_demo.py` passed. Tests use synthetic adapters/localhost only.
- [ ] Screen selection and subsequent UI brief. No firmware, UI, physical charging or live NDX operation in this slice.
- [ ] Deployment-host peak memory/throughput profiling, physical power and on-table acceptance remain open.

Preserved `docs/still-water/` byte-for-byte as supplied. Its iPhone-selection assertions and draft D028 conflict with this task's explicit open screen selection and the existing D028; D029 records precedence, without rewriting those source materials. The on-table trial must use a private artifact link or an external throwaway static server, never a new bridge route. Existing envelope concurrency/provider limits are preserved; no per-second bridge limiter existed or is claimed. See [contract](controller-contract-v1.md#still-water-brief-a-extension--23-september-2026) and [evidence](evidence.md).


### Brief A.1 follow-up — D029 amendment

`charge?` now reports `reason: "window"` for all fresh yes/no decisions, `"stale"` for expired reports and `"none"` for no report since boot. Stale and none remain no. Fresh validation: 137 Python tests, five JavaScript navigation tests and all six silent TLS demo stages passed. Boundary tests distinguish window/no from stale/no at exactly one hour, verify invalid reports cannot refresh expiry and confirm restart returns none. Brief A/A.1 and the unchanged 39-file Still Water source package form one coherent repository checkpoint. No new decision ID, UI, firmware, route or live-device operation.


**Live pairing diagnostic follow-up:** Windows authenticated live reads succeeded; physical iPhone pairing remains blocked. Stage-specific, secret-free enrollment diagnostics are prepared on the live-beta branch; native validation/distribution pending. Browser reachability is confirmed and does not prove app enrollment. No live mutations. See [trial report](ios-live-beta.md).


**Pairing diagnostic beta uploaded — 26 September 2026:** source `f0dba3e` (including diagnostics commit `d43a7d1`), tag `ios-preview-live-2026-09-26-pairing-v3`, passed all **32 native tests**, the unsigned device archive, signing and upload in [run 36264297307](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36264297307). The uploaded live build is **0.1.0 (11.1.0)**. The separate branch validation run 36264296786 also passed; artifact 10913830393 SHA-256 `bb416fe9cd69ec5ce3b0901e4df4de941505ae8bb6e5ffe0efcb40b0a799b749` was verified and the revised pairing capture inspected. Eleven local project/distribution checks passed, followed by four passing project checks after the local-network declaration. The earlier diagnostic-only release was cancelled before upload.

Apple processing and existing-group assignment await restored browser sign-in; the existing API key returned HTTP 403 for build reads. Do not claim the diagnostic beta is available in TestFlight yet. Physical pairing remains unresolved: the next attempt should expose a safe stage-specific error if the local-network declaration does not resolve it. No playback, volume or collection mutations.


**Diagnostic beta available — 26 September 2026:** Apple processed **0.1.0 (11.1.0)**, build `6fbc4f31-7ba4-48e1-a522-40668aa021e2`. After the user restored sign-in, it was assigned to the existing **Naim NDX2 Controller TestFlight** internal group and the page verified **Testing**. No tester or permission expansion. This supersedes the pending-processing/group-assignment note above. Phone update and pairing outcome remain pending; request the exact new Setup status if enrollment fails.
