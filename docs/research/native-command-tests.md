# Native control tests — 20 September 2026

These results are observations on API 1.4.0 / firmware 3.11.0.5662, not a vendor API guarantee. References below must come from the device, not arbitrary user-supplied URLs.

| Operation | Request | Observed result |
| --- | --- | --- |
| Collection | GET /inputs/tidal/favourites | Albums, artists, tracks and playlists |
| Collection page | GET /inputs/tidal/favourites/albums?offset=2&limit=2 | Two successive albums and totalCount |
| Play album/playlist | GET /inputs/tidal/{albums,playlists}/{id}?cmd=play | Replaces native queue, starts first track |
| Append track | GET /inputs/tidal/tracks/{id}?cmd=playLast | Count increments, track appears last |
| Insert next | GET /inputs/tidal/tracks/{id}?cmd=playNext | Track appears after current, playback not interrupted |
| Move queue item | GET /inputs/playqueue?cmd=move&what={queue-reference}&where={queue-reference} | Moves item before destination |
| Remove queue item | DELETE /inputs/playqueue/{id} | Item disappears, count decrements |
| Select queue item | PUT /inputs/playqueue?current={queue-reference} | Current reference changes and selected track starts |
| Transport | GET /nowplaying?cmd=next, prev, pause, resume, stop | Expected track/state changes after asynchronous delay |
| Seek | GET /nowplaying?cmd=seek&position={milliseconds} | Near-end seek followed by automatic next track |

Query values must be URL-encoded. Native TIDAL queue children have class object.track.tidal; now-playing identifies inputs/playqueue with sourceDetail=tidal. No audio data was requested or served by the controller process.

State reads immediately after commands can be stale. Observe the queue and playback after a bounded delay. Queue IDs change when replacing a queue; never reuse stale IDs across replacements. This firmware returned the entire queue despite a limit query. Collection pagination does respect offset/limit.

## Open investigations

- Catalogue search: tested GET variants using query, search, q, term and value, and guessed nested search paths, returned 400. An app request or vendor specification is needed to establish syntax; no supported search function is claimed.
- Quality resolved for 24-bit: the user corrected High to Max in the Naim app. Native bitrate changed from lossless to losslessHd. Replaying the identical native track through cmd=play returned FLAC 24-bit/44.1 kHz with error=0. Higher sample rates remain untested.
- Amplifier: automation.enabled=1, but the actual System Automation command remains unidentified. A live PUT /levels/room test changed readback 13 → 5 → 13 while music played; the user confirmed no audible volume change. Do not use that endpoint as amplifier control in this setup. Output mode was unchanged, level restored and playback stopped. Volume remains excluded from the client.
- Queue selection passed: selecting a returned second-track queue reference started that track and changed current. A subsequent stop was confirmed.
- Automatic transition passed. Audible gaplessness, prolonged playback, token renewal, app concurrency and actual network outage recovery remain unverified.

## Reference-code leads

On 20 September 2026 the current [official TIDAL OpenAPI schema](https://tidal-music.github.io/tidal-api-reference/tidal-api-oas.json) describes GET /searchResults with filter[query], countryCode and include, and GET /searchResults/{id}/relationships/{type} with page[cursor]. The result ID is opaque, unlike the search-text path in older examples. These endpoints list client-credentials access for third-party applications. The prototype follows that schema, but has only been tested with synthetic responses. Token acquisition follows TIDAL's documented client-credentials flow; no Naim token is reused.

The user-assisted app capture showed connections to api.tidal.com alongside local NDX library searches (/albums, /artists, /tracks and /descriptors). It did not expose the encrypted TIDAL request contents or an amplifier command. A separate metadata adapter is therefore a candidate for catalogue search. [TIDAL's authorization documentation](https://developer.tidal.com/documentation/api-sdk/api-sdk-authorization) permits catalogue access using an application's client credentials. [TIDAL's SDK search example](https://github.com/tidal-music/tidal-sdk-web/blob/main/packages/auth/examples/shared.js) demonstrates searchResults relationships. This would require our own developer application credentials and a live ID-to-native-reference test. It would handle metadata only; all playback would still be delegated to native Naim references. No TIDAL developer app has been registered or credentials provisioned in this project.

[M4rque2/Naim-App-Reversed protocol notes](https://github.com/M4rque2/Naim-App-Reversed/blob/40e09315504595923d78b7aafa74ee5d2376559a/PROTOCOLS_DETAILED.md) and [tekul/mina API implementation](https://github.com/tekul/mina/blob/323ed65a3ca0e16890a3bf6161d78d2bd7e6f184/src/api.rs) supplied command leads. Those projects are not authoritative Naim specifications; live tests establish the claims above. No source code was imported from them. Their generic UPnP media construction is not used.
