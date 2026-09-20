# Power component review

20 September 2026. Documentary research and engineering proposals only. No parts ordered, wiring approved or hardware measurements recorded.

## Finding that changes the route

Waveshare's [current user guide](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B/Instructions-For-Use) recommends a single 3.7 V cell of ≤2,000 mAh at the MX1.25 connector. Our proposed 5–10 Ah base pack falls outside that recommendation. Hold the onboard large-pack route pending manufacturer clarification; do not assume a connector adapter resolves it. The guidance does not establish a hard electrical capacity limit.

Leading research architecture: USB charging input → external charger/load sharing → 5 V boost → display USB supply, with one protected base pack connected to the external charger. Leave the display's battery socket empty. Supply routing, reverse-current behaviour and programming-USB coexistence still need revision-matched schematic review. This changes research priority, not the accepted display or final power selection.

## Narrowed component shortlist

Prices are manufacturer USD references checked 2026-09-20; tax, shipping and UK availability unresolved. BOM IDs remain authoritative.

| BOM | Candidate | Why it fits | Limitation / selection gate | Price |
| --- | --- | --- | --- | --- |
| HW-002 | [Adafruit 353, 3.7 V 6600 mAh](https://www.adafruit.com/product/353) | Protected assembled pack; 24.42 Wh nominal; 69 × 54 × 18 mm, 155 g suits a weighted base | No built-in thermistor. Use conservative vendor guidance: ≤1 A charge and <1.3 A sustained discharge. Product technical table gives higher limits; reconcile with supplier before final selection. UK battery shipping and fit unresolved | $24.50 |
| HW-003 | [Adafruit 4755, BQ24074](https://www.adafruit.com/product/4755) | USB-C input, load sharing, default 1 A charging matches conservative pack guidance | Load output ≤4.4 V, requiring boost; 1.5 A maximum load. Charge and load share input capacity. Linear charging needs thermal checks; optional 10 kΩ NTC requires implementation | $14.95 |
| HW-004 | [Pololu 2891, U3V70F5](https://www.pololu.com/product/2891) | 2.9–5 V input, regulated 5 V; true shutdown; 40.6 × 15.2 × 4.6 mm | Oversized current capability; enabled no-load current typically <1 mA is not our standby measurement. Compare a smaller converter on measured low-load efficiency. Its low-voltage lockout does not replace battery protection | TBD |
| HW-002 alternative | Protected 10 Ah pack, exact SKU unresolved | More energy reserve: 37 Wh nominal at 3.7 V | Needs credible datasheet, protection, thermistor, dimensions and UK supplier; capacity alone does not guarantee weeks of use | TBD |
| HW-005 / HW-008 | Fuel gauge and external service isolation, exact parts unresolved | Battery visibility and storage/service off with the external route | Gauge must measure the battery side, not regulated 5 V. Check bus addresses and low-battery recovery; display battery switch may not isolate external power | TBD |

The 6600 mAh pack consists of manufacturer-assembled parallel cells; this is not an instruction to parallel separate packs. Its vendor narrative is more conservative than its technical table. Keep the conservative current assumptions until clarified.

Screen + 6600 mAh pack + charger totals $76.44, excluding boost and remaining build parts. This is a scenario, not an order list.

## Touch wake feasibility

The [Waveshare pin map](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B) routes TP_IRQ to GPIO4; backlight enable is CH422G EXIO2 and touch reset EXIO1. [Espressif's ESP32-S3 sleep documentation](https://docs.espressif.com/projects/esp-idf/en/release-v5.4/esp32s3/api-reference/system/sleep_modes.html) allows external RTC wake on GPIO0–21.

Inference: GPIO4 provides a plausible deep-sleep wake path from the existing touchscreen. This uses the external touch-controller interrupt, not the ESP32 internal capacitive-touch wake API. It is not proven working. Retain touch power, confirm IRQ polarity/level and pull configuration, release/reset state, and ensure the touch-controller mode continues producing interrupts. Keep the converter on during touch standby; true shutdown is for storage unless another powered wake circuit is added.

Firmware trial: disable backlight, stop radio activity, configure GPIO4 external wake, enter sleep, then reinitialize UI/network and fetch fresh state. Suppress the wake contact as a playback command. Measure repeatability and whole-device current, including untouched overnight tests. No firmware has been implemented here.

## Quantified checks before selection

Using the existing illustrative 80% usable-energy factor and 2.25 W active load:

| Pack | Usable energy | Pure standby ceiling for 28 days | Standby ceiling with 15 minutes active/day |
| --- | --- | --- | --- |
| 6.6 Ah | 19.54 Wh | 29.1 mW | 5.7 mW during the remaining 23.75 h/day |
| 10 Ah | 29.60 Wh | 44.0 mW | 20.8 mW during the remaining 23.75 h/day |

These are calculated budgets, not measured performance; wake energy and additional reserve reduce the ceilings. At 30 minutes/day, 6.6 Ah lasts at most 17.4 days and 10 Ah 26.3 days even with zero standby consumption under these assumptions.

At 3 V battery and hypothetical 85% boost efficiency, 2.25 W requires about 0.88 A battery-side before other losses. That fits the conservative pack guideline only for this steady reference load; startup/Wi-Fi peaks remain unknown. Charger load ratings apply before the boost, not at its 5 V output.

At 1 A, empty-to-full charge arithmetic starts at 6.6 h for 6.6 Ah or 10 h for 10 Ah; taper, input sharing and thermal reduction make actual charging longer. Do not raise charging current simply because the charger supports 1.5 A.

## Next selection gates

1. Identify actual display PCB revision and visually review the matching power schematic; documentary pin mapping is not completed net-level review.
2. Measure USB-powered active peaks and touch-enabled sleep before committing battery geometry.
3. Compare converter low-load losses; retain the above module as a reference until the standby budget is demonstrated.
4. Resolve a UK-source protected pack, temperature sensing and charger thermal behaviour in the base.
5. Specify battery monitoring, service disconnect and one non-backfeeding charging/programming arrangement.
6. Only then finalize connectors, base layout and purchase BOM. Keep dock and ballast optional.

Source findings do not close the hardware validation milestone. See [validation](validation.md) and [research register](research.md).
