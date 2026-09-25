# Still Water Brief B — implementation and review report

**D033 available in TestFlight — 25 September 2026:** **0.1.0 (4.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group and Apple shows **Testing**. Source `1fddc6ac877e36c8e072acf2acba311bebd17459`, [run 36186308393](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36186308393), passed all **25 native tests**, unsigned archive and signed upload. NOW has a larger icon-only heart, warm ivory outlined/filled states, Find and Library icons, and one Find entry. Find opens idle voice input with explicit recording and secondary typing; both search paths share Results. Still artwork is about 9% larger, with metadata shifted right. The safe-area layout and locked orientation remain. Gallery: `local/ios/review-find/review.html` (36 captures). This remains a silent fixture preview; mounted-phone/user acceptance is open.

**D032 safe-area update available — 25 September 2026:** internal TestFlight **0.1.0 (3.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group and Apple shows **Testing**. Source `6f0b9afa49da5e6953c17664bdc5987e312a9524`, [run 36178335036](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36178335036), passed all 23 native tests and archive/sign/upload checks. The background fills the screen, content respects the system safe area plus an 8 pt inactive inset in the existing locked orientation, Like is compact beside the album, and secondary screens have one plain Back control. Other review suggestions were not adopted. Gallery: `local/ios/review-safe-area/review.html`. Mounted-phone/user acceptance remains open; this is still a silent preview.

**D032 remediation available in TestFlight — 25 September 2026:** version **0.1.0 (2.1.0)** was signed and uploaded from `dbd5c379c0c57e58bdab6a360a01e214f80d65bd` in [run 36174233828](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36174233828). All **23 native tests** passed, none failed or skipped; unsigned device archive and signed internal export succeeded. The phone-fit layout, larger type/transport, volume icons, exact artist/album navigation, track likes, album library controls, artist follow controls and row-specific membership actions are implemented. Fixture Library reflects per-item additions/removals. Apple processing completed; the build is assigned to **Naim NDX2 Controller TestFlight** and shows **Testing**. The existing tester can update through TestFlight; group distribution remains manual. Read [the parity checklist](ios-remediation.md). Physical readability and user acceptance of this replacement remain open; it is still a silent fixture preview.

25 September 2026. The user explicitly requested action on the revised `codex-prompt-B.md`, authorizing a native SwiftUI client under D030. The native project has now compiled and run on a private GitHub Mac runner, controlled from Windows. All 17 native tests passed, including the 23-state snapshot matrix and both interaction tests. This is not user or physical acceptance. [Cloud build and Windows review instructions](ios-cloud-build.md) supplement the [local Xcode guide](../ios/README.md).

## Implemented source

`ios/StillWater.xcodeproj` contains the app, unit/snapshot tests and UI tests. Bundled Instrument Serif Regular/Italic and Geist Regular/Medium include pinned upstream revisions, SHA-256 hashes and their OFL notices. The 1048 × 480 design canvas is scaled once by 0.7206 and clipped to a centered 755 × 346 pt window. A native paragraph renderer supplies the serif 1.02-em line height instead of accepting the font's 1.3-em default.

NOW includes Still, Touched, wake reveal, paused/stopped, long-title, missing artwork, offline, pending and uncertain-command compositions. The client includes read-only Up next with seven sleeve sizes and one reflected image draw per available cover; voice-first Find with explicit recording and a secondary real system keyboard, shared Results, native Detail, Library and the Settings group. Native browse resolves candidates before exposing Play; the bridge resolves again for every actual play. No play-next, queue editing or numeric amplifier claim is added. Missing queue art remains text; play-time estimates are omitted when the bridge has no durations.

Artwork uses registered authenticated actions: the 80-pixel preview supplies colour extraction and bounded queue thumbnails; 320-pixel sleeves assemble 16 chunks only when reference, dimensions, digest, boot, generation and monotonic expiry agree. Cover/colour data clears on navigation, stale snapshot, disconnect or expiry. A reference-keyed palette cache avoids repeated extraction. At most seven small queue previews and one large sleeve/colour preview are retained; the bridge's four-entry cache and response bounds are unchanged. A changed reference fetches a new preview. No arbitrary remote image URL is accepted.

The client retains the v1 request/envelope bounds, hostname verification and independently provisioned trust. The ephemeral HTTPS session has no cookies or credential cache, disallows redirects and caps streamed responses at 32 KiB. Enrollment and its bearer credential stay together in Keychain; pending enrollment is written before the one-use code is sent. Trust replacement is explicit, origin-preserving and commits only after a fresh authenticated probe. It does not silently adopt a new certificate. Playback writes get unique request IDs, an eight-second pending deadline and no automatic replay. Late replies and lost connections preserve an uncertain outcome. Acknowledging that notice sends no command. Reads reconnect with bounded backoff; provider credentials remain on the bridge.

Activation consumes the first contact and starts authoritative refresh. Deactivation cancels normal work, clears artwork, discards speech and releases the idle timer. Touched returns to Still after eight seconds. The idle-hold timeout releases the app's hold; it is not a promise that iOS locks at that instant. The only background task is a fresh battery observation while external power and network are available. The task has a 15-minute earliest start but the OS decides when it runs. Phase 1 permanently connects the phone to the bank; neither the task nor `charge?` controls a commercial pack. [Apple background scheduling](https://developer.apple.com/documentation/backgroundtasks/bgtaskrequest/earliestbegindate).

Find opens idle. An explicit microphone tap starts capture, shows partial text and stops at 30 seconds without searching. Back, switching to typing, Restart, navigation, loss of fresh state and backgrounding discard capture. Only an explicit search action submits text to shared Results, never playback. Returning to voice input always remains idle. Unsupported on-device recognition fails visibly and leaves typing available; there is no speech-server fallback. [Apple on-device requirement](https://developer.apple.com/documentation/speech/sfspeechrecognitionrequest/requiresondevicerecognition).

## Source-spec reconciliation (D031)

The spec tables and section 0b anchoring take precedence over the old 800 × 480 renders. These additional conflicts require explicit implementation interpretations, with final visual review still open:

- Move the whole transport trio 124 units to keep its spacing with the centered play ring. Moving only Play would overlap Next. Right-side amplifier halves are 72 × 64 separated by eight units inside the 152-unit pill; the older touching 76-unit halves conflict with the target-gap rule.
- Use caps-15 for the voice state rather than the isolated caps-13 instruction. Use the revised 70% secondary ink rather than the older 62% table entries. Font sizes follow the larger app table, not the render's smaller type.
- Compute contrast from the complete field including both glows. A luminance cap of 0.12 alone cannot provide 7:1 with the specified ink. The implementation darkens until sampled primary/secondary ratios exceed 7.2/4.7, then the native snapshot test checks rendered pixels at 7/4.5. The native snapshot suite now executes these checks. It averages the title-adjacent strip before computing contrast, matching the supplied Python gate; the palette calculation also checks the field grid independently.
- Keep the fixture label at y=24 on NOW; place it at y=6 on secondary screens to avoid their y=30 titles. Expand time-label height to 24 units, moving its top to 444, to retain glyphs in the actual font.
- Header buttons move two units upward to preserve the query/filter gap. Find rows begin at 224, Library rows at 148, with 64-unit row hit areas centered inside 72-unit rows. Settings hit areas are 72 inside an 80-unit pitch. This resolves table overlaps against the eight-unit target-gap requirement; the Library row shift exceeds the four-unit comparison tolerance and is explicitly documented rather than silently counted as a match.
- A native artist relationship needs a 56-unit link target below the two-line Detail title. The membership line moves to y=270 to avoid colliding with that target. Exact artist/album links are used when supplied; no guessed catalogue relationship is promoted to a native link.
- System Auto-Lock owns actual sleep. System keyboard, permission prompts and the trust file picker are not clipped by the application's inlay mask. A custom keyboard or private force-lock API is not substituted.

These choices do not revise D030 or edit the retained reference package. Physical acceptance can still require design changes. The automated snapshot gate has now passed Xcode execution and all captures have been inspected; this does not close user or physical acceptance.

## Validation actually performed

| Check | Recorded result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 141 tests passed |
| `node --test tests/test_navigation.cjs` | Five tests passed |
| `python tools/m2_demo.py` | Six silent TLS fixture stages passed |
| Python-generated iOS fixture vectors | Match real `Contract`; socket creation forbidden during the new conformance test |
| Xcode build-input graph, scheme, plist, fonts | Four new Python tests pass, including file coverage, dependency references, permissions, hashes and actual font PostScript names |
| Swift grammar parse | All 15 Swift files parsed using tree-sitter-swift; this does **not** type-check Apple APIs or prove compilation |
| Xcode build and unit/snapshot tests on hosted Mac | Native compilation and all 17 tests passed on iPhone 11 / iOS 18.6: 15 unit/snapshot plus two UI interaction tests |
| Physical phone, on-device speech and bank tests | **Not run** |

The full Python and demo runs used normal Windows permissions for existing protected temporary vault/TLS checks; protections were not weakened. No live NDX/playback/volume operation occurred. Firmware and `docs/still-water/` were checked against their task-start hashes and preserved, including pre-existing D030 edits. The existing prototype and bridge A/A.1 implementation were not changed. Python additions cover project/fixture generation, tests, cloud evidence export and the local screenshot review helper.

## Native review matrix and remaining gate

All 22 supplied reference renders were opened and inspected before implementation. All 23 native state captures from the corrected iPhone 11 snapshot harness were subsequently inspected at full size. The supplied renders remain references, separate from native evidence. Unit snapshots retain images as `.xcresult` attachments and audit layout bounds, minimum type size, measured text height, target dimensions/overlap/gaps, selected table coordinates and sampled rendered title contrast. The UI test exercises the actual keyboard; lifecycle tests cover consumed wake contact, stale state, cancellation, the 30-second limit and uncertain/late writes without replay.

| Reference | Native review state / check |
| --- | --- |
| 01 Sleep | Physical iOS Auto-Lock and inactive-lifecycle test; a black screenshot cannot prove panel-off |
| 02, 03 Presence | Excluded by Brief B |
| 04 Waking | `wake`, frozen mid-reveal |
| 05 Still | `still-fallback`, `still-artwork` |
| 06 Touched | `touched` |
| 07 River | `queue` |
| 08 Ask | `ask-recording`, `ask-stopped` |
| 09 Three | Future, excluded |
| 10–16 | `paused`, `stopped`, `offline`, `pending`, `unknown`, `longtitle`, `noart` |
| 17, 18 | `find`, real-keyboard UI test |
| 19, 20 | `detail`, `library` |
| 21, 22 | `settings`, `display` |
| Additional utilities | `connection`, `device`, `wifi`, `pairing` |

The cloud interaction suite is complete. Review the native gallery with the user next. Install on the selected phone only through a separately configured signing route, verify trust enrollment/recovery, keyboard/inlay interference, lock/wake and microphone permissions, and run the physical evaluation in `iphone-architecture.md` section 8. No standby duration, wake latency, speech quality, visual acceptance, heat, inlay fit or seated readability is claimed.

## Native capture inspection — 25 September 2026

The corrected snapshot harness removes the device notch safe-area inset from the isolated 755 × 346 pt test window. All 23 native state captures were inspected: the serif title hierarchy, two-line long titles, retained offline metadata, disabled/uncertain command states, wake mask, seven queue sleeves/reflections, rows, detail, speech states and utility text are present without accidental non-scroll clipping. Rows intentionally clip at their scroll viewport. Table anchoring and the D031 exceptions remain the comparison basis; the 800-unit reference is not stretched to the 1048-unit native canvas.

The review led to selected-palette markers and removal of the extra explicit dimming from the pending target; the target stays disabled and retains its pending ring. Native interaction checks exposed missed button taps. Idle observation now separates taps from drags, and transparent button labels declare their entire touch rectangle inside the label. The final UI tests pass first-contact consumption, navigation, a search-icon tap near the target edge, and keyboard Return dismissal.

Remaining design/device limits are explicit. The brightness slider and trust form use native controls, so their detailed appearance is not exact reference parity. The system keyboard covers part of the inlay and draws outside the app mask. The system home indicator is visible immediately after touch in the full-screen capture despite the app's auto-hide request. A snapshot of the isolated inlay cannot prove absence of OS chrome on the physical phone; mounted keyboard access and kiosk/Guided Access behavior remain open. Simulator fixture battery is unavailable. No user acceptance, physical speech, TLS/Keychain enrollment on a phone, power or runtime result follows from these captures.

## Passing cloud run and retained evidence

[Run 36130364216](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36130364216) tested `5c211f7e2dbe36f1e36d6156d73b23f105098597` with Xcode 16.4 (16F6), iPhone 11 and iOS 18.6 on macOS 15.7.9. All **17 tests passed**, none skipped: eight controller/lifecycle, five protocol/artwork, two snapshot/palette and two native UI interaction tests. The snapshot test covers **23 states**. The exported review adds full-screen first-contact, real keyboard and after-search captures, giving **26 PNGs**. The final changed captures were inspected; unchanged captures match the previously inspected native pixels.

Private artifact `still-water-ios-6` (ID `10861144380`) has SHA-256 `7a4ac56bcc9926eb9a1d320a8bfae749355caaa109076ed120086a15fe3dfaec` and GitHub expiry 2 October 2026. A local copy and `local/ios/review/review.html` are retained outside Git. [The Windows guide](ios-cloud-build.md) explains regeneration without extracting long xcresult paths. Original PNG bytes and orientation metadata are preserved. The browser tool refused automatic local-file preview; the gallery was checked for valid image links and JavaScript syntax, and PNGs were inspected directly. Open the saved HTML manually in a browser.

Early cloud attempts exposed invalid multiple property-wrapper declarations, a private synthesized initializer, the isolated-window safe-area offset, an incorrectly implemented contrast-strip calculation, ambiguous Search matching and missed button hit areas. These were corrected before the passing run; earlier failures are not counted as passes. Contrast thresholds remain 7:1/4.5:1, with the title-adjacent strip averaged as in the supplied Python gate. The full Windows Python suite initially hit the previously observed connection-aborted error in an existing origin/host rejection test; its unchanged full rerun passed all 141 tests without weakened ACL/TLS checks. Navigation (five tests), the six-stage silent TLS demo, and generated project/vector checks also passed.

The final documentation/gallery-helper commit does not change the tested app, test targets or cloud workflow; its commit message skips redundant CI. No simulator result proves signed installation, real-phone trust/recovery, speech, mounted touch/keyboard access, heat or battery performance.

## TestFlight preparation follow-up

After the user confirmed paid developer membership/admin access, the [silent preview preparation](ios-testflight.md#validation-checkpoint) passed 19 native tests and an unsigned iOS-device Release archive using Xcode 26.3 / iOS 26.2 SDK. Its two additional native tests verify compiled/bundled preview identity and rejection of live transport, enrollment, trust replacement and Keychain operations. The original normal build route is retained; the internal preview cannot activate it. The current preview is unsigned, has not been uploaded and is awaiting the Apple team/bundle identifiers and protected signing inputs. The prior 17-test evidence above remains the earlier implementation checkpoint.

## D034 UI amendment

Album and artist now have separate layouts, with optional bounded metadata (`biography`, `year`, `duration`) and graceful absence. The bridge contract is unchanged; the silent client fixture supplies fictional artist content for design review. Artist album artwork reuses registered authenticated browse/artwork reads and the existing expiring cache, limited to four cards. Artist tabs and list positions live in bounded Back contexts. Find provides progressive fixture transcript feedback, explicit Tap to search and clear/restart on every microphone tap. No actual microphone capture occurs in the internal preview. Presence is not part of this sprint.
