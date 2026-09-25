# Still Water Brief B — implementation and review report

25 September 2026. The user explicitly requested action on the revised `codex-prompt-B.md`, authorizing a native SwiftUI client under D030. This is a **source and offline-validation checkpoint, not iOS build or visual acceptance**. The host has no Xcode, Swift compiler or iPhone simulator. [Build and silent-trial instructions](../ios/README.md) are ready for a Mac.

## Implemented source

`ios/StillWater.xcodeproj` contains the app, unit/snapshot tests and UI tests. Bundled Instrument Serif Regular/Italic and Geist Regular/Medium include pinned upstream revisions, SHA-256 hashes and their OFL notices. The 1048 × 480 design canvas is scaled once by 0.7206 and clipped to a centered 755 × 346 pt window. A native paragraph renderer supplies the serif 1.02-em line height instead of accepting the font's 1.3-em default.

NOW includes Still, Touched, wake reveal, paused/stopped, long-title, missing artwork, offline, pending and uncertain-command compositions. The client includes read-only Up next with seven sleeve sizes and one reflected image draw per available cover; Find with the real system keyboard; native Detail, Library, Ask and the Settings group. Native browse resolves candidates before exposing Play; the bridge resolves again for every actual play. No play-next, queue editing or numeric amplifier claim is added. Missing queue art remains text; play-time estimates are omitted when the bridge has no durations.

Artwork uses registered authenticated actions: the 80-pixel preview supplies colour extraction and bounded queue thumbnails; 320-pixel sleeves assemble 16 chunks only when reference, dimensions, digest, boot, generation and monotonic expiry agree. Cover/colour data clears on navigation, stale snapshot, disconnect or expiry. A reference-keyed palette cache avoids repeated extraction. At most seven small queue previews and one large sleeve/colour preview are retained; the bridge's four-entry cache and response bounds are unchanged. A changed reference fetches a new preview. No arbitrary remote image URL is accepted.

The client retains the v1 request/envelope bounds, hostname verification and independently provisioned trust. The ephemeral HTTPS session has no cookies or credential cache, disallows redirects and caps streamed responses at 32 KiB. Enrollment and its bearer credential stay together in Keychain; pending enrollment is written before the one-use code is sent. Trust replacement is explicit, origin-preserving and commits only after a fresh authenticated probe. It does not silently adopt a new certificate. Playback writes get unique request IDs, an eight-second pending deadline and no automatic replay. Late replies and lost connections preserve an uncertain outcome. Acknowledging that notice sends no command. Reads reconnect with bounded backoff; provider credentials remain on the bridge.

Activation consumes the first contact and starts authoritative refresh. Deactivation cancels normal work, clears artwork, discards speech and releases the idle timer. Touched returns to Still after eight seconds. The idle-hold timeout releases the app's hold; it is not a promise that iOS locks at that instant. The only background task is a fresh battery observation while external power and network are available. The task has a 15-minute earliest start but the OS decides when it runs. Phase 1 permanently connects the phone to the bank; neither the task nor `charge?` controls a commercial pack. [Apple background scheduling](https://developer.apple.com/documentation/backgroundtasks/bgtaskrequest/earliestbegindate).

Ask starts on-device capture, shows partial text, stops at 30 seconds without searching, and discards capture on Restart, Cancel, navigation, loss of fresh state or backgrounding. Only an explicit Stop & search submits text, never playback. Unsupported on-device recognition fails visibly and leaves typing available; there is no speech-server fallback. [Apple on-device requirement](https://developer.apple.com/documentation/speech/sfspeechrecognitionrequest/requiresondevicerecognition).

## Source-spec reconciliation (D031)

The spec tables and section 0b anchoring take precedence over the old 800 × 480 renders. These additional conflicts require explicit implementation interpretations, with final visual review still open:

- Move the whole transport trio 124 units to keep its spacing with the centered play ring. Moving only Play would overlap Next. Right-side amplifier halves are 72 × 64 separated by eight units inside the 152-unit pill; the older touching 76-unit halves conflict with the target-gap rule.
- Use caps-15 for the voice state rather than the isolated caps-13 instruction. Use the revised 70% secondary ink rather than the older 62% table entries. Font sizes follow the larger app table, not the render's smaller type.
- Compute contrast from the complete field including both glows. A luminance cap of 0.12 alone cannot provide 7:1 with the specified ink. The implementation darkens until sampled primary/secondary ratios exceed 7.2/4.7, then the native snapshot test checks rendered pixels at 7/4.5. These are source assertions until run on iOS.
- Keep the fixture label at y=24 on NOW; place it at y=6 on secondary screens to avoid their y=30 titles. Expand time-label height to 24 units, moving its top to 444, to retain glyphs in the actual font.
- Header buttons move two units upward to preserve the query/filter gap. Find rows begin at 224, Library rows at 148, with 64-unit row hit areas centered inside 72-unit rows. Settings hit areas are 72 inside an 80-unit pitch. This resolves table overlaps against the eight-unit target-gap requirement; the Library row shift exceeds the four-unit comparison tolerance and is explicitly documented rather than silently counted as a match.
- A native artist relationship needs a 56-unit link target below the two-line Detail title. The membership line moves to y=270 to avoid colliding with that target. Exact artist/album links are used when supplied; no guessed catalogue relationship is promoted to a native link.
- System Auto-Lock owns actual sleep. System keyboard, permission prompts and the trust file picker are not clipped by the application's inlay mask. A custom keyboard or private force-lock API is not substituted.

These choices do not revise D030 or edit the retained reference package. Physical acceptance can still require design changes. The source snapshot gate must not be described as passed before Xcode execution and inspection.

## Validation actually performed

| Check | Result on Windows |
| --- | --- |
| `python -m unittest discover -s tests -v` | 141 tests passed |
| `node --test tests/test_navigation.cjs` | Five tests passed |
| `python tools/m2_demo.py` | Six silent TLS fixture stages passed |
| Python-generated iOS fixture vectors | Match real `Contract`; socket creation forbidden during the new conformance test |
| Xcode build-input graph, scheme, plist, fonts | Four new Python tests pass, including file coverage, dependency references, permissions, hashes and actual font PostScript names |
| Swift grammar parse | All 15 Swift files parsed using tree-sitter-swift; this does **not** type-check Apple APIs or prove compilation |
| Xcode build, XCTest and simulator snapshots | **Not run: unavailable on this host** |
| Physical phone, on-device speech and bank tests | **Not run** |

The full Python and demo runs used normal Windows permissions for existing protected temporary vault/TLS checks; protections were not weakened. No live NDX/playback/volume operation occurred. Firmware and `docs/still-water/` were checked against their task-start hashes and preserved, including pre-existing D030 edits. The existing prototype and bridge A/A.1 implementation were not changed. New Python work is confined to project/fixture generation and tests.

## Native review matrix and remaining gate

All 22 supplied reference renders were opened and inspected before implementation. No render is evidence of the native app. Unit snapshots retain images as `.xcresult` attachments and audit layout bounds, minimum type size, measured text height, target dimensions/overlap/gaps, selected table coordinates and sampled rendered title contrast. The UI test exercises the actual keyboard; lifecycle tests cover consumed wake contact, stale state, cancellation, the 30-second limit and uncertain/late writes without replay.

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

The next gate is to compile/type-check with Xcode, fix any build or test failures, inspect **every** resulting native capture against its reference and the anchored tables, and verify labels/targets within the declared exceptions. Geometry instrumentation is not a substitute for visual inspection. Then install on the selected phone, verify signing, trust enrollment/recovery, keyboard/inlay interference, lock/wake and microphone permissions, and run the physical evaluation in `iphone-architecture.md` section 8. No standby duration, wake latency, speech quality, visual acceptance, heat, inlay fit or seated readability is claimed.
