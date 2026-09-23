# Evaluation: prototype against goals and spec

23 September 2026. The prototype (`reference/still-water.html`) renders 22 states; every state was measured with an automated gate (`tools/still-water-gates.py` in this package) and inspected by eye. Renders are in `reference/`. This evaluates the design, not any build, hardware or power claim.

## Goals

| Goal | How it is met | Evidence | Verdict |
|---|---|---|---|
| A beautiful coffee-table object first | At rest the panel is off and the dark inlay is the object; nothing on screen resembles a phone or a tablet app | `01-sleep`, hero scene | Pass on paper; the physical inlay coupon and the on-table trial decide |
| Intriguing at rest | The music's own colour fills the inlay; no chrome, one hairline; Presence remains an option, not a dependency | `05-still`, `02-presence` | Pass for Still; Presence stays gated on power |
| Highly functional | Every action from the approved interaction design is reachable within one touch of Still: transport, amplifier, Up next, Ask, Find, Library; Settings by long-press | `06-touched` | Pass; Settings entry needs the physical trial |
| Music first, not a terminal | Title is the only sofa-readable element; status is typeset into the composition, never a bar or a badge | all NOW states | Pass |
| Honest states | Offline, pending, unknown, stopped, missing artwork each have a distinct render with no fabricated content and no spinner | `11` to `16` | Pass |
| Native Naim path, no automatic playback | Ask produces a search; results require a tap; Play is the only filled control | `08-ask`, `09-three`, `19-detail` | Pass by construction; enforced by the unchanged bridge |
| First touch never acts | Sleep and Presence taps go to Waking, not to a control | prototype logic | Pass |
| Volume remains bounded and unresolved | Amplifier is a separate pill with busy and unknown states; no slider, no hold | `13-pending`, `14-unknown` | Pass |

## Automated gate, all 22 states

| Check | Rule | Result |
|---|---|---|
| Tap targets | 72 × 64 minimum; pills and filter words 96 × 56; Play/Pause 80 × 80; Ask 72 × 72 | Pass after widening Find's search and mic buttons (64 → 72) and giving pills a 96 minimum |
| Overlaps | No two targets intersect | Pass |
| Text size | Nothing below 15 units | Pass after raising six labels (Amp, Up next, Plays in, Listening, Three for you, result kinds) from 10 to 13 up to 15 |
| Contrast | Ink @ 100% ≥ 7:1 and secondary ≥ 4.5:1 over the sampled field behind each title | Pass after raising secondary ink from 62% to 70% (measured 4.2:1 at 62% on sage) and keeping offline metadata at 70% rather than dimming it twice (2.9:1) |
| Clipping | No title overflows its box without the two-line ellipsis; list rows clip only inside their scroll container | Pass after adding the long-title step-down (56 → 44) |
| Canvas | No text outside 800 × 480 except inside a scroll container | Pass |
| Script errors | None | Pass |

## Eye review, findings acted on

- Long titles at serif-56 in a 384-unit column broke to about 12 characters a line and lost the title. Step-down added and specified.
- Touched: the Up next block and the elapsed time sit close at the foot. Kept; the iPhone window's extra width relieves it and P3 will judge it on the table.
- Pending: a hairline ring on Next reads correctly; the amplifier at 35% while busy reads as disabled, which is the intent.

## Still open, by design

| Item | Decided by |
|---|---|
| Seated readability of sans-18 and caps-15 at 600 to 800 mm | P3 on the table with the prototype on the phone |
| Touch accuracy through the inlay window edge | Physical coupon |
| Wake feel and latency | Gate 2 in `iphone-architecture.md` |
| Standby power on either platform | Gate 1 or HP-01 |
| Presence | Out of scope until a measured power budget exists |
| Results screen (`09-three`) | Future; needs explained suggestions from the bridge |
