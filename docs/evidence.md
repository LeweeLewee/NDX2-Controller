# Evidence ledger

## D033 voice-first Find and icon review — 25 September 2026

Final source `1fddc6ac877e36c8e072acf2acba311bebd17459`, tag `ios-preview-2026-09-25-5`, [run 36186308393](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36186308393): **25 native tests passed, zero failed/skipped**, and unsigned device archive passed. Nine local project/distribution checks and generated-project consistency passed. No bridge/firmware changes or live NDX/speech tests occurred.

Find now opens idle voice input; recording requires a microphone tap. Type instead opens a text entry mode; Use voice returns idle. Explicit typed or spoken submissions share Results, filters, row membership, details and bounded Back history. Mode changes and Back cancel recording; invalid/oversized input does not search. Model/UI tests verify these transitions and no playback mutations. NOW uses a 48-unit palette-coloured heart (outline/filled), 40-unit Find/Library icons with accessible labels, and no duplicate microphone entry. Resting artwork grows 272 to 296 units with its vertical centre retained; metadata shifts right by 24 units and preserves the right edge.

The first run at `34ca2e4` passed 24/25 tests: XCTest failed to terminate the prior app instance before the existing phone-layout test could launch. New model, snapshot, voice and keyboard tests passed. A fresh final runner passed the complete suite without weakening that test.

Artifact `10886282209` SHA-256 `fb18c46f4ec50deb52420aafece4bee722e4025275017e338594c2ae13bbe032` was downloaded and verified. `local/ios/review-find/review.html` retains 36 original native captures. Reviewed the ivory filled heart, resting artwork, long title, idle Find, typing and recording screens. The system-keyboard capture includes the iOS typing tutorial; the text field, mode switch and search remain above it, and the typed-submit tests passed. OS keyboard UI and physical mounted-phone acceptance remain separate from fixture validation. Signed upload succeeded at 2026-09-25T20:41:52Z. Apple processed **0.1.0 (4.1.0)** and the build was assigned to the existing internal group; **Testing** was visibly verified. No new tester/invitation or public release was created.


## D032 safe-area layout validation — 25 September 2026

Source `6f0b9afa49da5e6953c17664bdc5987e312a9524`, tag `ios-preview-2026-09-25-4`, [run 36178335036](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36178335036): **23 native tests passed, zero failed/skipped**, and unsigned device archive passed. Nine local iOS project/distribution tests and generated-project consistency passed. Bridge and firmware were unchanged; no live tests ran.

The locked landscape host now retains the system safe area and an extra 8 pt inset. A noninteractive music field extends under the notch/home area and across the entire screen, replacing the black frame. Like is compact and borderless beside the album, whose text target is bounded to leave a gap. Secondary headers expose a single plain Back action with previous-screen history. Other proposed layout rearrangements were not adopted.

The first run compiled and passed model/snapshot checks, but Previous/Next measured 71.8168 pt against the 72 pt UI minimum. Their invisible hit widths increased from 96 to 98 design units with icon centres unchanged; the minimum was retained and the final run passed. Play/Pause has a 76 pt minimum inside the smaller safe content area; physical readability remains a user gate.

Artifact `10883422826`, SHA-256 `783ff2f5e738b45a046c367f0b66d603c826a35674b10446114b1ed5859ad121`, downloaded and verified. The local gallery `local/ios/review-safe-area/review.html` retains 31 native captures. Final full-phone NOW/album and Find/Settings captures were inspected. This proves simulator layout and fixture behavior, not physical mounted-phone acceptance. Signed internal upload succeeded at 2026-09-25T19:24:42Z. Apple processed build **0.1.0 (3.1.0)** and it was assigned to the existing internal group; the visible status is **Testing**. No new testers or invitations were created.


## D032 native remediation validation — 25 September 2026

The user reported unused screen space, small type/transport targets and lost navigation/collection actions in the first TestFlight preview. Source inspection confirmed the fixed 755 × 346 pt host and missing NOW links. D032 authorizes remediation rather than treating the earlier snapshot pass as user acceptance.

[Final run 36174233828](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36174233828), source `dbd5c379c0c57e58bdab6a360a01e214f80d65bd`, passed **23 native tests**, with zero failures/skips, under Xcode 26.3 / iOS 26.2 SDK and iPhone 11 / iOS 18.6 simulator. It also passed the unsigned iOS device archive, distribution signing, code-sign verification and internal-only upload as **0.1.0 (2.1.0)**. Apple processing completed and the build was added to the existing **Naim NDX2 Controller TestFlight** internal group; Apple shows **Testing**. No additional tester or invitation was created. The native interaction test verifies actual phone target sizes and NOW artist/album navigation, Like/Unlike, Follow/Unfollow and album Add/Remove. Model tests cover per-reference isolation, row identity and browse-state preservation, Library addition/removal, unavailable membership and uncertain-write retention. Existing wake, keyboard, contrast, layout, lifecycle and no-replay checks remain enabled.

The first remediation run compiled and passed interaction/model tests but failed the eight-unit row-gap gate after typography enlargement. Row pitch increased to 88 units with a 72-unit text target; the same gap test then passed in run 36173653048 and again in the final run. No gate was weakened. The full offline suite passed 146 Python tests after one unchanged rerun of the already recorded Windows origin-test socket-abort; five JavaScript tests, six silent TLS demo stages and project generation checks passed.

Final artifact **10882550286**, `still-water-ios-2`, SHA-256 `f1b5b573b640afa31bf1edcbe5b70918d8ead2dabed282f680a151bbc3ef9146`, was downloaded and its digest verified; expiry 2 October 2026. The full ZIP and **31 original native captures** are retained under ignored `local/ios/`, with gallery `local/ios/review-remediation/review.html`. Full-phone NOW and album captures and the new artist/track membership states were inspected. Changed captures were reviewed; unchanged captures match the earlier inspected pixels. A brief disabled membership state after navigation reflects awaiting the next authoritative read, not a guessed saved state. System keyboard/home indicator remain OS-controlled.

Managed iOS files were copied back only after verifying the original versions matched the pre-remediation source; unrelated original-checkout work, bridge routes, firmware and retained design references were preserved. No live NDX, playback, volume or speech occurred. Signed distribution does not prove physical readability, mounted interaction, battery runtime or user acceptance.

## First signed internal TestFlight build — 25 September 2026

**Internal TestFlight ready — 25 September 2026:** version **0.1.0 (1.2.0)** was signed and uploaded from `eb72f22fe764f91687e16bff5f4a74714ba56102` in [run 36166397352, attempt 2](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36166397352). All 19 native tests passed. Apple processed the build and reports **Ready to Test**. The user-created internal group **Naim NDX2 Controller TestFlight** contains this build and only the explicitly approved tester, whose status is **Invited**. Build distribution is **Manual for Xcode Builds**. Phone installation and hands-on acceptance remain unverified. This is the compile-time silent fixture preview; live bridge, playback and speech remain disabled. This checkpoint supersedes older pending-signing/upload statements below.

The first upload attempt stopped during keychain setup before upload. Repackaging the same certificate/key into a macOS-compatible PKCS12 container resolved the failure; no app/workflow change or new certificate was needed. The compatible local package is additionally protected with current-user Windows DPAPI; GitHub transfer used environment-public-key encryption. Only the certificate-package secret changed. The retry retained the successful validation job and completed archive, code-sign verification and internal-only export/upload. Private receipt/logs are retained under ignored `local/ios/`. Validation artifact 10878875181 has SHA-256 `fa063adaa3a66f52595bd8a624a40fae6b3e78c6b4b8bfd1c9e3fd1af2ad8105`; exact validation JSON is retained under `local/ios/testflight-validation/`. This is distribution evidence, not physical runtime or design acceptance.

Last updated: 21 September 2026.

## Detailed-design entry audit — 20 September 2026

Repository inspection confirmed `software-feasibility-v1` resolves to commit `aa070fc0af4a616f769a7c0f15790831c90c112c`, matching HEAD at phase entry. No code or tag was changed. The user confirmed Waveshare was not purchased and reopened the display choice to include an old Android phone (D016). Model/version and hardware inventory remain unknown. New phase, deployment, interaction and candidate experiment documents are plans only: no board current, touch wake, microphone, Pi deployment or enclosure fit was tested in this audit. Existing untracked packaging work was left untouched. The album-save browser discrepancy is recorded as deferred B01 with unknown cause.

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
| Digital levels/room trial | Failed audible test; superseded by System Automation | Readback accepted 13 → 5 → 13, but user confirmed no audible volume change. This endpoint does not establish working amplifier control in the current setup |
| Existing wired System Automation | User confirmed | Both the NDX remote and Naim app control amplifier volume. The native command is now identified and tested; see [targeted capture investigation](research/system-automation.md) |
| System Automation command discovery | Static app evidence; both directions audibly confirmed | Android AutomationAPI and LeoAutomation specify GET automation?cmd=irVolumeDown/irVolumeUp with boolean repeat. Single taps were inconclusive. A press plus four held frames produced user-confirmed volume decrease and increase; player error remained 0 |
| Selective PAC recorder on phone | Failed; app access restored | NDX disappeared from app; no phone request reached the recorder. Recorder stopped and user confirmed visibility restored with proxy Off. Computer forwarding checks did not establish phone compatibility; retire this route |
| Full catalogue search | Unresolved | Exploratory GET query/path variants returned 400; correct syntax unknown. This does not prove search unavailable |
| Separate TIDAL metadata search adapter | Live search and pagination passed | Own app authenticated; artists, tracks, albums and playlists returned results and a distinct next page. Search-to-native-track playback has now passed through the UI |
| Collection pagination | Observed | favourites/albums with offset=0 and 2, limit=2 returned distinct successive pages and totalCount |
| Artwork retrieval and cache | Observed | Returned resources.tidal.com JPEG fetched (41,661 bytes), visually checked; second lookup reused cache. Host restriction, byte cap and eviction covered offline |
| Prototype Now Playing cover art | Observed | Player-supplied image loaded at 640 × 640 in the browser and was visually verified; albumName also displayed. No playback commands issued during this check |
| Album/playlist launch | Observed | cmd=play populated native queues of 11 and 50 tracks and started first tracks |
| Queue append/insert/remove/reorder | Observed | playLast appended; playNext inserted after current; DELETE removed returned queue reference; move placed item before destination |
| Next/previous, pause/resume | Observed | Titles and current queue references changed; pause state=3 held position, resume state=2 advanced |
| Automatic track transition | Observed | Seek near end followed by automatic next album track, native source retained, error=0 |
| Audible gaplessness | Not verified | Two-second state polling cannot measure an audible gap |
| Controller reconnect | Narrow test passed | New client read current track and advancing position during playback; no network or device outage induced |
| Long-term reliability and app coexistence | Not fully tested | Native app comparison pending; no concurrent command stress or authentication renewal test |
| Home Assistant reachable | Observed | Recognized page, HTTP 200; no login/configuration changes |
| ESP32 implementation | Not built | Computer-side HTTP prototype only |
| Battery and display performance | Not measured | Waveshare ESP32-S3-Touch-LCD-4.3B is the preferred candidate; final selection and physical validation pending |
| Hardware design and BOM | Planning record only | Manufacturer references and user preferences recorded in docs/hardware; no purchase, touch-wake or runtime evidence |

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

## Live public TIDAL catalogue — 20 September 2026

With explicit user approval, created the project's own NDX2-Controller developer application and used its client credentials for metadata requests. Searching for Massive Attack in GB returned 20 included resources for each of artists, tracks, albums and playlists. Each relationship endpoint returned 20 results and a distinct 20-result next page using the returned cursor. The report is kept in ignored local/evidence/tidal-live-catalog.json; credentials and access tokens were not written to project files.

Live results exposed that included-object ordering differs from result ordering. The CLI now resolves metadata against relationship data order. A repeat live check with this helper returned Massive Attack first among artists, Teardrop among tracks, Mezzanine among albums and Massive Attack Essentials among playlists. The offline suite now contains 23 passing tests, including shuffled metadata and missing metadata coverage.

These were catalogue-only requests: no audio manifest, audio transfer or NDX command was requested. The computer remains away from home, so candidate IDs have not been resolved or played on Naim. Personalized cloud resources, user OAuth and full TIDAL feature coverage remain unverified. The temporary loopback test service was stopped and the app secret left hidden in the portal.

## How to update this ledger

### Computer UI prototype — 20 September 2026

Published the revised design concept using the user's selected Waveshare ESP32-S3-Touch-LCD-4.3B without case. The hardware/BOM work remains separately maintained. Implemented the first 800 × 480 browser prototype and a loopback-only Python bridge. Browser inspection verified the now-playing layout, search/type filtering, album/track detail, demo play, next, pause, queue listing/addition and Back navigation. These checks used silent demo fixtures, not the NDX.

All 28 offline tests passed, including native-reference resolution before play and HTTP origin/host restrictions. The loopback test required local-socket permissions; it initially failed under the restricted network sandbox and passed with those permissions. No NDX commands were issued. Live UI integration, actual artwork display, queue-edit controls, embedded keyboard, physical touch usability and power measurements remain unverified or unimplemented as described in [prototype documentation](prototype-ui.md).

Record date, firmware, initial state, exact operation, observed result and final state. Distinguish API acknowledgement from actual state change. Link sanitized fixtures or local report filenames as appropriate. Never mark a capability complete solely because an endpoint exists or returned HTTP 200.

## Home-network UI and AI discovery — 20 September 2026

The user confirmed the computer was back home. Initial NDX status was stopped, native TIDAL source, error=0. Public TIDAL search in the browser returned Teardrop, which resolved through native browse. Browse descriptors are object.tidalTrack, object.tidalAlbum and object.tidalPlaylist, distinct from queue class object.track.tidal. The validator now requires an exact matching browse class and reference.

After announcing the test, Play now in our UI started Teardrop. Device samples showed playing state=2, positions 18111 → 21083 → 24055 ms, source=inputs/playqueue, sourceDetail=tidal, 16-bit/44.1 kHz, error=0. The queue contained one object.track.tidal. Cleanup confirmed stopped state=1, position=0, error=0. No volume command was sent. Filtered evidence: ignored local/evidence/ui-native-search-play.json.

The OpenAI project key was created securely and saved to the approved ignored destination. Live AI requests and refinements passed. Explore on a Tycho recommendation returned live TIDAL artists; selecting Tycho opened native Naim albums without playing music. 34 offline tests pass. The user tested Speak with the Bonobo request and confirmed: “Transcript appears correctly.” This verifies microphone capture and live transcription in that browser session, not future ESP32 hardware.

## System Automation UI verification

After user confirmation of both volume directions, Now Playing gained amplifier minus/plus controls. Browser inspection verified layout, disabled controls during each live request, re-enabled controls afterwards and a successful up-request acknowledgement. A down then up pair was exercised through the UI; playback continued. Exact physical starting-level restoration is not claimed. All 42 offline tests passed, including disabled-automation rejection, fixed burst length, stop-on-timeout without retry and rejection of numeric/extra volume parameters.

## TIDAL collection and Back navigation — 20 September 2026

The project's developer application now allows collection.read and collection.write with a loopback callback. The user completed music-account sign-in. OAuth PKCE and account collection reads worked. Initial full album and artist scans hit HTTP 429 after several pages; adding paced reads and a bounded Retry-After wait resolved the live checks. Null optional catalogue metadata is also handled defensively, but was not established as the cause of the live failure.

Real save → read-back saved → remove → read-back unsaved round trips passed for an initially unsaved album, track, artist and playlist. The album was Blue Lines, track Teardrop, artist Massive Attack and playlist Massive Attack Essentials. Mezzanine was already saved and was left unchanged. All test-added items were restored to unsaved. The ignored report is local/evidence/tidal-library-live.json. These requests did not send transport or amplifier commands; playback remained native TIDAL. Synchronization timing in the Naim app has not been observed.

Browser checks confirmed Back in AI discovery and album detail, restored search results after Back, and the real track heart changing from unsaved to saved and back to unsaved after UI clicks. Navigation tests cover query/type/cursor/scroll restoration and failed-browse recovery. The suite passes 49 Python tests and three JavaScript tests. This is computer-side proof; physical touchscreen and persistent sign-in deployment remain open.

## Now Playing album and artist shortcuts — 20 September 2026

Added exact TIDAL album/artist relationships from track IDs, including multiple-artist selection, plus clickable album and artist names on Now Playing. Live browser testing during Rhye playback opened Woman from its album name, then Rhye from the album detail link; both exposed the existing save/follow control and Back. No playback, volume or library mutation was needed for this check. Tests reject mismatched item IDs and unrelated included metadata, preserve multiple artists and keep metadata links separate from native playback authorization. All 52 Python tests and three JavaScript tests pass.

## Album search-result hearts — 20 September 2026

Album results now show separate saved-state heart buttons without nesting controls inside the album-opening button. Live UI checks saved Blue Lines (2012 Mix/Master), observed its filled heart while staying in search results, then removed it and observed the empty heart. The initial unsaved state was restored. Mezzanine remained saved. Search context and scroll position are retained; unknown state is not represented as unsaved. Five JavaScript tests pass, including distinct row identities and mutation targeting independent of the current detail selection. No backend or playback path changed.

## River Stone mechanical reference and packaging - 20 September 2026

Manufacturer 4.3B drawing visually inspected: lens 112.4 x 75.1 mm, VA 95.54 x 54.36 mm, maximum depth 17.4 +/-0.3 mm. The physical visible-area ratio must not be inferred from 800 x 480 pixels. [Source archive](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B/ESP32-S3-Touch-LCD-4in3B_Drawing.zip).

The reproducible [River Stone layout generator](../tools/river_stone_layout.py) checks three rectangular installation reservations against an inset elliptical footprint, each other and the rear plane of a 50-degree screen with 17.7 mm depth allowance. Checks pass; smallest normal clearance is 3.01 mm at the charger. This is partial analytical packaging evidence, not full shell fit, printed fit, component compatibility, stability, electrical validation or measured battery life. See [results](hardware/river-stone/clearance-checks.json).

## Display selection update — 21 September 2026

The user ruled out repurposed phones for the visual-design reasons recorded in D015 and selected Waveshare ESP32-S3-Touch-LCD-4.3B without case (D017). This is a design decision, not hardware evidence; no phone test failure is claimed. No purchase or new bench measurement is recorded; HP-01 is the next experiment.

## Repository reconciliation — 21 September 2026

Reconciled the detailed-design drafts with published commit `4e487da`. Preserved D015's dedicated-display rationale and assigned the draft bridge partition D018, updating its references. The River Stone layout was already tracked in `ef2576c`; corrected the phase plan's stale untracked-work description. The frozen `software-feasibility-v1` reference is unchanged. This is documentation reconciliation, not new firmware, deployment or hardware evidence.

Validation: 52 Python tests and five JavaScript navigation tests passed on the development computer. Documentation local-file links resolved and decision IDs were unique. Python 3.14 emitted a non-failing ResourceWarning while cleaning up a synthetic HTTPError fixture; no production code was changed. No live device commands were run.

## 21 September 2026 — M2 software fixtures (no live hardware)

Development-host synthetic tests and `python tools/m2_demo.py` pass a real localhost TLS/pairing slice: authoritative Now Playing, paginated search, album native-resolution simulation, one play request, refreshed player/queue state, Back context, three collection states, voice review/cancel/search and wake with no command replay. Protected Windows DPAPI restart/rotation, single-flight renewal, replacement failure, revocation, wrong server trust, durable duplicate/uncertain-command handling and stale-state gating are covered by offline tests. No real Naim or provider command was sent.

Official Waveshare archive downloaded privately and checksum-pinned; preparation generated an ESP-IDF 5.2.0/LVGL 8.4.0 fixture tree. Follow-up tooling installation enabled successful ESP32 firmware and Windows SDL/LVGL compilation, with two passing native C tests. The compiled UI passed a paired localhost TLS fixture flow, including Back, one silent native-play request, refreshed state and voice review/cancel; six framebuffer captures remain in ignored local storage. The album-detail capture was inspected for long-title readability. The final Python rerun passed 69 tests after one prior Windows 10053 failure in an existing HTTP test; JavaScript passed five tests. These are desktop and compilation results only. No flashing, Pi inventory, physical screen/touch/sleep/battery/microphone, power or P3/P4/P5 evidence was added. See [implementation limits](m2-software.md) and [vendor review/build instructions](../firmware/README.md).

Final M2 validation: 69 Python tests, five JavaScript tests and all five silent HTTPS demo stages passed; Python compileall and Git whitespace checks passed. The reference tag remains unchanged.

## 22 September 2026 — UI design approval and chat closeout

The user explicitly approved the final browser review after icon-only Search. [Approval](ui-review/approval.md) records the SHA-256 of the unchanged source; [closeout](m2-closeout.md) consolidates implementation and prior validation. This is desktop design acceptance, not native LVGL parity, new live observations or hardware evidence. Closeout edits documentation only; no new full-suite run, audible test, flash or physical trial was performed. Superseded review notes are retained as history.


## Shared approved UI implementation — 22 September 2026

The approved direction is now implemented as native C/LVGL slices: Playing layout and controls, filtered search, nested details and membership, collection/queue reads, immediate-record voice search and Settings. See the [parity inventory and actual evidence](m2-ui-parity.md) for implemented behavior and remaining integration gaps. Desktop evidence: 72 Python tests, five JavaScript tests, two CTests, five-stage TLS demo and expanded native LVGL/TLS smoke passed. HP-01 and physical P3/P4/P5 remain open; the hardware-arrival checklist is unchanged.


Final firmware validation, 22 September 2026: `python tools/build_m2.py esp32` **passed** with the final shared sources, pinned ESP-IDF v5.2 and LVGL 8.4.0. Application image `0x925b0` bytes fits the `0x100000` partition with 43% free. No flashing or efuse operation was run. This is compiler/linker evidence only; the default-disabled protected network path and physical behavior remain unvalidated.

## River Stone shell geometry - 21 September 2026

Created shell/cover STEP solids and STL meshes around the selected Waveshare (D017). The manufacturer STEP imported with 694 solids; the fit calculation uses a conservative 112.6 x 75.3 x 17.7 mm module envelope. A real cavity exposed collisions not captured by the previous plan-view approximation. Revised power reservations and cover-fastener positions now clear the shell and display. A continuous 120 mm vertical insertion sweep through the empty shell passes after hidden internal clearance relief. See [CAD study and exact checks](hardware/river-stone/shell-v1/README.md).

The delivered shell uses a separate inner loft after the constant-offset approach failed downstream solid operations; normal wall thickness is not certified. Shell, cover and module-envelope STL meshes are watertight, consistently wound, positive-volume single components within 256 mm bounds. No slicing, physical fit, retention-load, electrical, antenna or thermal test was performed. The exterior facet/crown, screen retention, ports, microphone space and print support requirements remain unresolved; these are study files rather than a build release.

## River Stone retention and print audit - 21 September 2026

[v2 study](hardware/river-stone/shell-v2/README.md) adds two internal retainers, four bosses and two small fastener-fit coupons. All seven exported meshes pass watertightness, winding, positive-volume and single-component checks. Retainers clear glass/PCB proxies and reserved power volumes; the continuous insertion sweep clears fixed bosses with retainers removed. Actual supplier-detail contact and glass loads remain unverified.

A proposed front-edge fillet produced open STL meshes despite passing CAD validity and was removed. The delivered exterior retains the v1 surface. A 2,048-ray audit found minimum sampled directional depth 0.764 mm at the lower rim and a 0.938 mm crown sample. This does not certify global minimum thickness. Overhang area above a 45-degree criterion is approximately 14,874 mm2 underside-down and 3,950 mm2 screen-facet-down; these are not slicer support estimates. Wall refinement, actual slicing and physical fit remain required before full-shell printing. No physical, electrical or live-device tests were performed.

## River Stone reinforced shell - 21 September 2026

[v3 CAD study](hardware/river-stone/shell-v3/README.md) reinforces the lower rim, lowers the upper cavity to add crown material, extends the cover bosses through the ledge, and adds a 2 mm screen-facet bevel. The matching cover is smaller to clear the reinforced rim. The bevel passes both CAD and mesh validation, unlike the earlier broad fillet. Seven meshes are valid closed single components; all applicable envelope clearances and continuous display insertion checks pass.

The final seeded 10,000-ray audit reports minimum sampled normal depth approximately 1.000 mm at the screen lip, with zero samples below 1 mm at 0.0001 mm numerical tolerance. First/fifth percentiles are 2.065/3.000 mm. An intermediate 0.746 mm screw-hole/ledge junction was reinforced before this final check. The audit and mesh reports identify the same final STL hash. Discrete sampling does not establish a global minimum or strength. Overhang screening remains substantial: 13,795 mm2 underside-down and 5,328 mm2 facet-down. No slicing, physical fit, glass-load or powered testing occurred; full build release remains pending.

## River Stone offline P1S slicing - 21 September 2026

[OrcaSlicer 2.4.2 study](hardware/river-stone/slice-v1/README.md) uses the bundled P1S 0.4 mm machine profile, compatible 0.20 mm process and provisional Generic PLA/textured-PEI settings, with three walls and 15% infill. Coupon slice exits successfully, reports inside-bed placement and no supports, and estimates 15m49s / 2.73 g. The committed 3MF contains the same G-code hash as its result report. Selected toolpath layers were rendered and inspected; nut-pocket/screw geometry remains present. No physical fit has been proven.

Normal automatic-support baseline estimates: underside-down 7h43m59s / 289.08 g; facet-down 6h18m02s / 224.85 g. Feature-tagged extrusion sums give 74.44 and 21.84 cm3 of commanded support respectively, excluding Custom startup/purge. Facet-down trades lower estimates for contact between the textured bed and visible front. No final orientation or finish was selected. All slices retain warning 1000C001 (bed temperature versus filament) with the inherited 55 C PLA plate setting; this has not been suppressed or physically resolved. Full-shell printing remains unreleased. No printer commands or physical tests were performed.

## 22 September 2026 — Larger battery source review

Reference evidence only, no physical test: [larger battery review](hardware/larger-battery-review.md) records visually inspected PKCELL drawings. BAT0014 maximum 69.5 x 57 x 20.5 mm body is dimensionally contained by the current 80 x 64 x 26 mm reserved battery box; cradle/cable fit remains unverified. BAT0015 maximum 75 x 69.5 x 20.5 mm body exceeds its short dimension. Live Pimoroni variant data reports BAT0014 £25 and available. Adafruit BQ24074 published Eagle schematic blob a97e12c1628a74e95eb0af333206ff6f3706126c connects TMR to GND; TI states this disables safety timers. This resolves the source timer question, not actual delivered board revision or charging behaviour.

## M2 authenticated artwork checkpoint - 22 September 2026

Authenticated bounded artwork renders in shared LVGL Playing/detail screens using silent local JPEG fixtures. Voice Restart now cancels pending transcripts. Fresh validation: 77 Python tests, five JavaScript tests, three CTests, both TLS demos, desktop and ESP32 builds passed (`0x92c00`, 43% free). Native artwork/changed-cover pixels were inspected and asserted. See [limits and detailed evidence](m2-artwork.md). Live artwork/quality, deployment-host resource profiling, provisioning/preferences and physical HP-01/P3/P4/P5 remain open. No audio or hardware operation occurred.

## M2 local preferences - 22 September 2026

Local palette, brightness intent and timeout persist across separate native desktop launches. Bounds/checksum, atomic replacement, writer locking, corrupted storage, coalescing and save failures have native tests. Restored Settings pixels were inspected. Fresh evidence: 77 Python tests, five JavaScript tests, four CTests, both TLS demos, preference restart smoke and both builds passed. The ESP32 NVS adapter is compiled only; hardware brightness/sleep and physical durability remain open. See [details and limitations](m2-preferences.md). No live Naim or hardware operation occurred.

## M2 offline recovery - 22 September 2026

Desktop startup outages, late pipe replies and helper recovery are fixed without retrying commands. Shared LVGL detects bridge restarts, rejects expired snapshots, bounds pending state, clears stale artwork/membership and preserves browsing while consuming old gestures. Silent fault injection proves one play and one volume request despite lost replies. Fresh evidence: 80 Python tests, five JavaScript tests, four CTests, TLS/native/preference/recovery demos and both builds passed (`0x971f0`, 41% free on ESP32). The screenshot harness now flushes current LVGL pixels before capture. See [recovery scope and evidence](m2-recovery.md). No live Naim or hardware operation occurred; physical gates remain open.

## M2 enrollment and revocation foundation - 22 September 2026

The [offline provisioning slice](m2-provisioning.md) adds protected enrollment intent, origin/trust-bound controller records, durable uncertain/revoked states, local ID inventory and setup-code cancellation. The desktop helper enforces new record bindings while preserving legacy fixtures. Fresh evidence: 93 Python tests, read-only TLS enrollment/revocation/re-pairing demo, native UI/artwork smoke and outage-recovery demo passed. No C/ESP32 or UI changes; prior build evidence was not rerun. Production setup UI, physical installation and HP-01/P3/P4/P5 remain open.

## Host setup console - 22 September 2026

The [operator setup flow](m2-setup.md) adds local status, hidden-code pairing, explicit read-only verification and confirmed local forgetting. It rejects piped secret input and echo fallback, retains durable unknown outcomes and supports local recovery without a trust file. Fresh evidence: 107 Python tests, setup/TLS fixture demo and enrollment regression demo passed; zero live commands or real credential changes. Native UI/firmware are unchanged. Physical terminal echo and deployment/hardware gates remain separate.

## Certificate renewal and trust recovery - 22 September 2026

The [trust lifecycle slice](m2-trust.md) proves same-CA leaf renewal retains pairing and expired/wrong-host/unexpected certificates fail. An explicit same-origin `trust-update` verifies a snapshot before atomically replacing the saved binding; status reports the saved digest for interrupted recovery. Fresh evidence: 118 Python tests plus trust/setup/provisioning TLS demos passed, with no live commands or real certificate changes. Native UI/firmware and physical gates are unchanged. Production certificate installation and ESP32 rotation remain separate.

## Portable desktop package - 22 September 2026

The [desktop package](m2-package.md) bundles the validated native executable, SDL and isolated Python runtime with a launcher and setup entry point. Explicit client dependencies exclude bridge/provider adapters. Launch/setup enforce external pairing/trust/configuration; preferences remain per-user or explicitly external. Fresh evidence: 126 Python tests and extracted native/TLS package acceptance passed; a second clean installation retained byte-identical pairing/preferences without command replay. This is a portable development build and upgrade-layout rehearsal on the current Windows host, not a signed release, clean-OS certification or physical deployment.

## User trial: Play/Pause and visual finish - 22 September 2026

The packaged standalone fixture revealed a real gap: transport commands were acknowledged but snapshot state always said playing, so Pause never changed to Play. Both shared C and Python TLS fixtures now update paused/resumed state; starting a new track restores playing. The UI remains driven by the refreshed snapshot rather than optimistically changing the icon. Actual native pointer taps and icon pixels pass Pause -> Play -> Pause in standalone and TLS modes, with one pause and one resume only. 127 Python tests and five desktop CTests pass.

The user also identified that the native port is less polished than the approved reference. The approved design remains the target, but the functional native port is not yet a final visual match. Generic LVGL glyphs/type, spacing/control styling, the diagnostic status strip and fixture-only missing artwork need a focused visual-parity pass. Do not restart the design or change the approved baseline. Earlier functional parity/packaging evidence does not establish finished visual polish. No live Naim control or physical acceptance is claimed.

Play/Pause correction build evidence: desktop and five CTests passed; ESP32 compiled at `0x97260` bytes, 41% free. Standalone and TLS native pointer/pixel regressions passed. No flashing or live transport command occurred. Newer hardware-order records were preserved.

## User trial: visible Next/Previous feedback

Next/Previous had the same silent-fixture gap: commands were logged without changing track data. Both fixtures now use a three-track sequence with distinct titles/references, wrapping in either direction and resetting position to zero. Queue/current-item/detail identity stays consistent. Skipping preserves paused state; explicit Play starts the selected fixture playback state. The icons for Next/Previous intentionally stay fixed; changed metadata is their feedback. Native pointer smoke now covers pause/resume, next, previous and wrapping with one request per tap. Live Naim adapters and D011 are unchanged; this is silent simulation, not live transport validation.

Fresh transport follow-up validation: 128 Python tests, five desktop CTests, standalone/TLS native pointer and pixel checks, and the native artwork smoke passed. Both builds passed; ESP32 image is `0x97420` bytes with 41% application partition free. The Next capture visibly shows Silent track 2 at 0:00. No real audio, live device command or flashing occurred.

## Native visual polish - 23 September 2026

[Visual-polish scope, screenshots and validation](m2-visual-polish.md) records a shared LVGL refinement of D020: consistent outline icons, clearer typography, quieter status, cohesive palettes/navigation, structured lists/settings and rounded artwork. Approved layout, hit areas and playback/recovery constraints remain. Five CTests, both builds, native TLS screen/artwork smoke, transport checks, preferences restart and recovery fault checks passed; an intermittent library-state smoke timeout passed on unchanged rerun and remains recorded. ESP32 image: `0x98210`, 41% free. Native photographic artwork quality and physical acceptance remain open.

## Object-led native design - 23 September 2026

The user clarified that the approved screens were rough prototypes and authorized expert iteration for the coffee-table ornament outcome (D027). [Design gate and evidence](m2-object-design.md) records three native iterations: 280 px artwork, quieter chrome/navigation, stronger Play/Pause emphasis, bounded long titles and larger browse text. The 13-state desktop composition gate passes; photographic artwork resolution, physical readability/touch/power and user acceptance remain separate. Six CTests, 128 Python tests, native TLS/transport/preferences/recovery checks and both builds passed; ESP32 `0x98810`, 40% free. Original demo sleeves are fixture-only and never conceal missing real covers.

Desktop design delivery follow-up: an extracted-package missed-tap timeout exposed an event-to-LVGL contact handoff gap. Immediate contact registration now precedes desktop UI timers without command retries. Rebuild/six CTests and the full native TLS smoke pass; details and limits are in [the design record](m2-object-design.md).

Final object-design package gate: corrected smoke readiness/press duration and redundant desktop frame presentation. Full extracted-package UI/artwork, isolated runtime, retained external state and standalone/TLS transport checks pass; no repeated commands were added. See [the complete iteration record](m2-object-design.md).

## Chat closeout and design pause - 23 September 2026

The user retained the working prototype but rejected the visual direction and paused design work (D028). The prior designer gate must not be described as user acceptance. [Closeout](chat-closeout-2026-09-23.md) records implementation b36098d, prior tests, final package identity, local artifacts, untracked revised-design materials and continuing constraints. This is documentation-only; no application tests, live actions or physical checks were rerun. Git/diff and documentation integrity checks are the closeout validation.


## Still Water Brief A — offline bridge evidence, 23 September 2026

136 Python tests, five JavaScript navigation tests and the six-stage silent TLS `tools/m2_demo.py` passed. Eight new tests cover complete 320 × 320 reassembly against independently normalized fixture pixels, digest mismatch on changed source, partial chunks, legacy 80 response, cache payload/entry bounds, registration/expiry/corruption, strict report validation, charge thresholds, exact one-hour expiry, replacement/restart, single-flight rejection and TLS unauthenticated/revoked refusal. GET paths for root/artwork/charge remain unsupported. No new route exists.

The first restricted targeted run hit Windows access denial creating protected temporary TLS files. Normal host execution retained ACL/trust checks. One new test import bug was then corrected; the final full suite passed. This is synthetic contract and localhost TLS evidence, not deployment-host memory profiling, live artwork/NDX operation, hardware charging, physical power or UI validation. Firmware and all UI/reference material were unchanged. See D029 and the contract extension for precise behavior and remaining client obligations.


### Brief A.1 — charge reasons, 23 September 2026

Fresh requested validation passed: `python -m unittest discover -s tests -v` (137 tests), `node --test tests/test_navigation.cjs` (five tests), and `python tools/m2_demo.py` (six stages). The existing fixture exercises the same contract as the bridge and now asserts window for fresh yes/no, none before any report and stale after advancing only its injected clock by one hour. Tests additionally cover exact expiry of both yes and no decisions, invalid-report rejection without freshness renewal, fresh replacement and reset to none after restart. The TLS test verifies the fresh reason field under authentication and retains revoked/unauthenticated refusal. Protected temporary vault and TLS checks ran outside the Windows sandbox with no security checks weakened. No live NDX, UI, firmware or new HTTP-route behavior is claimed.

## iPhone hardware direction and parked Waveshare fallback — 25 September 2026

User explicitly selected iPhone 11 plus UGREEN Nexode 20000mAh PD 20W QC Power Bank and asked to park the Waveshare base. D030 records selection and physical-design scope; selection is not a test result. Fast-forwarded the clean CAD checkout through the 25 newer shared commits before editing; preserved newer bridge/Still Water work and prior hardware purchase records. Waveshare geometry, slices and reports remain unchanged, now marked fallback.

The supplied “04 Tide pool” image was read after correcting the Windows path and retained as an interface reference. Published a rear-loaded cradle/masking proposal and schematic, not new fit CAD. Apple's nominal iPhone body dimensions inform the envelope; Still Water's 118 × 54 mm aperture remains unverified. UGREEN SKU 25683 dimensions are conditional manufacturer reference only, pending exact selected variant. No new physical fit, sensor, voice, charging, runtime, slicing, UI or live-device validation occurred.

## River Stone reference clarification — 25 September 2026

User clarified original 01 River Stone is the design basis; it now governs both the body and screen/stone interface. Tide pool is retained solely as superseded history. The user also requires that mounting not obstruct the iPhone microphones. Updated the mounting proposal, D030 and continuation records. These are requirements, not evidence of physical fit or acoustic performance; no CAD, printing or device tests occurred.

## iPhone mounting layout — 25 September 2026

User authorized proceeding and repeated the selected UGREEN Nexode 20000mAh PD 20W QC Power Bank name. Used the matching manufacturer 25683 dimensions (147 × 72 × 28 mm) provisionally, without claiming an exact physical-unit match. Generated front/section/underside layout and numerical record: 50-degree phone, 151 × 76 × 32 mm bank bay, and 6 mm rear allowance beyond nominal phone depth give 15.08 mm minimum vertical separation between the bay and the infinite rear allowance plane. No curved shell, insertion, connector or microphone-passage solids were checked. Original 01 River Stone remains the only visual reference.

Created a 118 × 54 mm paper aperture registration template with a 50 mm scale. Reserved separate front/notch, rear-camera and Lightning-end acoustic zones, with interrupted gasket and open passage proposals; exact microphone locations and acoustic behaviour remain unverified. Phone service currently assumes removing the bank first. No physical sample, voice recording, power trial or new slice was performed.

## Still Water Brief B — cloud simulator proof, 25 September 2026

Under the explicit Brief B and subsequent Windows cloud-build authorization, [GitHub run 36130364216](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36130364216) built `5c211f7e2dbe36f1e36d6156d73b23f105098597` unsigned in Xcode 16.4 and passed all 17 tests on iPhone 11 / iOS 18.6. Eight lifecycle/controller tests, five protocol/artwork tests, two snapshot/palette tests and two UI tests passed with none skipped. The 23-state native matrix and three full-screen interaction captures are retained in a Windows gallery; every state has been inspected. UI evidence covers consumed first contact, subsequent navigation, the full Search touch rectangle, actual keyboard and dismissal by icon and Return.

[The implementation report](ios-still-water.md#passing-cloud-run-and-retained-evidence) records original failures, fixes, exact artifact/hash, contrast methodology and known native-control/OS-chrome differences. The unchanged full rerun of 141 Python tests, five JavaScript tests, six silent TLS demo stages and generated project/vector checks passed. All 63 task-start firmware/reference files were preserved by hash, including pre-existing local edits; the cloud branch also retains newer mounting work through b976842. No new route, live NDX/playback/volume, signing, real-phone or power validation occurred. Simulator success is not user design acceptance.

## Internal TestFlight preview preparation — 25 September 2026

[Run 36134704504](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36134704504), commit `768ebece4120dae58ae8ad783f5b4bce60f18608`, passed all 19 native tests in Xcode 26.3 on iPhone 11 / iOS 18.6, then built and checked the unsigned Release archive against the iOS 26.2 SDK. Preview mode, icon, privacy declarations, version and source/binary identity were verified. The changed Pairing, queue and after-search captures were inspected; all other captures match prior inspected native pixels. [Exact artifacts, hashes and remaining gates](ios-testflight.md#validation-checkpoint) distinguish unsigned archive proof from signing/distribution.

146 Python tests, five JavaScript tests and six silent TLS stages passed; project/vector generation checks passed. All 63 task-start firmware/reference hashes remain unchanged. No signing secret was requested in chat or committed; no Apple certificate, profile, app record, upload or tester invitation was created. Protected signing inputs and team/app identifiers remain required. There was no live NDX, volume/playback, physical speech or firmware operation.

## App registration and build identity - 25 September 2026

Verified the signed-in Apple team and successful explicit App ID registration, then created the NDX2 Controller iOS App Store Connect record after the user resolved the agreement blocker. Apple rejected the initial Still Water account-record name as already used. The source and unsigned archive check now use `com.ndx2.controller`, with distinct test bundle identifiers and a matching battery-task identifier. Nine offline iOS project/distribution tests passed. [Run 36152860230](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36152860230) passed all 19 native tests, none skipped, and the unsigned iOS-device archive at `ba2d18f95778d1856ab052b4aa3d394c68ff4825`. Xcode 26.3, iOS 26.2 SDK and iPhone 11 / iOS 18.6 simulator match the previous toolchain. Archive metadata confirms `com.ndx2.controller`, preview mode, version `0.1.0` / build `8.1.0`, signed false and uploaded false. Original JSON is retained at `local/ios/registered-identity-validation/`; the artifact ZIP is retained byte-for-byte. This configuration change does not establish new physical or user design acceptance. No signing material, upload, tester invitation or banking change was made. Private account/record identifiers remain under ignored local/.

## D034 native amendment validation — 25 September 2026

Source `10313a8e417b29274112af09548c5d7546707182`, tag `ios-preview-2026-09-25-6`, [run 36191105906](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36191105906): all **26 native tests passed**, none failed or skipped; the unsigned device archive also passed. This includes progressive fixture transcript/reset and artist tab/history checks, every native snapshot's geometry/fonts/contrast, full iPhone safe-area and collection controls, keyboard submission and the normal wake-to-Find voice journey. Nine offline project/distribution checks and the generated-project check passed separately.

The first run at `056392b` passed 25/26 tests, including all compilation/layout/model checks. Its voice UI test incorrectly used frozen screenshot mode, preventing timer-driven transcript progress. The corrected test launches the normal silent fixture and navigates through wake and Find; the release gate was not weakened. The final source also preserves track-detail hearts and artist album pagination.

Native evidence artifact `10888885107`, SHA-256 `e18edfbd349061c007546c42db3a4f9cdd7857e19dea4a41b542a4ebf08c1768`, is retained privately under `local/ios/`. Signing/upload and Apple processing are recorded separately. The preview remains silent; no live playback, volume, NDX, speech, firmware or bridge-route validation occurred. Physical/user acceptance remains open. Presence was explicitly excluded from this sprint and queue.


## D035 B1 native validation — 26 September 2026

Source `85628f204f953453f38f0a8a159ae0f215f4ee27`, [run 36229392996](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36229392996), passed all 28 native tests and the unsigned device archive. The 46-capture gallery retains original native pixels: every changed capture was visually reviewed, while unchanged states match the earlier reviewed matrix byte-for-byte. Full-phone tests cover safe-area control spacing, settings background hold, typed keyboard submission, explicit voice stop/submit, simulated silence stop and history. Bounded biography decoding and artwork re-registration are tested. [The B1 report](ios-b1.md) records exact toolchain, artifact hash, source reconciliation and limits.

Fresh local validation passed 150 Python tests, five JavaScript tests, six silent authenticated TLS demo stages and project/fixture generation checks. Biography sanitation, exact artist identity/relationship selection, allowlisted portrait registration, 320 chunks, expiry and re-registration use fixtures; this does not prove live catalogue access. Native silence detection is implemented but actual microphone/noise calibration has not been trialled. TestFlight remains a compile-time silent fixture. No live NDX, playback, volume, speech, firmware or new route was exercised; Presence remains excluded. Signed upload and Apple group availability are tracked separately.


D035 distribution: [signed run 36230634817](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36230634817), tag `ios-preview-2026-09-26-b1`, repeated all 28 native tests and unsigned archive checks, then signed and uploaded version **0.1.0 (6.1.0)**. Apple processing completed; the existing internal group was assigned and Apple visibly reports **Testing**. No new tester was added. Release artifact `10902269009` was downloaded and verified against SHA-256 `56a5f119a42daddbeb8de4e5245bfab431c51ed5bf65d9cbc2637fdb8aa6062a`; original validation and upload logs are retained privately. This demonstrates availability, not installation or B1 user acceptance.

## Visual correction follow-up — 26 September 2026

The user rejected the prior visual result. Functional success at `85628f2` remains valid for that source, but does not establish design acceptance. Corrections are implemented on the isolated B1 branch and remain unverified natively. Fresh local checks passed 150 Python tests, five navigation tests, six silent authenticated TLS demo stages, project generation and fixture generation. Subsequent changes are Swift layout/test adjustments only.

[Run 36232443600](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36232443600), source `a73fe4e`, was cancelled by the replacement push during native tests. Its tiny export artifact is not validation evidence. [Run 36232563391](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36232563391), source `3a0312a`, failed before any runner or steps started. Check annotation: “The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings”. This is an external build blocker, not a compilation result. No billing settings were changed.

Native compilation, geometry tests, fresh screenshot comparison and an updated internal release remain pending. TestFlight 0.1.0 (6.1.0) remains unchanged. See [visual audit](ios-visual-audit.md).


## D035 visual correction retry — 26 September 2026

GitHub billing ceased blocking the user-requested retry. Native run 36233599779 compiled but found caption/artist target geometry failures; direct review exposed incorrect wrapped title height. These were corrected without weakening the gates. At `5e78b5f722bd16a80c44aa831c072b407c8f8f7d`, [run 36234432936](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36234432936) passed 28/28 native tests and unsigned device archive. Artifact10904305394 was verified against SHA-256 `4fbc064fb1934bd241f99836289c00147fd3cb0e2e37b39f132dcd710956aba7`. All 43 first-run captures were inspected, then the ten changed/new final captures; the other 36 final captures are pixel-identical. Gallery: `local/ios/review-b1-visual/review.html`.

[Signed release run 36235235938](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36235235938), tag `ios-preview-2026-09-26-b1-visual`, repeated 28 passing tests and archive validation, signed and uploaded 0.1.0 (7.1.0). Apple processing was observed; group availability is recorded separately. No live NDX, volume, playback, speech, firmware or route mutation occurred.

User feedback during upload identified a missed shared-header inconsistency. The latest source still places Silent Demo at y24 on NOW versus y6 elsewhere; this refactor remains open. Safe-area fitting and canvas centering were compared with the earlier B1 source and are unchanged. The visual review therefore does not constitute user acceptance; [audit](ios-visual-audit.md) records the affected screens and retained limitations.

Release completion: Apple processed build **0.1.0 (7.1.0)**; assignment to the existing **Naim NDX2 Controller TestFlight** group is verified with status **Testing**. Release artifact `10904386131` SHA-256 verified: `9c2f040628353880234e2d80d710d806bacbd51d7998fc4d0966cb340b4d910b`. Shared-boundary correction remains open.


## Brief B.1 testing amendment — 26 September 2026

Offline validation: 150 Python tests, five navigation tests, six silent TLS fixture stages and the generated iOS project check passed. No bridge/firmware/route change or live NDX command was made.

Native run 36246296700 at 6aac1917e6f065cee9726df00b319b8747469d95 passed 29 tests with zero failures and the unsigned iOS-device archive. Artifact 10907508574 is 69,608,552 bytes; SHA-256 7ae85874453c6dab336c9021ea224918db3c9b885a5c5e159741691e75c6ec9c verified. Gallery local/ios/review-b1-amendment-first/review.html contains 50 native captures. Forty-four were inspected directly; six (longtitle, noart, still-artwork, still-fallback, stopped, wake) are pixel-identical to the previously reviewed build. Shared marker, transport alignment, Library layouts, keyboard and phone safe areas were verified. Visual finishing aligns the artist selection underline with its label and fades the portrait boundary. Final evidence is tracked in ios-b1-amendment.md.


Final native source `0f9ecc6e1a2b9a9e4c49b614ff43edf2150fba41` passed all **30 native tests** and the unsigned device archive in [run 36247170788](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36247170788). Artifact `10908186354` (70,022,280 bytes) was SHA-256 verified: `2d83eb9cae1f086a41d375e77f93700fc888a7bc278b6ab453ce98dcba7d142f`. The final gallery is `local/ios/review-b1-amendment/review.html`, with 50 captures: eleven changed captures were inspected directly and 39 are pixel-identical to the first reviewed amendment. Artist underline, portrait fade, seeded playlists, queue and full-phone alignment were checked. This remains simulator visual evidence, not mounted-phone acceptance.

[Release run 36248128881](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36248128881) repeated all 30 native tests and archive checks, then signed and uploaded **0.1.0 (8.1.0)**. Apple processing completed; assignment to the existing **Naim NDX2 Controller TestFlight** group is verified with status **Testing**. Tag `ios-preview-2026-09-26-b1-amendment` remains at reviewed source `0f9ecc6e1a2b9a9e4c49b614ff43edf2150fba41`. Phone installation and acceptance of this amendment remain unverified.


## D036 live-beta preparation — 26 September 2026

Eleven offline project/distribution tests pass, including wrong-mode/wrong-bundle archive rejection. Native source `1fec99157969db2f94c116ccbb994365a54a31ac`, run 36251163829, passed 31 native tests and live-mode archive checks. Artifact 10908933076 SHA-256 verified: `1e42aef3af7fca96e0781dc30f58a86dc121805f40072515906cb32ae99a26bc`. Four changed captures were inspected; 46 match the reviewed 8.1.0 pixels. Gallery `local/ios/review-live-beta/review.html`. Release run 36252070759 repeated 31 passing tests and signed/uploaded 0.1.0 (9.1.0), with live build mode verified in the archive command. Apple processing and phone/bridge validation remain separate. No NDX address or live bridge was supplied, and no device command was attempted. [Trial plan](ios-live-beta.md).

Release completion: Apple processed **0.1.0 (9.1.0)** and the existing Naim NDX2 Controller TestFlight group assignment is verified with status **Testing**. Bridge host/address input, provisioning, physical pairing and actual NDX trials remain pending.


**Live pairing diagnostic follow-up:** Windows authenticated live reads succeeded; physical iPhone pairing remains blocked. Stage-specific, secret-free enrollment diagnostics are prepared on the live-beta branch; native validation/distribution pending. Browser reachability is confirmed and does not prove app enrollment. No live mutations. See [trial report](ios-live-beta.md).


**Pairing diagnostic beta uploaded — 26 September 2026:** source `f0dba3e` (including diagnostics commit `d43a7d1`), tag `ios-preview-live-2026-09-26-pairing-v3`, passed all **32 native tests**, the unsigned device archive, signing and upload in [run 36264297307](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36264297307). The uploaded live build is **0.1.0 (11.1.0)**. The separate branch validation run 36264296786 also passed; artifact 10913830393 SHA-256 `bb416fe9cd69ec5ce3b0901e4df4de941505ae8bb6e5ffe0efcb40b0a799b749` was verified and the revised pairing capture inspected. Eleven local project/distribution checks passed, followed by four passing project checks after the local-network declaration. The earlier diagnostic-only release was cancelled before upload.

Apple processing and existing-group assignment await restored browser sign-in; the existing API key returned HTTP 403 for build reads. Do not claim the diagnostic beta is available in TestFlight yet. Physical pairing remains unresolved: the next attempt should expose a safe stage-specific error if the local-network declaration does not resolve it. No playback, volume or collection mutations.


**Diagnostic beta available — 26 September 2026:** Apple processed **0.1.0 (11.1.0)**, build `6fbc4f31-7ba4-48e1-a522-40668aa021e2`. After the user restored sign-in, it was assigned to the existing **Naim NDX2 Controller TestFlight** internal group and the page verified **Testing**. No tester or permission expansion. This supersedes the pending-processing/group-assignment note above. Phone update and pairing outcome remain pending; request the exact new Setup status if enrollment fails.
