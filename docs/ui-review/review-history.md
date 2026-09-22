# Historical UI review notes — superseded proposals included

Archived at closeout on 22 September 2026. Read [approval.md](approval.md) for current decisions; this chronology is not an implementation specification.

# UI design review — approved baseline

**Approved by the user, 22 September 2026.** See [approval and final baseline](approval.md). The entries below are chronological review history; later refinements supersede earlier layouts. Firmware and physical acceptance remain pending.

## Styling revision 02

Settings added on 22 September: a top-bar gear opens Display, Connection and Device. Display previews brightness (30–100%), Sage/Sand/Slate palettes and screen-off preferences, persisted locally with review notes. Brightness is a browser-only visual approximation; timeout is stored without running a timer or pretending to implement hardware sleep. Connection provides synthetic Wi-Fi selection, pairing/revocation and bridge-account guidance; no passwords, real codes, credentials or network changes are involved. Device shows unavailable battery, fixture software and diagnostics, and a first-run Wi-Fi → pairing → Now Playing walkthrough. Settings are not a fifth primary tab. The Display layout, preference persistence and first-run transitions were checked in the browser.

22 September: Now Playing includes synthetic bitrate (`1,411 kbps`, explicitly fixture-labelled), a track-specific like/unlike heart, and album/artist navigation with Back. Track likes are independent of album saves; the unknown-membership preview disables the heart and marks it with `?`. Offline/uncertain states disable mutations. Album opens Mezzanine details; artist opens a separate Massive Attack album list. This remains a local UI simulation: production bitrate must come from observed player metadata and show unavailable rather than infer a value from format or quality labels. No provider collection writes are performed.

First expert styling pass, requested by the user. The board now uses a clearer title/artist/album hierarchy, a compact circular play/pause focus, consistent line icons, quieter navigation, and thumbnail-led result rows. Amplifier controls move below artwork, separate from the track transport. Input fields and selected states use consistent charcoal/sage contrast; surfaces, borders and corner radii are less prominent. The 800 × 480 canvas and both artwork/navigation alternatives remain available. This is a review-prototype change, not approved LVGL implementation. Existing review notes remain stored under the original browser storage key.

Draft, 21 September 2026. This is a reviewable proposal, not accepted product design or replacement firmware. It compares a labelled reconstruction of the documented concept with an actual M2 LVGL fixture capture, and supplies an interactive 800 × 480 proposal.

Run from the repository root:

```powershell
python tools/ui_design_review.py
```

Open `http://127.0.0.1:8766`. The server binds loopback and exposes only the board and the existing `local/m2/native-captures/01-now.bmp` fixture capture. No bridge, credentials, microphone or player is used. If the capture is absent, the comparison image is unavailable; the proposal still works. The source is `index.html` here; the existing browser prototype and shared firmware are unchanged.

## Review sequence

1. Compare the original direction and current fixture under **Compare the starting point**. The original panel is a reconstruction from `docs/design-concept.md`, `docs/interaction-design.md` and `ui/index.html`, not an original screenshot. The fixture panel is an actual capture.
2. Review **Now Playing** first. Compare 240 px and 190 px artwork, and four sections with Voice inside Find versus a fifth Voice tab. The recommendation is 240 px art and four sections, pending user preference.
3. Try Find → album → Back, then Play album → Now Playing. Tap the query for a provisional on-screen keyboard. Inspect Collection, read-only Queue and voice recording/review/cancel. All effects are local simulations; search content and recording time are illustrative fixtures, not real search/recording.
4. Switch state previews: offline, unknown command result, amplifier busy, missing artwork, long title, empty and sign-in required. Observe disabled mutations and explicit reconciliation rather than command replay.
5. Record notes or reply in the conversation with R01–R04 choices. Notes and the two visual options are remembered in browser storage when available; they are not sent to the assistant. Download provides a plain-text review record. Checkboxes are a temporary walkthrough aid, not persistent acceptance evidence.

## Decisions awaiting review

| ID | Proposal | Acceptance needed |
| --- | --- | --- |
| R01 | Prominent artwork, 240 px default; 190 px alternative | Balance between artwork and title space |
| R02 | Playing / Find / Collection / Queue; Speak inside Find | Voice discoverability versus a fifth navigation target |
| R03 | Transport beside track metadata; amplifier controls below artwork | Labels, hierarchy and comfortable placement |
| R04 | Distinct saved / unsaved / unknown with separate row action | Clarity and accidental-activation avoidance |

These are local review identifiers, not accepted architectural decision IDs. No new decision is accepted by generating this board. The palette remains charcoal/sage/sand. Abstract artwork is a locally drawn placeholder; real artwork layout and loading behaviour need implementation after approval.

## Completion criteria

Desktop design completion requires explicit agreement on the core screens, hierarchy, typography, spacing, navigation and alternate states, followed by implementing those approved layouts in shared LVGL and verifying task flows and captures. This board is the first review deliverable. Provider sign-in details, full result-type browsing, loading/empty/error transitions, icon treatment and actual artwork processing are not all implemented by this mockup.

Physical readability, touch targets, seated angle, keyboard accuracy, wake release, microphone and latency remain HP-01/P3 work. Desktop review can settle visual direction now but cannot close those gates. Do not add queue/playlist editing or treat AI suggestions as playback.

Artist/library parity: restored explicit Follow artist / Unfollow artist with Following / Not following status. Album details and track details use Add to library / Remove from library with separate membership status. The Now Playing title opens track details; its heart shares that track membership. Album row and detail actions share per-album fixture state, and saved albums appear in the album collection. Unknown album membership requires a status check before a write. Verified follow, album add and track add in the browser; all remain silent fixture actions.

Navigation/control refinement: Back is now unboxed text navigation; artist/album chevrons are removed while hover/focus and click targets remain. Album/track detail actions show + Library or checked Library, with explicit membership text and accessible add/remove labels; list rows share plus/check/question icons. Volume replaces the Amplifier label and uses paired rounded minus/plus controls without numeric level or repeat. The synthetic bitrate is now 20 px beneath progress (1,411 kbps), with unavailable state offline. Inspected Now Playing and album layouts and verified the library transition and Back.

Playback spacing review: bitrate moved from between timestamps to the source row at 18 px. Now Playing reserves separate metadata, timeline and 100 px transport bands; transport controls retain 72 px targets with 32 px gaps. Verified the rendered layout at the 800 x 480 design canvas. This supersedes the earlier bitrate placement below progress.

Latest layout refinement: remove duplicate top-strip titles for Find, Collection and Queue while retaining active bottom navigation. Move Volume and its paired controls into the right-hand playback band alongside transport, leaving the artwork column clear. Both volume controls still share the bounded-burst busy state. Browser review confirmed Now Playing composition and the simplified Find header.

Control consistency: playback and volume now use unboxed controls throughout. Removed the Play/Pause circle and volume capsule/divider, aligned their 72 px hit areas and kept subtle hover/pressed feedback plus keyboard focus outlines. No changes to command behaviour.

Volume refinement: removed the visible Volume label and replaced standalone minus/plus symbols with speaker-minus and speaker-plus icons. Accessible Volume down/up labels, 72 px targets and shared busy state are retained.

Voice flow update (user direction, 22 September): Find uses an accessible microphone icon. Entry starts the timed recording fixture immediately; Stop & search submits a synthetic transcript to search without playback, Restart discards the attempt and starts again, and Cancel/Back discards and restores the previous context. Recording stops at 30 seconds without automatic search; the user can then search, restart or cancel. This supersedes the review-board transcript-review step; physical capture and firmware integration remain pending. Verified immediate entry, Restart and Stop & search in the browser.
