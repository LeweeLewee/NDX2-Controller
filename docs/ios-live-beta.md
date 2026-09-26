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

Local project/distribution checks pass (11), including crossed-mode archive rejection. A sandbox temp-directory permission failure was resolved by running the same test under normal Windows permissions; protections were not weakened. Native source `1fec99157969db2f94c116ccbb994365a54a31ac` passed all 31 tests and the live-mode unsigned device archive in run 36251163829. Artifact 10908933076 SHA-256 verified: `1e42aef3af7fca96e0781dc30f58a86dc121805f40072515906cb32ae99a26bc`. Gallery: `local/ios/review-live-beta/review.html`, 50 captures; four changed captures inspected, 46 pixel-identical to the reviewed 8.1.0 gallery. The captures remain fixtures; they do not prove phone TLS or NDX compatibility. Tag `ios-preview-live-2026-09-26` selects this source for signed release. Host provisioning and all new live observations remain pending. This document does not claim a completed live trial.


## Signed internal release

[Release run 36252070759](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36252070759) repeated all 31 native tests and the live archive gate, then signed and uploaded **0.1.0 (9.1.0)** with `STILL_WATER_LIVE_BETA`. Apple processing completed; **0.1.0 (9.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group with status **Testing**. No credentials or private addresses are compiled into this app. Trial host/address input is still outstanding, so no new live NDX reads, playback, volume or collection mutations have occurred.


## Pairing diagnostics follow-up — 26 September 2026

The Windows host is provisioned and authenticated desktop snapshot/queue reads succeed against the live NDX. The phone reaches the host in Safari after correcting a browser-only port typo, but app pairing still fails and no phone enrollment exists at the bridge. Do not claim the browser typo explains the app failure. Private host details and readback remain in ignored local files. No playback, volume or collection mutations have occurred.

A diagnostic beta now identifies the failing enrollment stage and displays sanitized Keychain status or network/TLS error categories. It keeps the pending-before-request and no-automatic-retry behavior, existing HTTPS trust verification, and full-strength device credentials. Pairing status wraps visibly and the address has an explicit label. This diagnoses the unresolved failure; it is not yet a proven pairing fix. Native validation and distribution are pending.

The diagnostic update also declares NSAllowsLocalNetworking, following Apple guidance for IP-address/local-host transport. There is no NSAllowsArbitraryLoads exception; the client still requires HTTPS, TLS 1.2 or later, exact-host provisioned certificate trust and no redirects. The offline configuration check now requires exactly this narrow local declaration. This remains a candidate compatibility correction until tested on the phone. Reference: https://developer.apple.com/documentation/bundleresources/information-property-list/nsapptransportsecurity/nsallowslocalnetworking


**Pairing diagnostic beta uploaded — 26 September 2026:** source `f0dba3e` (including diagnostics commit `d43a7d1`), tag `ios-preview-live-2026-09-26-pairing-v3`, passed all **32 native tests**, the unsigned device archive, signing and upload in [run 36264297307](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36264297307). The uploaded live build is **0.1.0 (11.1.0)**. The separate branch validation run 36264296786 also passed; artifact 10913830393 SHA-256 `bb416fe9cd69ec5ce3b0901e4df4de941505ae8bb6e5ffe0efcb40b0a799b749` was verified and the revised pairing capture inspected. Eleven local project/distribution checks passed, followed by four passing project checks after the local-network declaration. The earlier diagnostic-only release was cancelled before upload.

Apple processing and existing-group assignment await restored browser sign-in; the existing API key returned HTTP 403 for build reads. Do not claim the diagnostic beta is available in TestFlight yet. Physical pairing remains unresolved: the next attempt should expose a safe stage-specific error if the local-network declaration does not resolve it. No playback, volume or collection mutations.


**Diagnostic beta available — 26 September 2026:** Apple processed **0.1.0 (11.1.0)**, build `6fbc4f31-7ba4-48e1-a522-40668aa021e2`. After the user restored sign-in, it was assigned to the existing **Naim NDX2 Controller TestFlight** internal group and the page verified **Testing**. No tester or permission expansion. This supersedes the pending-processing/group-assignment note above. Phone update and pairing outcome remain pending; request the exact new Setup status if enrollment fails.
