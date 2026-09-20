# NDX2-Controller

A compact, battery-powered coffee-table touchscreen for native Naim music playback, starting with TIDAL.

Project repository: [leweelewee/NDX2-Controller](https://github.com/leweelewee/NDX2-Controller).

**Status: concept agreed; software feasibility prototype.** Native TIDAL browsing and one-track playback have been demonstrated on an NDX 2 using a computer. ESP32 firmware and the physical controller have not been built.

## The product

- Small square form, bespoke touch interface and a substantial, well-finished 3D-printed enclosure.
- E-paper is the leading display direction, pending interaction testing.
- Large rechargeable battery and deliberate weight; cable-free use on the coffee table.
- Weeks of standby is a target, not a measured specification.
- Full TIDAL browsing and native playback; other sources can follow.

**The NDX 2 must use its native Naim TIDAL playback path.** The controller and any supporting Pi handle commands and metadata, never audio relay or transcoding. Alternative playback protocols do not satisfy this requirement.

## Documentation

| Document | Purpose |
| --- | --- |
| [Product brief](docs/product-brief.md) | Requirements, constraints and unresolved choices |
| [Architecture](docs/architecture.md) | Control path, responsibilities and integration boundaries |
| [Evidence](docs/evidence.md) | What the live tests actually established |
| [Decisions](docs/decisions.md) | Agreed decisions and their rationale |
| [Roadmap](docs/roadmap.md) | Work and acceptance criteria for the next prototype |
| [Development](docs/development.md) | Running diagnostics, tests and keeping records |
| [Research record](docs/research/native-tidal-feasibility.md) | Detailed research and references |

## Tools

Python 3.9+; no third-party dependencies. From the repository root:

```sh
python -m unittest discover -s tests -v
python tools/naim_native_probe.py NDX_IP --output local/naim-inventory.json
```

Replace `NDX_IP` with the streamer's private IPv4 address. The probe is read-only and saves a filtered interface inventory. It does not prove native playback by itself. See [development notes](docs/development.md) before using it.

Live reports and device-specific configuration belong in ignored `local/`. No credentials or raw network captures belong in Git. The initial code is a diagnostic tool, not a production control library.
