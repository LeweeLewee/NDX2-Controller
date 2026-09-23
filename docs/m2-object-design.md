# River Stone: native design for the object

23 September 2026. D027 supersedes treating the rough approved browser prototypes as a final visual constraint. The target is a deliberate listening-room object: calm in the original mineral pebble enclosure, readable when approached on the coffee table, and recognizably music-first rather than a diagnostic terminal.

## Iteration and judgement

1. Enlarged the Playing artwork from 240 to 280 px, rebalanced the right column, reduced permanent status/quality clutter and replaced boxed navigation with quiet labels and a short selection accent. The first native matrix exposed an unlaid-out fixture cover and clipped long track titles. Gate: fail.
2. Corrected cover sizing, bounded the title to two lines with ellipsis, retained readable cached metadata, and made offline plus uncertain outcomes explicit. Reviewed sage/sand/slate, paused, missing artwork, long text, lists, Settings and detail screens. The primary transport still needed stronger emphasis and browse titles needed more presence. Gate: revise.
3. Added a restrained tonal disc and heavier Play/Pause mark while retaining 80 x 64 px targets; enlarged list/search type to 24 px and quietened the query border. Reviewed the final matrix and exercised native pointer paths. Gate: pass for desktop composition and state clarity, subject to the separate limits below.

The judgement is that the screen now belongs more naturally in the enclosure reference: a large visual anchor, quiet mineral colours, generous spacing, clear music hierarchy and restrained controls. This is a designer assessment, not a measured aesthetic score or a claim that the user has approved the result.

## Desktop gate

| Criterion | Evidence / result |
| --- | --- |
| Music leads the composition | 280 px cover, 32 px title, 24 px artist; source and secondary metadata recede. Normal connection text and missing bitrate no longer occupy the music area. Known bitrate remains visible below the cover. |
| Clear primary interaction | Play/Pause has a subtle disc and stronger glyph; next/previous and amplifier controls remain separate with no repeat behaviour. |
| Readable palette hierarchy | Native-exported roles give primary contrast 12.42-13.63:1 and secondary contrast 6.96-7.36:1 against their screen backgrounds. These are sRGB calculations, not LCD measurements. |
| No title collisions | Long track names truncate cleanly over two lines; browse rows use ellipsis and separate artist/type subtitles. |
| Honest abnormal states | Missing real artwork stays unavailable. Offline, uncertain and pending states remain explicit; unavailable mutations are disabled. Cached metadata remains legible. |
| Consistent secondary screens | Outline icons, palette roles, larger browse text, structured settings and coordinated controls reviewed in actual LVGL pixels. |
| Generous distinct targets | Native gate checks all five transport/amplifier targets are at least 72 x 64 px, within the content band and non-overlapping; current targets are 80 x 64. Physical touch is not established. |
| Reproducible review | `python tools/m2_visual_review.py` renders 13 native states, converts captures and builds an ignored review board plus contrast report under `local/m2/design-review/`. The C executable uses synthetic state and the production renderer, with no network/mutation path. |

## Demo content and real artwork

The standalone fixture has three original geometric sleeve studies drawn at display resolution, explicitly selected only by native `fixture:studyN` markers while fixture mode and freshness allow them. They do not replace absent/corrupt network artwork or bypass the authenticated image protocol. `Silent demo` remains visible. Synthetic tracks are A Still Morning, Soft Light and Quiet Hours by River Stone Ensemble; they produce no audio. TLS fixtures retain their authenticated artwork checks and explicit cover variant, independently of track display titles.

Production photographic artwork remains the prior bounded 80 x 80 preview. Enlarging its space does not improve its resolution. Higher-resolution authenticated delivery is still required before claiming finished photographic quality; this gate establishes composition and states using known synthetic content, not a finished live listening experience.

## Fresh verification

- Desktop build and six CTests passed, including the new native visual geometry/state matrix.
- All 128 Python tests passed. The first suite attempt hit the previously observed Windows loopback `ConnectionAbortedError` in unchanged origin-rejection coverage; the unchanged rerun passed. No security check was weakened.
- Full native SDL/LVGL plus silent authenticated TLS screen/artwork smoke passed, including Back, Play, voice, follow/library, settings and consumed wake contact.
- Standalone/TLS transport taps and icon pixels passed, with one command per tap and preserved track identity/wrapping.
- Separate-process preference persistence passed with updated palette pixels.
- Startup outage, delayed read, lost mutation response and restart recovery passed with one silent play and one simulated amplifier request and no replay.
- ESP32 build passed: `0x98810` bytes, 40% application partition free. Compilation only; no flash, efuse, physical action or live audio.

## Still outside this gate

Actual screen contrast, seated viewing distance, finger accuracy, glare, enclosure-material samples, LCD frame timing and power require physical trials. The documented display visible area has a slightly different aspect ratio from 800 x 480; inspect the actual panel rather than treating a desktop screenshot as a physical-size proof. No always-on ornament mode or battery-life claim is added. HP-01 and P3/P4/P5 remain open. Native TIDAL resolution, D011, protected state, authentication and no-replay rules are unchanged.
