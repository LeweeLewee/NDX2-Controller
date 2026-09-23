# Approved UI baseline — 22 September 2026

> **Current status — 23 September 2026:** Work is paused at the user's request. The working prototype is retained, but its visual direction is not accepted. Earlier approval/gate/next-step statements below are historical and do not authorize further design work. Read [the chat closeout](../chat-closeout-2026-09-23.md) and D028; resume only under the user's revised direction.

The user approved the current review design after iterative screen and interaction refinement, ending with icon-only Search. This records design acceptance, not firmware parity, live service validation or physical acceptance.

## Accepted direction

- Landscape 800 × 480, artwork left, metadata and all playback controls right; charcoal/sage default with appearance presets.
- Five evenly spaced unboxed controls: previous, play/pause, next, speaker-minus and speaker-plus. No visible Volume label, numeric level or held-repeat. Keep bounded D011 delivery and both volume controls busy together.
- Readable bitrate alongside source, timeline separate from transport; unavailable metadata must not be invented. The review value is synthetic.
- Now Playing heart shares track library membership; title, artist and album open their respective details. Artist/album links have no trailing arrows.
- Quiet, unboxed Back. Find, Collection and Queue do not repeat their section names in the top strip. Bottom navigation identifies the section.
- Artist Follow/Unfollow and explicit status. Album/track + Library and checked Library, plus/check/question list icons, distinct unknown state and independent album/track membership.
- Find has magnifying-glass and microphone buttons. Microphone entry starts capture; Stop & search, Restart and Cancel replace the separate review step. Capture is bounded to 30 seconds and stopped on exit; search never auto-plays.
- Top-bar Settings: Display, Connection and Device; brightness/palette/timeout preferences, Wi-Fi/pairing/setup and diagnostics direction as reviewed.

The reviewed default is 240 px artwork and four main sections with voice inside Find. The alternate artwork size and fifth Voice tab remain comparison options, not additional required product modes.

## Handover and open gates

Port the approved design to shared LVGL, wire its states to the authenticated contract and verify parity using silent fixtures. Keep the frozen feasibility reference intact. Real artwork, authoritative bitrate, provider membership and hardware capture need integration rather than fabricated data. Loading/error/transcription-failure details may need further review as implemented.

Physical touch sizing, seated readability, keyboard, wake, microphone, battery, HP-01 and P3/P4/P5 gates remain open. Pi deployment and protected provisioning remain separate. No flashing, audio test, commit or push is implied by this approval.

## Baseline identity

Approved source: `docs/ui-review/index.html` after approval-label update.
SHA-256: `1886dfe3f6bea33d8206bbe27b0c799a45964c995144131ef02a9619a3c68bbc`.
Later edits should be recorded as revisions to this baseline. Browser-local notes and preferences are not a substitute for this approval record.

## Later user direction - 23 September 2026

The user clarified that these were rough prototypes and authorized expert visual/UI redesign for the high-end coffee-table ornament. D027 and [the native design gate](../m2-object-design.md) supersede treating this HTML as final visual geometry. Its hash remains a preserved historical reference; interaction and playback/security constraints remain in force.
