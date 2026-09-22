# Larger battery review
22 September 2026. Reference-data and dimensional assessment, not a physical fit or runtime test.

## Recommendation
Promote **Pimoroni BAT0014, 10,050 mAh / 3.7 V**, to the leading prototype battery candidate. It offers 37.185 Wh nominal, 52.3% more than the 6,600 mAh baseline, and its specified maximum body fits the existing battery reservation. Keep procurement not ordered and the external power route under validation. No accepted design decision or CAD release is implied.

| Pack | Nominal Wh | Price GBP | Body dimensions / fit | Position |
| --- | --- | --- | --- | --- |
| BAT0008 6,600 mAh | 24.42 | £15 | Previous baseline; do not substitute Adafruit 353 dimensions for this SKU | Lower-cost fallback |
| BAT0011 8,800 mAh | 32.56 | £17.50 | Exact drawing not linked on standard-range page; unverified | Cheapest capacity increase; not preferred over a documented fitting pack |
| BAT0014 10,050 mAh | 37.185 | £25 | Maximum 69.5 x 57 x 20.5 mm | **Leading candidate** |
| BAT0015 13,400 mAh | 49.58 | £35 | Maximum 75 x 69.5 x 20.5 mm | Larger capacity, requires bay/layout revision |

Prices and availability checked against Pimoroni public product JSON on 22 September: all four above returned available=true. These are current item prices before delivery; confirm destination VAT at checkout. Earlier cached high-capacity page advertised £17.50/£24.50 sale prices: live data and exact 10,050 mAh variant page show £25/£35, so use those. No stock reservation made.

Exact purchase links:
- [BAT0008 6600](https://shop.pimoroni.com/products/lithium-ion-battery-pack?variant=23417820487)
- [BAT0011 8800](https://shop.pimoroni.com/products/lithium-ion-battery-pack?variant=21758938251347)
- [BAT0014 10050](https://shop.pimoroni.com/products/high-capacity-lithium-ion-battery-pack?variant=32012684623955)
- [BAT0015 13400](https://shop.pimoroni.com/products/high-capacity-lithium-ion-battery-pack?variant=32012684656723)

All are alternatives within HW-002, not multiple packs to purchase or parallel together. UK supplier, road-only battery carriage. BAT0014 adds £10 to the former battery scenario, without adding a supplier.

## Fit assessment
Current main at 28a4c594 specifies battery bounds X=-41..39, Y=-10..54, Z=8..34 in tools/river_stone_shell.py: **80 x 64 x 26 mm**.

BAT0014 oriented 69.5 x 57 x 20.5 mm leaves total dimensional allowances of **10.5 x 7 x 5.5 mm** (5.25/3.5/2.75 mm per side if centred). These allowances must accommodate cradle, insulation, restraint and tolerances. The 100 ±5 mm lead and connector are outside the body envelope and need routing space. This is a box comparison inside the existing reservation, not collision validation of a new cradle or proof of physical fit. Existing CAD remains unchanged.

BAT0015's best flat axis-aligned orientation is 75 x 69.5 x 20.5 mm: it exceeds the bay's 64 mm dimension by 5.5 mm before mounting allowances. It cannot simply replace the pack in that reservation. Investigating a wider bay/rearranged electronics could preserve the outer shell, but has not been geometrically validated. Relative to BAT0014 it adds 33.3% nominal energy for £10, with more packaging work.

An alternative [Soldered 10000 mAh pouch pack](https://soldered.com/products/li-ion-battery-10000mah-3-7v) lists 100 x 60 x 11 mm: it exceeds the existing 80 mm body length and no UK-stock consolidation advantage was established. Ordinary USB power banks were not promoted: low-load shutoff and charging handover need explicit support, and their casing/ports change the layout.

## Charging and connector findings
The BAT0014 [PKCELL datasheet, 2020-05-13](https://cdn.shopify.com/s/files/1/0174/1800/files/ICR18650_10050mAh_3.7V_20200513.pdf?v=1595581299) gives 4.2 V charge voltage and 3 A maximum continuous charging/discharging. Its page 9 drawing was rendered and visually checked: maximum 69.5 x 57 x 20.5 mm, 22 AWG leads, JST-PHR-2P marked “reverse”. **Connector family alone does not establish matching polarity**; compare keyed orientation with the charger and meter-check the delivered pack before connection. Capacity is tested down to 2.5 V, whereas Pimoroni advises avoiding discharge below 3.0 V; do not equate nameplate Wh with usable system Wh.

The [13,400 mAh drawing](https://cdn.shopify.com/s/files/1/0174/1800/files/ICR18650_13400mAh_3.7V_20200513.pdf?v=1595581299), page 9, was also rendered and checked for the dimensions above.

**BQ24074 timer uncertainty resolved for the published board:** Adafruit's [Eagle schematic](https://github.com/adafruit/Adafruit-BQ24074-PCB/blob/master/Adafruit_BQ24074.sch), fetched with blob SHA a97e12c1628a74e95eb0af333206ff6f3706126c, connects X4/TMR to GND. [TI's BQ24074 datasheet](https://www.ti.com/lit/ds/symlink/bq24074.pdf) specifies that this disables the charge safety timers. Therefore the published Adafruit design does not have the fixed six-hour cutoff that disqualified BQ25185. This is a source-netlist finding; confirm the delivered board revision. It does not establish thermal or full charging-system performance. Normal charge termination is a separate function.

At 1 A, capacity/current is 10.05 hours for BAT0014; at 1.5 A, 6.7 hours. These are ideal charge-throughput figures, not full-charge predictions: taper, actual discharge endpoint, thermal regulation and operating load matter. BQ24074 input current is shared with the running controller, so a 1.5 A setting does not guarantee 1.5 A into the battery. Retain 1 A as initial evaluation setting; test charging temperature, termination and load sharing before increasing. Retain external NTC research and low-battery shutdown work.

No need to buy a larger converter simply because capacity rises: converter sizing follows the display's load peaks. Use the external charger/converter route, not the Waveshare onboard battery socket.

## Remaining checks
- Confirm connector polarity and charge/cutoff implementation.
- Fit a restrained BAT0014 envelope and lead route in the housing; inspect actual pack before final print.
- Measure charging, sleep, wake and recording loads with the selected display and converter.
- Recheck screen and supplier baskets together before ordering.

Energy ratios are calculated from nominal capacity at equal voltage. They are not a guarantee of 52% greater usable runtime or weeks of standby.
