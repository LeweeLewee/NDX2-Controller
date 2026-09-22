# Continuation prompt — approved UI implementation

Historical implementation prompt, retained for scope and constraints. The core port below is now implemented and validated: begin further work with [current parity and remaining gaps](m2-ui-parity.md), inspect Git status and continue from the current checkout. Do not repeat the port or assume the earlier uncommitted checkpoint is still current. Repository updates were subsequently authorized; live audio, flashing and deployment remain outside this prompt.

---

Continue the NDX2 Controller M2 work in `local/river-stone-repo` within the Naim NDX2 Controller workspace. Implement the approved UI in the shared C/LVGL layer, desktop first; do not stop at another plan or redesign the approved direction.

First inspect Git status. Preserve all modified and untracked M2 implementation and detailed-design files. Closeout was on main at fcf1406 with uncommitted deliverables. Never reset/clean the checkout or replace it with local/river-stone-shell-repo. Preserve software-feasibility-v1 as the behavioural reference.

Read AGENTS.md, README.md, docs/m2-closeout.md, docs/decisions.md, docs/milestone-handover.md, docs/detailed-design-plan.md, docs/architecture.md, docs/deployment-design.md, docs/interaction-design.md, docs/roadmap.md, docs/controller-contract-v1.md, docs/m2-software.md, docs/ui-review/README.md, docs/ui-review/approval.md, docs/ui-review/index.html, firmware/README.md and docs/hardware/first-experiment.md. Approval and the interactive source supersede older rough layouts and chronological review notes. Do not renumber historical decisions.

Inspect shared UI/state/protocol code, desktop/ESP32 transports, bridge adapters and tests. Make a concise parity inventory, then implement useful end-to-end slices. The browser design board is not firmware. Keep ESP32 native C/LVGL and existing pinned SDK dependencies; do not add a browser runtime. Extend bounded contracts/models only where necessary, preserving adapter semantics and the runnable feasibility demo.

Implement the approved 800 × 480 default: 240 px art left, all metadata/controls right, four bottom sections; five evenly spaced unboxed previous/play-pause/next/speaker-minus/speaker-plus controls. Keep bitrate beside source, separate timeline, track heart, title/artist/album detail links, quiet Back, no redundant section headers. Preserve query/filter/page/list position on Back. Artist follow/unfollow and status; album/track compact Library actions and saved/unsaved/unknown states. Search and microphone icons; Settings gear with Display/Connection/Device direction. Use labelled fixtures for unavailable hardware and unknown/unavailable values for absent real metadata, never fabricated live bitrate or battery.

Voice entry starts recording immediately; Stop & search, Restart and Cancel replace the old separate review step. Bound capture to 30 seconds without automatic submission; Cancel/Back/exit discard capture. Update native fixture smoke expectations accordingly. No physical microphone implementation until pins/hardware are selected. AI suggestions become searches, never automatic playback. Display brightness/timeout/Wi-Fi controls must distinguish fixtures from real capabilities.

Preserve native Naim TIDAL playback on the NDX 2, resolving catalogue candidates through native Naim browsing before playback. No audio relay or substitute protocol. D011 is exactly one press plus four held frames spaced 0.2 seconds, one bounded burst per tap, both volume controls busy through completion. No retry, continuous hold or numeric amplifier level. Never replay playback, queue, collection-write or volume commands. Duplicate IDs are suppressed; timed-out mutations remain outcome unknown until authoritative reconciliation. On wake/disconnect discard pending gestures/commands, preserve browsing context, disable unavailable mutations and fetch authoritative state; consume the wake contact and wait for release.

Keep authentication, provisioned TLS trust, protected persistence and atomic single-flight renewal intact. No unauthenticated LAN service, provider secrets in firmware, real credentials/captures/private addresses in Git, flashing or efuse operations. Development-host bridge remains supported; Pi installation is conditional on inventory. Do not perform audible/live mutations automatically. Missing hardware, Pi or live credentials does not block fixture work. Keep B01 deferred unless blocking and exclude queue/playlist editing and general feature parity.

Use existing local tool installations before downloading anything. From repo root run appropriate validation:

    python -m unittest discover -s tests -v
    node --test tests/test_navigation.cjs
    python tools/m2_demo.py
    python tools/build_m2.py desktop
    python tools/m2_native_demo.py
    python tools/build_m2.py esp32

Review design with `python tools/ui_design_review.py` at http://127.0.0.1:8766/; it may already be running. Firmware preparation output local/m2/esp32-compile-v2 already exists and refuses overwrite. The build runner updates its owned overlays. SDK v5.2 and build outputs are under the user profile .espressif; see firmware/README.md for pins and paths. Report unavailable tools honestly; do not weaken ACL or TLS checks for sandbox convenience.

Capture and inspect actual LVGL output at 800 × 480, exercise the vertical slice and navigation/state failure cases with silent fixtures, and add meaningful tests for changed behavior. Keep desktop tests, firmware compilation, live observations and physical evidence separate. Update repository parity/status/evidence docs with implemented behavior and remaining gaps. HP-01 and physical P3/P4/P5 remain open; retain the precise hardware-arrival checklist in docs/m2-software.md. Finish with implemented changes, actual validation results and remaining blockers.
