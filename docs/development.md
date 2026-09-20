# Development

## Repository layout

```text
docs/       Product, architecture, decisions, evidence and roadmap
tools/      Reusable diagnostic tools
tests/      Offline tests; no live device traffic
local/      Ignored configuration, reports and personal evidence
```

Python 3.9+ is sufficient. There are no external Python dependencies.

```sh
python -m unittest discover -s tests -v
python tools/naim_native_probe.py NDX_IP --output local/inventory.json
```

On a Pi, `python3` may be the interpreter name. Run from the repository root. A later snapshot needs a different output filename: the probe deliberately refuses to overwrite existing reports.

## Diagnostic scope

The probe reads descriptive endpoints on HTTP port 15081. It accepts a private IPv4 target, limits responses, refuses redirects, filters report values, and follows only two exact advertised input descriptions. It does not send play, stop, volume, source-selection, login or configuration commands.

The filter preserves some song/artist metadata. It is a reduction of sensitive content, not a guarantee that reports are anonymous. Keep them in local/ and review before sharing. Do not commit raw response bodies or network captures.

The tests exercise command rejection, redaction, target validation, response limits and redirect refusal using synthetic responses. They do not imply compatibility with a live streamer or prove native playback.

## Documentation workflow

For every meaningful change:

1. Update the relevant roadmap item and describe its acceptance evidence.
2. Add live findings to the evidence ledger with firmware and final device state.
3. Record accepted architectural changes in the decision log; label proposals provisional.
4. Keep the README status accurate. Do not turn a target into a specification without measurements.

Future live playback tests should inspect existing queue/playback first and explicitly verify the resulting state after commands. Network reads may succeed before asynchronous playback transitions finish. Do not use the device's reported digital volume as proof of amplifier control.

## Remote and licensing

The project remote is [leweelewee/NDX2-Controller](https://github.com/leweelewee/NDX2-Controller), configured as `origin`. Its existing visibility is unchanged. No distribution licence has been chosen. The probe is project-authored; external implementations are cited as research references, not vendored code.
## Native client and explicit transition test

`tools/naim_client.py` exposes native collection browsing, playback, transport and queue edits. It validates native references, bounds JSON responses, disallows redirects and never automatically retries a mutation. Search, volume and authentication are not implemented. Calls return device acknowledgements; verify subsequent status before presenting success.

After explicit authorization to replace playback, this live test starts a returned album reference, seeks near the end, samples a transition and recreates the controller connection. It stops playback in cleanup and records whether stop was confirmed:

```sh
python tools/check_transition.py NDX_IP inputs/tidal/albums/ALBUM_ID --replace-playback --output local/evidence/transition.json
```

Use an album ID obtained from native browsing. The output path must not already exist. This is a live test, excluded from offline test discovery. It cannot prove audible gaplessness. See [command evidence](research/native-command-tests.md).

## Catalogue search prototype

The NDX2-Controller application has been created in the [TIDAL developer portal](https://developer.tidal.com/). Use its own client ID and client secret. Do not reuse Naim application credentials or paste secrets into chat, source code or command-line arguments. Live catalogue authentication, search and pagination passed on 20 September 2026. Credentials were used in memory and were not saved to project files.

```sh
python tools/tidal_catalog.py "Massive Attack" --kind artists --country GB
```

The command prompts locally without echo for credentials unless TIDAL_CLIENT_ID and TIDAL_CLIENT_SECRET are already present in its environment. It keeps the token in memory and does not persist credentials. Supported types are artists, albums, tracks and playlists. Use the account's correct catalogue country; GB is a configurable initial assumption.

The API class also exposes page(result_id, kind, cursor) for a result ID and cursor returned by TIDAL. It constructs requests to fixed TIDAL endpoints instead of following arbitrary returned URLs. The CLI shows the first relationship page in returned result order, resolving metadata from included resources. The included array alone is not the result ranking. The interactive prototype supports search pagination and collection pagination. See docs/prototype-ui.md and docs/tidal-library.md for setup and feature limits.

Search result references are explicitly candidates. Before playback, resolve a candidate through NaimClient.browse and verify the returned native object. A live search → native browse → native play test is still required. Catalogue access uses client credentials; personalized cloud resources would require separate user authorization. Existing native Naim collection browsing is already available.

## Milestone reference

`software-feasibility-v1` is the frozen software feasibility baseline. Begin new work with docs/milestone-handover.md and keep decisions, evidence and backlog in the repository. Run `node tests/test_navigation.cjs` alongside the Python suite for UI logic changes. Credentials and private live reports remain outside Git.
