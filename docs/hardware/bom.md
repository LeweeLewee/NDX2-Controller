# Parts BOM

Revision 0.9 — 22 September 2026. Prototype procurement BOM; see [UK prototype shopping list](prototype-shopping-list.md) for supplier baskets, current quotes and purchase-readiness limits.
Six Pi Hut items are ordered, user confirmed 22 September: display, charger, converter, microphone and two harness parts. Delivery not yet confirmed. USB-C PSU, tools and wires are already owned. MicroSD sniffer is ordered from SK Pang, user confirmed 22 September; Pimoroni BAT0014 10,050 mAh battery is also ordered, user confirmed 22 September.

D017 selects HW-001 and excludes HW-019. Existing prices are historical references, not refreshed quotes or purchasing approval. Selection and procurement are separate.

## Procurement status — 22 September 2026

| Supplier / source | Items | Status |
| --- | --- | --- |
| Pi Hut | Waveshare bare 4.3B display; BQ24074 charger; U3V40F5 regulator; SPH0645 microphone; JST-PH lead; USB-A female breakout | 6 items ordered; delivery not yet confirmed |
| SK Pang | SparkFun microSD Sniffer TOL-09419 | 1 item ordered; delivery not yet confirmed |
| Pimoroni | BAT0014 protected 10,050 mAh battery | 1 item ordered; delivery not yet confirmed |
| Existing inventory | USB-C PSU, USB cable, tools and wires | Owned; no purchase needed |
| Remaining design work | Battery monitoring/low-voltage control, temperature probe, enclosure parts and final fittings | Not yet selected or procured; conditional items remain conditional |

Order status comes from the user's confirmation. **Ordered does not mean received, assembled or tested.** Final invoice totals, order references and delivery dates have not been supplied.

## Controller parts

| ID | Item / exact candidate | Qty per unit | Selection | Procurement | Price reference | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| HW-001 | [Waveshare ESP32-S3-Touch-LCD-4.3B](https://www.waveshare.com/product/arduino/boards-kits/esp32-s3/esp32-s3-touch-lcd-4.3b.htm), standard without case, SKU 27848 | 1 | selected | ordered from Pi Hut, user confirmed 2026-09-22 | USD 36.99; 2026-09-20; shipping/tax excluded | HP-01 after procurement; validate revision, touch wake and power |
| HW-019 | Old Android phone | 0 | excluded | not applicable — excluded | Not included | Ruled out by user, D017; no further phone trial |
| HW-020 | Adafruit 3421 SPH0645LM4H I2S microphone | 1 | evaluation candidate | ordered from Pi Hut, user confirmed 2026-09-22 | Pi Hut £6.70 incl VAT, 2026-09-21 | [Microphone review](microphone-review.md); proposed microSD pin reuse requires validation |
| HW-021 | SparkFun microSD Sniffer TOL-09419 / SK Pang USD-SNIFFER | 1 | evaluation candidate | ordered from SK Pang, user confirmed 2026-09-22 | £8.52 incl VAT, 2026-09-21 | Experimental mic pin access; confirm delivery, fit and continuity |
| HW-022 | External battery-temperature NTC probe compatible with charger | 1 conditional | research | not ordered | Unquoted | Specify sensor curve and mounting; separate from bench thermometer |
| HW-002 | Pimoroni BAT0014 protected 10,050 mAh / 3.7 V pack | 1 pack | prototype selection | ordered from Pimoroni, user confirmed 2026-09-22 | Checkout showed £25 subtotal + £10.74 shipping + £7.15 estimated tax = £42.89; final paid amount unconfirmed | [Larger battery review](larger-battery-review.md): body fits reserved envelope; polarity, restraint and power tests pending |
| HW-003 | Adafruit BQ24074 4755 charger and power path | 1 | prototype selection | ordered from Pi Hut, user confirmed 2026-09-22 | Pi Hut basket £14.40 incl VAT | Validate delivered revision, charge rate, simultaneous use/charge and termination |
| HW-004 | Pololu U3V40F5 5 V step-up regulator, POL4012 | 1 | prototype selection | ordered from Pi Hut, user confirmed 2026-09-22 | Pi Hut basket £9.60 incl VAT | Measure idle losses and startup peaks; system low-voltage control remains unresolved |
| HW-005 | Battery state monitoring: onboard capability to investigate; external fuel gauge conditional | 0 or 1 extra board | research | not ordered | TBD if needed | Confirm voltage/status access and low-battery behaviour |
| HW-006 | Internal battery/power harness with keyed connectors and strain relief | 1 assembly | design | partially ordered; two parts below | £3.40 listed parts; remaining TBD | Assemble and verify polarity; use existing USB-A to USB-C cable to avoid soldering the display |
| HW-006a | JST-PH 2-pin female connector lead, Pi Hut 102818 | 1 | prototype selection | ordered from Pi Hut, user confirmed 2026-09-22 | £0.80 incl VAT | Charger LOAD output to converter input; verify polarity |
| HW-006b | USB-A female breakout — horizontal, Pi Hut 106576 | 1 | prototype selection | ordered from Pi Hut, user confirmed 2026-09-22 | £2.60 incl VAT | Converter output to existing display USB cable |
| HW-007 | Accessible charging inlet: existing USB-C port initially; extension or dock conditional | 0 or 1 extra inlet | design | not ordered | TBD if needed | Resolve port access without compromising enclosure or serviceability |
| HW-008 | Service power isolation for external base pack; exact switch TBD | 0 or 1 | research | not ordered | TBD if needed | Do not assume Waveshare battery switch isolates external 5 V; verify coverage and accessibility |
| HW-009 | External wake device or low-power latch, only if touch wake cannot meet energy target | 0 or 1 | optional | not ordered | TBD if needed | Validate native touch wake before adding hardware; preserve touch-wake requirement |
| HW-010 | Custom printed upper housing / bezel | 1 | design | not ordered | TBD | Fit print after display measurements; choose material/finish |
| HW-011 | Custom printed base / removable underside | 1 assembly | design | not ordered | TBD | Size around selected pack, charge electronics and antenna clearance |
| HW-012 | Battery cradle, cushioning and electrical insulation | 1 assembly | design | not ordered | TBD | Prevent pack movement and compression; retain service access |
| HW-013 | Screws, inserts and board standoffs | TBD set | design | not ordered | TBD | Derive exact counts and sizes from mounting design |
| HW-014 | Non-slip silicone feet or base pad | 1 set | design | not ordered | TBD | Compare grip/stability, adhesive and removable-pad options |
| HW-015 | Protective perimeter gasket / glass support | 1 set if needed | design | not ordered | TBD | Prevent point loads; avoid unnecessary touch overlay |
| HW-016 | Additional base ballast | 0 or 1 | optional | not ordered | TBD if needed | Decide after battery mass and tilt-stability evaluation |
| HW-017 | Existing user-owned USB-C power supply and suitable cable | 1 supply | reuse existing | owned / fulfilled, user confirmed 2026-09-22 | £0 incremental | Use normal 5 V USB output into BQ24074 USB-C input; no Raspberry Pi PSU purchase needed. Exact owned model and bench behaviour not yet recorded |
| HW-018 | Charging dock and contact pair | 0 | excluded from current design | not applicable — excluded | N/A | Stationary River Stone uses a rear charging inlet proposal; no controller-to-base transfer |

## Existing system and included functions

| ID | Item | Status / cost treatment |
| --- | --- | --- |
| SYS-001 | Naim NDX 2 | Existing; outside controller BOM cost |
| SYS-002 | Existing Naim amplifier and System Automation connection | Wired down/up verified (D011); preserve connection. Exact model/cable inventory is separate; no new cable needed by this plan |
| SYS-003 | Existing Home Assistant Pi | Available optional command/metadata bridge; outside base battery and new-parts subtotal |
| INC-001 | ESP32-S3, Wi-Fi/BLE, touch controller and LCD interface | Included in HW-001; no separate MCU/Wi-Fi/touch board |
| INC-002 | microSD slot and onboard RTC | Included in HW-001; card and RTC backup cell not selected; add only if justified |
| EXC-001 | Speaker, DAC, audio amplifier and audio relay hardware | Excluded: NDX 2 performs native audio playback |

## Bench equipment — separate from installed BOM

| Item | Quantity | Status | Purpose |
| --- | --- | --- | --- |
| USB data cable and suitable 5 V source | 1 each | cable and USB-C PSU owned, HW-017 | Firmware and first powered tests |
| Current profiler / meter with suitable sleep-current range and peak capture | 1 | user reports tools owned; record model/range at test | Measure standby and wake energy; basic USB meter alone may miss microamp sleep or short peaks |
| Multimeter | 1 | owned, user confirmed | Polarity, voltage and continuity |
| Caliper | 1 | inventory unverified | Mounting, connectors and enclosure fit |
| Temperature probe | 1 | inventory unverified | Charging/enclosure thermal measurements |
| Bambu Lab P1S, 0.4 mm nozzle | 1 existing | user-confirmed home printer | Fit and finish prototypes; filament selection remains open |

## Cost accounting

Current order references: Pi Hut £34.10 plus the unrecorded display price and delivery; SK Pang sniffer £8.52 before unrecorded delivery; Pimoroni checkout £42.89 including shipping and estimated tax. These are not a verified final paid total. PSU is already owned (£0 incremental).

The following USD scenario is retained only as historical research and must not be used as the current order total:

Selected display reference subtotal: **USD 36.99 for HW-001 only**, quoted 20 September 2026. This is not a refreshed price or total build cost.
External-route candidate prices: HW-002 Adafruit 353 USD 24.50; HW-003 Adafruit 4755 USD 14.95, checked 2026-09-20, shipping/tax excluded. These are unselected alternatives within their functional rows, not extra parts. The historical scenario did not include a converter price; the ordered U3V40F5 is now listed above at £9.60. Screen + these two candidates = USD 76.44, an incomplete scenario subtotal excluding converter, monitoring, harness, enclosure and charging supply. See [power review](power-review.md) for limits.

All remaining costs are unknown or conditional. No GBP conversion, stock guarantee, shipping or tax estimate has been assumed.
Keep original quote currency. If a converted budget is added, record exchange rate and date.
Add exact supplier, part/revision, quantity, quote date, paid cost and procurement state to each row as selection progresses.
Do not sum alternative power routes or count included functions twice.

## Historical procurement research — 21 September (superseded by current status)

[Consolidated UK shopping list](prototype-shopping-list.md) covers all functional rows and assembly consumables. BAT0008 6600 mAh (£15 listed) is a UK battery candidate; confirm variant availability, polarity and fit. BQ24074 (£14.40) remains an external charger candidate. Smaller U3V16F5 (£6.70, sold out) is an alternative converter for load testing, not a selected replacement for U3V70F5. Do not sum alternative converters. Combined BQ25185/boost board rejected for this basket because fixed six-hour charging timeout is a poor match for the large pack. No power route is released or runtime validated.

Microphone + sniffer new-purchase subtotal is £15.22 before delivery and screen; display/charger PSU is now owned (£0 incremental), superseding the previous £22.92 subtotal. Historic USD figures above remain historical; no complete build price is claimed.

## Larger battery follow-up — 22 September

[Review](larger-battery-review.md) promotes BAT0014 10,050 mAh as the leading candidate: 69.5 x 57 x 20.5 mm maximum body within the 80 x 64 x 26 mm reservation, 37.185 Wh nominal. BAT0015 13,400 mAh requires layout revision. Published Adafruit BQ24074 schematic grounds TMR (safety timers disabled), resolving the earlier timer-configuration research item for that source revision. Delivered hardware, charging and runtime remain untested.

## Pi Hut order — 22 September

User confirmed all six items above ordered. Recorded basket subtotal is £34.10 plus the display and delivery; display paid price, final invoice total and arrival date are not supplied. Prices remain basket references, not invoice verification. Earlier converter comparisons and cost scenarios are historical; U3V40F5 is the ordered prototype converter. Procurement does not establish validated integration or battery life.

## Battery order — 22 September

User confirmed Pimoroni BAT0014 10,050 mAh ordered. Checkout screenshot showed £42.89 including shipping and estimated tax; no discount acceptance or final invoice supplied. Delivery not yet confirmed. All eight named prototype electronics/connector items across Pi Hut, SK Pang and Pimoroni are now ordered; PSU, tools and wires are owned. Remaining monitoring, temperature sensing and enclosure assembly details are still open.
