# Host controller setup console - 22 September 2026

The operator-facing host flow now uses the [tested enrollment foundation](m2-provisioning.md). It performs local status, private pairing, read-only verification and explicitly confirmed local forgetting. The approved native UI and its labelled hardware setup simulations are unchanged.

## Run it

Use a private interactive terminal in the repository, with the existing installed Python dependencies. Close the desktop controller/helper first: setup uses the same exclusive protected-vault lock and never bypasses it. Obtain the intended bridge origin and trust file through an independently trusted local channel. Do not discover or accept trust from the pairing response.

Prepare or reuse the public desktop JSON used by `--bridge`. Setup requires absolute trust/state paths, accepts only `url`, `trust`, `state` and optional boolean `allow_live`, and limits the file to 16 KiB. Example placeholders below are not an installed configuration:

```json
{
  "url": "https://bridge.example:8991",
  "trust": "C:/private/ndx-controller/trust.pem",
  "state": "C:/private/ndx-controller/state"
}
```

This file contains no setup code, bearer credential or provider authorization. Setup does not generate certificates, download trust, write this configuration or enable live operation. Keep private addresses and configuration outside Git.

```text
python tools/m2_setup.py --config C:/private/ndx-controller/desktop.json status
python tools/m2_setup.py --config C:/private/ndx-controller/desktop.json pair
python tools/m2_setup.py --config C:/private/ndx-controller/desktop.json verify
python tools/m2_setup.py --config C:/private/ndx-controller/desktop.json forget
```

- **Status:** local enrollment state and controller ID only. It does not contact a bridge or require the trust file to exist. A saved pairing is not a connectivity claim.
- **Pair:** only available for an unpaired record. Displays the intended origin and trust-file SHA-256; compare these with the bridge administrator through a trusted channel. Type `PAIR`, then enter the locally issued single-use code at the hidden prompt. The code is never a command argument, echoed output or durable field. Redirected/noninteractive input is refused. If Python cannot disable echo and attempts a fallback, setup aborts. Existing, unknown or damaged enrollment is not overwritten. One pairing request is sent; verification is a separate explicit step.
- **Verify:** sends one authenticated snapshot request. Can run noninteractively; never sends play, volume, transport, library writes or voice commands. A connection failure preserves pairing; revocation records authorization-required state.
- **Forget:** shows local state and explains that forgetting does not revoke the bridge credential. Requires an interactive `FORGET`; any other answer cancels. It works without a trust file and changes only local controller/enrollment records. Revoke the identified device at the bridge first; resolve ambiguous orphan IDs locally. There is no automatic remote revoke or re-pair.

The bridge's local console provides `devices`, `pair`, `cancel` and `revoke DEVICE`. Do not put setup codes in shell commands, shared logs or screenshots. The setup console rejects unexpected arguments without echoing them and reports failures without raw exception/configuration output. Successful commands exit 0; cancellation/operational failure exits 1; invalid arguments exit 2.

If interrupted, run status before retrying. An interrupted remote pairing may already have issued a credential; the durable pending marker reports an unknown outcome. Follow the [local recovery procedure](m2-provisioning.md#recovery-procedure-and-design-boundary). Do not automatically repeat setup or erase the bridge's command history. Stop after a storage error and inspect/reopen protected storage. Trust replacement requires explicit authenticated migration planning; do not use local forgetting to bypass identity checks.

## Fresh evidence

- **107 Python tests passed**, including 14 setup-console cases for hidden input, cancellation, noninteractive rejection, existing records, unknown outcomes, sanitized failures, local forgetting/status, read-only verification, argument redaction, public-config validation and refusal of echo fallback.
- **`python tools/m2_setup_demo.py` passed** against an authenticated silent loopback TLS bridge and temporary protected vaults. Real CLI subprocesses exercise status/verify, including revoked authorization. The console's pair/forget paths use injected synthetic terminal input, enroll once, cancel forgetting, recover without a trust file and explicitly re-pair. No setup code or issued credential appeared in captured output. The silent Naim adapter recorded zero playback/volume calls.
- **`python tools/m2_provisioning_demo.py` passed** after allowing local-only enrollment inspection/recovery without trust. Durable pairing, bound helper compatibility and old-credential rejection remain tested.

The hidden-entry test uses injected input; physical terminal echo suppression remains a manual host check. No actual user credentials or private configuration were accessed. No C/LVGL/ESP32 source or approved UI change occurred; native builds, screenshots and previous broader native smoke results remain prior evidence and were not rerun for this console-only slice. No hardware installation, flashing, efuse, Pi deployment or live Naim/provider operation occurred. HP-01 and physical P3/P4/P5 remain open.

Next: validate private prompt behavior on the intended host terminal with synthetic setup first. When NDX network access returns, use separately scoped read-only metadata/artwork/reconnect validation. Production certificate renewal/rotation, installation packaging and physical ESP32 provisioning remain separate work.
