# Prototype procurement BOM — UK
21 September 2026. Covers one controller and bench bring-up. Nothing ordered by this task.

User inventory: tools and wires already owned, including the supplies/meters asked about; regulated USB PSU missing. Screen not ordered, awaiting stock. Consolidate purchases when the screen is available. Exact meter capability should still be recorded with measurements.

## Proposed supplier baskets

Prices are listed GBP item prices checked 21 September, excluding delivery. Pi Hut prices include VAT. Pimoroni BAT0008 shows £15; confirm UK VAT and variant at checkout. Stock can change. A listing with an Add to cart button alone is not proof of stock.

| BOM | Part / supplier link | Qty | Unit price | Stock / purchasing status |
| --- | --- | --- | --- | --- |
| HW-001 | [Pi Hut Waveshare display listing](https://thepihut.com/products/esp32-s3-development-board-with-4-3-capacitive-touch-lcd-display-800-x-480): **ESP32-S3-Touch-LCD-4.3B, without case, Waveshare 27848** | 1 | Exact bare-board quote pending | Selected; user reports waiting stock. Do not substitute plain 4.3 or case variant |
| HW-020 | [Adafruit 3421 SPH0645LM4H I2S microphone — Pi Hut](https://thepihut.com/collections/audio/products/adafruit-i2s-mems-microphone-breakout-sph0645lm4h) | 1 | £6.70 | Listed in stock; evaluation candidate, integration untested |
| HW-021 | [SparkFun microSD Sniffer — SK Pang](https://www.skpang.co.uk/products/microsd-sniffer), USD-SNIFFER / SparkFun TOL-09419 | 1 | £8.52 incl VAT | Orderable listing; availability not explicitly confirmed. Experimental pin access, not a microphone interface |
| HW-017 | [Official Raspberry Pi 15 W USB-C PSU, UK plug — Pi Hut](https://thepihut.com/products/raspberry-pi-psu-uk), white SC0443 | 1 | £7.70 | Listed in stock; 5.1 V / 3 A, captive USB-C cable. For display bench power |
| HW-002 | [Pimoroni protected lithium-ion pack](https://shop.pimoroni.com/products/lithium-ion-battery-pack), **6600 mAh BAT0008** | 1 | £15.00 listed | Candidate; variant stock unresolved. Road shipping. Confirm connector polarity and mechanical envelope before ordering |
| HW-003 | [Adafruit BQ24074 4755 charger — Pi Hut](https://thepihut.com/products/adafruit-universal-usb-dc-solar-lithium-ion-polymer-charger-bq24074) | 1 | £14.40 | 11 listed available at research time; external-power evaluation candidate |
| HW-004 | [Pololu U3V16F5 4941 converter — Pi Hut](https://thepihut.com/products/pololu-5v-step-up-voltage-regulator-u3v16f5) | 1 alternative | £6.70 | Sold out; candidate only, load capacity must be measured. Existing U3V70F5 remains another candidate; do not buy both |
| HW-022 | 10 kΩ NTC battery-temperature probe suitable for BQ24074 | 1 conditional | Unquoted | Part curve and attachment to pack still to specify; not a generic interchangeable thermistor purchase |

**Subtotal for microphone + sniffer + PSU: £22.92**, excluding screen and delivery. Pi Hut portion £14.40; SK Pang portion £8.52.
Battery + charger + U3V16F5 add £36.10 at listed prices: **£59.02 partial electronics scenario**, excluding screen, shipping, any VAT adjustment on the battery, NTC and remaining assembly items. This is not a complete build total or a released battery-powered design.

Target primary basket: Pi Hut screen, microphone, PSU and whichever power parts pass selection. Use SK Pang for the sniffer only if that access route is retained. Pimoroni battery creates a third delivery unless a suitable pack becomes available from the primary supplier. This is a consolidation proposal, not a proven cheapest landed basket: delivery depends on destination and battery carriage. Do not place separate small orders while screen stock remains the gating item.

## Full remaining assembly coverage

Owned wires/tools are not automatic proof that all specialised connectors and mechanical stock are owned.

| BOM | Quantity / specification for prototype | Procurement treatment |
| --- | --- | --- |
| HW-005 battery monitoring | 0 boards initially for USB bench trial; 1 function required for battery build | Select accessible battery sensing/fuel gauge and low-voltage cutoff; do not assume Waveshare monitors an external pack |
| HW-006 harness | 1 assembly: pack-to-charger mating connector, charger OUT-to-converter, converter-to-display USB power cable; 5 mic signal/power wires plus channel-select strap | Reuse owned wire; identify keyed connector pitch/polarity and cable gauge against measured peaks. Short soldered I2S leads preferred. Final connectors/cable lengths pending |
| HW-007 charge inlet | 0 extension on open bench; 1 accessible rear inlet in housing | First use charger's own USB port. Select extension type/length only after charger and enclosure fit; display USB and charger USB are different power paths |
| HW-008 service isolation | 0 extra on bench when unplugging pack; 1 disconnect function in finished build | Keyed battery connector can provide service isolation with underside removed. If adding external switch, rate for DC startup current and account for USB power too |
| HW-009 wake circuit | 0 initially | Buy only if measured native touch wake cannot meet requirement |
| HW-010/011 housing/base | 1 printed shell, 1 matching removable cover; 2 printed screen retainers | P1S already owned. Use matching v3 files; full build remains unreleased |
| HW-012 battery restraint | 1 printed cradle, 1 insulating liner, 1 retention strap/cushioning set | Dimensions depend on actual pack; avoid crushing cells or covering antenna |
| HW-013 fasteners | 4 provisional M3 screen-retainer screws + 4 M3 nuts; 4 cover screws; electronics standoffs/fasteners additional | Nut-pocket approach in current CAD, not heat-set inserts. Exact lengths, cover thread treatment and board fasteners need fit coupon/actual board; no final fastener kit specified |
| HW-014 feet | 4 non-slip silicone feet or 1 cut base pad | Select thickness after base stability check; same-supplier consumable if available |
| HW-015 glass support | 2 compliant strips at retainer contacts; provisional 0.8 mm material | CAD assumes 0.2 mm compression; stiffness/load not validated. No pad over active display or touch surface |
| HW-016 ballast | 0 initially | Battery adds mass; decide after tilt test |
| HW-017 charging cable | PSU includes USB-C cable for screen; charger input cable may differ by board | Existing wire/cable stock first. Do not assume USB-C PSU connects directly to every candidate charger |
| HW-020 mic mounting | 1 small printed mount + compliant support; 1 acoustic opening | Keep bottom acoustic port unobstructed. Locate away from touch vibration and converter; no membrane/mesh selected yet |
| HW-021 sniffer restraint | 1 insulating support/strain relief | Exposed contacts and card overhang require fit check; no SD card inserted during mic use |
| HW-022 temperature sensing | 1 external probe if external charging route retained | Sensor for charging control differs from owned bench temperature measurement; confirm part and thermal contact |
| Filament / finish | Approximately one prototype's material, plus coupons/reprints | Existing filament inventory unspecified; no full new spool assumed. Slicer study does not cover a released complete assembly |
| Bench tools/wire/meters | Existing; £0 new acquisition allowance | User-confirmed. PSU above is missing item. Record meter model/range when running tests |
| HW-018/019, EXC-001 | 0 dock, phone, speaker, DAC or amplifier | Excluded; native NDX 2 playback |
| SYS-001/002/003, INC-001/002 | Existing Naim system/Pi and included display MCU/radio/touch/RTC | No duplicate purchases; microSD card and RTC cell not required for first trial |

## Purchase readiness and power findings

The USB-powered screen/voice evaluation can be specified now. A fully finalised battery and enclosure order cannot yet be promised: pin access, charge duration, load peaks, cutoff and mechanical fit remain untested. Keep the candidates in one procurement record instead of treating them as approved substitutions.

The [Pimoroni-linked BAT0008 datasheet](https://cdn.shopify.com/s/files/1/0174/1800/files/PKcell_ICR18650_6600mAh_Final.pdf) specifies 3.7 V nominal, 4.2 V charging, 3.0 V discharge endpoint and 3 A maximum continuous charge/discharge. This supports further evaluation with a 1 A charger; it does not establish connector polarity or fit in the existing Adafruit-353-derived CAD reservation.

[BQ24074 documentation](https://learn.adafruit.com/adafruit-bq24074-universal-usb-dc-solar-charger-breakout/pinouts) distinguishes its approximately 3–4.4 V load output from regulated 5 V. A boost converter is required for this route. Verify charge safety-timer configuration against the large pack, charge termination during use, thermal performance and low-voltage shutdown before integration. Keep the Waveshare battery socket empty on this external route. Avoid simultaneously feeding external 5 V and a programming host until backfeed paths are checked.

[Pololu U3V16F5](https://www.pololu.com/product/4941) is a smaller locally listed candidate, not a selected replacement for U3V70F5: its 1.6 A figure is input current, not 5 V output current. It has no true output disconnect and needs system-level low-battery control. Startup, full-brightness/Wi-Fi peaks and idle losses determine suitability.

The [Adafruit 6106 BQ25185 combined 5 V board](https://learn.adafruit.com/adafruit-bq25185-usb-dc-solar-charger-with-5v-boost-board/overview) was examined but is not recommended for this basket. Its fixed six-hour charge timeout can interrupt a depleted 6600 mAh pack's charge; the guide also flags startup difficulty with immediate loads above 200 mA. Its £8.60 price and reduced board count do not resolve these requirements.

Before releasing the whole order: confirm bare 4.3B stock/price, sniffer fit/net continuity from the board revision, battery dimensions/polarity, final charger/converter choice, and exact mechanical consumables. Recheck stock and supplier delivery totals together. No runtime or weeks-standby claim has been validated.
