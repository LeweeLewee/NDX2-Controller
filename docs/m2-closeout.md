# M2 software and UI review closeout — 22 September 2026

## Current preferences checkpoint - 22 September 2026

Continuation from `ece0fa3` implements local display preference persistence: versioned bounded records, atomic desktop replacement, native save/error feedback and an ESP32 NVS adapter. [Behavior, fresh tests and limits](m2-preferences.md) distinguish desktop restart evidence from compiled-only firmware storage. Fresh validation: 77 Python tests, five JavaScript tests, four CTests, both TLS demos, preferences restart smoke and both builds passed. Final ESP32 size: 0x97090 (41% partition free). Brightness and timeout remain intent only; physical gates are open.

## Prior artwork checkpoint - 22 September 2026

Continuation from `5bf0c8a` implements authenticated bounded artwork and shared LVGL rendering using silent local fixtures, plus the voice Restart cancellation fix. See [current evidence and limits](m2-artwork.md). Fresh results: 77 Python tests, five JavaScript tests, three CTests, both TLS demos and both builds passed. ESP32 image `0x92c00`, 43% partition free. Live artwork/quality and all physical gates remain open. Earlier next-slice statements below are historical.

## Prior published closeout — 22 September 2026

The approved core UI port and M2 foundation are committed and pushed: `04fcf17` (implementation) and `a87286a` (merge with concurrent hardware research through `4749541`). The working tree was clean at handover preparation. This closeout update is documentation-only; inspect Git status/history at the next start rather than assuming a fixed HEAD.

Use the rewritten [continuation prompt](continuation-prompt.md) and [native parity/evidence](m2-ui-parity.md). The previous prompt is retained as [history](m2-ui-port-prompt-history.md). Core UI implementation is complete to the bounded fixture scope; the recommended next slice is authenticated, bounded artwork delivery and native rendering, with any blocking recovery defects fixed first. Do not repeat the approved UI port.

Prior validation: 72 Python tests, five JavaScript tests, two CTests, five-stage TLS demo, expanded native LVGL/TLS smoke, desktop build and ESP32 build passed. Thirteen real LVGL captures were recorded and key screens inspected. The ESP32 image is `0x925b0` bytes with 43% application partition free. The 30-second voice smoke uses accelerated time. No tests/builds were rerun for this documentation-only closeout.

Remaining: native artwork, persistent device preferences, production protected provisioning/admin, live metadata/membership integration validation, and physical screen/touch/wake/backlight/sleep/microphone/power evidence. Pi suitability remains conditional. HP-01 and physical P3/P4/P5 remain open; merged enclosure and battery research does not pass those gates. No audio test, flashing, efuse, Pi installation or real credential provisioning was performed.

The approved HTML hash and frozen feasibility tag are unchanged. Private configuration, generated dependencies/builds and captures remain ignored. The user authorized repository updates when appropriate; preserve concurrent work and publish coherent validated checkpoints without force pushes. The older sections below describe the pre-port checkpoint and are retained as history.


This checkpoint closes the chat, not M2 or its physical acceptance gates. The repository is the durable source of truth. The next implementation is **approved UI parity in shared C/LVGL**, desktop first. Use the [continuation prompt](continuation-prompt.md).

## Source precedence and repository state

1. [Decisions](decisions.md) govern accepted architecture and safety semantics; D020 records UI approval. Earlier conflicting IDs were reconciled by content/provenance: D015 dedicated display, D016 historical comparison superseded by D017, D018 provisional bridge partition, D019 parallel software.
2. [UI approval](ui-review/approval.md) and its hash-identified [interactive source](ui-review/index.html) govern final desktop design. Earlier [review history](ui-review/review-history.md) and rough concept proposals are superseded where they differ.
3. [M2 runbook](m2-software.md), [contract](controller-contract-v1.md) and [firmware instructions](../firmware/README.md) describe implementation, commands and evidence limits.
4. `software-feasibility-v1` at `aa070fc0af4a616f769a7c0f15790831c90c112c` remains the behavioural reference.

At closeout, this checkout is `local/river-stone-repo`, branch `main`, HEAD `fcf1406`. M2 code, firmware, tests, design records and these handovers are modified/untracked local working-tree deliverables. They are not committed or pushed by this closeout. Preserve them; do not reset, clean or replace this checkout with `river-stone-shell-repo`. Review the complete diff and untracked-file inventory before any later commit. Secrets, captures, dependencies and generated builds stay outside Git.

## Implemented and evidenced

- Reusable prototype bridge logic extracted while preserving its runnable demo and native Naim adapter semantics.
- Versioned authenticated TLS contract: bounded requests/responses and pagination, freshness, explicit outcomes, persistent request-ID suppression and no automatic mutation replay.
- Protected development-host authorization, pairing/revocation, atomic token persistence/rotation and single-flight renewal, tested with synthetic credentials.
- Recovery/navigation foundations: authoritative reconnect, obsolete-reply rejection, disabled unavailable mutations, wake contact release and preserved browsing context.
- Shared C/LVGL state, codec and renderer; compiled Windows SDL and ESP32 fixture targets; asynchronous desktop TLS and gated ESP32 HTTPS worker.
- Silent fixture vertical slice through boot/reconnect, search, album, native-play request and refreshed state. Native framebuffer captures remain ignored local evidence.
- Approved browser design covers Now Playing, navigation, library/follow state, voice search and Settings. This design has not yet been ported to shared LVGL.

Recorded validation from the implementation checkpoint: **69 Python tests, 5 JavaScript tests, 2 CTests, five-stage TLS demo, native LVGL/TLS fixture smoke, desktop and ESP32 compilation passed**. A preceding Python run hit an existing Windows cross-origin test connection error; the rerun passed, as recorded in the runbook. Browser review subsequently exercised the UI refinements and JavaScript syntax checks. Closeout itself changes documentation only; these are prior results, not a new full-suite run.

No new live Naim/provider/Pi observation, audible test, flashing, efuse operation, hardware capture or physical acceptance is claimed. Compilation can exclude the default-disabled ESP32 network path at link time; it does not prove on-device networking or provisioning.

## Remaining work and blockers

| Work | Next action / dependency |
| --- | --- |
| Approved native UI | Port browser design into shared LVGL. Audit current model/contract gaps for artist/track details, Settings, metadata, membership, artwork and voice. Hardware is not a blocker. |
| Voice flow parity | Native/Python foundations still contain the earlier review step. Implement immediate record → Stop & search / Restart / Cancel; update fixture smoke expectations. Keep AI as searches. |
| Real service integration | Use authoritative bitrate/artwork/membership or unavailable states; retain native candidate resolution. Live credentials/checks remain separate from silent fixtures. |
| ESP32 deployment | Finish protected provisioning tooling and validate Wi-Fi/TLS trust, time bootstrap, revocation and power-loss behaviour on hardware. No provider secrets in firmware. |
| Bridge host | Keep development-host operation; Home Assistant Pi placement depends on private inventory and coexistence trial. |
| Physical controller | Hardware unavailable; board revision/pins, touch/wake, power, microphone and enclosure fit unvalidated. HP-01 and physical P3/P4/P5 remain open. |
| Deferred scope | B01 remains deferred unless blocking; queue viewing only. Queue/playlist editing and general feature parity are outside this continuation. |

## Reproduce without live audio

From the repository root, using existing installed dependencies:

```powershell
python -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
python tools/m2_demo.py
python tools/build_m2.py desktop
python tools/m2_native_demo.py
python tools/build_m2.py esp32
python tools/ui_design_review.py
```

The final command serves the design board and remains running. The native executable is `local/m2/desktop-verified/ndx_fixture.exe`. Dependency pins and fresh-host preparation are in [firmware instructions](../firmware/README.md); existing preparation output must not be overwritten. Windows builds use `.espressif/ndx2-m2-build` under the user profile to avoid long-path failures. Synthetic certificate generation needs `cryptography==46.0.7`. Restricted-sandbox ACL tests may require permitted execution outside the sandbox; do not weaken storage protection.

## Hardware arrival

Follow the precise [ten-step hardware-arrival checklist](m2-software.md#hardware-arrival-checklist) and [HP-01 procedure](hardware/first-experiment.md): record SKU/revision and schematic, inventory safe USB supply and measurement equipment, reproduce fixture/vendor builds, audit pins before touch/flashing, run screen tasks and wake/power trials, select microphone only after bus/power review, inventory the Pi, stage separately authorized live checks, and release battery/fit choices only from measurements. Do not guess touch-wake wiring or treat compile success as gate completion.


## Subsequent implementation checkpoint — 22 September 2026

This closeout's next-work statements describe its earlier checkpoint. The [native UI parity record](m2-ui-parity.md) now records the implemented shared C/LVGL slices and fresh desktop validation. Outstanding real artwork, device/provisioning and hardware work remains explicit there; the approved browser source and historical decisions have not been changed.

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
