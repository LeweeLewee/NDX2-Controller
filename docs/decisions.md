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

**D030 aperture revision — 26 September 2026.** The user rejected the small aperture and proposed 6.5 mm overlap inward from the outer phone edge. Adopt equal overlap on all four edges as the next physical-trial baseline: 137.9 × 62.7 mm on the nominal iPhone 11 body, superseding 118 × 54 mm. Maximise screen exposure; preserve microphone inlets and open acoustic paths with local lip relief and interrupted gasket as necessary. Notch concealment, corner geometry and relief dimensions require actual phone registration; no acoustic or production-fit approval is implied.

**D030 further aperture revision — 26 September 2026.** User reduced overlap to 6 mm on all four outer phone edges, superseding the 6.5 mm trial. Current nominal aperture is 138.9 × 63.7 mm. Microphone clearance and physical registration requirements remain unchanged.

**D030 partial aperture acceptance — 27 September 2026.** User passes the 138.9 × 63.7 mm window size, requests small radii because square corners expose areas outside the iPhone screen. Preserve 6 mm overlap and aperture bounds. R3 mm on all four corners is the next engineering trial, not an accepted or measured radius. Microphone clearance remains mandatory.
