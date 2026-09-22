# HP-01 — USB-powered display, touch wake and energy baseline

Status: ready-to-execute protocol, not executed. [Native fixture build recipe and diagnostic hooks](../../firmware/README.md) are prepared; compilation and hardware trials remain open. 20 September 2026. No procurement recorded. Dependencies: HW-001 exact model available, measurement equipment inventoried, revision-matched schematic and example reviewed.

## Question and setup

Can the preferred Waveshare ESP32-S3-Touch-LCD-4.3B without case render the core 800 × 480 interaction, wake reliably from touch, and reach a standby load worth pursuing with a base battery?

Start with board only, a known suitable regulated USB 5 V source and data cable. Leave the battery socket and DC input unused. Use one verified supply path; disconnect programming-host power for standalone measurements unless isolation is established. Do not attach a battery, external charger or boost for this experiment.

Record exact SKU/revision, matching schematic/example source revision, firmware commit, SDK version/configuration, brightness settings and measured input voltage. Check touch IRQ routing, wake capability, polarity, pull state, touch supply/reset and backlight control against the actual revision. The existing GPIO4 wake inference is a hypothesis. Measure lens/board outline, mounting, depth and connector protrusions separately; do not mistake glass dimensions for board dimensions.

Use a profiler/shunt setup resolving the expected low standby range and capturing startup/Wi-Fi peaks without introducing enough voltage drop to brown out the board. Record instrument accuracy, range, sample rate and burden voltage. A coarse USB meter may establish active consumption but cannot pass the sleep/peak gate. Use a multimeter for supply checks. Keep fixture on an insulating stable support.

## Minimal firmware scope

Pin the vendor example/toolchain and prove its display/touch demo first. Add a fixture-only 800 × 480 screen with artwork, scrolling rows, keyboard and touch coordinates; no live Naim commands. Add timestamped state markers and configurable active, backlight-off, light-sleep and deep-sleep trials. Retain touch power and configure the verified external interrupt wake source. Start with backlight off before deeper sleep so each reduction is separately observable.

After wake, consume the wake contact and wait for release before accepting actions. Reinitialize touch/display/network, fetch a fixture snapshot and label it fresh. Ensure a held finger does not cause immediate sleep/wake cycling. Serial logging/programming hardware may alter current: record this and repeat steady-state tests detached. A stock example demo alone does not pass the fixture or sleep gate.

## Run sheet

| Step | Procedure / sample | Record / gate |
| --- | --- | --- |
| 1 | Boot stock demo; inspect at actual table angle and low/medium/high brightness | No display faults; actual touch edge coverage and viewing legibility. Failure isolates board/example first |
| 2 | Run core UI fixture, keyboard and scrolling for 10 min | Dropped touches, frame latency, free/peak heap/PSRAM, resets; no memory exhaustion |
| 3 | Measure boot/reconnect peaks, 5 min browsing per brightness level and 10 min connected idle | Average W, peak current/voltage droop, integrated Wh; avoid treating current at 5 V as battery-side current |
| 4 | Measure backlight-off awake, lowest workable light sleep and deep sleep for at least 10 min each | Touch retained? Average W, IRQ state, spontaneous wakes, wake energy; mark unsupported states failed, not zero draw |
| 5 | 100 deliberate sleep/wake cycles spanning centre/edges; include 10 held-contact cases | Proposed gate: 100/100 intentional wakes, zero unintended fixture commands, no wake loop/reset; provisional p95 visible feedback ≤1 s and fresh fixture state ≤5 s on healthy LAN |
| 6 | At least 8 h untouched standby then touch; repeat with Wi-Fi unavailable then restored | Spontaneous wake count and energy, successful wake; honest stale/offline state, automatic fresh-state recovery and no queued command replay |

Latency thresholds are initial engineering targets, not agreed user requirements. A fixture network result is not Naim recovery proof. Keep live integration under P2 and announce audible tests separately.

## Decision and energy interpretation

Report each state rather than quoting MCU deep-sleep specifications. Select the lowest measured state that preserves repeatable touch wake. A failure leads to targeted touch/schematic/firmware diagnosis or comparison with light sleep; do not silently replace touch wake with a button.

Compare USB standby power with the existing [power-review budgets](power-review.md). For example, the illustrative 10 Ah / 28-day / 15-minutes-active scenario allows about 20.8 mW standby under its assumptions. Exceeding that at the display input already makes that scenario infeasible; passing does not establish feasibility because the external power chain and wake load remain unmeasured. Final P4 calculations use battery-side energy and avoid double-counting converter losses.

Exit artifact: sanitized report with measured values/uncertainties and per-step pass/fail, firmware/build recipe, raw capture locations under ignored `local/`, and recommendation: retain display for next trial, diagnose a named fault, or escalate a requirement tradeoff. Update evidence/BOM only with observations. No weeks-of-standby claim, battery selection or final enclosure dimensions follows from HP-01 alone.
