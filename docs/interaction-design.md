# 4.3-inch interaction trial

20 September 2026. Initial design specification for physical trials, not validated UI or a feature expansion. Preserve charcoal/sage/sand and tonal artwork from the reference.

D017 selects Waveshare and rules out Android. The 800 × 480 layout and external microphone investigation below are the active trial plan; actual panel usability remains unproven.

## Canvas and tasks

Use landscape 800 × 480 on the actual HW-001. Start with a 56 px top strip (Back, title, connection/battery status), 360 px content and 64 px bottom navigation (Now Playing, Find, Collection, Queue). Coordinates are a trial layout, not a manufacturing drawing. Reserve at least 8 px gaps and start at 72 × 72 px for primary touch targets; verify physical millimetres on the actual panel rather than assuming square pixels or a desktop scale. Start body text at 24 px and secondary text at 20 px; adjust after seated reading. Keyboard is a separate full-width mode with navigation temporarily replaced by input controls.

| Screen | Initial content and interaction |
| --- | --- |
| Now Playing | Artwork about 240 × 240; title/artist/album with exact detail links; previous/play-pause/next; separate amplifier minus/plus row. Busy volume disables both until the bounded request completes; no slider or continuous hold |
| Find | Search field plus Speak and Ask for music; result-type filters on a separate row. Large rows open details; album heart is an independent hit target. Unknown saved state is explicit |
| Details | Artwork/title and distinct Play now, Play next, Add to queue and save actions. Avoid squeezing all onto one row; scroll content while Back remains available |
| Collection | Albums, tracks, artists, playlists; sign-in required state routes to browser-assisted setup. Saves show pending then verified result, retain scroll and never imply a failed lookup means unsaved |
| Queue | Readable queue, current item and existing add flow. Reserve a future edit mode rather than adding unprioritized reorder/delete controls |
| Voice / discovery | Explicit start, recording indicator, Stop, Cancel and 30 s limit; transcript review before submission; suggestions lead to catalogue/native resolution, never automatic play |

On wake show immediate local feedback, suppress the wake gesture and reconcile state. Stale state displays its age/offline status; disabled playback controls explain reconnecting. Preserve query, filter, pagination, scroll and nested Back context through detail navigation. Timeouts distinguish failure from unknown mutation outcome; no generic retry button that repeats volume or playback.

## Physical trial acceptance

Run silent fixtures before live commands. From a seated position complete: wake, find an album by typing, open it and return to the same list position, save/remove in a clearly simulated collection, add to queue, reach Now Playing, use separate simulated volume buttons, dictate/review/cancel, refine an AI brief and explore a catalogue result. Use representative long titles and unavailable artwork as well as ideal content.

Record task completion, mis-taps, reading difficulty, latency and layout clipping with normal finger input. Initial gate: all tasks completed without external keyboard/help, no accidental play/volume activation, no clipped essential controls, and no more than one corrected mis-tap across ten repeated selections of each critical control. These are proposed usability targets; user comfort on the actual table decides final sizing/tilt. A desktop screenshot cannot pass this gate.

## Microphone experiment (after pin audit)

Audit HW-001 occupied RGB/touch/storage/expander pins and available peripheral bandwidth before selecting a digital MEMS microphone (I2S candidate) or another supported capture route. No onboard suitable microphone is assumed. Add one BOM row for the function; choose exact part only after voltage, bus, connector, pin conflicts and power isolation are resolved.

First capture bounded mono PCM clips locally with the display/Wi-Fi active; record sample rate/format, dropped samples, clipping, RAM/stream buffer and active/standby power. A provisional 16 kHz/16-bit/30 s mono clip is 960,000 payload bytes: validate the chosen transcription route and buffer strategy rather than assuming browser WebM support on ESP32. Do not add cloud/API configuration just to validate electrical capture.

Then test ten representative music queries from seated distance in quiet and ten with music playing at an ordinary level, using the existing authorized bridge setup. Record correct key artist/title/mood words, correction effort and capture failures; initial target ≥9/10 usable transcripts in each condition with review before action. Include Cancel, timeout, leaving the screen and network loss: capture must stop, discard cancelled audio and never play automatically. Recordings remain transient/private. Compare a provisional enclosure microphone opening against bare-board capture before final placement. No always-listening or wake word is added.
