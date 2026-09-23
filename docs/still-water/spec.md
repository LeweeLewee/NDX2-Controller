# Still Water: native UI specification

Platform: pending screen selection between the iPhone 11 (see `iphone-architecture.md`, sections 0 and 0b below) and the Waveshare ESP32-S3-Touch-LCD-4.3B (Appendix A). The design is platform-neutral: coordinates are design units from the top-left of the visible window, and every physical size is in millimetres, so the screen tables apply to both. Sections 0, 0b, 2.2 implementation notes, 7, 9 and 10 are written for the iPhone; Appendix A carries the Waveshare equivalents. Reference renders in `reference/` were made for the earlier 800 × 480 canvas; sizes carry over, widths do not. Where a value here differs from a render, this document wins.

Revision note, 23 September 2026: sections 0, 0b, 2.2 implementation, 2.4, 7, 9 and 10 were rewritten for the iPhone platform; the Waveshare and LVGL versions moved to Appendix A. Design lock is independent of the platform choice.

## 0. Panel facts this specification is designed against

| Fact | Value | Consequence |
|---|---|---|
| Panel | 6.1" IPS LCD (Liquid Retina), 1792 × 828 px at 2×, 326 ppi, about 139.9 × 64.6 mm landscape | Square pixels, 24-bit colour, no banding. Black is backlit dark grey, not off, so Asleep must be the panel off via auto-lock, never a black frame |
| Window | 118 × 54 mm exposed by the inlay; notch band and corners hidden | The app paints black outside the window; the opaque inlay hides that area, so the backlit black there is never seen. Inside the window, the darkest field tones will show a faint backlight glow in a dark room; this suits the wet-stone reading and no compensation is added |
| Renderer | Core Animation and Metal | All motion in section 9 is cheap; no fallbacks needed for cost, only for the reduced-motion preference |
| Brightness | Full software range | Still and Touched run at a fixed level set by the app (start at 35%; LCD black level rises with brightness, so keep it low and let P3 raise it). Asleep is the panel off via auto-lock. No dimmed ambient state is added |
| Touch | Capacitive, tap-to-wake native | First touch after wake is consumed and never acts, as before |
| Microphone | Three built in | Voice capture on device; transcript via on-device speech recognition |
| Seated distance | 600 to 800 mm, unmeasured | Only the title is sofa-readable; everything else is lean-in. P3 decides secondary sizes |

## 0b. Canvas and units

The window is 755 × 346 pt (1510 × 692 px at 2×), inset 70 pt from the long edges and 34 pt from the short edges of the 896 × 414 pt landscape screen. Design units: **1048 × 480**, 1 unit = 0.7206 pt = 1.441 px = 0.1126 mm. The earlier 800 × 480 canvas was 95.5 × 54.4 mm; the window is the same height and 22.5 mm wider, so every physical size in this document is unchanged and every table below still applies with one rule for the extra 248 units of width:

| Anchoring | Rule |
|---|---|
| Left-anchored (x measured from the left edge: covers, titles, lists starting at 48) | Unchanged |
| Right-anchored (amplifier pill, Find, Library, Back to now, remaining time, membership marks at 704, right edge 752) | Add 248 to x; the right margin stays 48 and the right edge is 1000 |
| Centred (Play/Pause ring, Ask ring, transcript, Ask buttons, ripples, results columns) | Add 124 to x |
| Full-width (waterline, hairlines, keyboard, filter rows) | Extend to 1048 |
| Text columns on NOW (start 336 or 368) | Width grows by 248; titles wrap later, which is welcome |
| Up next covers | Seven covers fit instead of six; add size 68 at opacity 24% |
| Results columns (future) | Column width 208 becomes 290 at x 48, 379, 710 |

Convert to points by multiplying by 0.7206. Derive layout constants from the unit values in code, not from hand-converted points, so these tables remain the source of truth.

## 1. Principles

1. **The music is the room.** The whole screen is a colour field derived from the current artwork. There is no panel, bar, card or chrome behind the music.
2. **Controls surface on touch, then sink.** The at-rest view (Still) shows artwork, title, artist, album and a waterline. Nothing else. The first touch reveals controls and never acts.
3. **One fixed mark: the waterline.** Progress is a full-width hairline at the foot of the glass, present in every music state.
4. **Serif for music, sans for the machine.** Titles, album names and spoken phrases are set in Instrument Serif. Labels, numbers, status and settings are set in Geist.
5. **Honest states, quiet delivery.** Offline, pending, unknown and unavailable states remain explicit, but they are typeset as part of the composition, not as alerts.
6. **No new claims.** Nothing here changes power, sleep, wake, recovery or command semantics.

## 2. Tokens

### 2.1 Ink and opacity (used over the derived field)

| Role | Value | Use |
|---|---|---|
| Ink | `#F1EBDF` | All text and icons |
| Ink primary | ink @ 100% | Track title, active labels, active icons |
| Ink secondary | ink @ 70% | Album line, artist row on secondary screens, offline metadata. Raised from 62% after the contrast gate measured 4.2:1 over the sage field |
| Ink caps | ink @ 55% | Small-caps labels (artist above title, section labels) |
| Ink tertiary | ink @ 35% | Disabled controls, hints |
| Hairline | ink @ 18% | Waterline track, dividers, unfilled rings |
| Played | ink @ 75% | Waterline played portion |
| Accent | `#F1C98D` | Ask (microphone) ring and glyph, listening state only. Nowhere else |
| Primary button | fill ink, text `#141614` | Stop & search only |

No red, green or amber status colours. Offline and errors are ink at secondary opacity with words.

### 2.2 Field (background)

The field is built from three colours extracted from the current artwork (section 6): `c1` mid tone, `c2` dark tone, `c3` light tone.

Layers, bottom to top:

1. Vertical gradient, full window: top `shade(c1, 0.62)` to 60% `shade(c2, 0.55)` to bottom `#070808`. `shade(c, f)` multiplies each RGB channel by `f`.
2. Glow A: radial gradient, centre (180, 220), radius 380, colour `c3` at 22% to transparent.
3. Glow B: radial gradient, centre (680, 48), radius 420, colour `c1` at 55% to transparent.

Outside the window: pure black, always. Implement the layers as `LinearGradient` and `RadialGradient` in SwiftUI or `CAGradientLayer` with `.radial`. No image assets.

Dimmed field (Up next, Ask, results): multiply layer opacities by 0.6, 0.28 and 0.35 respectively.

Fallback field when no artwork is available: `c1 #5A6360`, `c2 #141A19`, `c3 #CFD3C4`. The existing palette preference (sage/sand/slate) selects between three fallback sets; keep the preference field and its persistence, change only its meaning:

| Preference | c1 | c2 | c3 |
|---|---|---|---|
| Sage | `#5A6360` | `#141A19` | `#CFD3C4` |
| Sand | `#7A6858` | `#231A16` | `#E2CFAF` |
| Slate | `#4E5B66` | `#161C21` | `#C8D2D8` |

Contrast rule: after shading, the field luminance behind primary text must be at most 0.12 (sRGB relative luminance) so ink @ 100% reaches 7:1. If the extracted `c1` is too light, reduce the shade factor in layer 1 until it passes. Compute once per artwork change and cache with the artwork reference.

### 2.3 Type

| Token | Family | Size | Style | Use |
|---|---|---|---|---|
| serif-56 | Instrument Serif | 56 | regular | Track title (Still and Touched), spoken phrase |
| serif-32 | Instrument Serif | 32 | regular | Screen titles (Up next, Find, Library, Settings), list item titles on detail, queue selection |
| serif-26 | Instrument Serif | 26 | regular and italic | Album line, list row titles, search query text, result titles |
| sans-22 | Geist | 22 | regular | Body, settings values, buttons |
| sans-18 | Geist | 18 | regular | List subtitles, secondary text, times |
| caps-15 | Geist | 15 | medium, +0.18 em tracking, uppercase | Artist above title, section labels, small labels |

Physical sizes at 0.1126 mm per unit (multiply units by 0.7206 for points): serif-56 cap height about 4.8 mm; serif-32 about 2.7 mm; serif-26 about 2.2 mm; sans-22 about 1.8 mm; sans-18 about 1.5 mm; caps-15 about 1.2 mm (uppercase, tracked). The prototype renders used 24/20/16/13; the app uses the sizes in this table. Nothing below caps-15 is permitted anywhere. Text renders at 2× on the LCD, about 1.5 times the pixel density of the earlier panel, and will look crisper than the renders; do not shrink sizes because they look large on a Mac. If the P3 seated trial finds sans-18 unreadable, the next step is sans-20 with row heights increased by 8 px, not a smaller font elsewhere.

Line height 1.02 for serif titles, 1.3 for everything else. Numbers use tabular figures where the font provides them; otherwise right-align.

Long text: track titles longer than 18 characters step down one size (serif-56 → 44 on Still, 50 → 40 on Touched), then wrap to a maximum of two lines and truncate with an ellipsis. Without the step-down a 384-unit column holds about 12 characters a line and the title is lost. List rows use one line with ellipsis. Never clip glyphs.

### 2.4 Spacing and geometry

- Outer margin: 48 px left and right, 56 px top for content on NOW, 30 px for screen titles on secondary screens.
- Grid: 8 px. Column split on NOW: artwork column 48 to 296 (248 px cover in Touched) or 48 to 320 (272 px cover in Still); text column starts at 336 (Touched) or 368 (Still).
- Touch targets: 72 × 64 minimum for transport, list rows, icon buttons and amplifier halves; pills and filter words at least 96 × 56; 80 × 80 for Play/Pause and 72 × 72 for Ask. Gaps at least 8. The existing native gate that checks transport targets must keep passing.
- Radii: covers 3, pills full height, rings circular.
- Cover shadow: 0 18 40 rgba(0,0,0,.45).

### 2.5 Icons

Keep the 24-unit outline icon language from `ui_visual.h`, redrawn as SwiftUI `Path`s or a small bundled SVG set. Changes:

- Stroke 1.6 at 30 px for transport and navigation, 2.2 for the pause and play marks inside the primary ring.
- Remove the tonal disc behind Play/Pause; replace with the ring described in 4.3.
- Remove all icons from the foot of NOW except the microphone. Navigation words replace navigation icons.
- Keep disc, question, heart, plus, check for lists and detail.

## 3. Rest states (last touch and transport)

The ladder is driven by two inputs the controller already has: time since last contact, and whether transport is playing. No sensor is involved.

| State | Enter when | Shows | Leaves when |
|---|---|---|---|
| Asleep | existing `timeout` preference expires with no contact | backlight off | contact (existing wake path: contact consumed, wait for release, fetch state) |
| Waking | contact while asleep | field rises from the waterline over 400 ms; no controls | automatically to Still after the rise, or to Touched if contact continues after release |
| Still | 8 s after last contact on NOW; or after Waking | artwork, artist caps, title, album, waterline | contact → Touched; `timeout` → Asleep |
| Touched | any contact on NOW that is not the wake contact | Still plus transport, amplifier, Up next, Ask, Find, Library, times | 8 s without contact → Still |

Secondary screens (Find, Up next, Library, Detail, Ask, Settings) keep the existing timeout to Asleep. They do not auto-return to Still in this phase; note as a possible follow-up because it interacts with context preservation.

Transport not playing:

- Paused: Still and Touched keep the same layout. The artist caps line reads `PAUSED · <artist>`. Waterline played portion drops to ink @ 40%. The primary ring shows the play mark.
- Stopped or nothing loaded: title area shows `Nothing playing` in serif-32 at secondary opacity, artist caps line shows the source, cover space shows the fallback field with no placeholder box. Waterline hidden.

Offline: retain last-known metadata at secondary opacity (70%), cover at 62%. Artist caps line reads `RECONNECTING`. All mutation controls at tertiary opacity and disabled. No spinner. Existing stale/fresh rules decide when metadata is shown at all.

## 4. Screen: NOW

### 4.1 Still

| Element | x | y | w | h | Style |
|---|---|---|---|---|---|
| Cover | 48 | 72 | 272 | 272 | radius 3, shadow |
| Artist caps | 368 | vertically centred block | 384 | 16 | caps-15 @ 55% |
| Title | 368 | | 384 | up to 2 lines | serif-56 @ 100% |
| Album | 368 | | 384 | 26 | serif-26 italic @ 62% |
| Waterline | 0 | 472 | 800 | 1 (2 for played) | hairline / played |

The three text lines form one block with 14 px gaps, vertically centred on the cover (y 72 to 344). Do not top-align.

Missing artwork: no placeholder box. The cover area shows a 272 px square filled with `shade(c2, 0.8)` at radius 3 with the caption `Artwork unavailable` in sans-18 @ 35% centred inside. The field uses the fallback palette.

### 4.2 Touched

| Element | x | y | w | h | Style |
|---|---|---|---|---|---|
| Cover | 48 | 56 | 248 | 248 | as above |
| Text block | 336 | 56 | 416 | 190 | caps-15, serif-56, serif-26 italic; top-aligned within the block with 14 px gaps |
| Previous | 336 | 282 | 72 | 64 | icon @ 85% |
| Play/Pause ring | 428 | 274 | 80 | 80 | ring: border 1.5 px ink @ 70%, fill ink @ 12%; mark stroke 2.2 |
| Next | 516 | 282 | 72 | 64 | icon @ 85% |
| Amplifier pill | 600 | 282 | 152 | 64 | border 1 px hairline, radius 32; minus target 600–676, plus target 676–752 (76 × 64 each, meeting the existing 72 × 64 gate); `AMP` caps-15 @ 45% centred 22 px above the pill |
| Up next | 48 | 388 | 260 | 56 | caps-15 `UP NEXT` @ 50% at y 394; next track title serif-26 at y 412, one line ellipsis; whole area is the target; opens QUEUE |
| Ask ring | 364 | 376 | 72 | 72 | ring border 1.5 px accent @ 80%, mic glyph accent; opens VOICE |
| Find | 552 | 392 | 96 | 56 | sans-22 @ 85% word `Find`, right-aligned in its target; opens FIND |
| Library | 656 | 392 | 96 | 56 | sans-22 @ 85% word `Library`, right-aligned; opens COLLECTION |
| Elapsed | 48 | 446 | 100 | 20 | sans-18 @ 60% |
| Remaining | right edge 752 | 446 | 100 | 20 | sans-18 @ 60%, formatted `−m:ss` |
| Waterline | 0 | 472 | 800 | | as Still |

Settings: long-press (700 ms) on the artist caps line opens SETTINGS. Show a 1 px hairline underline on the caps line while the press is held so the affordance is discoverable. Alternatively a 40 × 40 gear at (752, 24) at 35% opacity is acceptable if long-press is unreliable with the existing contact handling; prefer long-press.

Amplifier busy (D011 in flight): both halves at tertiary opacity, pill border unchanged, no spinner. Unknown outcome after timeout: pill border becomes dashed hairline and stays until reconciliation.

Save/heart: the existing track membership action moves to Detail. It is not on NOW.

Controls fade in over 250 ms with a 6 unit upward drift; fade out over 400 ms.

### 4.3 Waking

Field, cover and text render immediately at full values behind a full-screen black overlay whose bottom edge clips upward from y 480 to y 0 over 400 ms (ease-out). The waterline is visible from the first frame. The contact that woke the panel is consumed as today. Skip the animation when the existing wake rules require an immediate authoritative refresh first; show Still directly.

## 5. Secondary screens

All secondary screens share: dimmed field (2.2), screen title in serif-32 at (48, 30), a `Back to now` pill at the right (56 high, at least 96 wide, right edge 752, y 26; border hairline, sans-18 @ 75%). No top status bar. No bottom navigation bar. Connection status appears only where it changes what the user can do (section 8).

### 5.1 QUEUE (Up next)

Read-only, as today.

- Baseline hairline at y 300, full width.
- Covers sit on the baseline, left to right from x 48 with 22 px gaps: sizes 200, 150, 124, 104, 90, 78 for positions 0 to 5; opacities 100, 92, 78, 62, 48, 34%. Position 0 is the current track. Only six are drawn; further items are reachable by horizontal scroll of the row.
- Reflection below the baseline: each cover mirrored, 40% of its height, opacity 22% of the cover's opacity, masked to transparent at the bottom. Drop reflections if they cost more than one extra image draw per cover.
- Selected cover (default position 1): 1.5 px ink @ 80% outline, 4 px outset.
- Below, at (48, 392): caps-15 `PLAYS IN n MIN` or `PLAYING NOW`; at (48, 412): serif-32 title, followed on the same baseline by artist in sans-18 @ 60%.
- Tap a cover to select it. No other actions.

### 5.2 FIND

- Title `Find` at (48, 30). `Back to now` at right.
- Query field at (48, 88), 536 × 64: no box. Text serif-26 @ 100%, placeholder `Artist, album or a kind of music` serif-26 italic @ 60%. A hairline under the field at y 152 from x 48 to 584; it becomes ink @ 75% while focused.
- Search glyph target (600, 88) 72 × 64; microphone target (680, 88) 72 × 64 in accent.
- Filters at y 160: the words `Albums  Tracks  Artists  Playlists` in sans-18, each a 120 × 56 target starting at x 48 with 8 gaps; selected word @ 100% with a 24 px hairline underline 6 px below the text; others @ 55%.
- Result rows from y 220, row height 72, full width from x 48 to 752: title serif-26 @ 100% at row y+12; subtitle `artist / kind` sans-18 @ 55% at row y+42; hairline separator at the row bottom from x 48 to 752. Membership marks (heart, plus, question) at x 704, 40 × 40, ink @ 70%.
- Empty and loading: `Looking…` or `Nothing found for “query”` in serif-26 italic @ 62% at (48, 232).
- Keyboard: the iOS system keyboard in dark appearance. It occupies roughly y 216 to 480 when open; filters and rows hide behind it and restore on dismiss.

### 5.3 DETAILS

- Cover at (48, 96), 200 × 200. For artists, no cover; the title block starts at x 48.
- Kind caps-15 @ 55% at (280, 100). Title serif-32 at (280, 122), up to two lines. Artist sans-22 @ 62% below.
- Membership line sans-18 @ 62% at (280, 236): `In your library`, `Not in your library`, `Library status unknown`, `Following`, `Not following`, `Follow status unknown`.
- Actions at y 300, height 56, left to right from x 280 with 12 px gaps: `Play` primary pill (fill ink, text `#141614`) 140 wide; `Play next` and `Add to queue` hairline pills only if the current control logic supports them (it does not today: omit); `Library` or `Follow` hairline pill 150 wide showing the pending state as `Saving…` in the same pill.
- Native children (album tracks, artist albums) as FIND rows from y 376, scrolling under Back.

### 5.4 COLLECTION (Library)

- Title `Library` at (48, 30). Sub-sections as filter words at y 88: `Albums  Tracks  Artists  Playlists`, same style as FIND filters.
- Rows from y 140 as FIND rows.
- Disconnected account: serif-26 italic @ 62% `Connect your collection on the bridge computer` at (48, 152), and nothing else.

### 5.5 VOICE (Ask)

Recording starts immediately, as today.

- Field: `#050707` base with the dimmed music field at 28%.
- Caps-13 accent @ 60% centred at y 40: `LISTENING · m:ss OF 0:30`. Stopped: `RECORDING STOPPED`. Unavailable: `MICROPHONE UNAVAILABLE`.
- Ripples: three concentric ellipse outlines centred at (400, 270), accent @ 55%, each expanding from radius 45 to 300 over 3.6 s, staggered 1.2 s, opacity fading to 0. Drawn as stroked circles in SwiftUI; cut to a static ring under Reduce Motion.
- Transcript (when the fixture or a future transcript provides it) centred at y 130, width 640, serif-56 italic @ 100%, wrapped in typographic quotes. Until a transcript exists, show `Say an artist, an album or the kind of music you want` serif-32 italic @ 62%.
- Microphone ring at (364, 258), 72 × 72, accent border and glyph, fill accent @ 12%.
- Buttons at y 388, height 56: `Cancel` hairline pill at x 120; `Restart` hairline pill at x 328; `Stop & search` primary pill at x 510. All sans-22. Existing semantics unchanged.
- Fixture note `Microphone fixture: no audio captured. Search only.` sans-18 @ 35% centred at y 456 when in fixture mode.

Results after Stop & search land in FIND with the query set to the transcript, as today.

### 5.6 SETTINGS, DISPLAY, CONNECTION, DEVICE, WIFI, PAIRING

Utility screens. Fallback field (not artwork-derived), same title and Back treatment.

- Rows 80 px high from y 96: title sans-22 @ 100% at row y+16, value or subtitle sans-18 @ 55% at row y+44, chevron sans-18 @ 45% at x 728, hairline separators.
- Display: palette words `Sage  Sand  Slate` as filter-style words; brightness as a hairline slider with a 20 px ink knob; sleep timeout as the existing dropdown restyled with hairline border and no fill.
- Preference feedback line at the foot in sans-18 @ 55%, wording unchanged.
- Wi-Fi and pairing fixtures keep their existing wording; typeset in sans-22 @ 62%.

## 6. Artwork colour extraction

Input: the existing 80 × 80 RGB565 authenticated preview.

1. Convert to RGB888. Ignore pixels within 4 px of the edge (labels and borders).
2. Median cut to 8 boxes, or k-means with k = 4 for at most 6 iterations from fixed seeds. Both are under 1 ms of work on the S3 for 5,776 pixels.
3. From the resulting colours, choose: `c2` = the darkest by luminance with population above 5%; `c3` = the lightest with population above 5%; `c1` = the most populous colour excluding `c2` and `c3`. If fewer than three qualify, fill from the fallback set for the preferred palette.
4. Desaturate `c1` by 20% and `c3` by 10% (blend toward their own grey) so the field is quieter than the sleeve.
5. Apply the contrast rule in 2.2 and cache the result with the artwork reference. Recompute only when the artwork target changes or clears.

No colour is ever extracted from the fixture sleeves in production; fixture mode uses their own known colours through the same function.

## 7. Fonts

Instrument Serif (Regular, Italic) and Geist (Regular, Medium), SIL Open Font License. Bundle the font files in the app target, register them under `UIAppFonts`, keep the licence files in the bundle. Point sizes are the unit sizes in 2.3 multiplied by 0.7206, rounded to the nearest half point: serif-56 → 40.5, serif-32 → 23, serif-26 → 19, sans-22 → 16, sans-18 → 13, caps-15 → 11 with 0.18 em tracking. Do not use Dynamic Type; the object has one viewing distance.

## 8. Status and connection

- No permanent status strip. `Silent demo` is shown as caps-15 @ 35% at (48, 24) on every screen while in fixture mode, and nowhere otherwise.
- Connection loss is shown in the artist caps line on NOW (`RECONNECTING`) and as a serif-26 italic line at the top of list screens (`Reconnecting to the bridge`). Controls that cannot act are at tertiary opacity and disabled.
- Pending mutation: the control that was tapped holds ink @ 100% with a 1 px hairline ring for the pending duration; nothing else animates. Unknown outcome after expiry: ring becomes dashed and the existing wording appears as sans-18 @ 62% beneath the control.
- Battery stays in Device.

## 9. Motion

| Motion | Duration | Where |
|---|---|---|
| Wake rise | 400 ms ease-out, black overlay clipped upward from the waterline | NOW |
| Controls in / out | 250 ms in with a 6 unit drift, 400 ms out | NOW |
| Field change on track change | 600 ms crossfade | NOW |
| Ask ripples | three rings, 3.6 s each, 1.2 s stagger, continuous while recording | VOICE |
| Everything else | none | |

Honour Reduce Motion by cutting instead of animating. No animation may delay input handling or the authoritative refresh after wake.

## 10. Acceptance

Snapshot tests render every state at the window size on an iPhone 11 simulator (2×) and on the physical phone: Still (fallback sage), Still (extracted colours from a fixture sleeve), Touched, paused, stopped, long title, missing artwork, offline, pending, Waking mid-frame, Up next, Find with rows, Find with keyboard, Detail, Library, Ask recording, Ask stopped, Settings, Display.

Pass criteria:

- Layout matches this specification within 4 units for every element in the tables, after the anchoring rule in 0b.
- No clipped glyphs; long titles show two lines then an ellipsis.
- Contrast: ink @ 100% over the field behind title text at 7:1 or better on every state; ink @ 62% at 4.5:1 or better, measured on the rendered snapshot.
- Every tap target at least 72 × 64 units (52 × 46 pt, about 8 × 7 mm), pills and filter words at least 96 × 56; Play/Pause 80 × 80 and Ask 72 × 72; non-overlapping, 8 units apart.
- No status bar, no home indicator, no bottom navigation bar, nothing drawn outside the window.
- The first touch after wake never issues a command; Cancel, Restart, Stop & search and the 30 s limit behave exactly as the existing controller tests specify; no automatic playback from voice; no replay of any mutation.
- Bridge protocol conformance passes against the existing Python fixture bridge.

Out of this gate: standby power, wake latency on the real LAN, seated readability, touch accuracy on the table, heat in the shell. Those are the measurements in `iphone-architecture.md` section 8.

## Appendix A. Waveshare ESP32-S3-Touch-LCD-4.3B equivalents

Applies only if the Waveshare panel is selected. Canvas 800 × 480 px, 1 px = 1 design unit, no anchoring rule (the tables were written for this canvas). Visible area 95.54 × 54.36 mm.

| Fact | Value | Consequence |
|---|---|---|
| Visible area | 95.54 × 54.36 mm, 800 × 480 | 0.119 mm per px horizontally, 0.113 vertically; pixels about 5% taller than wide. Draw rings 5% wider than tall (Play/Pause 84 × 80, Ask 76 × 72); targets keep stated sizes; covers accept the 5% |
| Colour depth | 16-bit RGB565 on the panel, 32-bit on desktop builds | Lift the gradient floor to `#0C0E0D`, enable `LV_DITHER_GRADIENT` (LVGL 8.4), and require at least one 16-bit capture in the review matrix; a 32-bit desktop capture does not prove the field is band-free |
| Renderer | LVGL 8.4.0 software renderer, no GPU | Field as one vertical gradient plus two recoloured 8-bit alpha-disc images; rebuild only on state or artwork change |
| Framebuffer | RGB panel refreshed from PSRAM, shared with Wi-Fi | Motion partial-region only; measure tearing and drift on HW-001 with Wi-Fi active; use ESP-IDF RGB bounce buffers if drift appears |
| Backlight | CH422G EXIO2, on or off only | No dimming of any kind; brightness preference stays hardware-unbound |
| Flash | 16 MB | Custom partition table with a 3 MB application partition for the fonts |
| Fonts | `lv_font_conv`, 4 bpp, range `0x20-0x7E,0xA0-0xFF,0x2013-0x2014,0x2018-0x201D,0x2026`, sizes 56/32/26/22/18/15 with italic 56 and 26 | Expect 150 to 250 KB in total; Montserrat removed |
| Motion fallbacks | Wake rise → cut; controls → cut in, fade out; field crossfade → cut; Ask ripples → static ring below 10 fps | Measured on HW-001 before keeping any |
| Acceptance | Extend `tools/m2_visual_review.py` to the section 10 matrix; existing native transport target gate (five targets, at least 72 × 64, non-overlapping) must pass; no Montserrat glyphs; no text below caps-15; rings 5% wider than tall in captures | Physical readability, touch, frame timing and power remain HP-01, P3, P4, P5 |

The earlier LVGL brief is in `codex-prompt.md` history only if Codex committed it; otherwise it is reconstructed from this appendix.
