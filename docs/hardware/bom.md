# Parts BOM

Revision 0.2 — 20 September 2026. Planning BOM, not a purchase list.
All new items are **not ordered**. Hardware ownership is only recorded where established; inventory still needs checking.

## Controller parts

| ID | Item / exact candidate | Qty per unit | Selection | Procurement | Price reference | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| HW-001 | [Waveshare ESP32-S3-Touch-LCD-4.3B](https://www.waveshare.com/product/arduino/boards-kits/esp32-s3/esp32-s3-touch-lcd-4.3b.htm), standard without case, SKU 27848 | 1 | preferred | not ordered | USD 36.99; 2026-09-20; shipping/tax excluded | Validate screen, board revision, touch wake and consumption |
| HW-002 | Protected rechargeable battery pack, base mounted; 5,000–10,000 mAh at nominal 3.7 V is an initial range only | 1 pack | research | not ordered | TBD | Select chemistry, topology, Wh, dimensions, protection and connector after load/charge assessment |
| HW-003 | Charger and power path: external route leads; Adafruit BQ24074 4755 candidate | 1 function; 0 or 1 extra board | research | not ordered | Candidate USD 14.95; 2026-09-20; shipping/tax excluded | Verify schematic, charge rate, simultaneous use/charge and termination |
| HW-004 | Regulated 5 V supply / load switching: external converter candidate; Pololu U3V70F5 reference | 1 function; 0 or 1 extra board | research | not ordered | TBD for external converter | Measure idle losses and startup peaks; avoid duplicate power hardware |
| HW-005 | Battery state monitoring: onboard capability to investigate; external fuel gauge conditional | 0 or 1 extra board | research | not ordered | TBD if needed | Confirm voltage/status access and low-battery behaviour |
| HW-006 | Internal battery/power harness with correctly keyed mating connectors and strain relief | 1 assembly | design | not ordered | TBD | Specify external charger/pack/5 V connections; leave HW-001 battery socket empty for route B; verify polarity and measured peaks |
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
| HW-017 | External USB charging adapter and cable | 1 set | research | not ordered | TBD | Inventory existing supply; select voltage/current after charging route |
| HW-018 | Charging dock and contact pair | 0 or 1 set | optional | not ordered | TBD if chosen | USB access is initial proposal; dock selection deferred |

## Existing system and included functions

| ID | Item | Status / cost treatment |
| --- | --- | --- |
| SYS-001 | Naim NDX 2 | Existing; outside controller BOM cost |
| SYS-002 | Existing Naim amplifier and System Automation connection | Existing amplifier; exact model/cable inventory and working command path unresolved; do not order a new cable speculatively |
| SYS-003 | Existing Home Assistant Pi | Available optional command/metadata bridge; outside base battery and new-parts subtotal |
| INC-001 | ESP32-S3, Wi-Fi/BLE, touch controller and LCD interface | Included in HW-001; no separate MCU/Wi-Fi/touch board |
| INC-002 | microSD slot and onboard RTC | Included in HW-001; card and RTC backup cell not selected; add only if justified |
| EXC-001 | Speaker, DAC, audio amplifier and audio relay hardware | Excluded: NDX 2 performs native audio playback |

## Bench equipment — separate from installed BOM

| Item | Quantity | Status | Purpose |
| --- | --- | --- | --- |
| USB data cable and suitable 5 V source | 1 each | inventory unverified | Firmware and first powered tests |
| Current profiler / meter with suitable sleep-current range and peak capture | 1 | research / inventory unverified | Measure standby and wake energy; basic USB meter alone may miss microamp sleep or short peaks |
| Multimeter | 1 | inventory unverified | Polarity, voltage and continuity |
| Caliper | 1 | inventory unverified | Mounting, connectors and enclosure fit |
| Temperature probe | 1 | inventory unverified | Charging/enclosure thermal measurements |
| 3D printer or print service | as needed | inventory unverified | Fit and finish prototypes |

## Cost accounting

Known preferred new-part subtotal: **USD 36.99 for HW-001 only**. This is not the total build cost.
External-route candidate prices: HW-002 Adafruit 353 USD 24.50; HW-003 Adafruit 4755 USD 14.95, checked 2026-09-20, shipping/tax excluded. These are unselected alternatives within their functional rows, not extra parts. HW-004 price remains TBD. Screen + these two candidates = USD 76.44, an incomplete scenario subtotal excluding converter, monitoring, harness, enclosure and charging supply. See [power review](power-review.md) for limits.

All remaining costs are unknown or conditional. No GBP conversion, stock guarantee, shipping or tax estimate has been assumed.
Keep original quote currency. If a converted budget is added, record exchange rate and date.
Add exact supplier, part/revision, quantity, quote date, paid cost and procurement state to each row as selection progresses.
Do not sum alternative power routes or count included functions twice.
