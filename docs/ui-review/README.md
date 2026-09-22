# Approved UI design

The user approved the desktop design on **22 September 2026**, after the icon-only Search refinement. [Approval and baseline identity](approval.md) governs the design; [index.html](index.html) is its interactive visual reference. [Historical notes](review-history.md) preserve earlier proposals without making them current requirements.

## Review locally

From the repository root:

```powershell
python tools/ui_design_review.py
```

Open http://127.0.0.1:8766/. This loopback-only server exposes the board and an optional existing fixture capture, with no player, bridge API, credentials or microphone access. Missing `local/m2/native-captures/01-now.bmp` affects only the comparison image. Browser-local notes/preferences are not repository acceptance evidence.

## Current baseline

- 800 × 480; 240 px artwork left, metadata and all controls right. Four sections: Playing, Find, Collection, Queue. Voice is inside Find.
- Five evenly spaced, unboxed controls: previous, play/pause, next, speaker-minus, speaker-plus. Quiet Back; no redundant section titles, Volume label, play circle or volume capsule.
- Bitrate beside source, separate timeline; track heart and title/artist/album links. Real metadata must be authoritative or explicitly unavailable.
- Artist follow/unfollow and status; album/track + Library or checked Library; saved, unsaved and unknown remain distinct.
- Magnifying-glass search and microphone icons. Microphone opens recording immediately; Stop & search, Restart, Cancel. Thirty-second bound, no automatic submission or playback.
- Settings via gear: Display, Connection, Device; Sage/Sand/Slate, brightness and timeout preferences, Wi-Fi/pairing/setup and diagnostics direction.

Settings, membership, bitrate and recording are labelled simulations. Brightness is a browser visual approximation; timeout is stored without implementing sleep. Alternative artwork/navigation options are comparison aids, not additional required modes.

## Implementation boundary

The browser board is approved design, **not ESP32 runtime or proof of shared LVGL parity**. Port it to the existing shared C/LVGL UI, retain authenticated bridge semantics, and validate desktop flows before hardware. Loading/error/transcription-failure details may need further design review. Touch sizes, wake release, readability, battery and microphone still require physical evidence. HP-01 and physical P3/P4/P5 remain open.

Continue with [the implementation handover](../continuation-prompt.md). No queue/playlist editing or automatic AI playback is included.
