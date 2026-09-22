# Deployment design — initial selection

20 September 2026 design; implementation update 21 September. The [M2 software workstream](m2-software.md) implements authenticated development-host TLS, pairing/revocation, protected persistence, atomic/single-flight renewal and command recovery with synthetic tests. No Pi installation, live LAN deployment or networked ESP32 service client has been validated.

## Responsibility boundary

Use an always-on bridge for metadata, account authorization, artwork resizing/cache and voice/AI requests. D017 selects Waveshare with native ESP32 display/touch firmware (LVGL candidate, version to pin after example review). Do not assume the ESP32 runs the prototype browser. The computer UI/adapters remain the frozen behavioral reference.

Android browser/kiosk deployment is retired by D017. Pi host selection, authenticated controller transport and firmware credential protection remain open deployment gates.

The bridge sends native Naim commands; the NDX 2 retrieves and decodes TIDAL music itself. No music audio, playback manifests, relay or substitute route passes through the bridge. User-initiated microphone clips are voice input, not playback audio. Wired amplifier control retains D011: one press plus four held frames spaced 0.2 s, one bounded burst per tap, busy until completion, no automatic retry or numeric level.

Prefer the existing home-automation Pi if it supports an isolated service with adequate storage, RAM and CPU headroom and reliable uptime. Inventory OS/install type, runtime support, backups, resource use, network reachability and administrative access privately first. A supported container or dedicated service account may fit a general-purpose OS; do not assume Home Assistant OS accepts arbitrary system services. Select the packaging after inventory. Avoid an unnecessary Home Assistant integration dependency: the bridge can use the proven Naim adapters directly. If host constraints fail, present a separate-host proposal before migration or purchase.

This partition keeps provider secrets off the controller, avoids embedding cloud authentication and AI complexity in limited display firmware, and lets the controller sleep while native playback continues. Its cost is bridge availability: when unavailable, show unavailable/stale state and offer reconnect; do not invent an alternative audio path. No queued playback mutations during outage.

## Credentials and trust

- Persist provider configuration, OpenAI key and TIDAL refresh authorization only on the bridge, outside Git and the web root. Use OS-protected service credentials where supported; otherwise an owner-only service directory/files (directory 0700, files 0600 on Linux). Encrypt backups with separately managed keys; a key next to ciphertext is not protection from host compromise. Full-disk/offline protection depends on host capabilities and must be recorded.
- Access tokens can remain in memory. Persist refresh-token rotations atomically before reporting renewal complete; retain the old token only when the provider omits a replacement. Serialize concurrent refresh requests. File errors fail visibly rather than silently losing durable authorization. Test process interruption around replacement. Disconnect deletes durable local authorization and caches; account-side revocation remains separate.
- Pair each controller using a short-lived, single-use setup code approved at the local administration interface. Issue a revocable device credential with control-only privileges. Provider secrets never appear in firmware, browser responses, command arguments or logs. Controller credential storage and ESP32 flash protection remain an implementation gate; a physically extracted device credential must be individually revocable.
- Use authenticated HTTPS for controller-to-bridge traffic with provisioned trust; validate certificates and define renewal before deployment. No public port forwarding. Restrict listening/firewall exposure to intended local clients; LAN membership alone is not authentication. Browser administration also requires authentication, origin/CSRF defenses and bounded requests.
- Preserve OAuth state, PKCE and collection-only scopes. Register a supported exact deployment callback after host identity and the provider's current callback rules are checked. The existing loopback redirect cannot simply become a remote callback. Complete account login in a trusted browser, then return only status to the controller. Never work around this with captured Naim tokens.

Current evidence: the prototype binds `127.0.0.1`, constrains Host/Origin, stores tokens in memory and contains refresh logic. The separate M2 service now adds tested TLS/controller authentication and durable single-flight renewal. Neither implementation proves secure host deployment or long-running provider renewal.

## Recovery contract

| Event | Required behavior |
| --- | --- |
| Controller wakes/reconnects | Discard pending gestures/commands; reconnect, authenticate, fetch current source/transport/queue and account status; display freshness and mark cached artwork/state stale until reconciled |
| Bridge or NDX unavailable | Disable device mutations; keep browsing context; bounded read retries with exponential backoff/jitter (initial design 1, 2, 4, 8…30 s), immediate explicit reconnect available |
| Mutating command timeout | Outcome unknown; never replay playback, queue or volume automatically. Read state where possible. Volume has no reliable absolute read-back: show uncertainty without corrective burst |
| Duplicate controller request | Unique request ID and server duplicate suppression. On server restart, uncertain previously sent mutations remain unknown; do not claim exactly-once delivery across NDX/network failure |
| Account token expiry | Single-flight refresh before expiry; persist rotation. Transient provider failure is distinct from revoked/invalid authorization; bounded retries for reads/refresh only, no automatic collection write replay |
| Revoked authorization | Mark collection disconnected and offer explicit reconnect; native Naim playback remains independent of this account session |
| Saved-state read fails | Unknown state, not unsaved; preserve existing fresh-read/write-once/read-back semantics |
| Other Naim app changes playback | Refresh actual player/queue state; do not overwrite it from controller cache. Native state is authoritative |
| Bridge reboot | Restore protected configuration/token state, start without playback/volume commands, then reconcile; report unavailable until adapters ready |

Proposed active-state polling: 2 s now-playing, queue refresh on entry/known changes; back off errors and pause controller requests during sleep. Measure load and adjust before acceptance. Do not poll cloud collection continuously. Bound artwork dimensions/cache, voice duration/upload size and request concurrency; port proven adapter logic rather than exposing diagnostic scripts wholesale.

## Deployment acceptance

The shared native controller now has an asynchronous, bounded HTTPS transport implemented for ESP-IDF and an authenticated SDL desktop transport. The ESP32 source compiles; only the desktop path has executed against TLS fixtures. Default firmware is offline unless encrypted NVS, secure boot, flash encryption and provisioned host trust/device authorization are present. No efuse changes or real controller provisioning have been performed. The protected NVS field contract and pinned build commands are in [firmware instructions](../firmware/README.md); physical trust bootstrap, revocation and recovery remain acceptance work.

Produce fixture tests for restart/atomic rotation, concurrent renewal, revoked tokens, forbidden unauthenticated clients, expired setup codes, wrong server certificates, duplicate/time-out commands and sanitized logs. Then run a private host trial: restart bridge and controller; expire/renew authorization; disconnect Wi-Fi and NDX independently; alter playback in Naim app; recover without duplicate mutations. Exercise known bounded volume only as an announced audible test, never a CI step. Verify actual native playback state, not HTTP success alone.

Run a proposed 24-hour host coexistence trial including voice/search bursts; record resource use and Home Assistant health before/during/after. This is an initial integration gate, not production reliability proof. M4 retains long-duration operation and battery testing. Current host suitability, callback registration and ESP32 credential provisioning remain open. Pairing, revocation and durable bridge storage now have development-host synthetic tests; they do not establish Pi or physical-controller deployment acceptance.

## Settings design boundary — 22 September 2026

Approved Settings screens illustrate display preferences, Wi-Fi, pairing/revocation and device diagnostics. The browser review implements local fixture behavior only; it provisions no real network or credential. Native UI integration must use the protected provisioning/trust interfaces above and clearly report unavailable hardware capabilities. Approval does not close host selection or on-device deployment gates. See [continuation](continuation-prompt.md).

## M2 enrollment and revocation foundation - 22 September 2026

The [offline provisioning slice](m2-provisioning.md) adds protected enrollment intent, origin/trust-bound controller records, durable uncertain/revoked states, local ID inventory and setup-code cancellation. The desktop helper enforces new record bindings while preserving legacy fixtures. Fresh evidence: 93 Python tests, read-only TLS enrollment/revocation/re-pairing demo, native UI/artwork smoke and outage-recovery demo passed. No C/ESP32 or UI changes; prior build evidence was not rerun. Production setup UI, physical installation and HP-01/P3/P4/P5 remain open.

## Host setup console - 22 September 2026

The [operator setup flow](m2-setup.md) adds local status, hidden-code pairing, explicit read-only verification and confirmed local forgetting. It rejects piped secret input and echo fallback, retains durable unknown outcomes and supports local recovery without a trust file. Fresh evidence: 107 Python tests, setup/TLS fixture demo and enrollment regression demo passed; zero live commands or real credential changes. Native UI/firmware are unchanged. Physical terminal echo and deployment/hardware gates remain separate.
