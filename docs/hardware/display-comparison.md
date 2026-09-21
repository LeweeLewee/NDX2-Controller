# Display comparison — superseded history

**Closed, 21 September 2026 (D017): Waveshare selected; Android ruled out by the user.** AP-01 and the selection gate below are retired, unexecuted plans retained for history. D015 records the visual-design reason for excluding repurposed phones; no failed test is inferred. Active work is [Waveshare HP-01](first-experiment.md).

20 September 2026; D016 user direction. Waveshare has not been purchased. Old Android phone model/version/condition are unknown. Both are candidates, neither is final. This is a validation plan, not new manufacturer research or measured hardware evidence.

| Decision dimension | Waveshare ESP32-S3-Touch-LCD-4.3B, without case | Old Android phone |
| --- | --- | --- |
| UI | 800 × 480 embedded implementation needed | Existing browser UI may accelerate proof; actual viewport, support and kiosk behavior unknown |
| Touch wake | GPIO4 external touch IRQ is a documented inference; HP-01 must prove it | Model/OS-dependent screen-off gesture and lock behavior; must prove touch wake without a side button |
| Voice | Mic/pins/buffering not selected | Built-in microphone is a candidate; browser capture, music interference and enclosure opening still require trial |
| Power | External charger/5 V route under research; battery-side measurements pending | Existing internal battery plus proposed base supply introduces a second power system; efficiency, low-load cutoff, heat and health pending |
| Packaging | Provisional supplier dimensions; verify actual module and connectors | Measure full phone, protruding plug, cable bend, microphone, vents and removal path; keep battery serviceable |
| Reliability/security | Firmware/credential protection and authenticated bridge client needed | OS/browser security support, certificate trust, kiosk resume and update behavior need model-specific assessment |
| Purchase | Not purchased; no order authorized | Availability/inventory unconfirmed; no replacement phone purchase assumed |

## AP-01: first practical experiment if the phone is available

1. Record model, Android/browser version, security support status from current official documentation once identified, usable dimensions, battery condition and known charging specification. Keep identifiers/accounts/screenshots with private details out of Git. A damaged or swollen battery excludes powered/charging trials until serviced; do not open or modify the phone as part of this experiment.
2. Use its ordinary approved charger and intact internal battery. Run a local silent UI fixture on the actual phone (or authenticated HTTPS bridge once ready); never expose the frozen loopback service by simply changing its bind address. Complete the interaction task set in [interaction design](../interaction-design.md), noting scaling, artwork, keyboard, navigation and portrait/landscape behavior.
3. Configure a reversible supported touch-wake setting if available. Perform 100 sleep/wake trials and an 8-hour untouched standby trial, recording missed/spurious wakes, held-contact behavior, lock-screen friction and time to fresh fixture state. The same provisional HP-01 latency/no-accidental-command gates apply. A phone that only wakes by pressing a side button has not met touch wake.
4. Test microphone permission, explicit record/stop/cancel, 30-second limit and transcript review through the existing authorized setup. Test quiet and ordinary music conditions as in the interaction plan. A browser permission or secure-origin failure is a deployment constraint, not evidence of a bad microphone.
5. Measure active and screen-off behavior separately. Log initial/final charge, elapsed time, settings and battery health information; percentage loss is only a rough screening observation. USB input readings while charging include battery replenishment and cannot establish phone standby consumption. A defensible runtime claim needs controlled energy measurement/full-cycle trials and the eventual base supply's losses.
6. Reboot, disconnect/reconnect Wi-Fi and leave overnight. Confirm usable UI restoration, authentication and stale-state labeling; prohibit replaying queued playback/volume commands. Test normal charging use and temperature before designing an enclosed base. Do not assume a USB bank supports pass-through charging or stays on at low load.

Produce an AP-01 report with pass/fail/unknown against each criterion. If the phone fails fit, touch wake, support or power requirements, identify the exact tradeoff; do not quietly relax requirements. If it looks viable, compare against the value/cost of procuring Waveshare for HP-01 before asking for a purchase. Neither a good phone demo nor a datasheet selects final battery/charging hardware.

## Selection gate

Record physical comfort, touch wake/recovery results, microphone results, maintenance/security viability, energy evidence and a serviceable charging/base-battery plan for each evaluated candidate. Label untested comparisons unknown. Decide only with sufficient evidence for the requirements; a user choice is needed if measured constraints force a consequential size/runtime/maintenance tradeoff. No numerical ranking based on invented phone specifications.
