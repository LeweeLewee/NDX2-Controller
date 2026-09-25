# Architecture

> **D030 update — 25 September 2026:** iPhone 11 + selected UGREEN power bank replace Waveshare as active physical hardware. [Mounting/interface proposal](hardware/river-stone/iphone-mount/README.md) is under discussion. Earlier Waveshare hardware/UI implementation details below are retained fallback; native playback and bridge security requirements remain. This physical-design update does not implement or approve the entire iPhone software/power draft.

## Detailed-design status — 21 September 2026

D017 selects Waveshare ESP32-S3-Touch-LCD-4.3B without case and rules out Android. D018 specifies a provisional embedded-controller/always-on-bridge partition; Pi reuse depends on private host inventory. See [deployment design](deployment-design.md) for credentials, pairing, renewal and recovery gates, and [phase plan](detailed-design-plan.md) for dependencies. The development-host v1 bridge, secure storage/recovery, desktop contract harness and native LVGL fixture foundation are implemented; see [M2 software](m2-software.md) and [contract](controller-contract-v1.md). The ESP32 HTTPS worker is implemented and compiled; protected provisioning, on-device networking, Pi hosting and physical validation remain open. The optional/direct paths below describe feasibility-era architecture, not the current deployment recommendation.

## Required playback path

```mermaid
flowchart LR
    UI[Native 800 x 480 controller] -->|Authenticated HTTPS| PI[Always-on bridge: development host; Pi conditional]
    PI -->|Native commands and metadata| NDX[Naim NDX 2]
    TIDAL[TIDAL service] -->|Native Naim audio retrieval| NDX
    NDX --> AMP[Existing Naim amplifier]
```

This is the intended architecture. The solid local control path was exercised from a computer; the native firmware fixture compiles and the shared LVGL UI passes a desktop TLS fixture flow, and Pi deployment remains conditional. Network packets to TIDAL were not independently captured, but the live native endpoint, native queue class and player source identified the Naim TIDAL path. The test process fetched no audio.

## Responsibilities

**Controller:** rendering, touch input, local UI state, cached artwork, sleep/wake policy and battery monitoring. It sends high-level requests and rechecks actual device state after reconnecting.

**NDX 2:** native music retrieval and decoding, native queue and playback state. Existing amplifier integration must be preserved.

**Bridge (provisional D018):** provider credentials, search/collection adapters, artwork processing, voice/AI and native Naim commands. Development-host implementation exists; the Pi is a conditional hosting option after inventory. Home Assistant's web page is reachable; no authenticated HA integration has been inspected or installed.

## Observed local interface

The tested NDX 2 exposes HTTP port 15081, API 1.4.0 and appVer 3.11.0.5662. Firmware changes could affect behaviour.

| Operation | Observed request or reference |
| --- | --- |
| System information | `GET /system` |
| Input descriptions | `GET /inputs` |
| Current playback | `GET /nowplaying` |
| Native queue | `GET /inputs/playqueue` |
| Favourites | `GET /favourites` |
| Native content | Returned `inputs/tidal/artists/...`, `albums/...`, `playlists/...`, `tracks/...` references |
| Single native track playback | `GET /inputs/tidal/tracks/{returned-id}?cmd=play` |
| Stop request | `GET /nowplaying?cmd=stop` |

Some GET requests mutate playback. HTTP method alone is not a read-only guarantee. The diagnostic tool uses a fixed command-free allowlist.

Native playback reports `source=inputs/playqueue`, `sourceDetail=tidal`; the queue item class was `object.track.tidal`. Merely seeing playqueue is not enough to identify the music source.

Do not assume every duration uses the same units: the track description returned seconds, while now-playing duration and advancing position appeared in milliseconds. Negative position occurred during startup. Production parsing needs explicit per-field handling and tests.

## Extensibility

Separate UI requests from service adapters and Naim player commands. Future providers must satisfy the same native-playback requirement. Avoid building a universal audio server as a shortcut. Native queue edits and wired System Automation amplifier control have passed live tests. Search uses the project’s public TIDAL catalogue adapter. Native search syntax is not required by this prototype; long-running authentication renewal and recovery remain deployment validation work.

## Catalogue metadata prototype

The computer-side UI uses a loopback-only Python bridge in tools/prototype_ui.py. It runs a labelled demo by default; optional live catalogue and NDX configuration use the existing adapters. This is an implementation aid for the chosen display, not a committed Pi deployment or ESP32 firmware architecture. See [prototype scope and validation](prototype-ui.md).

tools/tidal_catalog.py implements public TIDAL catalogue search separately from native Naim playback. It uses this project's own developer credentials, sends only metadata requests, and returns candidate native IDs for subsequent resolution on the NDX. It does not import Naim credentials, fetch playback manifests or transfer audio. Credentials and tokens stay in the computer/Pi process; provider secrets will not be deployed to the controller (D018). Live search and pagination pass for artists, tracks, albums and playlists. Public search → native track resolution → playback has passed through the UI. AI discovery supplies catalogue queries only; see [voice discovery](voice-discovery.md).

## Account collection and phase boundary

The prototype also uses the project’s own TIDAL OAuth authorization for collection read/write, with exact album/artist metadata links and native resolution before playback. See [collection integration](tidal-library.md). The computer bridge is a proven reference implementation, not a selected final deployment. Software feasibility is closed; [the handover](milestone-handover.md) governs detailed design and records the remaining reliability and hardware gates.

## Approved UI implementation boundary — 22 September 2026

D020 approves the [desktop design](ui-review/approval.md). Its core screens and interactions are now ported to the shared C/LVGL renderer and bounded state model. The browser board remains a design artifact, not ESP32 runtime. [Native parity and evidence](m2-ui-parity.md) records the metadata/collection/voice extensions, current desktop tests and firmware compilation, and remaining artwork/device integration. Native adapter semantics and the separate physical acceptance gates are unchanged.
