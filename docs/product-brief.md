# Product brief

## Intended experience

A small, stylish music controller that belongs on a coffee table. The design should feel like hi-fi equipment: softly rounded, visually restrained and reassuringly weighty, with a stable non-slip base. A conventional 8–9-inch tablet is too large.

The user can browse the full TIDAL catalogue, albums, artists, favourites and playlists, manage playback and adjust the existing Naim amplifier through the NDX 2. A bespoke interface must suit the small screen rather than reproduce a phone app at reduced size.

## Agreed constraints

- Native Naim TIDAL playback, as used through the Naim app, is mandatory.
- Compact square form; precise dimensions depend on the chosen display and battery.
- Battery powered, cable-free in normal coffee-table use, with weeks of standby as a target.
- Touch wake; e-paper's persistent now-playing image is desirable.
- A relatively large battery is welcome. Weight contributes to the piece.
- 3D-printed enclosure; serviceable assembly is the proposed direction.
- Budget is unconstrained at this stage.
- Existing home-automation Pi may support control and metadata work.

## Candidate choices, not final specifications

- ESP32-class controller, with ESP32-S3 a candidate.
- Approximately 3.5–4-inch display; monochrome e-paper with partial refresh is the leading candidate.
- 5,000–10,000 mAh battery considered; no pack has been selected.
- Charcoal finish, shallow tilt, silicone base and low battery placement.
- Separate charging location; contacts, dock or accessible connector still to be selected.

## Trade-offs to resolve

E-paper holds an image without display power, but touch electronics, radios and updates still consume energy. Instant track-change updates conflict with deep Wi-Fi sleep. Search, keyboard use, ghosting, refresh flashes and evening readability need a physical demonstration. Battery capacity alone cannot establish runtime.

The first product milestone is a complete native software interaction loop, followed by a representative screen/battery prototype. Final CAD should follow component selection.
