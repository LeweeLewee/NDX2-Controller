# Software feasibility closeout and detailed-design handover

**Accepted: 20 September 2026. Frozen baseline: `software-feasibility-v1`.**

The prototype achieved its purpose: demonstrate that a bespoke controller can browse, discover and manage TIDAL music while retaining native Naim NDX 2 playback and controlling the connected amplifier. It is a working computer-side reference, not finished embedded firmware or a production system.

## Start here in the next phase

Read this document, [decisions](decisions.md), [architecture](architecture.md), [roadmap](roadmap.md) and [hardware baseline](hardware/README.md). The repository is authoritative for requirements, code, decisions, evidence and backlog. New work must update those records; this chat is not needed to reconstruct the design.

The next task is **detailed design and hardware proof**, not further unrestricted feature expansion. Keep the baseline available for comparison and fix blocking defects. Add features when they resolve a specific design question.

## Verified capabilities

| Capability | Evidence and limits |
| --- | --- |
| Native Naim TIDAL playback | Native track, album and playlist playback, transport and queue operations demonstrated. The bridge never relays audio. |
| Catalogue search | Ranked tracks, albums, artists and playlists, pagination and native result resolution. |
| Amplifier volume | Wired Naim System Automation down/up audibly confirmed. Bounded press/held-frame sequence; no inferred numeric amplifier level. |
| Playback quality | Max setting enabled native 24-bit playback; higher sample rates and audible gaplessness are not fully tested. |
| Voice and AI discovery | Actual browser microphone transcription user-confirmed; recommendations lead to catalogue/native browsing. Embedded microphone untested. |
| Artwork and UI | Tonal artwork, transport, queue listing/addition, Back with restored browsing context, album/artist shortcuts from Now Playing. |
| TIDAL collection | Account-authorized save/remove round trips passed for albums, tracks, artists and playlists. Album search results have save/unsave hearts. Test changes restored. |

Detailed observations, including earlier failed experiments and subsequent resolutions, remain in [evidence](evidence.md). Historical entries are chronological evidence, not the current status summary. The latest applicable checks passed 52 Python tests and five JavaScript tests. Backend queue operations are proven; queue-edit buttons are still backlog work.

## Fixed requirements and design direction

- Native Naim TIDAL playback is mandatory. No audio proxy, generic URL playback, AirPlay, Chromecast or substitute playback route.
- Compact bespoke touchscreen in a substantial 3D-printed enclosure. A conventional tablet is too large.
- Preferred display: Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case, 800 × 480. Hardware validation remains outstanding.
- Large battery in the base; weight is welcome. Weeks of standby with touch wake is a target, not a measured claim. Cable-free use does not remove the need to design charging.
- Charcoal/sage/sand prototype palette and tonal artwork; finish and colour can follow final materials.
- Existing home-automation Pi is available as a possible control/metadata host. Final placement of the bridge is undecided.

## Next-phase work and acceptance gates

1. **Hardware proof:** evaluate the selected screen, actual touch usability, microphone options and wake behavior. Measure whole-board sleep, idle and active consumption before sizing the battery or promising runtime.
2. **Deployment:** decide controller versus Pi responsibilities. Design secure persistent credentials, account renewal, connection recovery, stale-state handling and coexistence with the Naim app. The current loopback-only server is not a LAN deployment configuration.
3. **Interaction design:** use the real 4.3-inch screen to decide navigation, touch targets, loading feedback and error recovery. Prioritize deferred queue/playlist editing and shuffle/repeat/seek controls explicitly.
4. **Enclosure:** package the measured hardware, base battery, charging, ventilation where needed and service access. Print fit prototypes before finalizing finish.

Proceed to an integrated physical prototype only with a selected power path, defensible energy budget, usable physical-screen interaction and a documented deployment/recovery plan. Production reliability remains a later gate.

## Reproducing the reference

From the repository root, use Python 3.9+:

```sh
python -m unittest discover -s tests -v
node tests/test_navigation.cjs
python tools/prototype_ui.py
```

The last command starts the silent demo at http://127.0.0.1:8990. See [prototype setup](prototype-ui.md), [TIDAL account setup](tidal-library.md), [voice setup](voice-discovery.md) and [System Automation protocol](research/system-automation.md) for live configuration. Use the project's existing service credentials through the documented local prompts or approved environment configuration; never add them to source or command arguments.

TIDAL app credentials and account tokens are held in the running process. Restarting requires configuration/reconnection; a browser tab is not a durable deployment. OpenAI credentials, local addresses, personal live reports and raw captures deliberately remain outside Git. Preserve private configuration separately if moving machines. The transient running server and chat are not required to run the documented demo or configure a fresh live session.

## Conversation retention

Archive the completed prototype conversation as supporting history rather than deleting it. Start detailed design in a fresh task against this repository and this handover. Archiving is organizational; the repository remains the source of truth regardless of whether the historical conversation is retained. No task creation or chat archive is implied by this document.
