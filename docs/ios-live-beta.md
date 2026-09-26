# Live NDX beta trial — 26 September 2026

The user authorized proceeding from the committed UI beta to live NDX testing. Preserve source `0f9ecc6`, tag `ios-preview-2026-09-26-b1-amendment`, and TestFlight 0.1.0 (8.1.0). Work continues on `codex/still-water-live-beta`; the newer primary checkout remains untouched by app changes.

## Build and trust

Only the explicit `STILL_WATER_LIVE_BETA` build condition enables bridge transport and enrollment. Other builds default to silent preview. Existing preview tags remain silent. The `ios-preview-live-*` tag convention selects the live mode through the existing internal-only signing workflow and existing app/group. No public release, new route or bundled credential is introduced. Both simulator modes remain fixture-driven, never contacting the NDX in CI.

An unpaired live build opens Pairing. Import the bridge certificate, verify its fingerprint independently, and enter a short-lived single-use console code. The existing client validates HTTPS hostname and certificate chain against that trust, refuses redirects and stores the bound enrollment in device-only Keychain. No automatic re-pair or mutation retry. Disconnect, stale state and uncertain outcomes retain existing gates.

Real speech remains disabled for this first control trial; use the keyboard for search. The microphone reports unavailable instead of asking for audio access. Provider search and collection require separately configured bridge credentials; do not confuse missing provider configuration with an empty collection. The privacy manifest remains accurate for this build: no tracking or developer collection, existing local preference/uptime reasons; no speech capture.

## Trial sequence and evidence

1. Select the bridge host and confirm the private NDX address. No provisioned live bridge was found in this checkout; user input is pending. Keep credentials and addresses in ignored `local/`.
2. Read-only native inventory, followed by authenticated phone pairing, snapshot, artwork, queue and available browse reads. Record actual firmware/state and distinguish desktop evidence from phone evidence.
3. Announce audible trials; capture existing playback/queue, test one transport action at a time, and verify authoritative device state. Do not substitute generic URL, AirPlay, DLNA or TIDAL Connect for native Naim TIDAL playback.
4. Test native TIDAL selection and collection changes using exact observed references. Record any intended queue replacement before performing it. Restore reversible collection changes.
5. Test amplifier volume separately using the D011 bounded one-press/four-held-frame sequence only. No arbitrary numeric level or inference from digital volume; audible confirmation requires the user.
6. Test reconnect/background/foreground and uncertain outcomes without replay. Never stop the bridge midway through an unverified mutation merely to test recovery.

Local project/distribution checks pass (10). Native build, signed distribution, host provisioning and all new live observations remain pending. This document does not claim a completed live trial.
