# Decision draft: D028, iPhone 11 as hardware-only display inside the River Stone

For Codex to record in `docs/decisions.md` without renumbering. Draft wording; the user accepts or edits.

## D028 - iPhone 11 as hardware-only display, touch and microphone

**User decision, 23 September 2026.** Replace the Waveshare ESP32-S3-Touch-LCD-4.3B display selection (D017) with the user's iPhone 11 (6.1" LCD, 1792 × 828) running stock iOS in a hardware-only configuration: no account, no SIM, Guided Access or Autonomous Single App Mode, one thin app that wakes on tap, draws the Still Water screens, captures voice, reports battery level and sleeps. The Pi bridge remains the only holder of credentials and the only path to the NDX 2; native Naim TIDAL playback (D001), bounded amplifier control (D011), recovery without replay, trust and persistence are unchanged. The River Stone housing direction (D014) is unchanged; the inlay exposes a 118 × 54 mm window and hides the notch band and corners, which answers the visual-identity objection recorded in D015. Power comes from a 20 Ah pack in the stone that tops the phone up inside a bridge-controlled charge window through a small power module; weeks of standby remains an unmeasured target. Jailbreaking is not used. The decision selects the display; it is not evidence of standby runtime, wake latency or speech quality, which are gated in `docs/still-water/iphone-architecture.md` section 8.

Superseded by this decision: the LVGL re-engineering brief in `docs/still-water/codex-prompt.md`, the external microphone investigation, the ESP32 partition change, and HP-01 as written for the Waveshare. D015 and D017 remain as history; their reasoning about a visible phone is addressed by the inlay window rather than overturned.
