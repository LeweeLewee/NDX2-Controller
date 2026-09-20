# Power budget and hardware validation

No hardware measurements yet. All checks below are pending; software tests do not validate electronics.

## Energy model

Use Wh to compare packs and loads at different voltages:
- Nominal pack Wh = nominal voltage x Ah.
- Usable Wh = nominal Wh x usable-capacity fraction x conversion efficiency.
- Daily energy = active W x active hours + idle W x idle hours + standby W x standby hours + wake energy.
- Runtime days = usable Wh / daily energy.

Use measured battery-side energy where possible; if measured there, do not apply converter losses again.
Record battery-side and USB-side measurements distinctly. Include converter/charger quiescent draw, touch sensing, LEDs, radio, self-discharge and startup peaks as applicable.

## Illustrative sizing only

Assume a 3.7 V pack, combined usable-energy factor 80%, and 2.25 W active load (manufacturer's 5 V / 450 mA reference; not a tested application value).
For 28-day pure standby, with no active use:

| Nominal pack | Usable energy under assumption | Maximum average load for 28 days | Continuous active equivalent at 2.25 W |
| --- | --- | --- | --- |
| 5,000 mAh | 14.8 Wh | 22.0 mW | 6.6 h |
| 10,000 mAh | 29.6 Wh | 44.0 mW | 13.2 h |

At 30 minutes/day at 2.25 W, active use alone consumes 1.125 Wh/day. The 10 Ah scenario then provides at most 26.3 days even with zero standby/wake consumption. Four weeks is an illustrative scenario, not the agreed target. Large battery size cannot replace a usage profile or measurement.

## Bench sequence

1. **Identity and fit:** photograph/record SKU and PCB revision, verify display and connector dimensions, map schematic sources. Record public results here; private photos/receipts can remain in local/.
2. **USB-powered screen test:** verify colour/artwork, touch edges, keyboard, scrolling, repeated controls, low brightness, viewing angle and touch stability. No audible Naim tests run automatically.
3. **Power states:** measure boot peak, Wi-Fi reconnect, active browsing at several brightness levels, connected idle, backlight off, deep sleep with touch sensing, and storage off. Capture both steady current and wake energy.
4. **Wake:** repeat touch wake after short and overnight idle; confirm first touch behaviour, fresh now-playing retrieval, Wi-Fi outage recovery and no unintended playback action. Compare measured delay with agreed target.
5. **Power route:** select route only after revision-matched connector/polarity and charging-path checks. Test regulated voltage at startup and low battery, charger plug/unplug and concurrent use. Measure charge duration and component/pack temperature inside a representative housing.
6. **Battery:** verify pack spec, usable energy and low-voltage handling. Implement warning and controlled shutdown before protection cutoff. Test recharge recovery and absence of repeated brownout loops.
7. **Enclosure:** check screen support, strain relief, service access, battery restraint, antenna clearance, heat, grip and tilt stability. Only then fix BOM quantities and final CAD.
8. **Daily use:** log real active/idle time and consumption over a representative period; reconcile predicted and observed runtime.

Touch wake is not proven by a controller having an interrupt pin. It requires retained power, compatible interrupt routing and working firmware in the chosen sleep state.

## Measurement record template

| Date / tester | HW-001 revision | Firmware commit | Power route / pack | State / brightness / Wi-Fi | Measurement point / instrument | Duration | Average / peak / energy | Wake delay / result | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Update [evidence](../evidence.md) only when tests establish or disprove a claim. Do not mark the hardware milestone complete from datasheets, purchase or a successful display demo alone.
