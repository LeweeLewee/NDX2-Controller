# M2 software and UI review closeout — 22 September 2026

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
