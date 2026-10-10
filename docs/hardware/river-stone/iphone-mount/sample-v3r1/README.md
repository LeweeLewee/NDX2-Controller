# V3r1 — R6.5 aperture correction

The supplied printed 0p20 v3 body fit passed. This separate revision changes only the four aperture corners from R3 to R6.5, keeping 138.9 × 63.7 mm bounds and the exact passed body walls. It is **unprinted**; the original R3 files remain in sample-v3.

The generator imports the supplied 0p20 STEP and adds only the four 1.2 mm thick corner regions. It verifies no original solid volume is removed, no wall volume above the lip changes, and the R6.5 aperture is clear. See validation.json and mesh-validation.json for executed checks.

[Corrected STEP](snug-frame-0p20-r6p5.step) · [Corrected STL](snug-frame-0p20-r6p5.stl)

No repeat body-fit print is required. Use the corrected geometry in the next enclosure; verify corner concealment there. Microphone, retention, thermal and final recess checks are outstanding. Reuse existing spacers as appropriate.

Reproduction: tools/iphone_mount_sample.py --revision v3r1 --deps <CadQuery directory>. Validation: tools/check_iphone_mount_sample.py --revision v3r1 --deps <trimesh directory>. The dedicated tools/iphone_mount_v3r1.py performs the exact STEP correction; it needs no unavailable outline cache or redistributed phone model.
