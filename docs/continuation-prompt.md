# Continuation prompt — M2 native integration after the approved UI port

Copy the text below into a new task in the Naim NDX2 Controller workspace.

---

Continue NDX2 Controller M2 in `local/river-stone-repo`. The approved core UI is already implemented in shared C/LVGL and published. Continue implementation; do not repeat feasibility, redesign the approved UI, or stop at another plan.

First inspect Git status and current history. The published implementation is `04fcf17`; `a87286a` merges it with the newer enclosure, slicing, procurement and battery research through `4749541`. The subsequent handover `5bf0c8a` updates documentation only. A later checkpoint implements authenticated artwork and a voice Restart cancellation fix; inspect current history for its commit. Work from current main and preserve any newer local/remote work. Do not reset/clean, replace this checkout with `local/river-stone-shell-repo`, or overwrite ignored build/capture directories. Repository updates are authorized when appropriate; review and commit coherent validated work, fetch and reconcile concurrent changes, then push without force. Preserve `software-feasibility-v1` at `aa070fc0af4a616f769a7c0f15790831c90c112c`.

Read `AGENTS.md`, `README.md`, `docs/m2-closeout.md`, `docs/m2-ui-parity.md`, `docs/m2-software.md`, `docs/controller-contract-v1.md`, `docs/decisions.md`, `docs/architecture.md`, `docs/deployment-design.md`, `docs/interaction-design.md`, `docs/roadmap.md`, `docs/detailed-design-plan.md`, `docs/ui-review/approval.md`, `docs/ui-review/index.html`, `firmware/README.md` and `docs/hardware/first-experiment.md`. Consult the merged hardware research if relevant; source research and CAD/slicing are not physical evidence. Older prompts and closeout sections are history. Do not renumber decisions. Approved HTML hash: `1886dfe3f6bea33d8206bbe27b0c799a45964c995144131ef02a9619a3c68bbc`.

Current implementation: native 800 × 480 Playing with 240 px artwork space left and metadata/controls right; four bottom sections; five evenly spaced unboxed previous/play-pause/next/speaker-minus/speaker-plus controls. Search filters, exact title/artist/album links, native detail children, bounded pagination, Library/Follow actions and saved/unsaved/unknown states, collection/queue reads, and Back context restoration exist. History is bounded to four entries. Gear opens Display/Connection/Device; palette works, palette/brightness/timeout persist locally; brightness/timeout remain hardware-unbound intent, Wi-Fi/pairing are labelled simulations. Authenticated artwork previews now render in these spaces; live image validation and final photographic resolution remain open. Optional metadata must be authoritative or unavailable; no fabricated live bitrate or battery.

Voice immediately starts its labelled recording fixture. Stop & search requests a transcript and searches; Restart discards; Cancel/Back/section exit/disconnect discard. Thirty seconds stops without submission. The wire action `voice_review` is retained for compatibility but there is no separate review screen. Physical microphone capture/upload and live AI integration remain absent; suggestions may only become searches, never automatic playback.

Implemented artwork slice: read `docs/m2-artwork.md`. Artwork uses the existing authenticated read envelope, registered metadata references, bridge-only bounded JPEG normalization, 80 x 80 RGB565 previews and fixed native buffers. Four normalized previews/32 registrations expire after 60 seconds. No arbitrary URL fetch or public image route exists. Stale/changed/obsolete covers clear; corrupt/missing artwork does not disconnect playback. Standalone firmware fixtures still have unavailable artwork. Restart invalidates pending transcript reads; preserve the native regression tests.

The subsequent local preference slice is implemented; read `docs/m2-preferences.md`. Preserve its versioned bounded record, atomic desktop replacement, native save feedback, coalescing and compiled-only ESP32 NVS adapter.

The subsequent offline recovery slice is implemented; read `docs/m2-recovery.md`. Preserve failed-pipe disposal without replay, bridge boot detection, eight-second pending expiry, stale-snapshot rejection and cached-membership invalidation. The approved UI remains unchanged.

The offline enrollment/revocation foundation is implemented; read `docs/m2-provisioning.md`. Preserve durable pending intent, no automatic re-pairing, explicit local recovery, origin/trust binding for new records and legacy-fixture compatibility. The subsequent operator-facing host console is implemented; read `docs/m2-setup.md`. Preserve hidden input, explicit trust confirmation, local-only recovery and no automatic pairing retry. No physical installer exists yet. The certificate lifecycle slice is also implemented; read `docs/m2-trust.md`. Preserve explicit same-origin trust updates, independent fingerprint approval, snapshot-before-atomic-commit ordering and saved-digest recovery. No production certificate installer or scheduler is implied.

The portable desktop package is implemented; read `docs/m2-package.md`. Preserve the isolated client runtime, external-state boundary and manifest checks. Rebuild packages into new destinations only. This is a development build, not a signed installer or cross-machine DPAPI migration.

User-trial correction: silent Play/Pause snapshots now change state; run `python tools/m2_transport_demo.py` to verify native icon pixels in standalone/TLS fixtures. The user finds the native UI less polished than the approved design. Functional parity is not final visual finish.

Next bounded work: a focused native visual-parity/polish pass against the approved reference (icons, typography, spacing/control styling and diagnostic strip), preserving the approved layout and all recovery/command constraints. Do not redesign or repeat infrastructure. Subsequently, live metadata/artwork validation when suitable private configuration and NDX network access are available, or intended-host deployment/terminal validation with synthetic setup; do not repeat portable packaging. Do not repeat persistent preferences or claim physical storage/brightness/sleep validation. Do not automatically run live playback/volume checks. Higher-resolution artwork and deployment-host resource profiling remain explicit follow-ups: 80-px previews are not final photographic quality. Production provisioning/admin and physical controls are separate work. Preserve the approved UI and recovery behavior.

Preserve native Naim TIDAL playback: resolve catalogue candidates through native Naim browse before a single play request. No audio relay or substitute protocol. D011 remains exactly one press plus four held frames spaced 0.2 seconds, once per tap, both volume controls busy until completion; no retry, continuous hold or numeric amplifier level. Never replay playback, queue, collection-write or volume commands. Keep durable duplicate-ID suppression and unknown outcomes until authoritative reconciliation. Wake/disconnect discard pending gestures/commands, preserve browsing context, disable unavailable mutations, fetch authoritative state, consume the wake contact and wait for release. Deferred navigation work may contain reads only.

Keep authenticated TLS, provisioned trust, protected persistence and atomic single-flight renewal intact. No unauthenticated LAN service, provider secrets in firmware, real credentials/captures/private addresses in Git, flashing or efuse operations. Development-host bridge remains supported; Pi deployment is conditional on private inventory. Do not perform audible/live mutations automatically. Missing hardware/Pi/credentials does not block fixture work. B01 stays deferred unless blocking; queue/playlist editing and general feature parity are excluded.

Use existing installed tools before downloading anything. From repo root run validation appropriate to changed behavior:

    python -m unittest discover -s tests -v
    node --test tests/test_navigation.cjs
    python tools/m2_demo.py
    python tools/build_m2.py desktop
    python tools/m2_native_demo.py
    python tools/m2_preferences_demo.py
    python tools/m2_recovery_demo.py
    python tools/m2_provisioning_demo.py
    python tools/m2_setup_demo.py
    python tools/m2_trust_demo.py
    python tools/build_m2.py esp32

Recovery checkpoint results: 80 Python tests, five JavaScript tests, four CTests, five-stage TLS demo, expanded native LVGL/TLS smoke, recovery fault-injection demo, and both builds passed. ESP32 image was `0x971f0` bytes, 41% application partition free. Fifteen BMP captures are in ignored `local/m2/native-captures/`; `06-voice-search.bmp` replaces the historical review capture. The 30-second smoke limit uses an accelerated clock. These are prior results, not permission to claim a fresh run. Recovery tests cover lost replies without mutation replay, boot changes, held contact, expired snapshots and recording outages. Native screenshot capture flushes LVGL before saving. Host dependencies are pinned in `tools/requirements-m2.txt`; firmware pins remain unchanged.

`local/m2/esp32-compile-v2` already exists; preparation refuses overwrite and the build runner updates owned overlays. SDK v5.2 and build outputs are under the user profile `.espressif`; pins and paths are in `firmware/README.md`. On this Windows host restricted compiler execution stalled; normal permitted execution succeeded. Protected-storage tests need appropriate user permissions. Never weaken ACL/TLS checks for sandbox convenience. The loopback design board at `http://127.0.0.1:8766/` may still be running; otherwise start `python tools/ui_design_review.py`.

Capture and inspect actual LVGL pixels at 800 × 480 after UI changes. Keep fixture tests, compiler results, live observations and physical evidence separate. Update parity/status/evidence and this handover with implemented behavior and remaining gaps. HP-01 and physical P3/P4/P5 remain open. Preserve the precise ten-step hardware-arrival checklist in `docs/m2-software.md`. Finish with concrete changes, actual validation and remaining blockers.

Latest enrollment checkpoint: 93 Python tests, read-only provisioning/TLS demo, native UI/artwork smoke and recovery fault demo passed. C/ESP32/UI sources did not change; compiler/CTest evidence above remains from the prior checkpoint. No live or physical provisioning was performed.

Latest host setup checkpoint: 107 Python tests, setup/TLS demo and enrollment regression demo passed. Secret input was synthetic; physical terminal echo behavior remains a manual host check. No native source changes or fresh compile claim.

Latest trust checkpoint: 118 Python tests, trust-renewal/rotation TLS demo and existing setup/provisioning demos passed. No native source changes, live certificate installation or fresh compiler claim.

Latest packaging checkpoint: 126 Python tests and extracted native/TLS package acceptance passed. Two clean installation directories retained external pairing/preferences byte-for-byte. The same archive was used for upgrade-layout rehearsal; native compilation, cross-machine portability and physical behavior were not newly validated. Build with `python tools/package_m2.py --out NEW-DIRECTORY`, then run `python tools/m2_package_demo.py PATH-TO-ZIP`.

Play/Pause correction build evidence: desktop and five CTests passed; ESP32 compiled at `0x97260` bytes, 41% free. Standalone and TLS native pointer/pixel regressions passed. No flashing or live transport command occurred. Newer hardware-order records were preserved.

Next/Previous fixture follow-up: both silent fixtures now display a three-track sequence with correct current/queue references, position reset and preserved paused state. The native transport smoke tests pointer taps through pause/resume and next/previous/wrap. Keep visual polish against the approved baseline as the next task; do not redesign it or return to infrastructure work.

Fresh transport follow-up validation: 128 Python tests, five desktop CTests, standalone/TLS native pointer and pixel checks, and the native artwork smoke passed. Both builds passed; ESP32 image is `0x97420` bytes with 41% application partition free. The Next capture visibly shows Silent track 2 at 0:00. No real audio, live device command or flashing occurred.
