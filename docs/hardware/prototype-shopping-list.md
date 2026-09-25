# Prototype procurement BOM — UK

> **D030 update — 25 September 2026:** active hardware is iPhone 11 + selected UGREEN Nexode 20000mAh PD 20W QC Power Bank. See [current mounting and power packaging](river-stone/iphone-mount/README.md). Waveshare-specific parts, experiments and purchase recommendations below are fallback history; actual prior order records remain valid. This update does not cancel orders or authorize more purchases.
Updated 22 September 2026. Covers one controller and bench bring-up. All eight named prototype parts are ordered: six from Pi Hut, one microSD sniffer from SK Pang, and one BAT0014 battery from Pimoroni. User confirmed 22 September; receipt/delivery not yet confirmed.

User inventory: tools and wires already owned, including the supplies/meters asked about; USB-C power supplies already owned (user confirmed 22 September; HW-017 fulfilled, no purchase needed). Screen became available and is included in the confirmed Pi Hut order. Exact meter capability should still be recorded with measurements.

## Supplier orders and outstanding purchases

Prices are listed GBP item prices checked 21 September, excluding delivery. Pi Hut prices include VAT. Pimoroni BAT0014 checkout screenshot showed £25 subtotal, £10.74 shipping and £7.15 estimated tax (£42.89 total); final paid amount and discount acceptance are unconfirmed. Stock can change. A listing with an Add to cart button alone is not proof of stock.

| BOM | Part / supplier link | Qty | Unit price | Stock / purchasing status |
| --- | --- | --- | --- | --- |
| HW-001 | [Pi Hut Waveshare display listing](https://thepihut.com/products/esp32-s3-development-board-with-4-3-capacitive-touch-lcd-display-800-x-480): **ESP32-S3-Touch-LCD-4.3B, without case, Waveshare 27848** | 1 | Exact bare-board quote pending | ordered from Pi Hut, user confirmed 2026-09-22; verify bare 4.3B revision on arrival |
| HW-020 | [Adafruit 3421 SPH0645LM4H I2S microphone — Pi Hut](https://thepihut.com/collections/audio/products/adafruit-i2s-mems-microphone-breakout-sph0645lm4h) | 1 | £6.70 | ordered from Pi Hut, user confirmed 2026-09-22; integration untested |
| HW-021 | [SparkFun microSD Sniffer — SK Pang](https://www.skpang.co.uk/products/microsd-sniffer), USD-SNIFFER / SparkFun TOL-09419 | 1 | £8.52 incl VAT | Ordered from SK Pang, user confirmed 2026-09-22; delivery not confirmed. Experimental microphone pin access, integration untested |
| HW-017 | Existing user-owned USB-C power supply | 1 owned; 0 to buy | £0 incremental | Fulfilled from existing stock, user confirmed 22 September. Use normal 5 V USB output with a suitable cable for the BQ24074 USB-C input |
| HW-002 | [Pimoroni BAT0014 10,050 mAh](https://shop.pimoroni.com/products/high-capacity-lithium-ion-battery-pack?variant=32012684623955), protected 3.7 V pack | 1 | £25.00 | Ordered from Pimoroni, user confirmed 2026-09-22. Body fits reserved envelope; confirm delivered pack polarity and cradle/lead routing |
| HW-003 | [Adafruit BQ24074 4755 charger — Pi Hut](https://thepihut.com/products/adafruit-universal-usb-dc-solar-lithium-ion-polymer-charger-bq24074) | 1 | £14.40 | ordered from Pi Hut, user confirmed 2026-09-22; external-power integration untested |
| HW-004 | [Pololu U3V40F5 — Pi Hut](https://thepihut.com/products/5v-step-up-voltage-regulator-u3v40f5), POL4012 | 1 | £9.60 | ordered from Pi Hut, user confirmed 2026-09-22; load and standby testing pending |
| HW-006a | [JST-PH 2-pin female connector lead — Pi Hut](https://thepihut.com/products/jst-ph-2-pin-cable-female-connector-150mm), 102818 | 1 | £0.80 | ordered from Pi Hut, user confirmed 2026-09-22; charger LOAD-to-converter lead |
| HW-006b | [USB-A female breakout — horizontal — Pi Hut](https://thepihut.com/products/usb-a-breakout-horizontal), 106576 | 1 | £2.60 | ordered from Pi Hut, user confirmed 2026-09-22; converter-to-display USB connection |
| HW-022 | 10 kΩ NTC battery-temperature probe suitable for BQ24074 | 1 conditional | Unquoted | Part curve and attachment to pack still to specify; not a generic interchangeable thermistor purchase |

**Pi Hut order: six items, £34.10 plus screen price and delivery**, using recorded basket prices including VAT. Screen paid price and final invoice total are not supplied. PSU already owned (£0 new spend). MicroSD sniffer is ordered from SK Pang (user confirmed 22 September; £8.52 reference price, final invoice/delivery not supplied). Pimoroni BAT0014 battery is also ordered, user confirmed 22 September; checkout total £42.89, final paid amount unconfirmed. No delivery or integration test is recorded.

## Full remaining assembly coverage

Owned wires/tools are not automatic proof that all specialised connectors and mechanical stock are owned.

| BOM | Quantity / specification for prototype | Procurement treatment |
| --- | --- | --- |
| HW-005 battery monitoring | 0 boards initially for USB bench trial; 1 function required for battery build | Select accessible battery sensing/fuel gauge and low-voltage cutoff; do not assume Waveshare monitors an external pack |
| HW-006 harness | 1 assembly: pack-to-charger mating connector, charger OUT-to-converter, converter-to-display USB power cable; 5 mic signal/power wires plus channel-select strap | JST-PH female lead and USB-A female breakout ordered; reuse owned wire and USB-A to USB-C cable. Check polarity and cable gauge against measured peaks. Short soldered I2S leads preferred. Final connectors/cable lengths pending |
| HW-007 charge inlet | 0 extension on open bench; 1 accessible rear inlet in housing | First use charger's own USB port. Select extension type/length only after charger and enclosure fit; display USB and charger USB are different power paths |
| HW-008 service isolation | 0 extra on bench when unplugging pack; 1 disconnect function in finished build | Keyed battery connector can provide service isolation with underside removed. If adding external switch, rate for DC startup current and account for USB power too |
| HW-009 wake circuit | 0 initially | Buy only if measured native touch wake cannot meet requirement |
| HW-010/011 housing/base | 1 printed shell, 1 matching removable cover; 2 printed screen retainers | P1S already owned. Use matching v3 files; full build remains unreleased |
| HW-012 battery restraint | 1 printed cradle, 1 insulating liner, 1 retention strap/cushioning set | Dimensions depend on actual pack; avoid crushing cells or covering antenna |
| HW-013 fasteners | 4 provisional M3 screen-retainer screws + 4 M3 nuts; 4 cover screws; electronics standoffs/fasteners additional | Nut-pocket approach in current CAD, not heat-set inserts. Exact lengths, cover thread treatment and board fasteners need fit coupon/actual board; no final fastener kit specified |
| HW-014 feet | 4 non-slip silicone feet or 1 cut base pad | Select thickness after base stability check; same-supplier consumable if available |
| HW-015 glass support | 2 compliant strips at retainer contacts; provisional 0.8 mm material | CAD assumes 0.2 mm compression; stiffness/load not validated. No pad over active display or touch surface |
| HW-016 ballast | 0 initially | Battery adds mass; decide after tilt test |
| HW-017 charging cable | Reuse existing suitable USB cable for owned PSU | BQ24074 has USB-C input; no separate Raspberry Pi PSU purchase. Confirm cable availability during assembly |
| HW-020 mic mounting | 1 small printed mount + compliant support; 1 acoustic opening | Keep bottom acoustic port unobstructed. Locate away from touch vibration and converter; no membrane/mesh selected yet |
| HW-021 sniffer restraint | 1 insulating support/strain relief | Exposed contacts and card overhang require fit check; no SD card inserted during mic use |
| HW-022 temperature sensing | 1 external probe if external charging route retained | Sensor for charging control differs from owned bench temperature measurement; confirm part and thermal contact |
| Filament / finish | Approximately one prototype's material, plus coupons/reprints | Existing filament inventory unspecified; no full new spool assumed. Slicer study does not cover a released complete assembly |
| Bench tools/wire/meters | Existing; £0 new acquisition allowance | User-confirmed. USB-C PSU also owned. Record meter model/range when running tests |
| HW-018/019, EXC-001 | 0 dock, phone, speaker, DAC or amplifier | Excluded; native NDX 2 playback |
| SYS-001/002/003, INC-001/002 | Existing Naim system/Pi and included display MCU/radio/touch/RTC | No duplicate purchases; microSD card and RTC cell not required for first trial |

## Purchase readiness and power findings

The eight prototype parts have been ordered for evaluation. Pin access, charge duration, load peaks, cutoff and mechanical fit remain untested. Monitoring, temperature sensing and final enclosure fittings still need resolution; the finished-build BOM is not yet complete.

The [Pimoroni-linked BAT0008 datasheet](https://cdn.shopify.com/s/files/1/0174/1800/files/PKcell_ICR18650_6600mAh_Final.pdf) specifies 3.7 V nominal, 4.2 V charging, 3.0 V discharge endpoint and 3 A maximum continuous charge/discharge. This supports further evaluation with a 1 A charger; it does not establish connector polarity or fit in the existing Adafruit-353-derived CAD reservation.

[BQ24074 documentation](https://learn.adafruit.com/adafruit-bq24074-universal-usb-dc-solar-charger-breakout/pinouts) distinguishes its approximately 3–4.4 V load output from regulated 5 V. A boost converter is required for this route. Verify charge safety-timer configuration against the large pack, charge termination during use, thermal performance and low-voltage shutdown before integration. Keep the Waveshare battery socket empty on this external route. Avoid simultaneously feeding external 5 V and a programming host until backfeed paths are checked.

Historical comparison (superseded for procurement by ordered U3V40F5): [Pololu U3V16F5](https://www.pololu.com/product/4941) is a smaller locally listed candidate, not a selected replacement for U3V70F5: its 1.6 A figure is input current, not 5 V output current. It has no true output disconnect and needs system-level low-battery control. Startup, full-brightness/Wi-Fi peaks and idle losses determine suitability.

The [Adafruit 6106 BQ25185 combined 5 V board](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board/overview) was examined but is not recommended for this basket. Its fixed six-hour charge timeout can interrupt a depleted 6600 mAh pack's charge; the guide also flags startup difficulty with immediate loads above 200 mA. Its £8.60 price and reduced board count do not resolve these requirements.

After the Pi Hut order: record display paid price and final invoice, check delivered board revisions, sniffer fit/net continuity, battery dimensions/polarity and exact mechanical consumables. Battery and sniffer are ordered; delivery and integration checks are pending. No runtime or weeks-standby claim has been validated.

## Larger pack update — 22 September

See [larger battery review](larger-battery-review.md). BAT0014 replaces BAT0008 and is ordered as the prototype battery, user confirmed 22 September. BAT0008 discussion above is historical comparison. BAT0014 body is 69.5 x 57 x 20.5 mm maximum, nominal energy +52.3%. The published Adafruit BQ24074 netlist grounds TMR, so its charge safety timers are disabled; check the delivered revision, thermal behaviour and charge termination. The earlier request to establish source timer configuration is now answered, not a claim of a tested charging system.
