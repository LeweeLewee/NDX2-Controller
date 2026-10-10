# River Stone curved shell — working checkpoint

10 October 2026. **Not released for full-shell printing.** Based on original 01, iPhone 11 and UGREEN 25683. The passed v3 0p20 body fit is retained, with derived, unprinted R6.5 aperture corners.

The candidate integrates the mounting frame into a curved shell, with two removable rear keeper bars and an underside bank cover. Four padded bank supports and two strap paths allow bank removal before phone service. Proposed keeper screws close against hard stops; foam thickness and preload are provisional until the spacer used for the passed fit is confirmed. Feet, cable routing and bank-port access are unfinished.

Bounds are approximately 211.1 × 145.3 × 105 mm, versus the earlier 210 × 145 × 102 mm packaging proposal. Curved lofts and spline overshoot account for the difference. The cavity uses radial profile insets, not a verified constant wall thickness. Print orientation/support and wall-depth checks remain open.

## Verification and export limitation

The internal indexed shell mesh reports one watertight component. **Reloading the exported shell STL reveals a nonmanifold edge**, so internal validity must not be represented as a successful print-file check. The actual community-phone collision and sampled removal checks are blocked by this export defect. Resolve it and rerun those checks before release. A conservative rectangular phone proxy overlaps the shell at rounded features and is not a fit pass or failure.

Internal mesh Boolean checks found zero bank-body, bank-bay, cover and camera-reservation overlap with the shell. Keeper interference values below 0.0001 mm³ are numerical-scale contacts, not a physical retention test. These checks do not establish assembly access, pressure on the phone, acoustics or temperature.

Acoustic channels are proposed at the notch, Lightning end and rear-camera area. Their geometry is not proof that microphone pickup is unobstructed in the assembled enclosure. Keep gasket interruptions and verify pickup physically.

Final shell/cover/keeper geometry is mesh-based STL/GLB. The two STEP files contain editable outer/inner loft sources only; **there is no fused final STEP or native Fusion model**. Preview meshes are reproducible with the generator.

## Small hardware coupon

`keeper-coupons.3mf` contains an M3 side-entry nut-pocket block and separate clearance-hole bar. It tests hardware fit only, not phone clamping. Individual STEP/STL sources are supplied. Provisional slicing: P1S, 0.4 mm nozzle, Generic PLA, textured PEI, 0.2 mm layers, three walls, 15% infill, no supports. Estimate: **17 min 36 s, 2.86 g**. Toolpaths at the base, pocket, roof and top were inspected.

The embedded 3MF reports `bed_temperature_too_high_than_filament` (1000C001) from the inherited 55 °C Generic PLA profile. Review the actual filament/bed settings in the slicer before printing. No printer was contacted and no physical nut fit is claimed.

## Cable measurement update

User supplied **18 mm L × 8.25 mm W × 5.25 mm H** on 10 October. Length is interpreted against the preceding request: plugged-in phone edge to flexible cable, including strain relief. The source generator now reads `../cable-measurements.json` and reserves a 20 × 10.25 × 7.25 mm plug cut (1 mm clearance beyond the end and around the sides, plus 1 mm cut overlap into the phone-end reservation). The bend-space placeholder follows the measured cable start; cable diameter and bend behaviour remain unknown.

**Existing STL/GLB/STEP study outputs and validation predate this measurement and have not been regenerated.** Resolve the export defect and regenerate/check the model before relying on the new cable geometry. The historical compact-layout outputs retain their original assumptions.

## Inputs still required

- Cable diameter and bend space.
- Bank port being used and cable exit position.
- Whether 0.4 mm, 0.8 mm or no spacers were used in the passed fit.

Keep cable and pad dimensions adjustable. Do not repeat the already passed phone body-fit trial solely for these changes.
