# Detailed design and hardware proof

> **D030 update — 25 September 2026:** iPhone 11 + selected UGREEN power bank replace Waveshare as active physical hardware. [Mounting/interface proposal](hardware/river-stone/iphone-mount/README.md) is under discussion. Earlier Waveshare hardware/UI implementation details below are retained fallback; native playback and bridge security requirements remain. This physical-design update does not implement or approve the entire iPhone software/power draft.

Started 20 September 2026. Updated 21 September: parallel M2 software implementation is now present; see [implementation, validation and hardware-arrival checklist](m2-software.md). No hardware or Pi deployment proof is claimed.

**Scope update, 21 September 2026:** Waveshare ESP32-S3-Touch-LCD-4.3B without case is selected; Android is ruled out (D017). The [comparison](hardware/display-comparison.md) is retained as history. HP-01 is the first hardware experiment; purchase and hardware proof remain outstanding.

## Reference and audit

The annotated tag `software-feasibility-v1` resolves to commit `aa070fc0af4a616f769a7c0f15790831c90c112c`. At the original phase-entry audit HEAD matched that commit; subsequent documentation and packaging commits extend it. Preserve the tag and computer prototype as the comparison reference; do not redesign its playback route or restart feasibility research.

Read together: [handover](milestone-handover.md), [decisions](decisions.md), [architecture](architecture.md), [hardware index](hardware/README.md), and all five documents linked by that index. The audit also inspected collection/voice documentation and the bridge/token adapters. Findings:

| Area | Established in repository | Unresolved / next deliverable |
| --- | --- | --- |
| Playback and amplifier | Computer-side native TIDAL, queue operations and bounded wired System Automation proven | Preserve adapters and D011 semantics; exercise integration/recovery, not a new audio path |
| Display | HW-001 exact preferred model recorded; manufacturer references only | Actual revision, physical usability, memory/render load, accessible pins and touch wake |
| Energy | Wh model and candidate external power route exist; no measurements | Whole-board standby and wake energy before battery sizing; no weeks-of-use promise |
| Power components | Onboard large pack on hold; external charger/boost shortlisted | Net-level revision review, low-load losses, peak/thermal limits, isolation and backfeed |
| Voice | Browser capture/transcription proven | No microphone selected; bus/pin availability, capture amid music, acoustic opening and power |
| Deployment | Loopback HTTP server, in-memory credentials and refresh logic exist | Persistent secure service, controller authentication, renewal/revocation and recovery |
| Interaction | 800 × 480 browser proof | Physical target sizes, keyboard, wake contact, busy/unknown/error behavior |
| Packaging | Base battery and serviceable printed shell required | Measured parts, cable/insertion clearances, thermals and seated touch stability |

The packaging work originally inspected as untracked is now recorded in commit `ef2576c`: `docs/hardware/river-stone/` and `tools/river_stone_layout.py`. Their README records a selected stationary River Stone concept and P1S/0.4 mm manufacturing constraint. Carry that direction into packaging review without reopening aesthetics. Its dimensions/reservations are proposals, not fit or electrical evidence. The phase plan does not release that layout for manufacture.

Two stale records described amplifier control as unresolved; the BOM and R10 now point to D011. No physical cable identification or new cable purchase is implied. The deferred browser discrepancy is B01 below; its cause is unknown.

## Work packages and gates

Sequence: P0 → P1; P2 and P3 specification can proceed during P1; P1 + P2 + P3 → P4 → P5. Procurement is separate from design approval. Time estimates depend on equipment availability; no purchase is recorded or authorized by this plan.

| Work | Deliverable | Dependencies | Acceptance / stop condition |
| --- | --- | --- | --- |
| P0 — bench readiness | HW-001 availability, equipment inventory and dated purchase proposal if needed | Existing BOM | Exact selected 4.3B without case; suitable supply/measurement equipment; purchasing approval before ordering |
| P1 — screen/touch/power proof | [Waveshare HP-01 report](hardware/first-experiment.md), reproducible firmware/build settings and sanitized traces | P0, revision-matched schematic/example review | Usable screen, repeated touch wake and measured power states; diagnose failures before integration |
| P2 — deployment proof | [Deployment design](deployment-design.md), host suitability record, service/config/recovery tests | Read-only Pi inventory; no existing HA workload changes without a concrete migration plan | Secure restart restores authorization; renewal, revocation, controller pairing and lost-command recovery pass; HA workload remains healthy |
| P3 — interaction and microphone | [Physical UI trial](interaction-design.md), task results; pin/bus budget and microphone capture report | P1 display; fixture bridge available before P2 deployment | Core tasks usable at actual size; transcript review/cancel works; recording stops on exit; microphone capture under display/Wi-Fi load succeeds |
| P4 — power selection | Measured battery-side energy budget, selected pack/charger/converter and wiring drawing; revised BOM | P1 loads, P3 microphone load, agreed use profile | Peak margins, standby budget, charge/use thermals, low battery and service isolation pass against chosen component ratings |
| P5 — fit and integrated prototype | Measured component CAD, bezel/mount sample, serviceable fit print and integration report | P1 dimensions, P3 acoustics, P4 selected parts | No glass point loads/pack compression; insertion and service paths work; charging, RF, heat and touch stability pass in housing |

P2 starts with a thin controller UI plus an always-on metadata/control bridge as the working architecture. Use embedded UI firmware on the selected Waveshare; Android work is retired. Reusing the existing home-automation Pi is preferred conditionally, not an assertion that its OS supports the service. See deployment gates before installing anything. A separate host is a fallback only if resource/isolation constraints require it; no new host purchase now.

## Parallel software preparation

While hardware is unavailable, the next software task can implement a development-host bridge, fixture-backed controller contract, recovery/security tests and an embedded UI/build foundation using the selected Waveshare assumption. This extends parallel preparation beyond specification; it does not pass P1, physical P3 or Pi deployment acceptance. Keep hardware-specific interfaces replaceable and distinguish simulation, compilation and live observations. Implementation started after repository cleanup: protected bridge state, authenticated TLS fixtures, navigation/recovery and native UI/build sources are now available. The shared desktop LVGL TLS flow, two native C tests and ESP32 fixture compilation now pass; provisioning and on-device network validation remain open. P2 software tests proceed independently of P0/P1; host suitability and physical gates remain open.

## First practical action and evidence discipline

Execute HP-01 on the selected Waveshare using USB power before connecting a large battery. It tests touch wake, standby consumption and recovery. Confirm board and instrument availability first; until hardware is available, complete revision-matched schematic review and prepare the build recipe. A desktop demo is not hardware proof.

Store private captures, host inventory, addresses, receipts and recordings under ignored `local/`. Commit sanitized summaries with date, board revision, firmware commit/build configuration, instruments, measurement boundaries, durations, failures and raw-evidence location. Add conclusions to [evidence](evidence.md) only after observation; update decisions and roadmap at each gate. A failed gate is useful evidence, not grounds to silently change native playback or touch-wake requirements.

## Backlog and unresolved user choices

| ID | Item | Trigger / disposition |
| --- | --- | --- |
| B01 | Album-save visibility differed between laptop browser and Codex preview; cause was not documented | Deferred. Investigate only if it blocks a deployment/UI acceptance task or the user requests it. Record exact build, mode, origin, account authorization and reproduction in both contexts then; do not assume caching or apply a speculative fix |
| B02 | Gaplessness, higher sample rates, Naim-app concurrency and real outage recovery | Schedule coexistence/outage checks in P2 integration; quality checks only when relevant. Preserve existing partial evidence |
| B03 | Queue-edit UI, playlist creation/editing, shuffle/repeat/seek and additional row hearts | Prioritize explicitly after core P3 task trial; no feature-parity expansion in this phase |
| B04 | Daily use and recharge target | Before P4 sizing agree active minutes/day, visible-display listening hours, standby weeks, wake tolerance and recharge duration. Use existing 15/30-minute and 28-day scenarios only as assumptions |
| B05 | Dock, ballast, e-paper alternative | Deferred unless measured charging convenience, stability or LCD energy failure makes one relevant |

Hardware availability is the immediate information dependency. Pi OS/install type/resources are the next deployment dependency. Purchasing, a host migration or a measured requirement tradeoff needs a concrete proposal for user decision; reversible documentation and fixture work continue independently.

## Current continuation — 22 September 2026

Desktop UI design is approved (D020). [M2 closeout](m2-closeout.md) records delivered software, prior validation and remaining gates; [the continuation prompt](continuation-prompt.md) starts the approved shared-LVGL implementation. The subsequent [native port](m2-ui-parity.md) implements the core layouts, Settings/detail navigation and immediate-record Stop & search, with integration limits recorded explicitly. This checkpoint does not close HP-01 or physical P3/P4/P5.


## Shared approved UI implementation — 22 September 2026

The approved direction is now implemented as native C/LVGL slices: Playing layout and controls, filtered search, nested details and membership, collection/queue reads, immediate-record voice search and Settings. See the [parity inventory and actual evidence](m2-ui-parity.md) for implemented behavior and remaining integration gaps. Desktop evidence: 72 Python tests, five JavaScript tests, two CTests, five-stage TLS demo and expanded native LVGL/TLS smoke passed. HP-01 and physical P3/P4/P5 remain open; the hardware-arrival checklist is unchanged.
