# Controller bridge contract v1

All traffic uses provisioned HTTPS trust and hostname validation. No redirects, CORS, cookies or query-string credentials. `POST /v1/pair` accepts `{ "code": "locally issued one-use code" }`; returns a device ID and bearer credential once. Every `POST /v1/request` requires `Authorization: Bearer …` and `Content-Type: application/json`.

```json
{"version":1,"request_id":"unique_16_to_64_character_id","action":"search","args":{"query":"quiet","kind":"albums","offset":0}}
```

Request IDs are 16–64 ASCII letters/digits/underscore/hyphen. Max request 8,192 bytes; response 32,768 bytes; strings 256 UTF-8 bytes except opaque provider cursors (4,096). Integers exclude booleans. Offsets are 0–10,000. Unknown fields/actions/versions are rejected. Pages contain at most 12 items. `next_offset` consumes the remainder of a provider page before using its `cursor`; retain `result_id` with search pagination. Native browse uses absolute offset. Queue is bounded and view-only. Oversize downstream responses fail explicitly, never silently truncate a command result into success.

| Action | Args | Meaning |
| --- | --- | --- |
| snapshot | none | Authoritative player, first queue page/total, account status, revision, age and validity |
| search | query, kind, optional offset/cursor/result_id | Catalogue candidates only |
| browse | reference, optional offset | Native resolution; item, playable, bounded children |
| queue | optional offset | Queue view |
| library_page | kind, optional cursor/offset | Bounded account collection page; same provider-page slicing as search |
| library_state | reference | Fresh read; saved / unsaved / unknown |
| library_save | reference, saved boolean | One explicit write with adapter read-back; no retry |
| play | reference | Resolve through native Naim again, then one replace/play request |
| transport | pause/resume/stop/next/prev command | Single native command |
| amplifier | up/down direction | One D011 burst, both directions serialized/busy |
| voice_review | fixture label | Bounded silent transcript fixture; physical upload not enabled |
| suggest | prompt | Fixture search queries only; live AI integration not enabled here |

Responses have `version`, `request_id`, `boot_id`, `fixture`, `outcome`, `data`, and `error` (null or `{code}`). Outcomes are `observed` for reads, `submitted` for a command accepted by the adapter, `rejected` before dispatch, and `unknown` when dispatch may have occurred. The UI adds local `pending`/busy while a request is in flight. Submitted is never proof that the requested track is playing; fetch authoritative player/queue state. No confirmed numeric amplifier state exists.

Errors include `VERSION_UNSUPPORTED`, `INVALID_REQUEST`, `INVALID_REQUEST_ID`, `INVALID_ACTION`, `INVALID_ARGUMENT`, `BUSY`, `STATE_STALE`, `REQUEST_ID_CONFLICT`, `JOURNAL_FULL`, `RESPONSE_TOO_LARGE`, `SERVICE_UNAVAILABLE`, `NOT_CONFIGURED` and `OUTCOME_UNKNOWN`. HTTP 401 covers authentication failure; malformed transport requests return 400. Provider errors, tokens, private addresses and raw responses are never echoed.

Snapshot `age_ms` includes time spent reading player and queue; `valid_for_ms` is the remainder of a five-second validity window. The client uses a monotonic deadline measured conservatively from request start and must mark cached information stale after it, regardless of wall clock or delayed delivery. Bridge boot IDs and revisions identify snapshots; reconnect always discards pending work and replaces player/queue/account state. Per-controller server freshness also rejects mutations if no successful snapshot was fetched in five seconds. Browsing context survives. Read recovery uses bounded exponential backoff with jitter up to approximately 30 seconds; mutations are never retried. A timeout becomes unknown even if the bridge eventually applies the command.

The durable journal is scoped to `(device ID, request ID)` and includes a canonical action/args fingerprint. A repeat returns its existing outcome; changed contents using the same ID are rejected. Before dispatch the bridge atomically records unknown, so a crash cannot cause replay after restart. It records submitted only after adapter return. A single non-blocking service lock rejects overlapping calls as busy; HTTP processing and adapter calls are bounded/serialized. The journal caps at 10,000 entries and then fails closed. It does not evict IDs automatically. A future retention protocol must introduce an explicit credential/session boundary before deleting suppression history. Exactly-once delivery across the NDX/network is not claimed.

Voice upload is intentionally not accepted in v1: fixtures exercise recording, 30-second stop without submission, explicit Stop & search, Restart, cancel, leaving the screen and network loss. The planned physical interface is bounded 16 kHz/16-bit mono PCM, max 30 s (960,000 bytes), streamed via a separate authenticated route once capture/pins and provider format are validated. Do not send base64 audio through the 8 KiB JSON route. AI suggestions and transcripts become searches and cannot issue playback commands.


## Native UI metadata extension — 22 September 2026

Snapshot optionally includes `current_item` (null when no verified TIDAL track is available). Item fields `artist`, `album`, `kind`, `artist_reference` and `album_reference` are optional bounded strings. Relationships come from the existing exact provider adapter and never grant playback capability. The native codec reads player source, transport, artist/album, duration/position and optional bitrate; missing or invalid numeric metadata remains unavailable, never zero or an inferred quality value. Live bitrate units/availability still require observation before a positive UI quality claim.

`voice_review` retains its wire name but is requested only by explicit Stop & search; there is no separate review screen and the 30-second limit never requests transcription or search. Physical uploads remain disabled. `library_page` is read-only and uses the existing account adapter. Security, request limits, journal suppression, TLS and mutation reconciliation are unchanged.

## Bounded artwork extension - 22 September 2026

`artwork` takes one required `reference` argument through authenticated `POST /v1/request`. Snapshot `player.artwork` and browse `item.artwork` optionally hold `/artwork/<64 lowercase hex>.jpg` references registered from allowed native metadata. They are identifiers, not accessible HTTP routes. Unknown/expired/unregistered references and corrupt images return `observed` with `{ "available": false }`; authentication/revocation applies before image work.

An available reply carries `available: true`, matching `reference`, `width: 80`, `height: 80`, `format: "rgb565be-hex"`, `pixels` (exactly 25,600 lowercase hex characters, big-endian RGB565) and `valid_for_ms` (1-60,000). Existing request/response ceilings remain. Client validity starts at request start and requires fresh authoritative state plus the still-visible reference/generation. Expiry, navigation, changed artwork and disconnect remove the cover. Optional image failures cannot cause mutation replay or a playback failure. These previews are initial bounded integration, not final image quality.

Bridge input: JPEG only, 1 MiB maximum, at most 1024 pixels per side, checked before decode. Normalized cache: four entries; registrations: 32; validity: 60 seconds. Raw bytes are discarded after normalization; negative caching suppresses corrupt-image decode loops. The existing URL allowlist/redirect refusal remains; clients cannot supply source URLs. See [memory and deployment limits](m2-artwork.md).


## Still Water Brief A extension — 23 September 2026

All actions below use authenticated TLS `POST /v1/request`, version 1, with the existing request IDs, trust/revocation checks, Origin rejection, 8-KiB request and 32-KiB response ceilings and single-flight execution. No new HTTP route exists. The current server bounds concurrency (one worker, queue of eight, five-second socket timeout); it has no independent requests-per-second limiter. Existing provider limits are unchanged. Screen selection remains open; neither UI is implemented by this extension.

### Artwork chunks

`artwork` still requires `reference`; optional `side` is an integer 1–320 (default 80), and `pixel_offset` is an integer multiple of 6,400, starting at zero and strictly below `side * side`. Booleans, floats, unknown arguments and invalid offsets are rejected. Omitting both additions preserves the complete legacy 80 × 80 response, including its original fields and format.

For a non-80 size, an available response carries the existing fields plus `offset`, `total_pixels`, `next_offset` (null on completion), and `image_id` (SHA-256 of the whole resized RGB888 image). Width and height describe the whole square, while `pixels` contains at most 6,400 row-major RGB565 pixels, at most 25,600 hex characters. A 320 × 320 image requires 16 reads. For example, send `{"reference": "<registered reference>", "side": 320, "pixel_offset": 0}`, then follow `next_offset`.

Clients must assemble only matching reference, dimensions, image_id, boot and visible generation; validate offsets/lengths and finish within every chunk's validity measured from its request start. Discard the assembly on unavailable data, mismatched identity, expiry, navigation or disconnect. A changed source between reads produces a different image_id; never mix it with earlier chunks. No client assembler or renderer is added in this bridge-only slice.

The same allowlisted registered JPEG source, RGB conversion, Lanczos square resize and RGB565 quantization apply. Registration count (32), registration/cache TTL (60 s), four-entry LRU and source bounds (1 MiB compressed, at most 1024 × 1024 before decode) are retained. Cache keys include reference/side/offset; each entry stores at most the original 25,600 hex characters plus its digest, so total cached pixel payload remains at most 102,400 characters. Only one chunk is encoded at a time. The transient resized RGB888 raster is at most 307,200 bytes, within the existing source decode/conversion scale; no complete high-resolution hex image or persistent source image is retained. A cache miss may re-fetch/re-decode the source, trading throughput for bounded retention. Deployment-host peak memory and throughput remain unprofiled. Corruption is negatively cached per chunk. Registration refresh does not extend an existing cache entry's expiry.

### Last battery report and charge query

`battery_report` requires `level` (integer percentage 0–100), `charging` (JSON boolean) and `client_id` (1–64 ASCII letters, digits, underscore or hyphen). Unknown/unavailable battery measurements must not be sent as a valid level. The authenticated write replaces one in-memory last report, with a bridge-owned monotonic receipt timestamp; response is `observed` with `{"accepted": true}`. Client id is a label, not a credential or role grant. Existing paired-device authority applies; this does not introduce separate display/module ACLs. No history, persistence, provider call, playback freshness renewal or mutation-journal entry is created. Reports are observations, not commands: send fresh measurements, never queue/replay old reports on reconnect. Invalid reports leave the previous report and its age intact.

`charge?` takes empty args and returns `observed` with both `charge` and `reason`. Brief A.1 adds the reason without changing charge decisions:

| Last report | `charge` | `reason` |
| --- | --- | --- |
| None since this bridge boot (including after restart) | `no` | `none` |
| Exists, but no longer younger than 3,600 seconds | `no` | `stale` |
| Fresh (age from 0 inclusive to 3,600 seconds exclusive) | `yes` or `no`, per the window below | `window` |

`reason` is always one of these three strings; every fresh reply uses `window`, including `{"charge": "yes", "reason": "window"}`. A report with a negative age is treated as stale. The distinction lets a power module distinguish a current window decision from missing/expired telemetry; it does not implement a fallback or authorize a hardware action.

No report, a restart, or report age >= 3,600 seconds gives no. With a fresh report: below 35% gives yes; at or above 75% gives no; 35–74% follows the reported charging boolean. This uses the last physical charging observation to maintain the window, without a second latched state or treating a prior yes as proof that charging started. Querying never refreshes report age. This is an advisory read only: no power switch, MCU fallback, battery-life claim or hardware control is implemented.


### Brief B1: artist metadata read

`artist_bio` is a read under the same authenticated v1 envelope, taking only `reference: inputs/tidal/artists/<numeric id>` (1–32 digits). It returns `reference`, `available` (biography present), `biography` (plain text or null), and `artwork` (registered portrait reference or null). Missing catalogue/relationships return unavailable, not invented text. Provider failures remain rejected/unavailable. No route, pairing, freshness-for-mutations or journal rule changes.

Biography HTML is stripped, script/style content discarded, entities decoded and whitespace normalized. At most 2,000 Unicode scalar values (8,000 UTF-8 bytes) are returned; the 32,768-byte envelope bound stays intact. This allowance applies only to `biography`; normal client strings retain their 256-byte bound. Only exact artist relationships from catalogue metadata are used. Portrait URLs pass the existing HTTPS TIDAL JPEG allowlist and registration, normalization, four-preview cache, chunk identity and expiry checks; callers cannot supply image URLs. Portrait/cover consumers use the existing 320 preview assembly. This read grants no playback capability and calls no NDX mutation.
