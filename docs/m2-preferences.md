# M2 local display preferences - 22 September 2026

Continued from clean `ece0fa3` while the development host is away from the NDX network. Palette, brightness intent and screen-off timeout now persist locally across desktop app restarts. The approved layout and network/playback contract are unchanged. This work uses silent fixtures only.

## Behavior and storage

The shared model accepts palette Sage/Sand/Slate, brightness 30-100 percent and timeout 1/2/5 minutes or Never. Defaults remain Sage, 80 percent and two minutes. Palette changes appearance immediately. Brightness and timeout remain saved intent: no backlight or sleep operation is implemented or invoked.

Edits coalesce for 750 ms after the last change, and save only after contact release. Desktop orderly shutdown flushes a pending edit. Abrupt termination before a successful save can lose the latest edit. The UI distinguishes defaults, pending, saved, storage unavailable and failed saves. A transient save failure leaves the current session value usable and the old durable file intact; there is no retry loop. Changing a setting retries a transient failure. An unreadable/corrupt/newer record leaves session-only defaults and is not overwritten; repair/storage recovery requires a restart. No migration or reset control is added.

The versioned 12-byte record has a magic, version, bounded values and CRC32. It contains no address, token, account information, command, queue or browsing history. CRC is corruption detection, not an authentication or encryption mechanism.

Windows desktop uses the SDL per-user preference directory (`NDX2/Controller/preferences.bin`). `--preferences PATH` selects an explicit UTF-8 path with an existing parent. A per-file OS lock prevents simultaneous writers. Saves create a new same-directory temporary file, write and flush it, then replace the destination using write-through. Failed replacement preserves the previous file. Unexpected leftover temporary files are never truncated. Invalid and future records fail closed to session defaults. Test programs pass isolated temporary paths and do not alter the user's ordinary preferences.

The ESP32 backend uses one NVS blob at `display_prefs/record`, separate from the protected `controller` credential namespace. It validates the same record, saves using NVS set/commit and never erases a partition to recover from an error. Preferences contain no secrets and can use fixture NVS; existing secure-boot/flash-encryption/encrypted-NVS gates for real network credentials are unchanged. This adapter is compiled only; no board or power-cut test occurred. UI save callbacks are synchronous small writes; device flash latency/endurance and power-loss behavior still need measurement.

## Validation and reproduction

Run from repository root with the installed pinned tools:

```powershell
python tools/build_m2.py desktop
python tools/m2_preferences_demo.py
python tools/m2_native_demo.py
python tools/build_m2.py esp32
python -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
python tools/m2_demo.py
```

Four CTests cover existing controller/protocol/recovery behavior plus preference round-trip, bounds/checksum, malformed records, failed replacement retaining the old value, leftover-file refusal and writer locking. Native LVGL event tests cover startup values, coalescing, held contact, save failure, retry, unavailable storage and orderly flush without bridge requests.

The preferences smoke opens two separate native LVGL processes. The first selects Sand and sets brightness 65/timeout five minutes; the second checks restoration. Native pointer events exercise Settings navigation/palette and actual LVGL value-change events exercise the slider/dropdown. The saved record and restored palette pixels are asserted. Actual 800 x 480 captures `14-preferences-saved` and `15-preferences-restored` are in ignored `local/m2/native-captures/`; the restored screen was visually inspected for legibility and honest hardware labels.

Fresh results: 77 Python tests, five JavaScript tests, four CTests, five-stage TLS demo, native LVGL/TLS artwork/playback smoke, preferences restart smoke and both builds passed. ESP32 image: `0x97090` bytes, 41% application partition free. One initial Python run hit Windows error 10053 in the unchanged TLS authentication test; the rerun passed without changing it. A restricted preferences run could not access its temporary directory; normal user execution passed. No ACL/TLS checks were weakened.

## Remaining gates

Live metadata/artwork validation, final artwork quality and deployment-host resource profiling remain open. Production provisioning/admin, physical brightness/sleep/wake/touch, microphone and NVS power-loss/endurance acceptance remain open. No Naim/network discovery, audible/live command, flashing, efuse operation, Pi installation or real credential provisioning occurred. HP-01 and physical P3/P4/P5 remain open. The hardware-arrival checklist, D011 and native Naim playback/no-replay requirements are unchanged.
