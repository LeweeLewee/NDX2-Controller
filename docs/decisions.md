# Decision log

## D001 — Native Naim playback is mandatory

**Accepted, 19 September 2026.** The NDX 2 must use its own native TIDAL implementation. Direct Naim content browsing and a single native playback request have worked. Music Assistant-to-DLNA and alternative audio paths are excluded. TIDAL Connect is distinct and is not an automatic replacement.

## D002 — Small bespoke controller

**Accepted.** A conventional tablet is too large. Use a compact square touch interface in a purpose-made printed enclosure. Exact diagonal and dimensions are pending hardware evaluation.

## D003 — Battery life and physical substance

**Accepted direction.** Weeks of standby, persistent now-playing display where practical, and a substantial battery. Weight is a positive part of the design. Capacity, total mass, charging and runtime are not finalized.

## D004 — E-paper and ESP32 remain candidates

**Provisional.** E-paper suits persistent information and low standby display power. Interaction latency, touch availability and refreshing need testing. ESP32-S3 is a credible candidate for the observed HTTP control path; no firmware demonstration has occurred.

## D005 — Pi is available, not mandatory

**Accepted architectural option.** The existing Home Assistant Pi can support control/metadata processing. Direct native browsing means a bridge is not automatically required. No audio may be relayed through it.

## D006 — Software proof before final hardware

**Accepted workflow.** Complete native search, queue, volume and quality validation before final component purchase and enclosure CAD. A representative screen prototype then verifies that the interaction is pleasant enough.

## D007 — Project repository

**Updated, 20 September 2026.** The user selected [leweelewee/NDX2-Controller](https://github.com/leweelewee/NDX2-Controller) as the project repository. The original local project and existing GitHub initial commit are preserved in the combined history. Personal reports remain ignored locally. Repository visibility is unchanged; no distribution licence has been selected. There is no affiliation with Naim or TIDAL implied by the project name.
