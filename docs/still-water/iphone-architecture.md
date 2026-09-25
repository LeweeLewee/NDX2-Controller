# Still Water on iPhone 11: hardware-only architecture

> **Current selection — 25 September 2026 (D030):** user selected iPhone 11 and UGREEN Nexode 20000mAh PD 20W QC Power Bank. Waveshare is parked fallback. Earlier “selection open” text below is historical. [Concealed mounting proposal](../hardware/river-stone/iphone-mount/README.md) governs the current physical discussion; the 118 × 54 mm window remains provisional. The draft custom battery/boost/MCU architecture, operating configuration and runtime expectations below are not validated or adopted wholesale. Do not execute embedded implementation prompts from this hardware-selection update.

23 September 2026. Working architecture after the decision to use an iPhone 11 as the display, touch and microphone hardware inside the River Stone, running a single thin app, with the Pi bridge doing everything else. Supersedes the Waveshare display selection for this design; see `decision-draft.md`. Housing direction (D014), native Naim playback (D001), bounded amplifier control (D011), recovery, trust and no-replay rules are unchanged.

## 1. Roles

| Element | Does | Does not |
|---|---|---|
| iPhone 11, stock iOS, no account | Wakes on tap, draws the Still Water screens, captures voice, reports battery level, sleeps | Hold credentials, talk to the NDX, search catalogues, run AI, poll while asleep |
| Pi bridge (existing) | Authenticated control and metadata service, native Naim resolution, artwork normalisation, catalogue search, transcript and discovery services, charge-window decisions | Carry audio |
| Stone power module (new, small) | 20 Ah pack, 5 V boost, load switch on the phone's charge feed, battery gauge, one MCU (ESP32-C3 class) that asks the bridge whether to charge | Anything the user sees |
| NDX 2 | Plays TIDAL natively, as today | |

The phone is a terminal. If it is replaced by another phone or a different panel later, the bridge and the design do not change.

## 2. Phone configuration ("hardware only")

No Apple ID, no iCloud, no SIM, cellular off, no passcode, no Face ID. Wi-Fi on; Bluetooth, AirDrop, hotspot off. Low Power Mode on. Background App Refresh, Siri, notifications, location, analytics, automatic updates off. Auto-lock 30 s, brightness fixed by the app. Guided Access with its own exit code, or Autonomous Single App Mode through a free MDM profile if Guided Access does not survive a battery shutdown and restart.

The app is installed with a paid Apple Developer account (signed for a year) or TestFlight. A free account requires re-signing every seven days and is not acceptable for a table object.

Jailbreaking is not used. It does not reduce power draw and pins the phone to old iOS versions.

## 3. Display window

The panel is a 6.1" IPS LCD, 1792 × 828 px at 2× (326 ppi), about 139.9 × 64.6 mm in landscape, with a notch at one short end in landscape and rounded corners. The inlay exposes a rectangular window and the app paints pure black outside it. Because this is an LCD, black is backlit dark grey rather than off: the opaque inlay hides everything outside the window, and Asleep is always the panel off through auto-lock, never a black frame. Inside the window the darkest tones carry a faint glow in a dark room, which suits the wet-stone reading.

| | Value |
|---|---|
| Window, physical | 118 × 54 mm, centred on the panel, notch band and corners hidden by the inlay |
| Window, points | 755 × 346 pt at 2×, inset 70 pt from the long edges and 34 pt from the short edges of the 896 × 414 pt landscape screen |
| Design units | 1048 × 480, where 1 unit = 0.7206 pt = 0.1126 mm. `spec.md` coordinates are in these units |
| Orientation | Landscape, notch on the left (Lightning connector at the right; home indicator along the bottom long edge), locked in the app |

The old 800 × 480 canvas was 95.5 × 54.4 mm. The window is the same height and 22.5 mm wider, so every physical size in `spec.md` carries over unchanged. Section 0b of `spec.md` says how the extra width is used.

## 4. App

Swift and SwiftUI, one target, iOS 17 or later. The iPhone 11 (A13) runs current iOS, so stay on it; do not downgrade for a jailbreak.

| Module | Responsibility |
|---|---|
| Bridge client | The existing v1 request and reply codec over TLS with the provisioned trust and enrolment, ported from `bridge_protocol.c`. Same actions, same bounded responses, same eight-second pending expiry, no replay |
| State | A struct mirroring `controller_t`: screen, context history of four, online, fresh-until, outcome, voice state, current track, transport, artwork reference |
| Screens | Still, Touched, Waking, Up next, Find with the system keyboard, Detail, Library, Ask, Settings group. Compositions per `spec.md` |
| Colour | Three-colour extraction from the bridge's artwork preview per `spec.md` section 6, cached by artwork reference. The bridge may send a larger preview than 80 × 80 now; the extraction still runs on a downsampled 80 × 80 |
| Voice | `AVAudioSession` capture on tap, on-device `SFSpeechRecognizer` for the transcript, transcript sent to the bridge as a search or discovery request. Cancel, Restart, Stop & search and the 30 s limit as today. Nothing plays automatically |
| Wake | On `scenePhase` becoming active: consume the wake contact (first touch never acts), fetch authoritative state, render Waking then Still. No timers or network while inactive |
| Power report | On every wake and every 15 min while active, send battery level and charging state to the bridge. Also register a background processing task that requires external power, so the phone reports while a charge window is running and the bridge can end the window at 75% instead of the MCU's fallback timer. Nothing else runs in the background |
| Kiosk | Landscape lock, idle timer disabled only while Touched or Ask, status bar hidden, home indicator hidden, black outside the window |

Not in the app: credentials for TIDAL or Naim, catalogue keys, AI keys, any direct NDX access.

## 5. Power module in the stone

| Part | Role |
|---|---|
| 20 Ah Li-ion pack with protection | Reservoir. Charged through the rear inlet |
| 5 V boost, 2 A, with true shutdown | Feeds the phone through a load switch |
| Load switch (P-channel MOSFET or a switch IC) | Opens and closes the charge feed |
| Fuel gauge on the pack | Reports pack level to the MCU |
| ESP32-C3 class MCU | Wakes every 10 min, asks the bridge `charge?` and gets `yes` or `no` with a `reason` (`window`, `stale` or `none`), derived from the phone's last reported level (charge from below 35% until 75%; D029). On `yes` it closes the switch; on `no` with `window` it opens it; on `stale`, `none` or an unreachable bridge it applies a bounded fallback of 20 min charging in every 6 h, so a sleeping phone still gets topped up overnight. It reports pack level and sleeps |
| Lightning cable to the phone, or a Qi coil behind the cradle | Wired is 20 to 25% more efficient and simpler; Qi keeps the phone port free and the cradle clean. Start wired |

The MCU is also the natural home for the light seam later. It is not a controller and never sends playback commands.

## 6. Budget, to be measured

| Item | Expectation |
|---|---|
| Phone standby, hardware-only configuration, aged cell (3,110 mAh nominal) | 5 to 8% a day |
| Phone in use, 30 min a day plus voice | about 0.5 Wh; the LCD backlight draws the same for dark and light content, so the dark design saves nothing here |
| Pack usable | about 62 Wh from 74 Wh nominal |
| Stone runtime between charges | 40 to 60 days wired; about 40 over Qi |
| Wake to drawn Still screen on the LAN | under 1 s |

These are expectations. The measurements that decide them are in section 8.

## 7. What this removes from the previous plan

- ESP32-S3 display firmware, LVGL re-engineering, bitmap fonts, the partition table change, gradient dithering, the RGB panel tearing question.
- External MEMS microphone, pin audit, PCM upload.
- Deep-sleep and touch-wake proof on the Waveshare (HP-01 as written).
- The 16-bit banding and non-square pixel workarounds in `spec.md` section 0.

## 8. Gates before commitment

1. Two-day standby measurement of the configured phone on Wi-Fi with a USB meter, screen off, Guided Access on.
2. Wake latency from tap to drawn Still screen against the existing bridge.
3. Guided Access behaviour through a low-battery shutdown and restart.
4. Speech recognition quality from seated distance with music playing, ten queries quiet and ten with music, same acceptance as `interaction-design.md`.
5. Heat in the sealed shell while the pack charges the phone, with the cradle at 50°.
6. Touch through the inlay window edge: no cover is added over the panel in this design; the window is a clear opening.

## 9. Build dependencies

An iOS app needs a Mac with Xcode and an Apple Developer account. If neither is available, the fallback is a full-screen web app served by the bridge and pinned with Guided Access in Safari. It gives the same visuals but microphone access from a standalone web app on iOS is unreliable, so voice would stay on the bridge side with a wired or Bluetooth microphone. Confirm the Mac and account before starting the app.
