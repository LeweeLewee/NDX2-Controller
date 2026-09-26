Brief B.1 refinement, same authorisation and constraints as Brief B (D030; keep the Waveshare fallback, the bridge contract, D011, recovery and no-replay rules intact). Read `docs/still-water/spec.md` sections 4.2, 5 and 5.3/5.3b as revised on 26 September, and open `docs/still-water/reference/06-touched.png`, `21-detail.png` and `22-artist.png`. These are user decisions from the first on-phone review; implement them as written.

NOW, Touched:
1. Ask: the accent microphone ring at the centre foot (364, 376, 72 × 72) opens Find already listening. The Find icon opens Find idle. Keep the merged Find screen.
2. Foot right: Find (search glyph) and Library (library glyph) icons at x 632 and 704, y 384, 72 × 64, aligned to the volume icons above them at x 632 and 704, y 282. No gear. No words.
3. Remove all times from NOW. The waterline is the clock.
4. Artist line on Touched in caps-15 tracked at 55%, matching Still.
5. Volume stays as bare glyphs; busy at 35%; unknown outcome shows a dashed outline around the two glyphs with `Volume outcome unknown` beneath.
6. Remove the heart from NOW.
7. Settings by a 700 ms long-press anywhere on Touched that is not a control.

Find (merged voice and typed), per spec 5.2 as revised, and `17-find.png`, `08-ask.png`, `18-results.png`:
8. Three states: Idle, Listening, Ready, then Results. One ring with three faces: mic to start, square to stop, up arrow to search; a reset ring beside the arrow discards and listens again; Back discards in every phase. Remove the Cancel, Restart, Stop & search and Type instead buttons and the `VOICE SEARCH` caps line. No caption under the ring in any phase; the status caps at the top carry `LISTENING · m:ss OF 0:30`, `STOPPED · m:ss` or `NOTHING HEARD`. Idle has the prompt, the ring, and the query field at the foot (`Or type here`). Listening: status caps, transcript as it forms, ripples centred on the ring (radius 45 to 260, three rings, 3.6 s, 1.2 s stagger). Ready: status caps, transcript, arrow ring, reset ring; empty transcript shows `NOTHING HEARD` with the arrow disabled. Results is the field with the query, filters, rows and the mic beside the field. See `18-find.png`, `08-ask.png`, `09-ready.png`, `19-results.png`.
8a. Stop on silence: a setting, default on, that ends Listening after 2 s of silence following speech and lands in Ready, exactly as a ring tap. The 30 s limit does the same. Nothing is searched until the arrow is tapped, so the explicit-submit rule holds.

Detail screens:
9. Album per spec 5.3: cover 248 at (48, 56), artist caps, serif-32 title, one facts line built only from available metadata, Play filled, Add to library hairline pill carrying the membership state (no separate status line), numbered track rows with durations in a clipped list with a foot fade. No screen title; Back is chevron plus `Back`, 112 × 56 at the right.
10. Artist per spec 5.3b: portrait plate on the left third fading into the field, name serif-44, bio clamped to four lines and expandable on tap, Follow pill carrying its state, the artist's albums as a row of 96-unit covers. Degrade exactly as the spec lists when portrait, bio or albums are missing; never a placeholder.
11. Row subtitles: build from the parts that exist; never a leading `/`.
12. Artwork: fetch the chunked 320 preview from Brief A for covers and scale smoothly; the 80 × 80 path is for lists only.

Bridge, read-only, within the existing authenticated envelope, no new routes: (a) register artist pictures through the existing artwork registration so the app can fetch a portrait preview up to 320 × 320 by reference; (b) one bounded artist bio read: plain text, 2,000 characters maximum, HTML stripped, from the catalogue client's artist metadata, returning unavailable when the catalogue has none. Update the contract and the fixture (give the fixture artist a portrait study and a bio) with tests.

Kiosk: document in `docs/hardware/iphone11-primary.md` that Guided Access disables the hardware buttons so the volume overlay cannot appear.

Validation as Brief B, plus rerun the snapshot matrix with the three revised screens and add Artist to it. Update `docs/roadmap.md` and `docs/continuation-prompt.md`. No live playback, volume or NDX mutations.
