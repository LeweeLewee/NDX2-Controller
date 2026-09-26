# Still Water B1 implementation and validation

Branch `codex/still-water-b1` starts from D034 `66ec6fd`. The earlier branch/tag and dirty primary checkout are preserved. User authorization: proceed after the B1 review, 26 September 2026. D035 records this refinement without changing D030 or D029.

## Source reconciliation

Use the revised 26 September repository spec and references. The supplied prompt's first Find filenames are stale; current names are 18-find, 08-ask, 09-ready and 19-results. Portrait/album references are 22-artist and 21-detail. Earlier references remain historical. Reference-only microphone diagnostic footers are omitted.

Keep the full-screen colour field, system safe area plus 8 pt and landscape-right lock. The 800-unit reference coordinates adapt to the 1048 canvas. Large transport targets and 8-unit minimum separation take priority over conflicting literal positions. Plain Back preserves history and discards recording/input. Keep direct artist Tracks selection when returned and row/detail likes; row taps retain detail navigation with explicit Play, avoiding an unexpected playback side effect from browsing. No NOW heart or gear remains. Settings is a 700 ms background hold with an accessibility action; controls do not invoke it.

Find has Idle, Listening, Ready, Results. Ask starts Listening; Find starts Idle. The square stops; the arrow alone submits speech; reset clears and records again. Back discards. Default-on Stop on silence is in Settings > Device and persists independently of the older display record. After speech, 2 seconds without detected audio activity stops to Ready; 30 seconds also stops without searching. Fixture speech/silence uses the same model clock. Native audio activity uses a conservative RMS threshold and requires recognized text before silence can end recording; room/microphone calibration remains a physical trial. The distributed preview refuses real speech and live transport.

Artist has an original fictional portrait study in the fixture. Real missing portrait/bio/albums disappear rather than becoming placeholders. A four-line biography expands to a scrollable view; Follow and album membership pills show pending/unknown states. Album facts use available metadata only. Primary artwork, portraits and artist album covers assemble 320 chunks; queue lists and palette extraction retain 80 previews.

`artist_bio` uses exact catalogue artist relationships under the existing authenticated envelope. HTML stripping and Unicode/response bounds are tested. The public TIDAL reference lists biography and profileArt relationships, but its linked OpenAPI JSON returned 404 during this implementation; provider access/field acceptance has not been tested against a live account. Missing metadata degrades honestly. No live playback/volume/NDX or firmware/HTTP-route changes.

## Validation

Local: 150 Python tests, five navigation tests, six silent TLS demo stages, generated project and Python-contract fixture checks passed. The demo now also reads artist biography and a registered 320 portrait. Windows protected vault/TLS tests required normal host execution; safeguards were not weakened. Font licence line endings are pinned to LF so byte-exact manifest hashes work in Windows checkouts.

[Native run 36229392996](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36229392996) passed all **28 tests**, none failed or skipped, and the unsigned iOS-device archive at `85628f204f953453f38f0a8a159ae0f215f4ee27`. This comprises 14 controller, two preview, two snapshot, six wire and four full-phone UI tests. Xcode 26.3 / iOS 26.2 SDK; iPhone 11 simulator running iOS 18.6 on macOS 15.7.9. Earlier failures (two missing method separators in tests and a misplaced metadata assignment) were corrected without weakening the gate.

Artifact `10902137813` (`still-water-ios-16`, 66,557,540 bytes) was downloaded and its SHA-256 verified: `c19f0911fd911edc9083235b9a527903712dc085e00290a00032235eca1b8c37`. The original ZIP and 46 native captures are retained in ignored `local/ios/`; gallery `local/ios/review-b1/review.html`. Every changed capture was visually inspected; unchanged captures were compared byte-for-byte with the earlier reviewed matrix. Review includes full-phone safe area/keyboard, enlarged transport, album hierarchy, artist Tracks and expanded/missing/long-name variants, voice Idle/Listening/Ready/empty states and uncertain volume feedback. This is simulator evidence, not mounted-phone acceptance.

## Internal distribution

Tag `ios-preview-2026-09-26-b1` points to the tested source above. [Signed workflow 36230634817](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36230634817) passed native validation again, then archived, signed and uploaded **0.1.0 (6.1.0)** successfully at 08:51 UTC on 26 September. The original validation and upload logs are retained privately. Apple processing completed; **0.1.0 (6.1.0)** is assigned to the existing **Naim NDX2 Controller TestFlight** group and Apple shows **Testing**. No tester or account permissions changed. The prior 5.1.0 build was observed Ready to Test without a group; B1 is the delivered replacement.

The release workflow again passed all 28 native tests. Its evidence artifact `10902269009` (`still-water-ios-6`, 66,523,726 bytes) is retained byte-for-byte with verified SHA-256 `56a5f119a42daddbeb8de4e5245bfab431c51ed5bf65d9cbc2637fdb8aa6062a`. Its archive JSON describes the unsigned validation job; the separate successful signing/upload job and observed Apple Testing state prove distribution. Source is identical to the visually reviewed gallery.

## Phone review

- Open Find with the search icon: it is idle. The centre-foot Ask microphone starts simulated listening immediately.
- Stop with the square, or let default-on Stop on silence end the simulated phrase. Search only with the up arrow. Reset clears and listens again; Back discards.
- Type in the foot field, then use the search icon or keyboard Search. Results support editing and preserve explicit submission.
- Open album/artist details; test library/follow states, track hearts, Albums/Tracks and expanding/closing the biography. Fixture artwork and biography are fictional.
- Hold a non-control area of Touched for 700 ms to open Settings; Stop on silence is under Device.

Physical speech, provider metadata acceptance, mounted readability and user design acceptance remain open. Presence was excluded and is not queued.
