# Decision log

## D001 — Native Naim playback is mandatory

**Accepted, 19 September 2026.** The NDX 2 must use its own native TIDAL implementation. Direct Naim content browsing and a single native playback request have worked. Music Assistant-to-DLNA and alternative audio paths are excluded. TIDAL Connect is distinct and is not an automatic replacement.

## D002 — Small bespoke controller

**Updated, 20 September 2026.** A conventional tablet is too large. Use a compact touch interface in a purpose-made printed enclosure. Rectangular and square proportions are both acceptable; screen quality and usability take priority. Exact dimensions follow hardware evaluation.

## D003 — Battery life and physical substance

**Accepted direction.** Weeks of standby, persistent now-playing display where practical, and a substantial battery. Weight is a positive part of the design. Capacity, total mass, charging and runtime are not finalized.

## D004 — E-paper and ESP32 remain candidates

**Updated, 20 September 2026; see D009.** E-paper remains an alternative for persistent information. The leading display is now a colour LCD with integrated ESP32-S3. Neither ESP32 Naim firmware nor display/battery performance has been demonstrated.

## D005 — Pi is available, not mandatory

**Accepted architectural option.** The existing Home Assistant Pi can support control/metadata processing. Direct native browsing means a bridge is not automatically required. No audio may be relayed through it.

## D006 — Software proof before final hardware

**Accepted workflow.** Complete native search, queue, volume and quality validation before final component purchase and enclosure CAD. A representative screen prototype then verifies that the interaction is pleasant enough.

## D007 — Project repository

**Updated, 20 September 2026.** The user selected [leweelewee/NDX2-Controller](https://github.com/leweelewee/NDX2-Controller) as the project repository. The original local project and existing GitHub initial commit are preserved in the combined history. Personal reports remain ignored locally. Repository visibility is unchanged; no distribution licence has been selected. There is no affiliation with Naim or TIDAL implied by the project name.

## D008 — Prototype catalogue search separately from playback

**Provisional implementation, 20 September 2026.** Test TIDAL's public metadata API using this project's own developer application. Native Naim playback remains mandatory. The search adapter cannot play audio; candidate IDs require native resolution before handoff. The developer app is now created and live catalogue search/pagination passed. Whether this becomes the final architecture still depends on native result compatibility and small-screen usability. Credentials were used in memory only; deployment storage is undecided.

## D009 — Preferred display and base battery

**Accepted preference, 20 September 2026; final hardware selection pending validation.** The user prefers Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case. Responsive browsing, search and colour artwork motivate the choice. The large battery will be separate and mounted in the base; an included battery is not required or a selection advantage. Screen aspect ratio is flexible. Do not confuse this model with Waveshare's 4B or other 4.3 variants.

Onboard power circuitry versus an external charger/converter remains a research choice. Touch wake, screen-off standby, charging and runtime must be measured. No purchase is recorded. See [hardware design and BOM](hardware/README.md).

**Reopened, 20 September 2026; superseded selection status by D016.** The user confirmed the Waveshare has not been purchased and requested comparison with an old Android phone. Preserve this entry as history, not a final selection instruction.

## D010 — Voice and AI discovery

**Accepted, 20 September 2026.** Add explicit microphone recording and natural-language music discovery, with moods, reference artists and refinements. OpenAI handles interpretation/transcription off the controller; project key creation and its local destination were explicitly approved. Suggestions become catalogue searches, never direct playback commands. Microphone hardware and power remain unverified; computer-browser transcription is user-confirmed. Colours can follow the eventual enclosure material. See [voice discovery](voice-discovery.md).

## D011 — Bounded wired System Automation volume

**Verified implementation, 20 September 2026.** Use the NDX automation IR commands for amplifier volume, preserving fixed audio output. Both directions were audibly confirmed using one press frame and four held frames, spaced 0.2 seconds apart. A UI tap sends this bounded sequence once; no continuous hold, retries, numeric slider or inferred amplifier level. Controls remain busy until completion. See [protocol evidence](research/system-automation.md).

## D012 — Real TIDAL collection actions

**Accepted implementation direction, 20 September 2026.** Hearts and library saves use the project's own TIDAL OAuth authorization, limited to collection read/write. Native Naim playback remains mandatory and independent. Do not implement cosmetic local hearts in live mode or silently assume a failed saved-state lookup means unsaved. Tokens stay in memory for this prototype. Provide persistent Back navigation with restored browsing context. See [collection design and setup](tidal-library.md).

## D013 — Close software feasibility and move to detailed design

**Accepted, 20 September 2026.** The user agreed that software feasibility has achieved its purpose. Freeze the working reference at `software-feasibility-v1`; use the repository as the source of truth for decisions, evidence, implementation and backlog. Further feature expansion must answer a next-phase design question. Detailed design prioritizes physical screen/touch/power proof, bridge deployment and authentication/recovery, followed by enclosure packaging. Open reliability checks and feature gaps remain explicit in the roadmap and handover. Chat history is supporting history, not a required project specification.

## D014 - Original River Stone, stationary on the coffee table

**Accepted by user, 20 September 2026.** Resume the original 01 River Stone rather than its four later variations or Crescent embrace. The controller stays on the table. Preserve its asymmetric pebble form, inset landscape display and premium appearance; manufacture at home on the Bambu Lab P1S with 0.4 mm nozzle and favour minimal finishing. This removes the separate handheld, second battery and controller-to-base charging interface. One shell plus recessed underside cover, low battery and rear cable charging are the working construction proposal. Dimensions, screen angle, filament and electrical parts remain provisional. The user authorized continued development without repeated confirmation and requested repository updates. See [River Stone layout](hardware/river-stone/README.md).

## D015 — Dedicated display; repurposed phone route ruled out

**Accepted by user, 21 September 2026.** Visual identity is a primary requirement. Rule out an intact Android phone or iPhone inset into the enclosure: the user considers its recognizable phone proportions and details incompatible with the purpose-built audio-controller appearance. Do not pursue a dismantled-phone route in the current design; no concrete integration approach has demonstrated sufficient visual benefit to justify the additional packaging and servicing complexity. Reconsider only if a specific proposal resolves that visual concern.

Continue with a dedicated display assembly and the original River Stone enclosure direction. Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case, remains the leading candidate pending physical screen, touch-wake and power validation. This is a design decision, not evidence that phone battery life is inadequate; no phone standby trial was performed.

## D016 — Reopen display selection: Waveshare versus old Android phone

**Superseded by D017, 21 September 2026.** Renumbered from a duplicate D014 to preserve the existing River Stone decision ID; this entry is historical.

**Accepted user direction, 20 September 2026.** No Waveshare purchase has occurred. Compare the exact ESP32-S3-Touch-LCD-4.3B without case against an old Android phone; phone model, Android version, ownership/condition and dimensions remain to be recorded. Neither candidate is selected. The compact bespoke touchscreen, substantial printed enclosure, large base battery, cable-free table use and touch-wake intent remain. A phone is not approval to switch to a conventional tablet or drop these requirements.

Validate both routes for seated usability, touch wake, real energy consumption, microphone, charging and recovery before selecting. A phone's existing internal battery does not establish compatibility with the intended base battery or weeks of standby. Do not remove/bypass its battery or assume always-on charging is suitable. See [candidate comparison](hardware/display-comparison.md). Existing Waveshare research remains useful candidate-specific evidence, not the governing selection.

## D017 — Waveshare selected; Android ruled out

**Historical selection; superseded by D030 on 25 September 2026. Waveshare is parked fallback.**

**Accepted user decision, 21 September 2026.** Select Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case (SKU 27848), 800 × 480. Repurposed phones are ruled out for the visual-design reasons recorded in D015; no failed phone trial is claimed. This supersedes the D016 comparison and closes display choice while retaining D015's rationale. Continue with HP-01 screen/touch/wake/power proof, embedded UI, microphone selection and River Stone packaging. Selection is not purchase authorization or proof of touch wake, battery runtime, charging compatibility or enclosure fit. Procurement remains not ordered pending a recorded update. All native Naim playback and existing System Automation requirements remain unchanged.

## D018 — Bridge partition for detailed-design trials

**Repository reconciliation, 21 September 2026:** this draft previously used D015. Renumbered to D018 to preserve the published D015 dedicated-display decision from commit `4e487da`; the two decisions address different subjects.

**Provisional engineering direction, 20 September 2026; host selection conditional.** Put provider credentials, metadata/artwork processing, voice/AI requests and native Naim adapters on an always-on bridge. Evaluate the existing home-automation Pi first after private read-only inventory; no installation or host migration is approved by this record. Use embedded UI firmware for the selected Waveshare (D017); the earlier Android browser/kiosk branch is retired. Keep native music playback entirely on the NDX 2 and retain D011 amplifier semantics. [Deployment design](deployment-design.md) defines security and recovery gates; no LAN-ready implementation is claimed.

## D019 — Parallel M2 software implementation and conservative command delivery

**Accepted user scope and implemented engineering direction, 21 September 2026.** Start hardware-independent implementation alongside delayed procurement. Preserve D015 dedicated-display identity, D017 selected SKU and D018 provisional bridge partition; their IDs were reconciled by content/provenance in `fcf1406`, not reassigned here. Native C/LVGL UI with isolated board interfaces; development-host authenticated HTTPS bridge; protected per-controller credentials and durable mutation-ID suppression. Never replay uncertain mutations. Fixture evidence and build preparation do not close HP-01, physical P3/P4/P5 or Pi deployment. [M2 runbook](m2-software.md) records exact scope and remaining integration work.

## D020 — Approved desktop UI baseline

**Accepted by user, 22 September 2026.** The user approved the iterated design after icon-only Search. [Approval](ui-review/approval.md) identifies the source hash and final interactions; it supersedes conflicting earlier rough UI proposals, including artwork-side volume and the separate voice review step. Implement the design in shared native C/LVGL; the browser board remains a design reference. D011 command semantics and D017/D018 architecture remain unchanged. Approval is not firmware parity, production provisioning or HP-01/physical P3/P4/P5 acceptance. See [closeout](m2-closeout.md).

## D021 - Bounded authenticated artwork preview

**Implementation choice within the authorized M2 slice, 22 September 2026.** Keep artwork processing on the D018 bridge and send fixed 80 x 80 RGB565 previews through the authenticated v1 read envelope. Native code validates fixed bounds and renders with LVGL; provider URLs and JPEG decoding stay off the controller. Preserve approved artwork-space dimensions, clear stale/obsolete covers and leave optional failures unavailable. This fits the current 32-KiB response bound without a new image route. Resolution is provisional; live visual quality, deployment-host resource profiling and physical memory remain validation work. See [contract](controller-contract-v1.md) and [evidence](m2-artwork.md).

## D022 - Controller-local display preferences

**Authorized offline M2 slice, 22 September 2026.** Save palette, brightness intent and timeout on the controller, separately from bridge/account credentials and commands. Use a versioned, strictly bounded record, coalesced saves and visible failure states. Windows writes use atomic replacement and a writer lock; ESP32 uses one separate NVS blob without erase-on-error recovery. Missing records use defaults; corrupt/future records remain untouched and session-only. Brightness/sleep remain hardware-unbound until physical validation. See [implementation and evidence limits](m2-preferences.md).

## D023 - Bounded offline recovery without command replay

**Authorized M2 continuation, 22 September 2026.** Recreate a failed desktop pipe/helper only for a subsequent request, never to retry a mutation. Shared LVGL treats a bridge boot change as lost interaction context, requires fresh authoritative state and contact release, and invalidates requests pending eight seconds. Preserve browsing and local preferences; clear remote artwork/membership claims. Unknown mutation outcomes remain unknown where snapshots cannot prove completion, particularly amplifier commands. This implements D019 recovery rather than changing native playback or D011. See [fixture evidence and physical limits](m2-recovery.md).

## D024 - Durable host enrollment and explicit device recovery

**Authorized offline design/fixture slice, 22 September 2026.** Persist setup intent before a single pairing request; lost replies remain uncertain and require local inventory/revocation decisions, never automatic re-pairing. Bind newly persisted controller authorization to independently supplied origin/trust, keep status redacted, and distinguish local forgetting from bridge revocation. No new HTTP admin endpoint or physical secret installer. Preserve legacy fixture compatibility without claiming retroactive binding. [Provisioning design and evidence](m2-provisioning.md) records recovery and production gates.

D024 implementation follow-up: the [host setup console](m2-setup.md) now requires private terminal code entry and explicit local trust/forget confirmations, sends no automatic verification or command, and supports local recovery without a trust file. Native UI and physical provisioning gates are unchanged.

## D025 - Explicit same-origin trust replacement

**Authorized offline slice, 22 September 2026.** Retain controller pairing across leaf renewal under unchanged trust. Permit an independently verified, explicitly confirmed same-origin trust update to probe one authenticated snapshot and atomically replace the saved trust digest while preserving identity and command history. Fail closed on invalid TLS, origin changes, unsupported enrollment or storage uncertainty; no automatic rollback/re-pair/command replay. [Evidence and deployment limits](m2-trust.md) distinguish fixture renewal from production certificate installation.

## D026 - Replaceable desktop package with external user state

**Authorized offline slice, 22 September 2026.** Assemble a Windows x64 portable development package from the existing native build, SDL and installed Python 3.14.3 standard runtime. Include an explicit client file list, isolated imports, license notices and content hashes. Keep configuration, trust, pairing and preferences outside replaceable application files; launch checks setup and allows transient offline recovery without replay. No provider adapter/service, credential migration, installer privileges or automatic update is added. [Evidence and release limits](m2-package.md) distinguish a same-host upgrade rehearsal from production distribution.

D020 implementation follow-up, 23 September 2026: user requested high-end native visual polish after confirming transport fixes. The [bounded native refinement](m2-visual-polish.md) preserves the approved layout and source identity, using native outline icons and palette/type hierarchy. This does not revise D011/D018/D021 or close physical gates.

## D027 - Design for the coffee-table object, beyond the rough UI prototypes

**User-directed, 23 September 2026.** The user clarified that the approved screens were rough prototypes and requested high-end visual/UI design assessed against the River Stone coffee-table ornament, followed by iteration until the designer's quality gate passes. D020 remains functional/interaction history; its pixel layout and unboxed styling are no longer a final visual constraint. Preserve the original mineral pebble enclosure direction and all playback, security, no-replay, hardware and power constraints. Do not interpret an ornamental display as permission for always-on operation or a new power claim.

The [native design review](m2-object-design.md) records three render/review iterations and a desktop composition/state gate. The music view now uses 280 px artwork, restrained chrome and a subtle primary-control disc. The historical approved HTML/hash is preserved as a reference. Desktop designer acceptance does not imply user acceptance, physical readability, live artwork quality or HP-01/P3/P4/P5 completion.

## D028 - Pause design implementation pending revised user direction

**Explicit user direction, 23 September 2026.** The user said: "Pause there, we have a working protoptype but the design direction is not where I want to be. I will return with a revised direction". Retain the functional prototype at b36098d; stop the current aesthetic iteration. D027's designer-assessed pass does not establish user acceptance and no longer supplies an active design brief. D020/D027 visual references are history; future composition follows the revised user brief. Playback, security, recovery and hardware constraints remain intact. No automatic next artwork/polish slice is authorized by older prompts. [Chat closeout](chat-closeout-2026-09-23.md) preserves evidence, artifacts and resumption instructions. The untracked still-water directory was preserved without adopting its contents.


## D029 — Still Water Brief A bridge additions, screen choice open

**Explicit user authorization, 23 September 2026.** Adopt `docs/still-water/` as revised-direction material for Brief A only. Preserve b36098d and newer work. Add authenticated, bounded artwork reads up to 320 × 320 alongside the unchanged 80 × 80 protocol, one volatile last battery report and a charge-window query. Chunk artwork within existing response/cache payload bounds; use report charging state within 35–74%, request charging below 35%, stop at 75%, and fail closed when no report is younger than one hour. See [wire contract](controller-contract-v1.md#still-water-brief-a-extension--23-september-2026).

Screen selection remains open; no iPhone selection is recorded. D028 continues to record the design pause. Do not implement either UI or change firmware under Brief A. The package's platform-selection claims and duplicate D028 draft are proposals, not accepted decisions. No credential-free bridge route: any on-table visual trial uses the private artifact link or a throwaway static server outside the repository. Native Naim playback, D011, trust, protected credentials, recovery and no-replay constraints remain.


**D029 amendment — Brief A.1, 23 September 2026.** The user authorized a single coherent commit and non-force push of Brief A/A.1 and the adopted `docs/still-water/` package. Extend `charge?` with `reason`: `window` for every fresh report, whether the charge answer is yes or no (explicit user clarification); `stale` when a report exists but is not younger than one hour; `none` when no report has arrived since boot. Stale and none always return `charge: "no"`. Preserve thresholds, receipt-time freshness, last-report-only storage and the authenticated envelope. No new decision ID, UI, firmware or HTTP route change; screen selection remains open. The source design package is committed unchanged, with its draft selection claims still subject to the preceding D029 scope.

## D030 — iPhone 11 and selected UGREEN power bank; Waveshare parked

**Explicit user direction, 25 September 2026.** Active hardware is iPhone 11 with the selected **UGREEN Nexode 20000mAh PD 20W QC Power Bank**. Park the Waveshare base design as a retained fallback. This supersedes D017's active screen selection, D015's exclusion of an intact iPhone for this concealed mounting approach, and D029's open-selection status. Keep past purchasing and validation records intact; no cancellation, new purchase, physical fit or runtime proof is implied. Exact bank SKU remains to be confirmed for dimensions.

The user suggests mounting from behind/inside the stone so the phone edges disappear and it reads as a purpose-made screen. Develop the [rear-loaded cradle and masked aperture proposal](hardware/river-stone/iphone-mount/README.md) for agreement. A 118 × 54 mm aperture, recess depth, gasket, sensor masking and cradle details are provisional, not accepted production dimensions. **Subsequent user clarification, 25 September 2026:** original **01 River Stone** is the sole visual reference for the overall body and screen/stone interface. “04 Tide pool” is superseded reference history, not a source for the new contour. Mounting must not obstruct the iPhone microphones; preserve acoustic paths and validate mounted voice pickup.

This resumes physical mounting/interface design under the revised brief, not automatic execution of embedded Still Water prompts or authorization to implement the iOS app. D029 bridge semantics, native Naim playback, D011, credentials, trust and no-replay requirements remain unchanged. The iPhone software/power-module draft is not adopted wholesale: operating mode, charge switching and runtime require separate proof with the selected commercial bank. The [fallback index](hardware/river-stone/fallback-waveshare.md) preserves the Waveshare CAD/slicing work.

## D031 — Brief B native client implementation boundaries

**Implementation under the user's explicit revised Brief B request, 25 September 2026.** Produce the thin native SwiftUI app and its Xcode/test targets in `ios/`, using the existing authenticated v1 actions and offline synthetic Python-contract fixtures. D030 remains the hardware selection; this entry does not reselect the phone or bank. Preserve the working prototype, A/A.1, all firmware and the supplied revised-direction documents. Do not add HTTP routes or direct NDX/provider access.

Use independently provisioned, hostname-validated TLS trust and a durable Keychain enrollment record; never automatically re-pair or replay a mutation. Consume the first wake contact, reject stale snapshots/late command replies and retain uncertain outcomes. Native speech is on-device only and can submit only an explicit text search. Phase 1 uses the permanent bank connection; the app reports observations and neither switches charging nor pretends to control iOS Auto-Lock. Background reports are opportunistic, not a timing guarantee.

Resolve the conflicting source values in favor of minimum text/target/gap, honest availability and rendered contrast. The transport trio moves together with the centered ring; amplifier hit areas are 72 units separated by eight. Use caps-15 and 70% secondary ink, compute contrast including glows, and preserve glyph height. The secondary fixture label, Library row start and Detail membership placement have explicit exceptions where the source's positions would collide. [The implementation report](ios-still-water.md#source-spec-reconciliation-d031) records exact interpretations and the reference review matrix without modifying the reference package.

This is not visual or hardware acceptance. Windows lacks Xcode/Swift; native build/type-check, XCTest, complete snapshot inspection and physical evaluation remain required. Record source checks separately from simulator/device evidence and never infer standby life, wake latency, speech quality or seated readability from the fixtures.


**Cloud validation follow-up:** the user authorized a GitHub-hosted unsigned simulator build from Windows. Use the private build branch, read-only workflow permissions, silent fixtures and bounded runtime/artifact retention. No signing or distribution is part of this follow-up.

D031 cloud validation outcome, 25 September 2026: native compilation, the 23-state snapshot matrix and both UI interaction tests now pass (17 tests total). The Windows review gallery retains original captures and references. [The evidence report](ios-still-water.md#passing-cloud-run-and-retained-evidence) identifies the tested commit, corrections and remaining physical/user gates. This follow-up completes simulator validation without a new platform decision or signing/distribution authorization.

**D031 TestFlight preparation follow-up, 25 September 2026:** the user confirmed paid Apple Developer Program membership and Account Holder/Admin access after the proposed private TestFlight route. Prepare an internal-only silent preview, upgrade the hosted build to Xcode 26.3, add distribution resources and verify a device archive. A compile-time preview mode starts in fixtures and refuses live transport, Keychain enrollment, speech capture and background reporting. Signing uses a supplied distribution certificate/profile in an ephemeral runner keychain; no automatic certificate/profile creation or revocation. Upload requires the selected team/app identifiers and protected signing inputs. This does not authorize live playback or close user/device acceptance.

**D031 registration follow-up, 25 September 2026:** use the user-proposed stable bundle identifier `com.ndx2.controller`, now registered. The App Store Connect record uses NDX2 Controller because Still Water was unavailable there; the phone display name remains Still Water. This is a private, non-commercial TestFlight preview. No public release or banking changes are part of the work.

## D032 — Restore functional parity and phone usability

**Explicit user authorization, 25 September 2026.** Following review of TestFlight 0.1.0 (1.2.0), the user reported wasted display space, small text/transport controls, unwanted Amp wording, and missing artist/album navigation and collection controls. The user accepted the proposed remediation. Retain Still Water's visual direction while restoring the agreed controller interactions. Fit the landscape phone with a narrow non-interactive border and keep targets clear of notch/home gestures; enlarge actual rendered type and transport controls, use volume icons, expose exact artist/album links and stateful track Like/Unlike, album Add/Remove and artist Follow/Unfollow. Settings must not obstruct artist navigation.

A prototype-to-iPhone checklist and real full-phone interaction checks replace visual-reference matching as the sole acceptance basis. Preserve authentication, no replay, uncertain outcomes, unavailable metadata and native Naim playback. Publish only the silent internal TestFlight preview for this review; no live NDX, bridge, speech, firmware or hardware mutation is authorized. Physical readability and user acceptance remain open until the replacement is reviewed. See [remediation checklist](ios-remediation.md).

D032 delivery: the internal silent remediation build **0.1.0 (2.1.0)** passed 23 native tests and archive/sign/upload checks, processed successfully, and is available to the existing test group. [Evidence](evidence.md#d032-native-remediation-validation--25-september-2026) and [parity checklist](ios-remediation.md) preserve the user/device acceptance gate.


**D032 layout amendment, 25 September 2026:** user review of build 2.1.0 identified notch collision and the black perimeter. Retain the existing landscape-right lock only. Fit content inside the system safe area plus an 8 pt inactive inset; extend the same music colour field across the full display, including the safe perimeter. Make NOW Like a compact borderless action alongside the album; simplify secondary headers to one plain chevron-and-Back action preserving previous-screen history. Other suggested rearrangements are not adopted. All 23 native tests passed; signed build 0.1.0 (3.1.0) was uploaded and Apple shows Testing in the existing internal group. Physical mounted-phone acceptance remains open.


## D033 — One voice-first Find entry with explicit recording

**Explicit user direction, 25 September 2026:** enlarge NOW's heart and remove its visible label; use icons for Find and Library. Find opens the voice input screen idle, never recording automatically, with Type instead as a secondary input. Remove the redundant NOW microphone shortcut and the former dedicated text-entry Find page. Typed and spoken submissions share the existing bounded results/filter/detail flow. Results can reopen Find, while Back preserves browsing history and always cancels recording. Keep accessible icon labels, observed membership state, the locked safe-area layout and the silent preview boundary. Search never initiates playback. All 25 native tests passed in run 36186308393; signed build 0.1.0 (4.1.0) processed successfully and is Testing in the existing internal group. Physical/user acceptance remains open.

**D033 heart clarification:** the user explicitly rejects the red liked heart. Use the existing warm ivory ink for both states: outlined when unsaved and filled when saved, never an emoji/system-red glyph. Include a saved NOW-state capture in native review.

**D033 Still-screen follow-up:** the user requests slightly larger resting artwork and all text shifted right correspondingly. Increase resting artwork 272 to 296 design units (about 9%), retain its vertical centre, shift the resting text origin 368 to 392 and reduce its width to retain the safe right edge. Touched control layout is unchanged. Validate resting, paused/stopped and long-title cases in the native snapshot suite.

## D034 — Single UI amendment sprint: browse hierarchy and quieter Find

User authorization, 25 September 2026: implement the accumulated album, artist and Find recommendations together. Remove NOW elapsed/total text while retaining the progress line. Album uses one title, a left-aligned artist link, primary Play, a quieter stateful library action and numbered tracks with available durations. Artist has a portrait/neutral illustration, short available biography with Read more, Follow/Following, and Albums/Tracks/About tabs; preserve browsing context on Back. Missing provider metadata must remain honest; the silent fixture supplies fictional biography, albums and durations for review, not evidence of live integration.

Find keeps explicit microphone start, replaces secondary typing wording with a labelled keyboard icon, centers ripples on the microphone and progressively displays fixture text. Tap to search submits explicitly; every microphone tap clears/restarts input. Remove the redundant hint, developer footer, Restart and Stop & search buttons. Real speech remains disabled in the distributed silent preview. Keep the locked safe-area layout, warm ivory membership states and existing authenticated bridge boundary. Presence is expressly excluded and is not queued. One final internal TestFlight update is authorized after native validation; no live NDX, firmware, route or tester changes.


## D035 — Brief B1 refinement on an isolated branch

User authorized proceeding on 26 September 2026 after review. Branch `codex/still-water-b1` starts from the clean D034 checkpoint `66ec6fd`; preserve the main checkout and earlier releases. Adopt revised B1 NOW/Find/album/artist hierarchy, explicit Ready-before-search voice flow, optional default-on two-second silence stop, artist portrait registration and a bounded authenticated biography read. This supersedes D033/D034 interaction details only where B1 explicitly changes them. D030 hardware and D011/native playback remain unchanged.

Reconciliation: retain full-bleed field, locked orientation, system safe area plus 8 pt, enlarged transport, 8-unit target gaps and plain history-preserving Back. Coordinates adapt the 800-wide reference to the existing 1048 canvas. Keep track likes in rows/details and an artist Tracks choice when tracks exist; row taps retain detail navigation, with explicit Play on detail. Missing portrait/bio/albums are omitted, never represented by invented artist metadata. B1 silence and timeout stop in Ready without search; only the arrow submits. The silent preview still simulates speech and refuses live bridge/audio. Presence remains excluded.

The reviewed source is the revised repository spec and 25-state reference set, not stale filenames in the supplied prompt. Remove obsolete diagnostic captions from implementation even where reference images retain them. Biography is the only widened text field; envelope, artwork registration/expiry, trust, recovery and no-replay bounds remain. Native validation and distribution evidence are recorded separately; no live NDX, firmware, route or tester changes.


D035 delivery: **0.1.0 (6.1.0)** is Testing in the existing internal group after all 28 native tests, archive/sign/upload and Apple processing completed. The isolated branch and older releases remain preserved. B1 phone review is the next acceptance step; this does not revoke the separately recorded initial physical trial result for its earlier configuration.

**D035 visual correction amendment — 26 September 2026:** following the user's rejection of native/reference fidelity, the user authorized a comprehensive visual comparison and correction on the existing B1 branch. Preserve accepted safe-area, transport-target and navigation behavior while correcting hierarchy, spacing, controls and fixture presentation. Correct reference mapping and compare without aspect distortion. Screenshot typography is the current reversible implementation assumption, pending the user's answer about screenshot versus written-font priority; it is not a newly accepted font decision. Native validation is blocked by GitHub Actions billing/spending limits; no corrected release or visual acceptance is claimed. [Audit and remaining work](ios-visual-audit.md).


**D035 shared-boundary clarification — 26 September 2026:** user specifies Now Playing as the common outer content boundary, with its Silent Demo label as the design anchor across screens. Preserve the iPhone 11 left safe area and inactive inset; do not shift the canvas left to gain room. The secondary header inconsistency is confirmed and recorded in the visual audit. The current request is confirmation and affected-screen identification; no new header refactor is claimed in 7.1.0. Native validation and release progress are recorded in evidence.


**D035 Brief B.1 testing amendments — 26 September 2026:** the user completed testing and authorized the accumulated changes as one sprint. Use NOW Silent Demo x48/y24 on all pages; keep the system safe area and 8 pt inset unchanged. Secondary titles move beneath this anchor, with subsequent bands moved down to avoid collision. NOW keeps its mic, shifts transport right 8 units to centre play/pause above it, increases touched artwork 248→256 with text 336→344, removes Find, and aligns all transport/volume centres. Artist tabs and children share the text column. Adopt Library addendum 13–16: six-column 104 covers with 16 gaps and 156 row pitch, stacked playlists, round artist portraits/initial fallback, shared thumbnail rows, settled visible-cover tint and 320 previews for every displayed cover. Preserve detail navigation/track likes, plain Back, fixture-only release and no replay. No bridge, firmware or route changes. Library content starts at y180 to clear the newly required common caption/title/header band; cover sizes and grid x coordinates remain exact.
