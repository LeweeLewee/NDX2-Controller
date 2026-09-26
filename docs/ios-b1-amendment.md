# Brief B.1 — accumulated testing amendments, 26 September 2026

Implementation is on `codex/still-water-b1` in the isolated checkout. The working prototype and newer primary-checkout work remain preserved. This amendment follows the user's completed-testing instruction; validation and release are pending below.

## Adopted changes

- One Silent Demo anchor at x48/y24. Secondary title baseline bands move below it; Back remains inside the same safe boundary. Artist portrait decoration also stays inside the content boundary. KioskHost centering, system safe area, the extra 8 pt inset and locked orientation are unchanged. Only the colour field extends to the full screen.
- NOW microphone stays fixed. Transport shifts eight design units right; play/pause and mic share x524. Previous, play/pause, next and volume share y316. Touched cover grows to 256, metadata shifts right eight units. Remove the NOW Find shortcut; the microphone retains the B1 immediate-listening entry, with typed entry available after stopping/back to idle.
- Artist tabs, album sleeves and track rows share the name/biography column. Follow is placed to the right of the biography so the retained tabs can sit below without overlap.
- Library Albums and Playlists use six 104-unit covers at x48,168,288,408,528,648, 16 gaps and 156 row pitch; titles are sans-15 at 70%, one line with ellipsis. Playlists have a second cover edge offset up/right six units at 50%. Artists use round portraits or a hairline circle/serif initial. Covers open their existing detail route.
- Library Tracks and Find Results use the same row renderer, 72 high, 56-unit thumbnail with radius 3, text inset 72 only when artwork is available, serif-26 title, sans-18 subtitle at 55%, honest metadata joined by a middle dot, a separator and a membership action. Track likes remain available. Lists and grids clip at the canvas foot with a 40-unit fade.
- The common header takes priority over old y30 title coordinates: Library filters start at y112 and content at y180; Find results move below their field/filter band. Sizes and Library column coordinates are retained.
- Every displayed cover, including Up next, uses an authenticated chunked 320 preview, smoothly downscaled. The 80 path remains solely for current-art palette sampling. Library field extraction uses the same bounded deterministic section 6 algorithm, sampled from the loaded preview. Scrolling geometry is debounced until settled; it selects the first cover still visible, with loaded-cover fallback before the palette fallback. Preview expiry and request generation checks are preserved. Existing metadata reads register artwork; artist portraits use the existing artist_bio action. Client card cache is bounded to 24 current-page items; no bridge limits or routes change.

## Validation

The nine Windows project/distribution checks pass. Native snapshot matrix now includes Library albums, tracks, artists and playlists, alongside all previous states. New checks cover the common marker, transport alignment, cover grid geometry, 320-only card requests, settled palette source and expiry. Full-phone checks retain the iPhone 11 safe-area assertions and updated microphone navigation. Native results, visual review and TestFlight availability will be recorded after verification.

No live playback, volume, NDX, speech, bridge, firmware, route, trust, or tester changes. Presence remains excluded.
