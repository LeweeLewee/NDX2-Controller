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

## Initial validation state (historical)

At the first checkpoint, a fresh native build, screenshot-by-screenshot review and final internal release were pending. Do not infer visual acceptance from geometry tests alone.

## Visual correction follow-up — 26 September 2026

The user rejected the prior visual result. Functional success at `85628f2` remains valid for that source, but does not establish design acceptance. Corrections are implemented on the isolated B1 branch and remain unverified natively. Fresh local checks passed 150 Python tests, five navigation tests, six silent authenticated TLS demo stages, project generation and fixture generation. Subsequent changes are Swift layout/test adjustments only.

[Run 36232443600](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36232443600), source `a73fe4e`, was cancelled by the replacement push during native tests. Its tiny export artifact is not validation evidence. [Run 36232563391](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36232563391), source `3a0312a`, failed before any runner or steps started. Check annotation: “The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings”. This is an external build blocker, not a compilation result. No billing settings were changed.

Native compilation, geometry tests, fresh screenshot comparison and an updated internal release remain pending. TestFlight 0.1.0 (6.1.0) remains unchanged. See [visual audit](ios-visual-audit.md).


## First native correction review

GitHub's billing blocker cleared on the user's requested retry. Run 36233599779 compiled `4cf422f` and exported 43 native captures, but failed the snapshot gate (caption height and artist target separation) and one full-phone launch/termination check. Artifact 10903148808 was verified against SHA-256 `504e33bd686157ce0bae208f4acf3f7ea7ef05f25ac5c2310c49ee73efd01462`. All 43 exported captures were visually inspected. The missing three phone captures must be recovered by a passing full-phone run.

Visual inspection additionally exposed overlap for the long track title and long artist name. The measurement paragraph used truncation and therefore underestimated wrapped height; wrapping must be measured before the visible line limit. The test measurement now uses wrapping too. Caption height and artist target spacing were corrected without weakening minimum targets or gaps. Missing-portrait Follow is separated from the album/track selector; missing biography retains the simple left-aligned action. The pairing address prompt uses the theme ink explicitly.

Observed limitations retained: RGB565 artwork has visible colour banding and the 80-pixel queue sleeves are softer than browser art; these remain within the existing bridge format. Fixture text/data are fictional and may differ from reference titles. Native keyboard chrome, safe perimeter, larger transport targets, track hearts and plain Back are deliberate differences. Full-phone captures include the perimeter, so only inlay captures provide equal-content-height comparison. A passing rerun and fresh review remain required.


## Passing native rerun

[Run 36234432936](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36234432936), source `5e78b5f722bd16a80c44aa831c072b407c8f8f7d`, passed all 28 native tests (24 unit/snapshot/wire and four full-phone interaction tests) with zero failures, followed by a successful unsigned iOS-device archive. The intervening `fa2be86` run was cancelled when the visually discovered wrapping fix superseded it; it is not a pass. Fresh rendered review and release are tracked below.

The gallery now fits comparison columns at the native/reference width ratio, with aligned image tops and a full-pixel option. Browser automation's URL policy prevented opening the new local gallery; inspection uses the native PNG files directly, not a browser-rendered substitute.


## Final simulator visual review

Successful artifact `10904305394` (`still-water-ios-21`, 65,455,673 bytes) was verified against SHA-256 `4fbc064fb1934bd241f99836289c00147fd3cb0e2e37b39f132dcd710956aba7`. The gallery is `local/ios/review-b1-visual/review.html`, retaining all 46 original native captures and the exact source identity. Its ten changed/new captures were inspected directly: long track title, long artist name, artist following/no-bio/no-portrait/tracks, full-phone artist tracks, full-phone album actions, full-phone NOW and keyboard. The other 36 images are pixel-identical to the already inspected first-run captures. Text overlaps are resolved, album sleeves clear the edge, retained controls are separated, and full-phone background/safe areas remain intact.

This is a completed engineering visual review for the internal trial, not user design acceptance or exact pixel identity with an 800-wide browser reference. The screenshot-first Times/Arial assumption remains explicit. The native pairing address still renders system-blue despite its explicit prompt styling; this utility has no supplied reference, and its trust/recovery behavior is retained. Artwork banding/soft queue previews, native keyboard chrome and fixture-content differences remain documented limits. No live playback, volume, NDX, speech, bridge routes or firmware were changed or tested.

Tag `ios-preview-2026-09-26-b1-visual` points to the tested source. [Internal release run 36235235938](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36235235938) completed successfully: repeated native validation, signing and upload passed. Apple processing completed and **0.1.0 (7.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group, with status **Testing**. Release artifact `10904386131` (65,410,557 bytes) was downloaded and verified against SHA-256 `9c2f040628353880234e2d80d710d806bacbd51d7998fc4d0966cb340b4d910b`.


## User follow-up: shared outer boundary (open)

During the upload, the user identified an inconsistent boundary across secondary pages, using Now Playing's Silent Demo label as the anchor. Confirmed in the latest tested source: the marker is at x48/y24 on NOW and x48/y6 everywhere else. The shared header title is at y30, so simply moving the marker would collide with it; the secondary header/content band needs refactoring together. This was missed in the earlier visual review and is not fixed in build 7.1.0.

Affected: Up next; Find Idle/Listening/Ready/Results and typing header; Library; album/track details; all artist variants; Settings, Display, Connection, Device, Wi-Fi and Pairing. Artist portrait decoration needs boundary review too. NOW supplies the reference boundary and should remain the layout anchor.

Verified: the latest work did not alter KioskHost positioning, Design.fit, system safe-area handling, the extra 8-point inset or the x48 primary text anchor. The entire design has not been shifted left into the iPhone 11 notch area. Only the colour field ignores the device safe area. The requested follow-up is confirmation and affected-screen identification; this record does not claim a new alignment implementation or another release. Preserve the left exclusion zone in any subsequent shared-header refactor.


## Shared boundary and accumulated testing amendments

The user completed testing and authorized implementation on 26 September. The shared marker is now x48/y24 across every screen; secondary headings and contents are adjusted together. This supersedes the open implementation item above, but 7.1.0 itself remains unchanged. The safe-area container and left exclusion zone remain unchanged. See [Brief B.1 amendment](ios-b1-amendment.md) for implementation, all validation, remaining release status and the other queued changes.


Final native source `0f9ecc6e1a2b9a9e4c49b614ff43edf2150fba41` passed all **30 native tests** and the unsigned device archive in [run 36247170788](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36247170788). Artifact `10908186354` (70,022,280 bytes) was SHA-256 verified: `2d83eb9cae1f086a41d375e77f93700fc888a7bc278b6ab453ce98dcba7d142f`. The final gallery is `local/ios/review-b1-amendment/review.html`, with 50 captures: eleven changed captures were inspected directly and 39 are pixel-identical to the first reviewed amendment. Artist underline, portrait fade, seeded playlists, queue and full-phone alignment were checked. This remains simulator visual evidence, not mounted-phone acceptance.

[Release run 36248128881](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36248128881) repeated all 30 native tests and archive checks, then signed and uploaded **0.1.0 (8.1.0)**. Apple processing completed; assignment to the existing **Naim NDX2 Controller TestFlight** group is verified with status **Testing**. Tag `ios-preview-2026-09-26-b1-amendment` remains at reviewed source `0f9ecc6e1a2b9a9e4c49b614ff43edf2150fba41`. Phone installation and acceptance of this amendment remain unverified.
