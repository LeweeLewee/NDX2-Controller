# Home Assistant bridge trial

The 1 November 2026 user authorization permits deployment on the inspected Home
Assistant Pi and a 24-hour coexistence trial, with Windows retained as fallback.
Native playback remains on the NDX. The iPhone build is unchanged.

## Package

Build a new, source-only local app directory with
`python tools/package_pi_bridge.py DESTINATION`. The builder copies tool Python
sources and pinned bridge dependencies, never local state, tokens or certificates.
Home Assistant OS builds the `deployment/home-assistant` Dockerfile for aarch64.
The container has no Home Assistant/Supervisor API, host network, Docker socket,
device access or ingress. Only the existing HTTPS contract port is published.
No new HTTP routes are introduced. Keep protection mode enabled.

`tools/pi_bridge.py` uses the same bridge contract, artwork bounds, authentication,
rate limits, native Naim adapters, deferred catalogue reads and read-only TIDAL
collection adapter as the Windows trial. Explicit controls enable only the tested
native album/track/queue Play, Pause/Resume, Next/Previous and bounded amplifier
step actions. Collection writes and arbitrary playback URLs stay disabled.

## Private provisioning

Supervisor creates `/app_configs/local_still_water_bridge` when the app first
starts; a start before provisioning exits without opening a listener. The app
maps this directory to `/config`. Provision `/config/private` with mode0700 and:

- `host.json`: private NDX address and explicit boolean `controls_enabled`.
- `server-chain.pem`, `server-key.pem`, `trust.pem`: certificate chain, owner-only
  leaf key and public CA. Include SAN, key usage/EKU, SKI and AKI for strict TLS.
- `vault/authorization.bin`: POSIX owner-only Vault JSON, including `devices`,
  `commands`, `refresh` and `tidal`. TIDAL contains the existing app credentials,
  account tokens and wall-clock `expires_at`; pending OAuth intent is not migrated.

Never copy Windows DPAPI ciphertext as if it were a POSIX vault. Export only in
memory under the owning Windows account and encrypt the migration to a temporary
public certificate generated on the Pi. Verify the transfer checksum before
decrypting directly into the protected app directory. Keep the CA signing key on
Windows; issue a host-specific leaf. No plaintext provider data in browser input,
shell history, app options, image layers, repository, or logs.

The app atomically persists rotated TIDAL tokens. Do not actively use both hosts
against a shared refresh-token session. On rollback, stop the Pi and securely
synchronize its latest TIDAL authorization to the protected Windows state before
restarting Windows if the account token has rotated. Preserve the Windows vault,
TLS identity, launcher and existing device records. A phone origin change requires
explicit local re-pairing; it does not justify weakening trust checks.

Pairing is local-admin only: create `private/issue-pairing`. The service consumes
it and writes owner-only `pairing.json` with one eight-digit, ten-minute code.
The unchanged five-attempt limit and single-use semantics apply. The file is
removed after use/expiry. No code is printed in app logs or exposed through HTTP.

## Trial and acceptance

Take a Home Assistant backup before installation. Verify strict TLS, authenticated
real snapshot/queue/collection reads, 320px artwork and a repeated cached read;
check unauthenticated requests are rejected. Restart only the bridge app and verify
the same operator enrollment works. Enable start-on-boot and Supervisor watchdog.

Run `tools/pi_trial_sampler.sh NEW_PRIVATE_OUTPUT_DIRECTORY` with `nohup` inside
the existing Terminal app. It samples bridge and HA Core resource statistics plus
sanitized bridge status every five minutes for24 hours. Sampling runs on the Pi,
independent of the Windows PC. A Terminal app/Pi restart can interrupt sampling;
missing samples or missing `completed_at` are not a pass. No automatic playback
or volume tests, cloud collection polling or raw response capture occurs.

Host observation start is distinct from phone cutover/acceptance. Check the phone
on the new origin for artwork/navigation, Pause/Resume, Next/Previous and one
bounded volume step. During ordinary use, inspect reconnect/no-replay behavior,
prefetch and artwork retention. At the end inspect logs, resource trends, restarts,
HA availability and user-reported behavior. A completed timer alone is not
acceptance. Preserve Windows fallback until this review passes.
