# Still Water: visual design package for the native UI

23 September 2026. Design handover for the Still Water UI, platform-neutral pending screen selection between the iPhone 11 (`iphone-architecture.md`) and the Waveshare 4.3B (`spec.md` Appendix A). Bridge protocol semantics, recovery, security and D011 are out of scope and must not change.

| File | Purpose |
|---|---|
| `iphone-architecture.md` | Roles, phone configuration, display window, app modules, power module, budget and the measurement gates |
| `spec.md` | The design: principles, tokens, rest-state machine, every screen in design units with coordinates, artwork colour extraction, fonts, motion, abnormal states, acceptance criteria |
| `decision-draft.md` | D028 wording for the decision log |
| `codex-prompt.md` | Two briefs: bridge additions now (platform-independent), and the iOS app once the screen is selected |
| `evaluation.md` | The design evaluated against the project goals and the automated gate, with what was changed as a result |
| `reference/still-water.html` | Interactive prototype, 22 states (open in a browser; fictional music, no device commands) |
| `reference/*.png` | Reference renders of all 22 states at exactly 800 × 480 design units, at the spec type sizes |
| `tools/still-water-gates.py` | Playwright script that renders every state and checks targets, overlaps, text size, contrast and clipping |

## This sprint

Lock the design, not the platform: extend the prototype to the full state matrix, freeze this spec at v1.0, put the prototype on the iPhone 11 on the table under Guided Access, run the two-day standby measurement, and have Codex do only the bridge additions. Choose the screen at the end of the sprint; then one final build.

## Scope

In: visual composition, typography, colour, hierarchy, motion, touch layout, rest ladder timing based on last touch and transport state.

Out: presence sensing, light seam, enclosure CAD changes beyond the inlay window, queue editing, AI suggestions beyond the existing search path, any new network route from the phone, always-on operation, any battery claim.

## Panel check

Section 0 of `spec.md` records the iPhone 11 panel facts and section 0b the window and unit mapping; Appendix A records the Waveshare panel facts and LVGL implementation notes.

## Precedence

D027 authorises this redesign of the visual layer and D028 (draft) the platform. Where this package conflicts with `docs/m2-object-design.md` pixel geometry or `docs/hardware/design.md` display selection, this package wins. Where it conflicts with `docs/decisions.md`, `docs/controller-contract-v1.md` or `docs/m2-recovery.md`, those win and the conflict should be recorded in the roadmap rather than resolved silently.
