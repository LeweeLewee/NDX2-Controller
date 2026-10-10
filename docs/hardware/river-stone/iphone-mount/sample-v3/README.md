# Printed v3 reference — historical R3 aperture

User reported snug-frame-0p20 printed and fit perfect on 28 September 2026. Adopt **0.20 mm per side**. Files here are the supplied original R3 models, preserved as history; do not use their R3 opening for new enclosure work. The print exposed inactive display at all corners. The derived R6.5 correction is in [v3r1](../sample-v3r1/README.md), with no repeat body-fit print required.

The supplied validation.json and reference-check.json contain CAD-derived results and pre-print status wording. These are imported evidence, not checks rerun here. File provenance is recorded in import-manifest.json. The later physical pass supersedes their unprinted status only for 0p20 body fit; it does not validate the other variants, retention, acoustics or charging temperature.

Original source scripts are retained under tools/iphone_v3_reference. They depend on outline_pts.json, phone.brep and phone_mesh.stl caches not supplied in the package. The corrected revision instead uses the exact supplied 0p20 STEP, avoiding reconstruction of the passed body outline. The community phone reference itself is not redistributed.
