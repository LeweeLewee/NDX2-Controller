# NDX2-Controller

A compact, battery-powered coffee-table touchscreen for native Naim music playback, starting with TIDAL.

Project repository: [leweelewee/NDX2-Controller](https://github.com/leweelewee/NDX2-Controller).

**Status: M2 hardware-independent software implemented and tested on the development host; hardware validation remains open.** See the [M2 runbook](docs/m2-software.md), [v1 contract](docs/controller-contract-v1.md) and [native firmware foundation](firmware/README.md). Native TIDAL collection browsing, album/playlist playback, queue edits, transport control and 24-bit playback have been demonstrated on an NDX 2 using a computer. Public TIDAL catalogue search and pagination also pass live tests. Search-result handoff to native Naim playback has passed through the UI; wired System Automation volume down/up are now audibly confirmed and available in the UI. The ESP32 fixture firmware and shared desktop LVGL UI now compile; the physical controller remains unbuilt and unvalidated.

The project's TIDAL developer app is created. Its metadata-only adapter retrieves ranked artists, tracks, albums and playlists. The prototype also supports voice input and live AI music discovery; microphone transcription is user-confirmed. TIDAL account collection controls and persistent Back navigation are implemented; see the collection documentation for live evidence and remaining feature coverage.

The frozen reference is tagged `software-feasibility-v1`. Start the next phase from the [milestone closeout and detailed-design handover](docs/milestone-handover.md).

**Published checkpoint and continuation, 22 September 2026:** [M2 closeout](docs/m2-closeout.md) and [continuation prompt](docs/continuation-prompt.md). The [desktop UI is approved](docs/ui-review/approval.md); the [shared LVGL port and fixture evidence](docs/m2-ui-parity.md) now cover the approved core screens and interactions. Approval does not imply native UI parity or physical acceptance.

## The product

- Compact form with flexible proportions, bespoke touch interface and a substantial, well-finished 3D-printed enclosure.
- Selected display: Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case, 800 × 480 (D017). Android ruled out; hardware validation and procurement remain outstanding.
- Large rechargeable battery and deliberate weight; cable-free use on the coffee table.
- Weeks of standby is a target, not a measured specification.
- Full TIDAL browsing and native playback; other sources can follow.

**The NDX 2 must use its native Naim TIDAL playback path.** The controller and any supporting Pi handle commands and metadata, never audio relay or transcoding. Alternative playback protocols do not satisfy this requirement.

## Documentation

Start current work with the [detailed-design plan](docs/detailed-design-plan.md), [display selection history](docs/hardware/display-comparison.md), [deployment design](docs/deployment-design.md) and [physical interaction trials](docs/interaction-design.md).

| Document | Purpose |
| --- | --- |
| [Updated design concept](docs/design-concept.md) | Selected Waveshare screen, physical direction and parallel investigation brief |
| [Voice and AI discovery](docs/voice-discovery.md) | Describe a mood, refine suggestions and explore native TIDAL content |
| [TIDAL collection](docs/tidal-library.md) | Real hearts, library saves, account connection and Back navigation |
| [Prototype UI](docs/prototype-ui.md) | Run the 800 × 480 demo and configure the experimental live bridge |
| [Product brief](docs/product-brief.md) | Requirements, constraints and unresolved choices |
| [River Stone enclosure](docs/hardware/river-stone/README.md) | Stationary original 01 concept, dimensioned packaging and build constraints |
| [Hardware and parts BOM](docs/hardware/README.md) | Design baseline, parts, sourcing and validation |
| [Architecture](docs/architecture.md) | Control path, responsibilities and integration boundaries |
| [Evidence](docs/evidence.md) | What the live tests actually established |
| [Decisions](docs/decisions.md) | Agreed decisions and their rationale |
| [Roadmap](docs/roadmap.md) | Work and acceptance criteria for the next prototype |
| [Host controller setup](docs/m2-setup.md) | Private pairing, status, read-only verification and local recovery |
| [Development](docs/development.md) | Running diagnostics, tests and keeping records |
| [Research record](docs/research/native-tidal-feasibility.md) | Detailed research and references |

## Tools

Python 3.9+; no third-party dependencies. From the repository root:

```sh
python -m unittest discover -s tests -v
python tools/naim_native_probe.py NDX_IP --output local/naim-inventory.json
```

Replace `NDX_IP` with the streamer's private IPv4 address. The probe is read-only and saves a filtered interface inventory. It does not prove native playback by itself. See [development notes](docs/development.md) before using it.

Live reports and device-specific configuration belong in ignored `local/`. No credentials or raw network captures belong in Git. `tools/naim_client.py` is an experimental native control client; `tools/check_transition.py` is an explicit live playback test. Neither is production firmware. See the development notes for authorized live use.
