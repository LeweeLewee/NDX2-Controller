# Coffee-table controller — design concept

> **D030 update — 25 September 2026:** iPhone 11 + selected UGREEN power bank replace Waveshare as active physical hardware. [Mounting/interface proposal](hardware/river-stone/iphone-mount/README.md) is under discussion. Earlier Waveshare hardware/UI implementation details below are retained fallback; native playback and bridge security requirements remain. This physical-design update does not implement or approve the entire iPhone software/power draft.

Revision 0.2 — 20 September 2026. Published baseline for parts investigation and the first UI prototype.

## Selected screen for the concept

**Waveshare ESP32-S3-Touch-LCD-4.3B, standard version without case (SKU 27848).** Use its 4.3-inch colour IPS touchscreen and 800 × 480 landscape canvas as the working prototype baseline. ESP32-S3, Wi-Fi and touch are integrated. This is the user's preferred prototype selection; hardware validation and final purchase selection remain open.

This replaces the earlier approximately square e-paper screen assumption. The physical direction is now the original 01 River Stone, stationary on the coffee table; see D014. The enclosure follows the actual display assembly, rather than forcing square proportions.

See the [manufacturer's display documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B) and the maintained [hardware design](hardware/design.md) for specifications and mechanical references. The [parts BOM](hardware/bom.md) is the authoritative component list; this concept does not duplicate prices or connector specifications.

## Physical character

The original 01 River Stone: a low asymmetric pebble with inset landscape display and a refined mineral surface. It stays on the table; there is no separate handheld controller. The [dimensioned packaging study](hardware/river-stone/README.md) proposes a 220 x 155 x 105 mm envelope and 50-degree screen angle, both provisional. A substantial rechargeable battery sits low in the base, contributing stability and weight. The base is non-slip, the glass has perimeter protection, and a removable underside gives access to the battery and electronics. Final dimensions, fasteners, wall thickness and charging access follow component measurements.

Cable-free coffee-table use remains mandatory. A discreet rear cable charging inlet is the working proposal; controller-to-base charging is outside the stationary design. Weeks of standby remains an unmeasured target. With the selected LCD, standby means the screen turns off. Touch wake and whole-board consumption must be demonstrated; an always-visible now-playing screen has a separate energy budget.

## First UI prototype

- **Now playing:** prominent album artwork, track and artist, source, transport and queue access.
- **Find music:** touch-sized search field, artists/albums/tracks/playlists filters and ranked result rows; selecting an item opens a detail view before play or queue actions.
- **Collection:** native Naim favourites and their children, preserving the streamer's returned references.
- **Queue:** current queue inspection and clear feedback for additions. Do not display a requested change as a confirmed playback result.
- **Wake and reconnect:** retrieve fresh player state. When disconnected, show that state and leave browsing available where possible.

Use 800 × 480 as the design canvas, with large controls and restrained warm accents on charcoal. A computer browser is a software prototype only: it cannot validate touch accuracy at physical size, LCD power, ESP32 frame rate or wake latency.

The first UI excludes amplifier volume until the actual System Automation command passes an audible test. The user subsequently requested voice and natural-language AI discovery, now included in the computer prototype. See [voice discovery](voice-discovery.md) for behaviour and outstanding microphone hardware work. The palette stays adjustable to the final enclosure material.

## Required software path

TIDAL catalogue metadata → resolve the chosen reference through native Naim browsing → native Naim play/queue command → verify player state. The NDX 2 retrieves and decodes the audio. The controller and optional Pi carry commands and metadata only.

Public catalogue search and pagination have passed live tests. Native collection playback, queue commands and 24-bit playback have also passed independently. Combining a public search result with native playback has now passed through the UI on the home network. Full personalized TIDAL functionality is not yet established.

## Independent investigation tracks

| Track | Inputs now available | Evidence needed before final selection |
| --- | --- | --- |
| Display and embedded UI | Exact Waveshare candidate; 800 × 480 canvas | Touch usability, rendering, wake behaviour and firmware pin availability |
| Battery and power | Large protected pack in base; existing onboard power path to assess first | Whole-board active/sleep measurements, charging rate, shutdown and runtime |
| Enclosure | Original River Stone, stationary, serviceable underside, low battery placement | Actual board/connector/pack dimensions, antenna clearance, stability and fit |
| Software | Catalogue and native clients; working live evidence | Search-to-native handoff, app coexistence, recovery and audible amplifier control |

Record parts and research in [Hardware](hardware/README.md), accepted changes in [Decisions](decisions.md), and measurements in [Evidence](evidence.md). Parts research can proceed alongside the UI; final purchases and enclosure CAD still follow the software feasibility gate.
