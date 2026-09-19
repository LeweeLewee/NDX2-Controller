# Native Naim TIDAL controller — feasibility record

Research date: 19 September 2026. Updated after live testing: native TIDAL browsing and a single-track native playback command have SUCCEEDED on the user's NDX 2. Full product feasibility is still pending search, queue, amplifier and quality validation.

## Live result

The NDX 2 responded on its local HTTP port 15081, API 1.4.0, firmware appVer 3.11.0.5662. Home Assistant's web page was also reachable. No Home Assistant configuration was changed.

The streamer returned 300 favourites, including objects classified as native TIDAL playlists, albums, artists and tracks. Following the native references returned real content: a playlist with 50 tracks, an artist with three albums, an album with 21 tracks, and individual track metadata. This was actual device browsing, not mock data or a separate TIDAL library.

With the streamer initially idle and its queue empty, the test sent:

```text
GET /inputs/tidal/tracks/448228338?cmd=play
```

This played the discovered track Eternity by Alex Warren. Naim reported FLAC, 16-bit/44.1 kHz, error 0 and transportState 2. Position advanced from 3065 to 6130 milliseconds between polls. The Naim internal queue gained one item classified `object.track.tidal`. Subsequent state explicitly reported `source=inputs/playqueue` and `sourceDetail=tidal`. These observations establish successful control through the native Naim TIDAL path, rather than generic renderer playback.

The test process made only local JSON control/status requests. It fetched, decoded and relayed no audio; Home Assistant was not involved in playback. No packet-level cloud-route capture or audible-output confirmation was performed, and this short test does not establish prolonged stability or high-resolution performance.

A stop command was sent after the brief test. An immediate read still showed the previous playing state, demonstrating asynchronous state changes; a later read showed transportState 1 and position 0. The device was no longer reporting active playback. The selected test item remains in the queue. The levels endpoint reported volume 13 both before and after; no volume command was sent. That numeric value has not yet been established as actual amplifier volume.

Read-only probes of `/inputs/tidal/search?query=Massive%20Attack`, `/inputs/tidal/search` and `/search` returned HTTP 400. These parameter/path guesses did not establish native search. They do not show that native search is impossible. The correct search interface still needs to be identified.

Evidence files: `naim-lan-inventory.json`, `naim-native-followup.json`, `naim-native-browse.json`, `naim-native-playback-test.json`, `naim-stop-and-search.json`. The earlier `naim-first-inventory.json` records only the restricted network attempt, which failed; the elevated local-network test succeeded.

The sections below retain the original research rationale; live findings above supersede questions they have answered.

## Non-negotiable requirement

The controller must launch and control the NDX 2's native Naim TIDAL playback, as used through the Focal & Naim app. The NDX 2 must fetch and decode the audio. A Pi may provide control, catalogue and artwork services, but must not relay, decode or transcode audio. Music Assistant-to-DLNA, AirPlay, Chromecast and Roon playback are excluded as substitutes. Merely providing a cloud audio URL to a generic renderer is not sufficient proof. TIDAL Connect is a distinct route and is not silently substituted for the requested Naim-app integration.

The wider brief remains: compact square bespoke touch UI, ESP32-class hardware, e-paper under consideration, substantial replaceable battery and reassuring weight, printed enclosure, cable-free coffee-table use, weeks of standby. Full TIDAL browsing is required. Other services may follow only through compatible native playback paths. An existing home-automation Pi is available; model and software are not yet known.

## What the evidence establishes

1. Naim documents integrated TIDAL and TIDAL Connect separately. Native service support on the streamer is established; a public third-party control contract is not.
   Source: https://www.naimaudio.com/help/streaming-music-with-naim-sources-and-compatibility

2. Naim's 2020 Control4 announcement explicitly includes NDX 2 and browsing/playback of TIDAL. This is a historical official external-controller precedent, not verification of a current standalone Pi implementation.
   Source: https://m.naimaudio.com/ja/node/27887.html

3. Naim's Crestron announcement explicitly includes NDX 2, service search, personal collections, recommendations and TIDAL/Qobuz playlists. It distinguishes media control from zone control and states that streaming-service credentials are built into the driver. The exact authentication scheme, permitted access and current compatibility need establishing. Do not infer that a normal TIDAL developer key provides equivalent capabilities.
   Source: https://www.naimaudio.com/news/naim-adds-crestron-support

4. A community Naim client contains HTTP reads for system, inputs, now-playing, levels and favourites, plus generic browsing of `ussi` item references and item-play requests. It is an implementation lead. There is no TIDAL-specific login, search or queue construction in the inspected client; it does not prove full native TIDAL control on NDX 2. The repository's verified model list does not explicitly include NDX 2.
   Sources: https://github.com/mase1981/uc-intg-naim
   https://raw.githubusercontent.com/mase1981/uc-intg-naim/main/uc_intg_naim/client.py

5. Naim software director Steve Harris historically described TIDAL Connect's cloud queue separately from Naim's native implementation. His explanation is useful architectural context, not current firmware documentation. Historical resolution/MQA claims are not used as current specifications.
   Source: https://community.naimaudio.com/t/tidal-connect/11949/82

## Current unknowns

- Does this NDX 2 expose the local HTTP interface on port 15081?
- Does a native TIDAL input expose browsable objects, or is catalogue browsing performed by the app against TIDAL separately?
- Where are native session/account state and playback authorization maintained?
- What exact native queue request starts an arbitrary TIDAL item? A generic play/pause endpoint cannot answer this.
- Can our authorized integration obtain the required service access without depending on proprietary embedded credentials?
- Which network command controls the existing amplifier System Automation path? A digital volume value on the streamer must not be mistaken for amplifier volume.
- Does the native path support the required quality, queue transitions and coexistence with the Naim app on the installed firmware?

Some Intrinsic driver catalogue/document URLs could not be retrieved through the available web tools. No driver package was obtained or inspected. No claim is made about its internal protocol or licensing. No vendor has been contacted.

## Prepared read-only probe

`naim_native_probe.py` runs with Python 3.9 or later, including on a suitable Pi. It uses standard-library HTTP requests and requires no packages or credentials.

It queries a fixed allowlist of descriptive endpoints only: root, system, inputs, now-playing, levels and favourites. It checks an alternate `/naim` prefix if needed. It reads `inputs/tidal` and `inputs/playqueue` only when those exact paths are advertised by the device. It does not follow arbitrary returned links or redirects, and issues no query-string commands. It writes a bounded report containing field structure and selected metadata; unknown scalar values and credential-like fields are omitted. It never saves the original response bodies. Selected song names and artwork-independent metadata may remain in the report.

Run on a computer able to reach the NDX 2. Replace NDX_IP with the actual private IPv4 address:

```text
python3 naim_native_probe.py NDX_IP --output naim-idle.json
```

On Windows, the launcher may be `python` instead of `python3`.

If native TIDAL is already playing through the Naim app, take another snapshot with a different filename, such as `naim-native-tidal.json`. The probe will not start playback itself. It does not overwrite existing reports.

Six local automated tests pass for command rejection, fixed GET reads, default-deny redaction, advertised-input filtering, target validation, body limits and redirect refusal (some cases are combined). These unit tests use synthetic responses. Separate live investigations are recorded above. An accessible HTTP port or a TIDAL-labelled input alone must not be reported as playback success.

## Live validation sequence

1. Obtain the NDX 2 address, firmware version and baseline native-TIDAL status. Identify the Pi's software and network reachability.
2. Inspect the read-only reports. Follow only positively identified descriptive objects after reviewing their semantics.
3. Establish the app's native queue mechanism and authorization. If necessary, observe only relevant app-to-NDX traffic on the user's own network, keeping account tokens out of reports. Read-only state snapshots can narrow the question but cannot reconstruct every command. Stop at any access boundary that requires vendor-provided integration access rather than improvising a substitute playback path.
4. Implement the smallest native queue operation with an authorized track selection. Do not change amplifier volume until its control mechanism is established.
5. Verify the selected track and the following queued track play through Naim's native path. Confirm source/queue state and the network audio route against a Naim-app baseline. Continuing for a few seconds after disconnecting a controller is insufficient proof because buffering can conceal a relay.
6. Check catalogue search, albums/playlists, queue edits, metadata, amplifier volume, app coexistence and native audio quality. Record actual results rather than inferring them from successful HTTP responses.

Single-track native control and content browsing are now established by live evidence. Full acceptance still requires catalogue search, queue operations and transitions, amplifier control, current audio-quality settings, coexistence with the Naim app and longer operation. These should be established before final hardware and firmware decisions.
