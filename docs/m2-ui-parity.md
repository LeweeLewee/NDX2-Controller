# Approved UI port — 22 September 2026

Implements D020 in shared C/LVGL, using the approved browser source unchanged. Implementation began in `local/river-stone-repo` on main at `fcf1406`, preserving the pre-existing modified/untracked deliverables and `software-feasibility-v1`. The user subsequently authorized updating the repository; this checkpoint collects the foundation, approved UI port, tests and evidence. Generated builds, captures and private configuration remain ignored.

## Parity inventory

| Area | Starting foundation | Implemented native slice / limit |
| --- | --- | --- |
| Playing | Text-only, two amplifier buttons, wake button | 800 × 480; 240 px artwork space left; source/bitrate, title/artist/album links, track heart, separate timeline and five evenly spaced unboxed controls right; four bottom sections |
| Artwork and metadata | Placeholder text/title only | Explicit unavailable artwork; bounded authoritative source, artist, album, transport, duration/position and optional bitrate. No inferred bitrate or battery. Authenticated bounded LVGL preview implemented; live validation and final resolution remain open (see below) |
| Details | Album title, separate Save/Remove | Native album/track/artist/playlist browse, exact related links, children, bounded paging, artist Follow/Unfollow/status, compact Library actions and distinct saved/unsaved/unknown |
| Browsing | Albums only, basic Back | Four search filters, collection pages, read-only queue, independent row membership actions. Back retains query/filter/cursor/page/items/scroll and selected detail/membership. History remains bounded to four entries |
| Voice | Record → review → search | Microphone entry records immediately; Stop & search explicitly requests fixture transcription and searches; Restart discards; Cancel/Back/section exit/disconnect discard; 30 s stops without submission. No physical microphone or live AI integration |
| Settings | Absent | Gear → Display/Connection/Device; native brightness slider, palette options, timeout dropdown, Wi-Fi/pairing setup guidance and labelled simulations. Display preferences now persist locally (see follow-up); hardware brightness/sleep and network provisioning remain unavailable |
| Recovery and commands | Protected TLS and state foundation | Retained authentication/trust, no mutation replay, generation rejection, freshness gates and wake-release suppression. Both amplifier controls use the same in-flight gate. D011 adapter unchanged |
| Standalone firmware fixture | Static scaffolding | In-memory bounded request/reply fixture serves the same screens before hardware/provisioning; all operations are silent simulations |

## Contract changes

The v1 envelope and security/mutation semantics are unchanged. Added bounded `library_page` reads, native encoding of the existing transport/voice actions and selectable search kind. Snapshot can carry an optional verified current TIDAL item; browse/current items carry exact album/artist relationships when available. Missing relationships are unavailable, never guessed from a title search. Provider credentials stay on the bridge. Every play still resolves through native Naim browse before one native play request.

The historical action name `voice_review` is retained for compatibility as a fixture-only transcript read. It no longer represents a separate UI review step. No audio upload route is enabled; AI suggestions remain query data only.

## Desktop evidence

- `python -m unittest discover -s tests -v`: **72 passed**, including voice timeout with no read/submission, restart/exit, independent membership and exact/missing relationships; prior security, duplicate ID and D011 tests still pass.
- `node --test tests/test_navigation.cjs`: **5 passed**, preserving feasibility reference navigation behavior.
- `python tools/m2_demo.py`: **five silent TLS scenario stages passed** with updated voice expectations.
- `python tools/build_m2.py desktop`: **build and 2 CTests passed**. C tests now cover nested detail restoration, filters/cursors, recording bound/exit, live capture refusal, transport/filter/library encoding and absent metadata sentinels.
- `python tools/m2_native_demo.py`: **native SDL/LVGL plus paired localhost TLS passed**. Real LVGL pointer events cover search/detail/Back/native-play/voice/restart/search/cancel/settings/artist-follow/track-save and consumed wake contact. The 30-second limit uses an accelerated monotonic clock, not a physical timing measurement.
- Thirteen BMP captures in ignored `local/m2/native-captures/`, from `01-now.bmp` through `13-wake-restored.bmp`; key screens inspected at 800 × 480. These are actual LVGL pixels, not browser renders. Historical `06-review.bmp`, if present, belongs to the prior checkpoint.
- Approved board reviewed at `http://127.0.0.1:8766/` using `python tools/ui_design_review.py`; its approved source/hash is unchanged.

Initial development runs caught and fixed Python edit syntax, unavailable LVGL glyph/font configuration, native draw-call signatures and an ESP32 fixture request-ID format mismatch. The restricted desktop compiler run was stopped and repeated with normal user permissions. Protected-storage tests ran without weakening ACL or TLS checks. SDK/tool versions were not changed or downloaded.

## Firmware and open gates

`python tools/build_m2.py esp32` passed with the final shared sources: image `0x925b0` bytes, 43% of the 1 MiB application partition free. Compilation is separate from execution: no flashing, efuse, physical touch/power/microphone trial, live Naim/provider mutation, Pi installation or credential provisioning was performed. The default ESP32 network path remains gated on protected provisioning and may be removed by the linker in a fixture build.

HP-01 and physical P3/P4/P5 remain open. Follow the unchanged ten-step [hardware-arrival checklist](m2-software.md#hardware-arrival-checklist). Development-host bridge operation remains supported; Pi placement depends on private inventory. B01 remains deferred; queue/playlist editing and general feature parity remain outside scope.

Remaining integration: live artwork validation and final preview quality; live validation of exact metadata and membership; production provisioning/admin UI; physical preference effects and durability; physical screen/backlight/sleep/microphone behavior and error usability trials. Source selection and multiple-artist presentation need later review if real metadata exposes those cases. Desktop fixture success is not physical acceptance.

## Authenticated artwork follow-up - 22 September 2026

The next bounded integration is implemented. See [artwork bounds, recovery fix and fresh evidence](m2-artwork.md): 77 Python tests, five JavaScript tests, three CTests, both TLS demos and both builds passed. Actual Playing/detail/changed-cover pixels were inspected. Older artwork-unavailable statements describe the earlier checkpoint; live image quality and physical gates remain open.

## Local preferences follow-up - 22 September 2026

Palette, brightness intent and timeout persist across native desktop launches. Versioned validation, atomic replacement, save feedback, coalescing and storage-failure behavior are tested. The ESP32 NVS adapter compiles; physical durability and brightness/sleep behavior remain open. See [preferences evidence](m2-preferences.md). Four CTests and the separate-process LVGL restart smoke pass alongside the existing 77 Python/five JavaScript tests and TLS demos. The approved layout/source remain unchanged.

## M2 offline recovery - 22 September 2026

Desktop startup outages, late pipe replies and helper recovery are fixed without retrying commands. Shared LVGL detects bridge restarts, rejects expired snapshots, bounds pending state, clears stale artwork/membership and preserves browsing while consuming old gestures. Silent fault injection proves one play and one volume request despite lost replies. Fresh evidence: 80 Python tests, five JavaScript tests, four CTests, TLS/native/preference/recovery demos and both builds passed (`0x971f0`, 41% free on ESP32). The screenshot harness now flushes current LVGL pixels before capture. See [recovery scope and evidence](m2-recovery.md). No live Naim or hardware operation occurred; physical gates remain open.

## M2 enrollment and revocation foundation - 22 September 2026

The [offline provisioning slice](m2-provisioning.md) adds protected enrollment intent, origin/trust-bound controller records, durable uncertain/revoked states, local ID inventory and setup-code cancellation. The desktop helper enforces new record bindings while preserving legacy fixtures. Fresh evidence: 93 Python tests, read-only TLS enrollment/revocation/re-pairing demo, native UI/artwork smoke and outage-recovery demo passed. No C/ESP32 or UI changes; prior build evidence was not rerun. Production setup UI, physical installation and HP-01/P3/P4/P5 remain open.

## User trial: Play/Pause and visual finish - 22 September 2026

The packaged standalone fixture revealed a real gap: transport commands were acknowledged but snapshot state always said playing, so Pause never changed to Play. Both shared C and Python TLS fixtures now update paused/resumed state; starting a new track restores playing. The UI remains driven by the refreshed snapshot rather than optimistically changing the icon. Actual native pointer taps and icon pixels pass Pause -> Play -> Pause in standalone and TLS modes, with one pause and one resume only. 127 Python tests and five desktop CTests pass.

The user also identified that the native port is less polished than the approved reference. The approved design remains the target, but the functional native port is not yet a final visual match. Generic LVGL glyphs/type, spacing/control styling, the diagnostic status strip and fixture-only missing artwork need a focused visual-parity pass. Do not restart the design or change the approved baseline. Earlier functional parity/packaging evidence does not establish finished visual polish. No live Naim control or physical acceptance is claimed.

Play/Pause correction build evidence: desktop and five CTests passed; ESP32 compiled at `0x97260` bytes, 41% free. Standalone and TLS native pointer/pixel regressions passed. No flashing or live transport command occurred. Newer hardware-order records were preserved.

## User trial: visible Next/Previous feedback

Next/Previous had the same silent-fixture gap: commands were logged without changing track data. Both fixtures now use a three-track sequence with distinct titles/references, wrapping in either direction and resetting position to zero. Queue/current-item/detail identity stays consistent. Skipping preserves paused state; explicit Play starts the selected fixture playback state. The icons for Next/Previous intentionally stay fixed; changed metadata is their feedback. Native pointer smoke now covers pause/resume, next, previous and wrapping with one request per tap. Live Naim adapters and D011 are unchanged; this is silent simulation, not live transport validation.

Fresh transport follow-up validation: 128 Python tests, five desktop CTests, standalone/TLS native pointer and pixel checks, and the native artwork smoke passed. Both builds passed; ESP32 image is `0x97420` bytes with 41% application partition free. The Next capture visibly shows Silent track 2 at 0:00. No real audio, live device command or flashing occurred.

## Native visual polish - 23 September 2026

[Visual-polish scope, screenshots and validation](m2-visual-polish.md) records a shared LVGL refinement of D020: consistent outline icons, clearer typography, quieter status, cohesive palettes/navigation, structured lists/settings and rounded artwork. Approved layout, hit areas and playback/recovery constraints remain. Five CTests, both builds, native TLS screen/artwork smoke, transport checks, preferences restart and recovery fault checks passed; an intermittent library-state smoke timeout passed on unchanged rerun and remains recorded. ESP32 image: `0x98210`, 41% free. Native photographic artwork quality and physical acceptance remain open.
