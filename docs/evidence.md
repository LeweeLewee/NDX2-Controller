# Evidence ledger

Last updated: 20 September 2026.

| Claim | Status | Evidence / limitation |
| --- | --- | --- |
| NDX 2 local API reachable | Observed | HTTP 15081; API 1.4.0, firmware 3.11.0.5662 |
| Native TIDAL enabled | Observed | Native input returned; supportsTidalMax=1 is capability metadata, not a playback-quality test |
| TIDAL favourites available | Observed | Native favourites include playlists, artists, albums and tracks |
| Native content browsing | Observed | Playlist returned 50 tracks; artist returned albums; albums returned tracks |
| Native single-track launch | Observed | Returned track reference plus cmd=play caused native queue and advancing playback |
| Native source identification | Observed | sourceDetail=tidal and queue class object.track.tidal |
| Audio carried by our test process | None | Process made JSON requests only; no audio fetch, decode or relay |
| Audible output | User confirmed | Music was audible during the volume trial; packet-level cloud route not independently checked |
| Playback quality | Observed at 24-bit/44.1 kHz | User corrected Naim app setting from High to Max; API changed lossless to losslessHd. Same native track command then returned FLAC 24-bit/44.1 kHz, playing state, error=0 |
| Stop behaviour | Observed, asynchronous | Immediate read stale; subsequent state=1, position=0, no longer active playback |
| Amplifier control | Unresolved; levels/room failed audible test | Readback accepted 13 → 5 → 13, but user confirmed no audible volume change. This endpoint does not establish working amplifier control in the current setup |
| Full catalogue search | Unresolved | Exploratory GET query/path variants returned 400; correct syntax unknown. This does not prove search unavailable |
| Separate TIDAL metadata search adapter | Offline tested only | Current public API schema consulted; own developer credentials and live search-to-Naim ID verification still required |
| Collection pagination | Observed | favourites/albums with offset=0 and 2, limit=2 returned distinct successive pages and totalCount |
| Artwork retrieval and cache | Observed | Returned resources.tidal.com JPEG fetched (41,661 bytes), visually checked; second lookup reused cache. Host restriction, byte cap and eviction covered offline |
| Album/playlist launch | Observed | cmd=play populated native queues of 11 and 50 tracks and started first tracks |
| Queue append/insert/remove/reorder | Observed | playLast appended; playNext inserted after current; DELETE removed returned queue reference; move placed item before destination |
| Next/previous, pause/resume | Observed | Titles and current queue references changed; pause state=3 held position, resume state=2 advanced |
| Automatic track transition | Observed | Seek near end followed by automatic next album track, native source retained, error=0 |
| Audible gaplessness | Not verified | Two-second state polling cannot measure an audible gap |
| Controller reconnect | Narrow test passed | New client read current track and advancing position during playback; no network or device outage induced |
| Long-term reliability and app coexistence | Not fully tested | Native app comparison pending; no concurrent command stress or authentication renewal test |
| Home Assistant reachable | Observed | Recognized page, HTTP 200; no login/configuration changes |
| ESP32 implementation | Not built | Computer-side HTTP prototype only |
| Battery and display performance | Not measured | Hardware not selected |

## Test conditions

The native playback trial began with no current music and an empty queue. It selected Eternity by Alex Warren from a previously returned album listing. The NDX reported error 0, playing state 2 and advancing position. A stop was sent after approximately nine seconds of polling; the later state showed the transition had completed. The test left one item queued and made no volume adjustment.

Filtered live JSON reports are retained locally under ignored `local/evidence/`. They are intentionally not committed because they contain personal listening metadata. The committed record summarizes the evidence without account data. The original one-off scripts remain outside this repository; only the reusable read-only probe has been imported.

## Expanded live tests — 20 September 2026

The user explicitly authorized replacing sessions and using the NDX freely. Tests began with existing playback and a previous test queue. No amplifier volume, power, network or account setting was changed. Albums and playlists replaced the queue; queue edits were checked by subsequent listing rather than HTTP status alone. All returned queue entries remained object.track.tidal. The final automated transition test confirmed state=1 and position=0 after stop, leaving the test album queued.

Observed transport values on this firmware are 1=stopped, 2=playing, 3=paused. Seek positions and now-playing duration are milliseconds; browse-track duration is seconds. Queue limit was ignored, unlike collection pagination. Controller reconnection means recreating the client only, not recovery from an actual Wi-Fi outage. Whole-playlist loading was checked for one 50-track playlist, not a large multi-page playlist.

The reusable native client and explicit transition test now live in tools/. Twelve offline tests passed, covering native references, rejection of URL/parameter injection, response bounds, request methods, page bounds and transport values. Filtered trial and transition reports remain in ignored local/evidence/.

The quality discrepancy was resolved: the user corrected an earlier report and confirmed that the Naim app was set to High, then changed it to Max. API bitrate changed from lossless to losslessHd. Replaying the same native track reference with the unchanged cmd=play request returned 24-bit/44.1 kHz FLAC and error=0. The final quality test paused at position 2136 ms, state=3. Higher sample rates such as 96/192 kHz have not been demonstrated. No separate audio transport or controller-supplied stream URL was introduced.

An additional album remained 16-bit/44.1 kHz with Max enabled; Max does not imply every recording is high-resolution. Fifteen offline tests now pass including the bounded artwork cache. A temporary user-configured HTTP proxy captured Naim app reads and encrypted connections to api.tidal.com. HTTPS was not decrypted; no credentials or response bodies were recorded. No amplifier-volume command appeared. This is a lead for separate cloud metadata search, not proof that the NDX lacks a search endpoint. The proxy was stopped after the user finished.

Queue selection with PUT current also passed: the returned second-track reference became current and started playback. Final device state after that test was stopped (state=1, position=0), with the 17-track test album queued. Max was retained; no amplifier-volume command was sent by our scripts.

## Audible volume trial

The user authorized an audible volume comparison. With output mode unchanged, a native TIDAL track played while PUT /levels/room changed the reported setting from 13 to 11 and back to 13. Subsequent reads confirmed those values and advancing playback. Cleanup confirmed volume=13, mute=0, stopped state=1, position=0 and error=0. The user confirmed audible music but said the change was unclear. This result is inconclusive for amplifier control; it is not a pass or proof of no effect.

A second trial used a larger reduction, 13 → 5 → 13, without exceeding the starting setting. Readback confirmed each level; final state again showed stopped, position=0, volume=13, mute=0 and error=0. The user confirmed no audible volume change. This is a failed audible-control test for /levels/room in the current setup, not a failure of native playback or proof that System Automation is unavailable. Neither trial changed the fixed/variable output mode. Keep volume out of the implemented control client until the actual amplifier command is identified and verified.

### Capture-only recorder limitation

A follow-up recorder restricted to one phone and allowlisted status reads prevented the Naim app from showing the NDX. Its log showed blocked device-description requests on a separate advertised port, plus startup reads and paginated input/favourite queries outside the allowlist. This capture cannot establish amplifier command behaviour. The recorder was stopped immediately after the user reported the problem. Direct system, power and now-playing requests all returned HTTP 200; the streamer remained on and stopped with error=0. The user turned the phone proxy Off, reopened Naim and confirmed that the NDX was visible again. App access is restored. Do not repeat this restricted proxy workflow as a working capture procedure.

## Away-from-home development

The next service-discovery attempt timed out. The user confirmed the computer is away from the home network; this is not evidence of an NDX failure. No live mutations were attempted in that session. Independent development added a public TIDAL metadata adapter, bringing the passing offline suite to 22 tests. Live catalogue search remains unverified.

## How to update this ledger

Record date, firmware, initial state, exact operation, observed result and final state. Distinguish API acknowledgement from actual state change. Link sanitized fixtures or local report filenames as appropriate. Never mark a capability complete solely because an endpoint exists or returned HTTP 200.
