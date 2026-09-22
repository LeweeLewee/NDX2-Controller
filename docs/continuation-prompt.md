# Continuation prompt — M2 native integration after the approved UI port

Copy the text below into a new task in the Naim NDX2 Controller workspace.

---

Continue NDX2 Controller M2 in `local/river-stone-repo`. The approved core UI is already implemented in shared C/LVGL and published. Continue implementation; do not repeat feasibility, redesign the approved UI, or stop at another plan.

First inspect Git status and current history. The published implementation is `04fcf17`; `a87286a` merges it with the newer enclosure, slicing, procurement and battery research through `4749541`. The subsequent handover commit updates documentation only. Work from current main and preserve any newer local/remote work. Do not reset/clean, replace this checkout with `local/river-stone-shell-repo`, or overwrite ignored build/capture directories. Repository updates are authorized when appropriate; review and commit coherent validated work, fetch and reconcile concurrent changes, then push without force. Preserve `software-feasibility-v1` at `aa070fc0af4a616f769a7c0f15790831c90c112c`.

Read `AGENTS.md`, `README.md`, `docs/m2-closeout.md`, `docs/m2-ui-parity.md`, `docs/m2-software.md`, `docs/controller-contract-v1.md`, `docs/decisions.md`, `docs/architecture.md`, `docs/deployment-design.md`, `docs/interaction-design.md`, `docs/roadmap.md`, `docs/detailed-design-plan.md`, `docs/ui-review/approval.md`, `docs/ui-review/index.html`, `firmware/README.md` and `docs/hardware/first-experiment.md`. Consult the merged hardware research if relevant; source research and CAD/slicing are not physical evidence. Older prompts and closeout sections are history. Do not renumber decisions. Approved HTML hash: `1886dfe3f6bea33d8206bbe27b0c799a45964c995144131ef02a9619a3c68bbc`.

Current implementation: native 800 × 480 Playing with 240 px artwork space left and metadata/controls right; four bottom sections; five evenly spaced unboxed previous/play-pause/next/speaker-minus/speaker-plus controls. Search filters, exact title/artist/album links, native detail children, bounded pagination, Library/Follow actions and saved/unsaved/unknown states, collection/queue reads, and Back context restoration exist. History is bounded to four entries. Gear opens Display/Connection/Device; palette works, brightness/timeout are session fixture preferences, Wi-Fi/pairing are labelled simulations. Actual artwork remains unavailable. Optional metadata must be authoritative or unavailable; no fabricated live bitrate or battery.

Voice immediately starts its labelled recording fixture. Stop & search requests a transcript and searches; Restart discards; Cancel/Back/section exit/disconnect discard. Thirty seconds stops without submission. The wire action `voice_review` is retained for compatibility but there is no separate review screen. Physical microphone capture/upload and live AI integration remain absent; suggestions may only become searches, never automatic playback.

Next useful slice: inspect the current code and implement bounded artwork delivery/rendering through the authenticated bridge and shared LVGL, desktop first, with synthetic local image fixtures. Reuse the existing metadata registration/cache semantics where appropriate. Do not expose arbitrary URL fetches or an unauthenticated image route; bound image dimensions, bytes, decode memory and cache lifetime. Handle missing, corrupt, stale and changed-track artwork without blocking UI or displaying the previous track's cover as current. Keep ESP32 C/LVGL and pinned dependencies; no browser runtime. If inspection reveals a blocking navigation/command-state defect, fix and test it first. Add targeted native tests for affected failure/cancellation paths. Persistent preferences, production provisioning/admin, live metadata validation and physical controls remain later work unless required by this slice.

Preserve native Naim TIDAL playback: resolve catalogue candidates through native Naim browse before a single play request. No audio relay or substitute protocol. D011 remains exactly one press plus four held frames spaced 0.2 seconds, once per tap, both volume controls busy until completion; no retry, continuous hold or numeric amplifier level. Never replay playback, queue, collection-write or volume commands. Keep durable duplicate-ID suppression and unknown outcomes until authoritative reconciliation. Wake/disconnect discard pending gestures/commands, preserve browsing context, disable unavailable mutations, fetch authoritative state, consume the wake contact and wait for release. Deferred navigation work may contain reads only.

Keep authenticated TLS, provisioned trust, protected persistence and atomic single-flight renewal intact. No unauthenticated LAN service, provider secrets in firmware, real credentials/captures/private addresses in Git, flashing or efuse operations. Development-host bridge remains supported; Pi deployment is conditional on private inventory. Do not perform audible/live mutations automatically. Missing hardware/Pi/credentials does not block fixture work. B01 stays deferred unless blocking; queue/playlist editing and general feature parity are excluded.

Use existing installed tools before downloading anything. From repo root run validation appropriate to changed behavior:

    python -m unittest discover -s tests -v
    node --test tests/test_navigation.cjs
    python tools/m2_demo.py
    python tools/build_m2.py desktop
    python tools/m2_native_demo.py
    python tools/build_m2.py esp32

Prior actual results: 72 Python tests, five JavaScript tests, two CTests, five-stage TLS demo, expanded native LVGL/TLS smoke, and both builds passed. ESP32 image was `0x925b0` bytes, 43% application partition free. Thirteen BMP captures are in ignored `local/m2/native-captures/`; `06-voice-search.bmp` replaces the historical review capture. The 30-second smoke limit uses an accelerated clock. These are prior results, not permission to claim a fresh run. The merge changed no validated M2 code.

`local/m2/esp32-compile-v2` already exists; preparation refuses overwrite and the build runner updates owned overlays. SDK v5.2 and build outputs are under the user profile `.espressif`; pins and paths are in `firmware/README.md`. On this Windows host restricted compiler execution stalled; normal permitted execution succeeded. Protected-storage tests need appropriate user permissions. Never weaken ACL/TLS checks for sandbox convenience. The loopback design board at `http://127.0.0.1:8766/` may still be running; otherwise start `python tools/ui_design_review.py`.

Capture and inspect actual LVGL pixels at 800 × 480 after UI changes. Keep fixture tests, compiler results, live observations and physical evidence separate. Update parity/status/evidence and this handover with implemented behavior and remaining gaps. HP-01 and physical P3/P4/P5 remain open. Preserve the precise ten-step hardware-arrival checklist in `docs/m2-software.md`. Finish with concrete changes, actual validation and remaining blockers.
