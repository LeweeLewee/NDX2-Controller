# M2 provisioning and revocation foundation - 22 September 2026

This is the authorized offline design/fixture slice following `82acab3`. Host-side lifecycle code and local administrator controls are implemented and tested. It is not a production setup UI, physical credential installer, Wi-Fi provisioning tool or deployment acceptance.

## Trust and ownership

The operator must supply the HTTPS bridge origin and independently verified trust file through a trusted local channel before pairing. There is no discovery-based trust, trust-on-first-use, certificate download, redirect acceptance or fallback to HTTP. The host foundation validates origin shape, uses the existing verified TLS client and binds new controller credentials to the canonical origin and SHA-256 of the supplied trust file. Changing either requires explicit enrollment recovery; leaf renewal under an unchanged trust bundle needs no binding change. CA/bundle replacement needs a separately planned authenticated migration, not silent acceptance.

The bridge remains the sole holder of provider authorization. `Pairing.issue()` creates one 120-second setup code with the existing five-attempt limit. The existing local console displays that short-lived code only on explicit `pair`. Do not capture that console into shared logs. No bearer credential is printed, placed in command arguments, added to a public config or returned by the new status API. The bridge persists only each device's credential hash. The controller's existing protected Vault stores its own credential and public binding. No new network administration route is added.

Local administration now supports `devices` (IDs only), `cancel` (invalidate the unredeemed code), and the existing `revoke DEVICE`. A failed storage operation reports a generic failure instead of claiming success. Revocation affects subsequent authentication; a request already admitted may complete, and revocation cannot undo a native Naim command. Device revocation is separate from provider-account disconnection.

## Implemented host lifecycle

`tools/m2_provisioning.py` provides `Enrollment(vault, url, trust)` with these operations. This is a library boundary exercised by the demo, not a finished user setup flow.

| Operation/state | Behavior |
| --- | --- |
| `status()` / unpaired | Redacted local status; no network or pairing code |
| `pair(code)` | Persist versioned pending intent before exactly one `/v1/pair` request; validate the returned device/credential and atomically persist the bound record |
| Unsupported/damaged local record | Report `recovery_required`; refuse pairing/credential use rather than overwrite or downgrade |
| Pending after interruption | Report `outcome_unknown`; never repeat enrollment automatically |
| Storage failure | Report `storage_uncertain`; stop using the current enrollment object until storage is inspected/reopened |
| Paired | Durable authorization exists; this does not claim current connectivity |
| `verify()` | One authenticated snapshot only; never play, volume, transport, save or microphone submission |
| Transient verify failure | Retain pairing; explicit read verification may be attempted later |
| HTTP 401 | Persist `authorization_required`; subsequent credential loads fail closed until explicit recovery |
| `forget()` | Explicitly remove only local controller/enrollment records; preserve other vault data, preferences and command history; no remote revocation claim |

The desktop helper uses the bound credential loader. New records must have supported version/state, valid device/credential shape and matching origin/trust digest before credentials can be used. A bound record without its enrollment marker is rejected, not downgraded. Legacy unbound fixture/manual records remain compatible, but receive no retroactive binding guarantee and are not automatically migrated. Explicitly re-enroll such installations before production acceptance. Helper startup errors are generic and close protected storage without printing private configuration.

## Recovery procedure and design boundary

1. Record the existing bridge controller IDs locally before setup. Obtain verified trust and the intended origin out of band; do not learn them from an untrusted pairing response.
2. Issue a fresh code at the bridge's local console. Enrollment receives the code in memory, with no shell argument or durable copy.
3. Pair once, persist authorization, then verify by snapshot. Connectivity failure after durable pairing calls for read-only verification, not a second pairing.
4. If pairing outcome is unknown, inspect bridge IDs locally. Revoke an identified orphan before explicitly forgetting local enrollment and issuing a fresh code. If the identity is ambiguous, resolve it locally; do not guess or revoke every controller. Storage failures require reopening/inspection first because durable state may differ from the failed process's memory.
5. To remove a controller, revoke its ID at the bridge and verify rejection. Forgetting its local credential alone is not revocation. Lost/extracted controller credentials must be individually revocable.
6. Re-pair explicitly with a new code after local recovery. Never restore the old credential, replay pending commands or reset the bridge's durable duplicate-suppression ledger.

For ESP32, the existing `controller` NVS namespace and secure-boot/flash-encryption/encrypted-NVS checks remain the physical deployment gate. A future installer must authenticate the intended board and host, stage and verify origin/trust/device authorization atomically, keep provider secrets off the controller, and handle certificate-time bootstrap and interrupted installation. This host record is not an ESP32 NVS image; no translation, plaintext export, flashing, efuse change or real secret installation is implemented here. The approved Wi-Fi/pairing screens remain labelled simulations. Display preferences remain independent.

## Fresh evidence and limits

- **93 Python tests passed**, including 13 new enrollment/admin cases: durable intent ordering; restart; lost reply with no repeat; failed writes before/after issuance; malformed reply; existing-record protection; origin/trust mismatch; revocation; read-only recovery; explicit forget; admin cancellation/listing; failed revoke persistence; invalid codes; rejected downgrade/future version.
- **`python tools/m2_provisioning_demo.py` passed** with temporary protected vaults and authenticated loopback TLS. It enrolls, reopens storage, verifies through the actual desktop helper, revokes, reopens the authorization-required state, explicitly replaces pairing and proves the old credential remains rejected. Its silent Naim adapter records **zero mutations**.
- **Native LVGL/TLS smoke and recovery fault demo passed** with the updated helper. Artwork pixel checks passed; recovery still delivers exactly one silent play and amplifier request despite lost replies.
- Native C/LVGL, ESP32 sources, approved HTML and SDK pins are unchanged. The previous four CTests and desktop/ESP32 compile results remain prior evidence; builds were not repeated for this Python-only implementation slice.

Run the Python suite and `python tools/m2_provisioning_demo.py` from repo root; the demo uses temporary synthetic state and never provisions a real device. Logs/captures remain ignored under `local/m2/`. No live Naim/provider/Pi access, real credential changes, audio, hardware write or physical acceptance occurred. HP-01 and physical P3/P4/P5 remain open.

Next offline slice: an operator-facing host enrollment flow using this library, with private code entry and explicit recovery guidance, while keeping the approved controller UI intact. Live read-only metadata/artwork validation can resume when NDX network access and private configuration are available. Physical installation and certificate rotation deployment need separate validation.

## Operator flow follow-up

The subsequent [host setup console](m2-setup.md) now wraps this library with private input and explicit recovery. Earlier next-work statements above describe the foundation checkpoint. No physical installer or native UI provisioning is implied.

## Explicit trust migration follow-up

[Same-origin trust updates](m2-trust.md) now preserve the existing credential after operator approval and verified read-only probing, with one atomic local binding replacement. This supersedes the earlier unimplemented-migration boundary for the host library only; production certificate installation and physical ESP32 migration are still open.
