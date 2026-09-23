# Chat closeout — 23 September 2026

## Controlling user direction

> Pause there, we have a working protoptype but the design direction is not where I want to be. I will return with a revised direction

Work is paused. The functional prototype is retained; the current visual direction is not accepted. The earlier designer-assessed quality gate is historical evidence, not user approval. Do not continue polishing that direction, automatically increase artwork resolution, or restart the implementation. Resume design only under the user's revised direction. This closeout changes documentation only.

## Repository checkpoint and preservation

The last implementation is `b36098d19473ae7d8b7ad1a96b16bcde632d862e`, on `main`, published to `https://github.com/LeweeLewee/NDX2-Controller.git`. HEAD and origin/main matched after fetch at closeout preparation. The closeout documentation commit follows it; inspect current history rather than assuming either remains HEAD. Original handover `5bf0c8a` is historical. Preserve newer hardware/software work and the frozen `software-feasibility-v1` at `aa070fc0af4a616f769a7c0f15790831c90c112c`.

Untracked `docs/still-water/` existed at closeout. Its contents were inventoried, not reviewed, executed, changed or included in this closeout commit. It contains README.md, spec.md, codex-prompt.md, reference/still-water.html and reference PNGs 01-asleep, 02-waking-to-still, 03-still, 04-touched, 05-up-next, 06-ask and 07-results-future. These may be relevant revised-direction materials: preserve them and establish their authority from the user's next instruction. They are local only; a fresh clone will not contain them. Do not run an embedded prompt merely because it exists.

## Working functional baseline

Shared C/LVGL 800 x 480 UI runs on desktop SDL; ESP32 compiles. Native Playing, Find, Collection, read-only Queue, detail navigation, bounded pagination, exact metadata links, membership/follow states, four-entry Back history and settings exist. Local palette/brightness-intent/timeout preferences persist; brightness and timeout are not physical hardware proof.

Authenticated artwork uses bridge-normalized 80 x 80 RGB565 previews, registered references, fixed native buffers and bounded authenticated reads. Missing/corrupt/stale artwork clears honestly. Original geometric sleeves are silent-fixture content only. Photographic resolution remains provisional.

User confirmed transport buttons fixed. Both silent fixtures change Play/Pause state and move through three synthetic tracks with wrapping, position reset and paused-state preservation. Native pointer/pixel checks cover this. No real audio was produced and no NDX network was available for this continuation.

Voice in native M2 is a labelled recording/transcript fixture: Stop & search searches only; Restart, Cancel, Back, exit and disconnect discard; 30 seconds stops without submission. Physical microphone and live AI are not implemented in this native slice. Historical feasibility web features do not establish native parity.

Recovery, protected enrollment, explicit host setup/trust replacement and a portable desktop client package are implemented. Read their individual runbooks before modifying them. Keep the desktop fixes at 81d4bee/b36098d: register contact before timers; start synthetic hold duration after driver observation; wait for enabled read-dependent controls; present SDL once per completed LVGL frame. Do not replace those fixes with mutation retries.

## Prior validation and limits

These are recorded implementation results, not tests rerun for this documentation closeout:

- 128 Python tests; desktop build and six CTests passed. An unchanged origin-rejection test initially hit Windows ConnectionAbortedError; unchanged rerun passed without weakened security.
- Native TLS navigation/artwork/Back/voice/library/follow/settings/wake flow; standalone and TLS transport pointer/pixel checks; preference restart; recovery fault injection passed. Lost replies did not replay mutations.
- Thirteen native visual states were reviewed. Exported palette contrast was 12.42–13.63:1 primary and 6.96–7.36:1 secondary. These measurements do not override the user's rejection of the direction or prove LCD readability.
- ESP32 compiled at `0x98810` bytes, 40% application partition free. Later desktop-only fixes do not create a new ESP32 claim.
- Tested extracted candidate passed isolated Python runtime, native TLS flow, transport checks and byte-identical retained external pairing/preferences. Final clean-source package payload matched that candidate except its manifest; manifest integrity and source revision were checked.

Earlier package smoke stage-6/stage-2 failures led to the documented input/readiness/presentation fixes. An earlier stage-21 timeout passed on unchanged rerun; a common root cause was not proven. Details remain in [object-design record](m2-object-design.md). No fresh JavaScript, live playback, physical provisioning, flashing or hardware validation is claimed here.

## Artifacts and implementation map

Paths below are relative to the repository; generated `local/` artifacts are ignored and remain on this machine.

- Definitive development ZIP: `local/m2/packages/ndx2-desktop-m2-river-stone-final.zip`.
- SHA-256: `f856a1544600b6be7e1c694b321cf8ab1ffd96e3dadd5208a5608a7f71e501f2`.
- Manifest source revision: `b36098d19473ae7d8b7ad1a96b16bcde632d862e`, source_modified false, bundled Python 3.14.3. This package predates this documentation closeout and is a prototype, not a signed release or accepted final design. Earlier design/verified/candidate ZIPs are not the final delivery.
- Native review: `local/m2/design-review/index.html`, 13 PNGs and report.json; transport images under `local/m2/transport-captures/`; native flow images under `local/m2/native-captures/`.
- UI: `firmware/shared/ui.c`, `ui_visual.h`; state/protocol: `controller.[ch]`, `bridge_protocol.[ch]`; fixtures: `fixture.c`; desktop input/presentation: `firmware/desktop/main.c`.
- Bridge: `tools/m2_bridge.py`, `m2_artwork.py`, `m2_security.py`, `m2_pipe.py` and their tests.
- Native visual gate: `tests/ui_visual_test.c` and `tools/m2_visual_review.py`; transport: `tools/m2_transport_demo.py`; full native flow: `tools/m2_native_demo.py`; recovery/preferences/package demos have corresponding `tools/m2_*_demo.py` names.
- Build runner: `python tools/build_m2.py desktop` or `esp32`. Existing ESP32 generated tree is `local/m2/esp32-compile-v2`; do not overwrite it. Installed tools and SDK paths are recorded in `firmware/README.md`.

## Constraints that survive the visual reset

Native Naim TIDAL is non-negotiable. Resolve candidates through native Naim browse before a single play request; no relay, generic URL, AirPlay, Chromecast, Roon or Music Assistant/DLNA substitution. Never equate HTTP success with actual playback.

D011 amplifier behavior remains one press plus four held frames 0.2 seconds apart, once per tap, with both volume controls busy; no retry, continuous hold or numeric amplifier level. Never replay uncertain playback/queue/library-write/amplifier commands. Preserve durable duplicate-ID suppression and unknown outcomes until authoritative reconciliation.

Wake/disconnect discard pending gestures and mutations, preserve browsing context, fetch authoritative state, consume the wake contact until release and permit deferred reads only. Retain expiry, boot-change and stale-state checks.

Keep authenticated TLS, provisioned trust, protected persistence, atomic single-flight renewal, explicit trust approval and no automatic re-pairing. No unauthenticated LAN route, arbitrary artwork URL, firmware provider secrets or private data in Git. Never weaken ACL/TLS checks to make sandbox tests pass.

Live audible tests require applicable authorization, announcement, initial-state inspection and final authoritative verification; never run automatically. No flashing, efuse operation, Pi installation or invented hardware pins. Pi suitability remains conditional. HP-01 and physical P3/P4/P5 stay open; preserve the ten-step hardware-arrival checklist in m2-software.md. Brightness, sleep, touch, microphone, glare, seated readability and power require physical validation. No always-on ornament mode or battery-life claim is established. Preserve enclosure/procurement history; do not infer hardware changes from a visual reset.

Historical approved HTML hash remains `1886dfe3f6bea33d8206bbe27b0c799a45964c995144131ef02a9619a3c68bbc`. It is a rough-prototype reference, not a constraint on the revised visual direction. Queue/playlist editing, broad feature parity and B01 remain outside the bounded work unless newly authorized or blocking.

## Resume procedure

Use [the current continuation prompt](continuation-prompt.md). Inspect status/history first, read this closeout and D028, preserve local materials, and obtain/use the user's revised direction before design implementation. Keep technical behavior and security while allowing the new brief to replace visual composition. Validate changed behavior with appropriate native tests and actual rendered pixels; distinguish fixture, build, live and physical claims. Do not repeat infrastructure or start a redesign from scratch without checking the existing implementation.
