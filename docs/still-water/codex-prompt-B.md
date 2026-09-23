Send only after the screen selection is closed in favour of the iPhone 11. If the Waveshare is selected, rebuild this brief from `docs/still-water/spec.md` Appendix A instead.

---

Continue NDX2 Controller in `local/river-stone-repo`. The user has decided to use an iPhone 11 as hardware-only display, touch and microphone inside the River Stone, with one thin iOS app and the existing Pi bridge doing everything else. Read `docs/still-water/README.md`, `docs/still-water/iphone-architecture.md`, `docs/still-water/spec.md`, `docs/still-water/evaluation.md` and `docs/still-water/decision-draft.md` in full. Open all 22 renders in `docs/still-water/reference/` (`01-sleep` to `22-display`; `02` and `03` are the Presence states and are out of scope for the app; `09-three` is future). Read `docs/still-water/tools/still-water-gates.py`: its rules (targets, overlaps, text size, contrast sampled behind titles, clipping, canvas) are the acceptance rules the app's snapshot tests must implement, in design units after the section 0b anchoring rule. Record the decision in `docs/decisions.md` from `decision-draft.md` under the next available ID (D028 is the design pause) without renumbering.

Scope of this task: a SwiftUI app in a new `ios/` directory implementing `iphone-architecture.md` section 4 and every screen in `spec.md`, plus the bridge-side changes needed to serve it. Do not change the ESP32 or LVGL sources; leave them in place and mark them superseded in `firmware/README.md`.

Keep intact: the v1 bridge codec and its bounded responses, provisioned trust and enrolment, eight-second pending expiry, no replay of any mutation, stale-snapshot rejection, native Naim resolution before any play, D011 amplifier sequencing on the bridge, voice semantics (immediate recording, Stop & search, Restart, Cancel, 30 s limit, no automatic playback), and the rule that the first contact after wake never acts.

Bridge-side additions, all read paths or bounded writes: a battery report action from the app; a `charge?` query for the stone power module returning yes or no from the last battery report with the 35% to 75% window; an artwork preview size up to 320 × 320 for the app while the 80 × 80 path stays for compatibility. Keep the fixture bridge able to drive every app screen without a network or an NDX.

Implementation order:

1. Bridge client and state model in Swift, with conformance tests against the Python fixture bridge.
2. NOW: Still, Touched, Waking, paused, stopped, offline, missing artwork, long titles; rest ladder timers; colour extraction with caching and the contrast rule; fonts bundled.
3. Secondary screens: Up next, Find with the system keyboard, Detail, Library, Ask with on-device speech recognition, Settings group.
4. Kiosk behaviour: landscape lock, window mask with black outside, idle timer handling, wake handling on scene activation, battery reporting.
5. Snapshot tests for the state matrix in `spec.md` section 10, run on the iPhone 11 simulator, implementing the gate rules from `tools/still-water-gates.py`; inspect every snapshot against the matching reference render and the spec tables with the section 0b anchoring rule. Where a render and a table disagree, the table wins; say so in the report.
6. Bridge changes with tests, and a fixture for the power module query.

Validation from the repo root, as appropriate:

    python -m unittest discover -s tests -v
    node --test tests/test_navigation.cjs
    python tools/m2_demo.py
    xcodebuild test -scheme StillWater -destination 'platform=iOS Simulator,name=iPhone 11'

Building and signing need a Mac with Xcode and an Apple Developer account. If the environment lacks them, produce the project and tests, run what can run, and say plainly what was not built.

Finish by updating `docs/roadmap.md`, `docs/evidence.md` for anything proven or disproven, `firmware/README.md` for the superseded targets, and `docs/continuation-prompt.md`. Report concrete changes, actual validation results and remaining blockers. Do not claim standby runtime, wake latency, speech quality or physical readability; those are the measurements in `iphone-architecture.md` section 8. No live playback, volume or NDX mutations.
