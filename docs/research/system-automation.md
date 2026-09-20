# System Automation volume investigation

The user confirms that both the NDX 2 remote and the Naim app already change the
connected amplifier's volume through the wired remote connection. The amplifier
model is not a prerequisite for reproducing this existing NDX control path.

Naim calls this **System Automation**. Its [support documentation](https://www.naimaudio.com/help/product-compatibility-for-integrated-and-pre-amps-nait-nac-nap)
describes app volume and input control. The [older NDX guide](https://media.focal-naim.com/naim/file_manager_files/produits/old-products/ndx-1/system-automation.pdf)
describes RC5 output and wired remote connections; it is background, not an NDX 2
HTTP command specification.

## Established facts

- Static Android app inspection now identifies the System Automation volume
  requests below. One volume-down request was accepted by the NDX during
  playback; audible confirmation is pending.

- Live `/automation` reads report enabled=1 and class `object.automation`.
- The existing `/levels/room` trial changed numeric readback without changing
  audible amplifier volume. It is not a working System Automation command.
- Advertised UPnP services expose generic volume setters, but no explicit
  System Automation action. No UPnP mutations were tried in this investigation.
- Public [Naim app protocol reference](https://github.com/M4rque2/Naim-App-Reversed/tree/40e09315504595923d78b7aafa74ee5d2376559a)
  was inspected as text. Its REST volume code does not establish the required
  amplifier command; legacy n-Stream commands are not evidence for this NDX 2.

## App implementation evidence

Inspected Focal & Naim Android package `com.naimaudio.naim.std`, version 8.2.2,
version code 1449320, downloaded from the [APKPure package page](https://apkpure.net/focal-naim/com.naimaudio.naim.std/download).
The package was read as data, never installed or run. XAPK SHA-256:
`1f4e20cda5fa0011168d4ddbcfe5894c308a8f4968b453f9c1ee404aa29699c9`.
This is a mirrored package; signing-certificate provenance was not independently
verified. No app binary, decompiled source or bundled credentials are committed.

In `classes19.dex`, Retrofit annotations on
`com.naimaudio.leolib.data.repository.AutomationAPI` establish:

| Method | HTTP request | Parameter |
| --- | --- | --- |
| `decreaseVolume` | GET `/automation?cmd=irVolumeDown` | Boolean query `repeat` |
| `increaseVolume` | GET `/automation?cmd=irVolumeUp` | Boolean query `repeat` |
| `toggleMute` | GET `/automation?cmd=irMuteToggle` | None |

The separate `com.naimaudio.leo.LeoAutomation` implementation corroborates the
volume commands: it appends the boolean to `?cmd=irVolumeDown&repeat=` or
`?cmd=irVolumeUp&repeat=` and calls the product's GET request method. A bounded
single tap uses `repeat=false`; hold/repeat behaviour is not validated.

The first live trial sent exactly one GET
`/automation?cmd=irVolumeDown&repeat=false` after confirming automation enabled
and music already playing. The device returned its normal automation response.
Player state remained playing, position advanced from 100075 to 102060 ms,
and error stayed 0. No track, queue, output setting or volume-up request changed.
Filtered trial details are in ignored `local/evidence/system-automation-down-test.json`.
The user found the single-tap change too small to judge. A second announced
trial sent five discrete down commands, 0.5 seconds apart, each with
`repeat=false`. All five were accepted; playback remained active with error 0
and position advanced 183066 to 186070 ms. The resulting level was left for the
user to assess; no upward correction was sent. The report is in ignored
`local/evidence/system-automation-five-down.json`.

**Audible effect, volume-up and mute remain unverified.** Do not expose volume
as working in the product UI until the user confirms the physical effect.

## Targeted app capture — failed on the phone; retired

The subsequent user trial again made the NDX disappear from the Naim app.
The log contained only the computer's two verification requests, with no phone
requests or volume command. Thus successful computer-side forwarding did not
establish phone connectivity or app compatibility. The recorder was stopped;
the user set Configure Proxy back to Off and confirmed the NDX was visible
again. Direct NDX reads still returned HTTP 200, power on, automation enabled
and playback error 0. No volume command was sent by the recorder.

Do not repeat phone proxy setup as the next investigation step. The precise
failure cause is unproven; the old phone address, phone-to-computer access and
PAC handling were not independently verified. Future command discovery needs
app implementation evidence or a capture method that preserves normal phone
network settings.

`tools/naim_request_recorder.py` is a temporary diagnostic, not part of the UI
server. It generates an automatic proxy configuration (PAC) that routes only
HTTP requests to the selected NDX through the recorder. All other destinations
remain direct. It does not intercept TLS or record response bodies/headers.
Query and JSON body fields are filtered to command metadata. Keep reports in
ignored `local/evidence/`; they can contain private device references.

Unlike the retired restricted proxy, it forwards all ordinary HTTP methods and
paths on the explicitly configured NDX ports, including device descriptions,
pagination and the user's app commands. Requests are sent once, never retried.
The accepted phone address and listening interface must match the current LAN.
The PAC permits direct fallback if the recorder is unavailable. The server
expires after 15 minutes by default; restore the phone's proxy setting to Off
after the capture regardless.

Local fake-device tests passed for startup reads, pagination, PUT forwarding,
redaction, target restrictions and PAC fallback. Live read-only checks through
the recorder returned HTTP 200 for the PAC, NDX automation metadata and the
advertised device-description XML. **Phone capture subsequently failed as
described above; it did not identify a volume command.** No amplifier
commands were generated by these checks.

The subsequent static app inspection above supersedes command discovery through
this failed recorder. An HTTP acknowledgement is still not proof of amplifier
movement.
