# iPhone aperture fit sample v1

27 September 2026. Open, hand-supported sample for the accepted **138.9 × 63.7 mm / R3 aperture with 6 mm overlap**. Original 01 River Stone remains the exterior reference; this test fixture does not define the stone silhouette.

![CAD rear view](sample-preview.png)

## Files and printing

- [Frame STL](aperture-frame.stl) / [STEP](aperture-frame.step).
- [0.4 mm spacer gauge](spacer-0.4mm.stl) and [0.8 mm spacer gauge](spacer-0.8mm.stl). Duplicate four of the chosen thickness in the slicer. Do not mix thicknesses.
- [Solid checks](validation.json) / [STL checks](mesh-validation.json).

P1S with 0.4 mm nozzle. Trial starting point: familiar plain PLA, 0.2 mm layers, three walls, front face flat on the bed as exported. Use the normal profile for the actual filament and plate. Inspect sliced layers and spacer adhesion. No slice, time estimate or G-code is validated here.

Frame: 170 × 95 × 5.2 mm. Lip: 1.2 mm. Both short ends and the back remain open. Two long-edge stiffeners have a 79 mm inner gap versus nominal 75.7 mm phone width. They are not locating jaws or verified button clearances. Geometry is designed to grow from the flat flange without unsupported overhangs.

## Trial

1. Inspect for burrs, flatness and dimensional error before bringing the print near glass. Do not force the phone between rails.
2. Support the phone by hand from behind: **there is no retention**. Keep the rear camera, microphones, connector and buttons clear; do not rest the rear camera on a worktop.
3. Centre the accepted paper mask to register the opening. Select four spacer positions on the actual non-display perimeter, away from microphones, sensors and buttons. Positions are deliberately not fixed in CAD. Do not place gauges on active pixels. If safe positions cannot be established, hold the frame clear and report that before adding retention.
4. Compare 0.4 mm spacers (1.6 mm nominal glass recess including the lip) and 0.8 mm spacers (2.0 mm recess). Added protective film or padding increases the gap. Final recess remains unselected.
5. Check corner concealment, alignment, edge touch access and seated/oblique views. Keep cable plugs clear of microphone openings.
6. Compare bare-phone and sample-mounted voice recordings at the same orientation and distance using the intended app and existing Voice Memos/front/rear camera checks. Do not add continuous gasket or tape across inlets. An open back or narrow gap alone does not prove an unobstructed acoustic path.

Production retention, screw stops, padded supports and acoustic passages follow actual hardware mapping. This sample tests aperture/lip access and rear-loading space; it is not a finished cradle and does not validate the eventual closed stone's acoustics.

## Verification

Three valid CAD solids; zero intersection between accepted aperture cutter and frame. All three STL meshes are watertight, consistently wound, single-component and fit within 256 mm. Preview comes from actual CAD tessellation. No physical printing or voice test claimed.

Reproduce with tools/iphone_mount_sample.py --deps followed by the CadQuery dependency directory; tools/check_iphone_mount_sample.py --deps followed by the trimesh directory; and tools/render_iphone_mount_sample.py. Python 3.12 with CadQuery 2.8, NumPy/Pillow and trimesh was used.
