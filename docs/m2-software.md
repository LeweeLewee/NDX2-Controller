# M2 parallel software workstream

21 September 2026. Implemented in `local/river-stone-repo` while hardware procurement and validation are delayed. The starting checkout was clean at `fcf1406`; no files from `river-stone-shell-repo` were substituted. `software-feasibility-v1` remains at `aa070fc`. D015/D016/D017/D018 were reconciled by the existing provenance records before adding D019.

## Implemented boundary

`tools/controller_service.py` extracts the prototype Bridge and native-item normalization verbatim. `prototype_ui.py` imports it, preserving the existing loopback demo and its tests. Native candidate resolution, matching Naim object/class checks, collection fresh-read/write-once/read-back, bounded artwork cache, and the Naim adapter remain the behavioural reference. D011 still calls the existing `NaimClient.amplifier_nudge`: one press plus four held frames, each spaced 0.2 seconds, once per tap. No numeric amplifier level or automatic retry was added.

`m2_bridge.py` adds the versioned authenticated contract and a silent fixture adapter. `m2_security.py` implements durable device authorization, pairing/revocation, a write-ahead command journal and serialized durable refresh rotation. `m2_library.py` integrates persistence with the existing PKCE and collection adapter. `configured_service()` wires protected provider configuration to these adapters; `--live` is explicit and has not been exercised in this workstream. Default startup cannot contact an NDX or provider.

`m2_client.py` implements controller navigation, freshness, wake suppression, reconnect and voice state. `m2_desktop.py` is an 800 × 480 native Tk contract harness. `firmware/shared/` supplies the bounded C controller model, protocol codec and LVGL renderer shared by SDL desktop and ESP32 entry points. Both targets now compile. The SDL worker uses an authenticated TLS Python transport; the ESP32 worker uses `esp_http_client` with provisioned trust. Generation checks discard obsolete replies, mutations never retry, and UI polling stays off the network worker. Hardware interfaces separate display, touch, sleep, battery and microphone. The default firmware remains a silent fixture: its network path requires encrypted NVS, flash encryption, secure boot and local provisioning, which remain physical deployment gates.

## Exact desktop commands

Run from this repository root with Python 3.10+ (the preparation helper uses `Path.is_relative_to`) and Node. The bridge itself uses the standard library; generating synthetic certificates needs `cryptography==46.0.7`, available on the tested development host. Tk is required only for the visual harness.

```powershell
python -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
python tools/m2_demo.py
```

The demo creates temporary synthetic credentials and a seven-day localhost certificate, starts a TLS server on an ephemeral loopback port, pairs, runs assertions and removes its temporary state. It prints only sanitized pass lines. It makes no external network or audio requests. On Windows, owner-only temporary storage/DPAPI/ACL tests need to run outside the restricted sandbox. Do not weaken the ACL or encryption to make a sandbox test pass.

For two interactive terminals:

```powershell
python tools/m2_certificates.py --out local/m2/tls
python tools/m2_bridge.py --cert local/m2/tls/trust.pem --key local/m2/tls/key.pem
```

At the bridge's local console enter `pair`. In another terminal:

```powershell
python tools/m2_desktop.py --url https://127.0.0.1:8991 --trust local/m2/tls/trust.pem
```

Paste the code into the hidden prompt; it expires after 120 seconds and is single-use. First contact is consumed; release before using controls. Use Find → Search albums → open result → Play now. Back restores the query, filter, page and list position. Fixtures include long titles, absent artwork and saved/unsaved/unknown states. Queue is read-only. Voice Record/Stop/Cancel/Search operates on a labelled transcript fixture, never a microphone or automatic playback. `revoke DEVICE` at the bridge console invalidates that controller. The controller ID is in its protected local state; credential values must not be copied into logs. `quit` stops the bridge. Existing reference demo: `python tools/prototype_ui.py`.

Synthetic certificates refuse overwrite and are for localhost only. Regenerate into a new directory and deliberately reprovision trust when expired. Do not use certificate-validation bypasses. Default endpoints bind loopback; any explicit LAN binding remains TLS authenticated, but LAN installation still requires host identity, firewall and provisioning review.

## Storage and authorization

Windows vault contents use current-user DPAPI, with exclusive process locking, same-directory temporary files, flush/fsync and atomic replacement before an access token is published. POSIX requires an owner-only directory and files; directory replacement is fsynced. DPAPI protects vault confidentiality, not availability against another local user deleting files. Run under a dedicated bridge account in deployment. TLS keys use owner-only ACLs/permissions because Python's TLS stack requires a PEM key. No secrets belong in Git, firmware source, command-line arguments, web content or captures. State defaults beneath ignored `local/m2/`; choose a non-synced private service directory for actual deployment because this checkout's parent is OneDrive.

The device store retains only credential hashes. Setup codes stay in memory, have a five-attempt budget and are issued only through local console administration. There is no web administration endpoint and browser Origin requests are rejected. The controller stores its credential in its own protected vault. ESP32 flash encryption/secure boot/NVS provisioning are still a deployment gate; no provider secret is ever provisioned to the controller.

Refresh is single-flight within the exclusive bridge process. Omitted replacement tokens retain the previous refresh token; `invalid_grant` deletes durable authorization, while transient failure retains it and briefly backs off. Persistence errors block further renewal in that process. Restart reads the last durable state; a provider rotation followed by process/power failure before durable commit may require explicit account sign-in. Atomic local replacement cannot make the remote OAuth exchange transactional. Access tokens are memory-only. Disconnect deletes local durable refresh authorization and collection caches; provider-side revocation is separate.

Live account bootstrap still uses the existing exact registered loopback OAuth/PKCE flow. No remote OAuth callback is introduced or claimed validated. Deployment callback registration and a trusted local administration integration are pending. `PersistentLibrary.finish()` supplies the durable hook when that administration flow is connected. Provider configuration is injected into the protected vault under `provider_config` by trusted host administration; it contains `ndx_address`, `client_id`, `client_secret` and optional `country`. Do not paste real values into the repository. Existing prototype sign-in remains memory-only, intentionally preserving the frozen demo's semantics.

## Validation result — 21 September 2026

Final run: **69 Python tests passed** (52 existing + 17 M2), **5 JavaScript tests passed**, all five `m2_demo.py` scenario stages passed, Python compileall passed, and `git diff --check` found no whitespace errors. `software-feasibility-v1^{commit}` still resolves to `aa070fc0af4a616f769a7c0f15790831c90c112c`. No Git reset, checkout substitution, commit, push or audible test was performed.

## Evidence and remaining limits

- Existing Python and JavaScript tests cover the unchanged reference semantics, including the exact D011 frame sequence and fail-stop on uncertain response.
- New desktop tests exercise pairing expiry/reuse/revocation, wrong TLS trust, protected restart persistence, concurrent renewal, omitted rotation, transient/revoked authorization, replacement failure, duplicate/conflicting IDs, pre-dispatch durability, uncertain commands, stale state, pagination, navigation, wake and voice cancellation.
- `m2_demo.py` demonstrates the complete silent contract slice over real localhost TLS, not an in-process transport substitute.
- Pinned tooling is now installed. ESP-IDF v5.2/LVGL 8.4.0 firmware and the Windows SDL/LVGL executable compile; both CTests pass. `python tools/m2_native_demo.py` drives the actual compiled LVGL interface over paired localhost TLS through search, detail, Back, one silent native-play request, refreshed state and voice review/cancel. Six 800 × 480 framebuffer captures are retained in ignored `local/m2/native-captures/`; the long-title detail capture was inspected for readability. This is desktop rendering evidence, not physical touch acceptance.
- The final Python suite passed all 69 tests on rerun. One preceding run encountered Windows error 10053 in the existing cross-origin HTTP test; no application change was made to hide this intermittent host connection failure. Five JavaScript tests and the five-stage standalone TLS demo also passed.
- No live Naim/provider/Pi observations, audible tests, physical captures, screen/touch trials, wake timing, power, battery or microphone evidence were added. Hardware gates HP-01 and physical P3/P4/P5 remain open. B01 stays deferred.

## Hardware-arrival checklist

1. Record exact SKU 27848, standard without case, PCB revision and markings; photograph privately and obtain the matching schematic. Check archive/board compatibility despite the vendor package's BOX name.
2. Inventory regulated USB 5 V/data cable and measurement equipment (accuracy, sample rate, burden voltage and low-current resolution). Leave battery and DC input unused; use one supply path.
3. Reproduce the compiled fixture using the pinned tools in [firmware instructions](../firmware/README.md), and build the unmodified vendor display example for comparison. Record compiler, SDK, archive hash, configuration and firmware commit; compilation does not authorize flashing before revision review.
4. Audit RGB, GT911, expander, reset, backlight and touch IRQ wiring against the actual revision. Touch IRQ is `-1` in the inspected driver; GPIO4 is not accepted as a wake pin. Only then prepare with `--touch-reviewed`. Add a revision-specific wake implementation only after routing/polarity/power checks.
5. Run silent layout, keyboard, scrolling, long-title, absent-artwork and saved-state tasks on the actual screen. Check edges, font readability, target sizes and seated angle. Record heap/PSRAM, latency and resets; tune the provisional layout from evidence.
6. Execute every HP-01 measurement and cycle test, including 100 wakes with 10 held contacts, eight-hour standby, Wi-Fi outage/recovery and zero accidental fixture commands. Distinguish backlight-off, light sleep and deep sleep; unsupported modes are pending/failed, never zero-power observations.
7. Audit remaining pins/buses and supply before selecting a microphone. Then validate bounded capture, 30-second stop, Stop & search / Restart / Cancel, dropped samples and quiet/music-playing recognition. No physical capture is currently implemented.
8. Inventory the Home Assistant Pi privately before choosing service packaging. Provision host TLS identity/trust and device credentials; rehearse rotation/revocation/restart. Run the 24-hour coexistence trial only after host suitability is established.
9. Prepare separately announced live Naim checks: read current playback/queue, test native resolution and state reconciliation, app coexistence/outages, and D011 only under existing audible-test authorization. Never replay an uncertain mutation.
10. Use measured loads and an agreed daily-use profile for P4 battery/charging selection; measure parts before P5 fit/CAD release. Procurement, HP-01, physical P3, P4 and P5 remain open until their own evidence passes.

## UI approval follow-up — 22 September 2026

The commands and implementation evidence above describe the existing technical foundation, including its earlier voice review flow. D020 now approves [the refined UI](ui-review/approval.md); the subsequent [native port and smoke updates](m2-ui-parity.md) now implement its core slices. Immediate recording with Stop & search / Restart / Cancel supersedes the separate review step for the next implementation. [Closeout](m2-closeout.md) and [continuation prompt](continuation-prompt.md) are the current entry points.


## Shared approved UI implementation — 22 September 2026

The approved direction is now implemented as useful native C/LVGL slices: Playing layout and controls, filtered search, nested details and membership, collection/queue reads, immediate-record voice search and Settings. See the [parity inventory and actual evidence](m2-ui-parity.md) for implemented behavior and remaining integration gaps. Desktop evidence: 72 Python tests, five JavaScript tests, two CTests, five-stage TLS demo and expanded native LVGL/TLS smoke passed. No live or physical acceptance is inferred. HP-01 and physical P3/P4/P5 remain open; the hardware-arrival checklist is unchanged.


Final firmware validation, 22 September 2026: `python tools/build_m2.py esp32` **passed** with the final shared sources, pinned ESP-IDF v5.2 and LVGL 8.4.0. Application image `0x925b0` bytes fits the `0x100000` partition with 43% free. No flashing or efuse operation was run. This is compiler/linker evidence only; the default-disabled protected network path and physical behavior remain unvalidated.

## Local preference persistence - 22 September 2026

The offline continuation now saves palette, brightness intent and timeout locally. [Preference behavior and evidence](m2-preferences.md) records atomic desktop replacement, native save/error states, separate-process restart tests and the compiled ESP32 NVS backend. Hardware brightness/sleep and physical storage durability remain unvalidated. Existing playback, authentication and the ten-step hardware-arrival checklist above are unchanged.

## M2 offline recovery - 22 September 2026

Desktop startup outages, late pipe replies and helper recovery are fixed without retrying commands. Shared LVGL detects bridge restarts, rejects expired snapshots, bounds pending state, clears stale artwork/membership and preserves browsing while consuming old gestures. Silent fault injection proves one play and one volume request despite lost replies. Fresh evidence: 80 Python tests, five JavaScript tests, four CTests, TLS/native/preference/recovery demos and both builds passed (`0x971f0`, 41% free on ESP32). The screenshot harness now flushes current LVGL pixels before capture. See [recovery scope and evidence](m2-recovery.md). No live Naim or hardware operation occurred; physical gates remain open.

## M2 enrollment and revocation foundation - 22 September 2026

The [offline provisioning slice](m2-provisioning.md) adds protected enrollment intent, origin/trust-bound controller records, durable uncertain/revoked states, local ID inventory and setup-code cancellation. The desktop helper enforces new record bindings while preserving legacy fixtures. Fresh evidence: 93 Python tests, read-only TLS enrollment/revocation/re-pairing demo, native UI/artwork smoke and outage-recovery demo passed. No C/ESP32 or UI changes; prior build evidence was not rerun. Production setup UI, physical installation and HP-01/P3/P4/P5 remain open.

## Host setup console - 22 September 2026

The [operator setup flow](m2-setup.md) adds local status, hidden-code pairing, explicit read-only verification and confirmed local forgetting. It rejects piped secret input and echo fallback, retains durable unknown outcomes and supports local recovery without a trust file. Fresh evidence: 107 Python tests, setup/TLS fixture demo and enrollment regression demo passed; zero live commands or real credential changes. Native UI/firmware are unchanged. Physical terminal echo and deployment/hardware gates remain separate.

## Certificate renewal and trust recovery - 22 September 2026

The [trust lifecycle slice](m2-trust.md) proves same-CA leaf renewal retains pairing and expired/wrong-host/unexpected certificates fail. An explicit same-origin `trust-update` verifies a snapshot before atomically replacing the saved binding; status reports the saved digest for interrupted recovery. Fresh evidence: 118 Python tests plus trust/setup/provisioning TLS demos passed, with no live commands or real certificate changes. Native UI/firmware and physical gates are unchanged. Production certificate installation and ESP32 rotation remain separate.
