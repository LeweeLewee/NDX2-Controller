# Certificate renewal and trust-change recovery - 22 September 2026

This offline slice follows the host setup console at `9aa4c15`. It tests ordinary server-certificate renewal and adds an explicitly approved, same-origin trust-binding update. It does not install or renew production certificates, download trust, change the approved native UI or provision hardware.

## Behavior

A controller is bound to the HTTPS origin and exact trust-file SHA-256, not to a particular server leaf certificate. A replacement leaf signed by the same trusted CA, with valid time and hostname, therefore retains pairing. The TLS fixture proves this with a new leaf key/certificate. The earlier synthetic self-signed certificate doubles as its own trust anchor: replacing it changes trust and needs the explicit update below. Do not mistake that fixture for an operational CA renewal service.

Expired, wrong-host and unexpected-CA certificates fail verification. TLS and hostname checking remain mandatory. Neither failure nor an HTTP success alone authorizes a trust change. There is no automatic fallback to old credentials, re-pairing, trust-on-first-use or command retry.

`Enrollment.update_trust()` accepts only an existing supported bound pairing at the **same origin**. It uses the new trust already verified by the local operator, makes one authenticated snapshot request and requires an observed response. Only then does it atomically replace the saved trust digest in the existing protected controller record. Device ID, credential, origin, provider state, display preferences and durable command history are preserved. It cannot repair revoked/legacy/damaged enrollment or migrate to another host. A different origin requires separate explicit enrollment.

The update deliberately permits the existing credential to authenticate to a server covered by the newly approved trust. Independent identity verification is therefore essential; a successful snapshot is not a substitute for comparing trust with the real bridge administrator.

## Operator procedure

1. Close the desktop controller/helper so setup can acquire the protected-vault lock. Keep the old public configuration and trust file available for diagnosis; do not erase the bridge's authorization or command history.
2. Obtain the proposed trust file through an independently verified local channel. Prepare a public desktop configuration using the same origin and state directory, with the proposed absolute trust path. Setup does not copy/overwrite trust files, modify public configuration or install bridge certificates.
3. Run `python tools/m2_setup.py --config C:/private/ndx-controller/new-desktop.json trust-update` in an interactive terminal. Paths are examples, not an installed configuration. Compare the displayed saved and proposed SHA-256 values and bridge origin with the administrator. Type `UPDATE TRUST` only after independently verifying the change. Cancellation or piped input sends no probe and changes no binding.
4. The approved action sends a snapshot only. If it succeeds and storage commits, use the proposed configuration with the desktop controller. Run `verify` explicitly when needed; no pairing or playback is sent automatically.
5. After interruption or storage failure, close setup, inspect/reopen protected storage and run `status`. It now reports the saved trust digest without needing a trust file or network connection. Match that digest to the retained old/proposed trust and choose the corresponding public configuration. Do not guess or repeat a mutation. If the proposed trust cannot authenticate, the saved old binding remains; resolve server rollout/identity locally. An explicit verified update can later select the old trust again if that server identity is available; no automatic rollback occurs.

## Failure boundaries

| Failure point | Durable result / recovery |
| --- | --- |
| Before confirmation | No network probe or binding change |
| Origin mismatch, changed trust file after prompt, unsupported enrollment | Refuse before attaching/sending the credential to the proposed client |
| TLS/authentication/snapshot failure or interrupted read | Retain old binding; no local commit or remote mutation |
| Atomic write fails before replacement | Current object reports storage uncertainty; reopened storage retains old binding |
| Replacement completes but reporting fails | Current object remains uncertain; reopened storage reports committed new digest |
| Normal completion | Same controller identity/credential with new trust digest; old configuration fails binding validation |

The transaction is one local protected-vault replacement after a remote read. There is no multi-file credential/config transaction or pending remote command to replay. Keep trust files immutable during an operation; the library checks that the current target still matches the target shown at setup. Existing file protection and TLS verification remain intact.

## Fresh evidence

- **118 Python tests passed**, including 11 new library/console cases: one snapshot and identity/history preservation; interrupted/failed probe; failure before and after durable replacement; changed origin; changed trust after setup; revoked/legacy refusal; explicit confirmation; cancellation and noninteractive refusal.
- **`python tools/m2_trust_demo.py` passed** with temporary synthetic CAs and server leaves over actual verified loopback TLS. Same-CA leaf renewal retained pairing. Expired leaf, wrong-host leaf and unexpected CA were rejected. Cancelled and approved console trust updates, protected-vault reopen and old-binding rejection passed. No pairing was repeated; no playback or volume calls occurred. Operator confirmation is injected fixture input, not live operator acceptance.
- **Existing setup and provisioning TLS demos passed** after adding saved-fingerprint diagnostics. Their synthetic secrets remain absent from captured output; no live credential or Naim operation occurred.

`tools/m2_tls_fixture.py` creates only synthetic fixtures under temporary test directories, with the existing exclusive file creation and private-key protection. It is not a production CA tool. No C/LVGL/ESP32 or approved HTML changed; native build/physical evidence remains from earlier checkpoints and was not rerun. No certificate was installed on a real host, no real credentials or configuration were accessed, and no Pi/flash/efuse operation occurred. HP-01 and physical P3/P4/P5 remain open.

Next: intended-host terminal/deployment validation with synthetic setup, then live read-only metadata/artwork/reconnect checks when NDX access is available. Production certificate issuance/scheduling, distribution, installation packaging and physical ESP32 trust rotation remain separate acceptance work.
