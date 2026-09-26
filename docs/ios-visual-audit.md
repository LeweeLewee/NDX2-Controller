# Native visual correction — 26 September 2026

The user rejected B1 visual fidelity and authorized a complete native/reference comparison. B1 remains tagged and available; corrections continue on its isolated branch. The earlier statement that the visual review passed is superseded: functional tests did not establish reference fidelity.

## Comparison method

Use the revised 25-image reference set and compare at an equal 480-unit height, preserving aspect ratios. The old gallery incorrectly matched several states to older filenames and displayed native/reference images at different scales. Both faults are corrected. Presence is excluded. No reference is silently substituted to make a native result pass.

The native phone is wider than the 800-unit reference. Preserve full-bleed colour, the locked orientation, safe area plus 8 pt, enlarged transport targets, plain history-preserving Back, artist Tracks access and row/detail hearts. These accepted interactions remain explicit differences. The silent-demo marker remains. OS keyboard and trust/pairing behaviour stay native; no bridge routes, firmware, live audio or security settings change.

Typography: screenshot serif appears to be the browser's broader Times fallback, not the bundled Instrument Serif. Asked the user which takes priority; absent an answer during this pass, use the supplied screenshots as the visual target (Times New Roman / Arial, available on iOS). Original licensed bundled fonts remain intact. This choice is visible and reversible, not a claim that the screenshots used Instrument Serif.

## Initial findings and corrections

| Screens | Defect in B1 | Correction under review |
|---|---|---|
| Still, long title, stopped, missing artwork, wake | Oversized 64/100-unit text frames; oversized artist; weak vertical grouping | Measured title height, caps-15, compact 14-unit rhythm, block centred on artwork |
| Touched, paused, pending, unknown, offline | Metadata spread vertically; oversized glyphs; mic tangent to waterline; heavy next label | Compact top-aligned block; keep large targets but quieter glyphs; lift mic/navigation; caps Up next; rounded uncertain-volume outline |
| Album and track detail | Title vertically centred far below artist; facts/actions too low; track rows oversized | Top-aligned title; facts at 168 and actions at 212; 72-unit list rhythm with retained heart targets |
| Artist, long name and missing metadata | Name/kind too high, dense bio, bottom-clipped album sleeves, blocky portrait | Reference hierarchy; adaptive name/bio spacing, quieter bio, full sleeves above bottom; atmospheric fictional portrait; preserved Tracks and biography expansion |
| Find Idle and unavailable | Unbalanced single-line prompt, low mic, unstyled field | Balanced two-line prompt; mic at reference height; italic field |
| Listening, Ready, empty | Oversized glyphs, heavy reset ring, mismatched text silhouette | Reference typography and ring faces; centred ripples; explicit-submit lifecycle retained |
| Results and Library | Oversized filter/subtitle text, missing query rule, loose rows | 18-unit filters/subtitles, query hairline, 72-unit row rhythm |
| Queue | Repeated identical sleeves obscured depth; type mismatch | Distinct procedural reference-style sleeves through existing normalized preview path; shared type correction |
| Settings and Display | Over-bright utility field; oversized type; unclear timeout wording | Reference field intensity; shared type correction; clear screen-off wording |
| Connection, Device, Wi-Fi, Pairing | No supplied render; inherited type/field inconsistency | Same utility typography and field; preserve wording, authenticated recovery and native controls |

Fixture art is procedural and fictional, transcribed from the supplied HTML compositions. iOS fixture vectors still pass through the real Contract artwork normalization/chunking. No external photos or provider claims are introduced.

## Validation

Pending fresh native build, screenshot-by-screenshot review and final internal release. Do not infer visual acceptance from geometry tests alone.

## Visual correction follow-up — 26 September 2026

The user rejected the prior visual result. Functional success at `85628f2` remains valid for that source, but does not establish design acceptance. Corrections are implemented on the isolated B1 branch and remain unverified natively. Fresh local checks passed 150 Python tests, five navigation tests, six silent authenticated TLS demo stages, project generation and fixture generation. Subsequent changes are Swift layout/test adjustments only.

[Run 36232443600](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36232443600), source `a73fe4e`, was cancelled by the replacement push during native tests. Its tiny export artifact is not validation evidence. [Run 36232563391](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36232563391), source `3a0312a`, failed before any runner or steps started. Check annotation: “The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings”. This is an external build blocker, not a compilation result. No billing settings were changed.

Native compilation, geometry tests, fresh screenshot comparison and an updated internal release remain pending. TestFlight 0.1.0 (6.1.0) remains unchanged. See [visual audit](ios-visual-audit.md).
