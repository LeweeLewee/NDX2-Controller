# Evidence ledger

Last updated: 19 September 2026.

| Claim | Status | Evidence / limitation |
| --- | --- | --- |
| NDX 2 local API reachable | Observed | HTTP 15081; API 1.4.0, firmware 3.11.0.5662 |
| Native TIDAL enabled | Observed | Native input returned; supportsTidalMax=1 is capability metadata, not a playback-quality test |
| TIDAL favourites available | Observed | Native favourites include playlists, artists, albums and tracks |
| Native content browsing | Observed | Playlist returned 50 tracks; artist returned albums; albums returned tracks |
| Native single-track launch | Observed | Returned track reference plus cmd=play caused native queue and advancing playback |
| Native source identification | Observed | sourceDetail=tidal and queue class object.track.tidal |
| Audio carried by our test process | None | Process made JSON requests only; no audio fetch, decode or relay |
| Audible output / packet-level cloud route | Not independently checked | Device state supplied the playback evidence |
| Playback quality | Observed for one track | FLAC 16-bit/44.1 kHz; high-resolution selection remains untested |
| Stop behaviour | Observed, asynchronous | Immediate read stale; subsequent state=1, position=0, no longer active playback |
| Amplifier control | Not tested | levels/room read 13 before and after; no volume command sent |
| Full catalogue search | Unresolved | Three exploratory read requests returned 400; correct syntax unknown |
| Album/playlist launch and queue edits | Not tested | Browsing succeeded; no full queue workflow demonstrated |
| Long-term reliability and app coexistence | Not tested | Only a brief playback trial |
| Home Assistant reachable | Observed | Recognized page, HTTP 200; no login/configuration changes |
| ESP32 implementation | Not built | Computer-side HTTP prototype only |
| Battery and display performance | Not measured | Hardware not selected |

## Test conditions

The native playback trial began with no current music and an empty queue. It selected Eternity by Alex Warren from a previously returned album listing. The NDX reported error 0, playing state 2 and advancing position. A stop was sent after approximately nine seconds of polling; the later state showed the transition had completed. The test left one item queued and made no volume adjustment.

Filtered live JSON reports are retained locally under ignored `local/evidence/`. They are intentionally not committed because they contain personal listening metadata. The committed record summarizes the evidence without account data. The original one-off scripts remain outside this repository; only the reusable read-only probe has been imported.

## How to update this ledger

Record date, firmware, initial state, exact operation, observed result and final state. Distinguish API acknowledgement from actual state change. Link sanitized fixtures or local report filenames as appropriate. Never mark a capability complete solely because an endpoint exists or returned HTTP 200.
