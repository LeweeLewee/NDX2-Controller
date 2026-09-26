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

Native compilation, full snapshot matrix and interaction results are pending. Do not infer TestFlight availability or physical acceptance from local tests.
