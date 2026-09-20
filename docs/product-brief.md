# Product brief

## Intended experience

A small, stylish music controller that belongs on a coffee table. The design should feel like hi-fi equipment: softly rounded, visually restrained and reassuringly weighty, with a stable non-slip base. A conventional 8–9-inch tablet is too large.

The user can browse the full TIDAL catalogue, albums, artists, favourites and playlists, manage playback and adjust the existing Naim amplifier through the NDX 2. A bespoke interface must suit the small screen rather than reproduce a phone app at reduced size.

## Agreed constraints

- Native Naim TIDAL playback, as used through the Naim app, is mandatory.
- Compact form with flexible rectangular or square proportions; screen quality and interaction lead enclosure dimensions.
- Battery powered, cable-free in normal coffee-table use, with weeks of standby as a target.
- Touch wake is required to validate. LCD screen-off standby is the working direction; persistent visible now-playing remains a trade-off.
- A separate large rechargeable battery belongs in the base. Included small display batteries are unnecessary; weight contributes to the piece.
- 3D-printed enclosure; serviceable assembly is the proposed direction.
- Budget is unconstrained at this stage.
- Existing home-automation Pi may support control and metadata work.

## Candidate choices, not final specifications

- ESP32-S3 integrated into the preferred Waveshare display assembly; no separate MCU board is assumed.
- Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case, is the leading 4.3-inch 800 x 480 colour touchscreen candidate. No hardware performance is proven.
- 5,000–10,000 mAh battery considered; no pack has been selected.
- Charcoal finish, shallow tilt, silicone base and low battery placement.
- Separate charging location; contacts, dock or accessible connector still to be selected.

## Trade-offs to resolve

LCD needs ongoing power to show now-playing; screen-off standby sacrifices the visible image. E-paper alternatives retain an image without display power, but touch electronics, radios and updates still consume energy. Instant track-change updates conflict with deep Wi-Fi sleep. Search, keyboard use, ghosting, refresh flashes and evening readability need a physical demonstration. Battery capacity alone cannot establish runtime.

The first product milestone is a complete native software interaction loop, followed by a representative screen/battery prototype. Final CAD should follow component selection.

Hardware design, parts and unresolved selections are managed in [Hardware](hardware/README.md).

The [updated design concept](design-concept.md) records this screen selection and the shared brief for parts investigation and the prototype UI.
