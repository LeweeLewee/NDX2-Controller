# M2 offline recovery checkpoint - 22 September 2026

This follows the published artwork and local-preference slices. It preserves the approved C/LVGL layout and D011/D019 command constraints. All new execution evidence is silent and local; the NDX network was unavailable.

## Delivered behavior

- The desktop helper survives individual request failures, including an unavailable bridge at startup. Fixture-only mutation checks still run before every mutation unless the existing explicit live configuration is present.
- The native desktop worker discards failed pipes and their late replies, closes its owned helper and starts a new helper for the next request. It never repeats the failed request. Resource cleanup also covers partial initialization. Credentials remain in protected storage, with verified TLS in the helper.
- Shared LVGL observes bridge boot IDs. A changed boot cancels old interaction intent, clears artwork and cached membership claims, invalidates obsolete replies and requires an authoritative snapshot. A current snapshot can itself provide that recovery state. Browsing query/filter/page/cursor/scroll/history remain intact; unknown membership is shown until explicitly read again.
- Expired snapshots cannot overwrite metadata or enable controls. An eight-second UI deadline releases stuck pending state, invalidates the request generation and starts bounded read-only recovery. Timed-out mutations remain unknown, including after a subsequent snapshot; volume completion cannot be inferred from that snapshot.
- Disconnect clears the held gesture, pending read intent, voice capture and cached saved-state claims across retained history. Controls require current authoritative state and contact release. Snapshot polling continues during recording so an outage can cancel it.
- Native screenshot capture now flushes LVGL before saving. Validation exposed a stale-frame capture immediately after a successful state update; this corrects the harness without changing the approved UI.

## Fresh validation

| Check | Actual result |
| --- | --- |
| Python suite | 80 passed, including three new helper outage/security/no-replay cases |
| JavaScript navigation | Five passed |
| Desktop build / CTest | Passed; four CTests, expanded native LVGL recovery assertions |
| `python tools/m2_recovery_demo.py` | Passed against the actual compiled desktop transport, Python helper and authenticated loopback TLS bridge |
| Existing five-stage TLS demo | Passed |
| Native LVGL/TLS smoke | Passed after fixing stale screenshot timing; artwork pixel assertions passed |
| Separate-process preference smoke | Passed; no network/audio or ordinary user preference writes |
| ESP32 build | Passed, `0x971f0` bytes, 41% application partition free; no flash |

The recovery demo starts with a non-serving bridge, delays a read by six seconds, delays both the play preflight and executed play reply by four seconds each (crossing the native 6.5-second pipe deadline), and loses the executed amplifier reply to a six-second delay. A fresh contract instance then supplies a new boot ID while retaining the same protected bridge vault. Every following snapshot succeeds. The fixture and request logs assert exactly one play and one amplifier request; no mutation is retried. The fixture server discards expected broken-client response writes only within this test.

Native LVGL tests separately exercise query/page/cursor/scroll/history retention; held-contact consumption; membership/artwork invalidation; expired snapshots; eight-second stalls for play, both volume directions, save, remove and transport; obsolete replies; new-boot mutation replies; and recording outage cancellation. These are deterministic renderer/state tests, not a claim of physical radio fault testing.

Actual 800 x 480 Playing and restored Find pixels were inspected. Find retains its query/list and shows unknown membership after recovery. Captures and logs remain ignored under `local/m2/`. Run the recovery demo after `python tools/build_m2.py desktop`; it uses temporary synthetic pairing state and never accesses a Naim device.

## Boundaries and next work

No live Naim/provider operation, audible output, provisioning, Pi installation, flashing or efuse operation occurred. TLS/ACL checks, durable duplicate-ID suppression, native Naim candidate resolution and the exact D011 burst are unchanged. The approved HTML hash and frozen feasibility tag are unchanged. HP-01 and physical P3/P4/P5 remain open; ESP32 compile success does not prove on-device recovery, timing or storage durability.

Next: live read-only metadata/artwork/reconnect validation when private configuration and NDX network access are available. While offline, a separately scoped production provisioning/revocation design and fixture slice can proceed; physical controls, production credential installation and audible checks stay separate. Higher-resolution artwork and deployment-host resource profiling remain explicit follow-ups.
