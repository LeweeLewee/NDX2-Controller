# Native embedded UI foundation and HP-01 build

Target: Waveshare ESP32-S3-Touch-LCD-4.3B, standard without case, SKU 27848, landscape 800 × 480. This is C/LVGL firmware, not a browser. Shared controller, protocol and UI code serve both ESP32 and SDL. Hardware operations are explicit callbacks; unsupported battery/sleep/capture report unknown or unavailable. Default startup and all verification use silent fixtures.

## Reviewed official example and pins

Reviewed 21 September 2026: [Waveshare 4.3B ESP-IDF guide](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B/ESP-IDF) and the [linked official archive](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B/ESP32-S3-Touch-LCD-4.3B-BOX-Demo.zip). The guide describes SDK 5.5.2 and a differently named example; the archive contains `ESP-IDF/08_lvgl_Porting` with SDK **5.2.0** in `sdkconfig.defaults`. The inspected archive compiles with official ESP-IDF tag **v5.2**, commit `11eaf41b37267ad7709c0899c284e3683d2f0b5e`, and its GCC 13.2.0 toolchain. This establishes compilation compatibility, not board compatibility.

Archive SHA-256: `57186c266f5ed5d9cd22b80b3d3d1d19d54dec2449d7ec220c8b3abc60ee0092`.

Archive component pins: LVGL **8.4.0** (`4495f428630cc1741bd8bfd977f080e8460e8e8d`); esp_lcd_touch **1.1.2** (`54e9ba5f17d0f007f5a4073240b5f6c20e099f91`); GT911 **1.1.1~1** (`30d2504a679c1cb0d10833f772d97453098b4c08`). These component directories are already in the archive. The preparation script removes floating main component requirements and retains those vendored sources and licenses. No vendor code is committed to this repository.

Review findings: 800 × 480 selected; 16-bit RGB; PSRAM and 16 MB flash defaults; I2C 8/9 in the driver; touch disabled in the delivered header; touch reset/IRQ both `-1`; backlight delegated to vendor board code. Driver files stay in the generated project, separate from `shared/`. No GPIO4 wake assumption is implemented. The archive's BOX name is not evidence that every board revision is identical. Verify against the physical standard board before enabling touch or flashing.

## Reproducible preparation and build

From repository root in PowerShell:

```powershell
New-Item -ItemType Directory -Force local/m2
Invoke-WebRequest 'https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3B/ESP32-S3-Touch-LCD-4.3B-BOX-Demo.zip' -OutFile local/m2/vendor.zip
python tools/prepare_m2_firmware.py --out local/m2/esp32-compile-v2
```

The script refuses an existing output directory or changed archive hash. For another build choose a new directory; it never overwrites a checkout. It overlays the shared C UI and ESP entry point, disables stock auto music/demo UI, and inserts wake-contact filtering before LVGL input. Touch remains off until revision review. After that review, prepare a **new** output directory with `--touch-reviewed`. This flag does not configure any wake GPIO or sleep mode.

Install official ESP-IDF **v5.2** and matching tools outside the repository. On this Windows host the SDK lives at `$env:USERPROFILE/.espressif/esp-idf-v5.2`, with its isolated Python 3.11 environment at `.espressif/python_env/idf5.2_py3.11_env`. Installation for a new host (use a base Python 3.11 interpreter, not an activated virtual environment):

```powershell
git clone --branch v5.2 --depth 1 --recurse-submodules --shallow-submodules https://github.com/espressif/esp-idf.git "$env:USERPROFILE/.espressif/esp-idf-v5.2"
py -3.11 "$env:USERPROFILE/.espressif/esp-idf-v5.2/tools/idf_tools.py" install --targets esp32s3
py -3.11 "$env:USERPROFILE/.espressif/esp-idf-v5.2/tools/idf_tools.py" install-python-env
python tools/build_m2.py esp32
```

The runner refreshes only owned overlay sources in the generated directory, validates its archive marker, and disables unused vendor demos. Build output uses `$env:USERPROFILE/.espressif/ndx2-m2-build` to avoid Windows dependency-file path limits; source remains in this checkout. The fixture binary compiled successfully (approximately 516 KiB, fitting its 1 MiB application partition). No flash or efuse operation ran. Save configuration/build manifests privately. HP-01 remains open; flashing requires the actual board and revision review.

## Shared SDL desktop build

The verified Windows runner pins CMake 3.28.3, Ninja 1.11.1.1, Zig 0.13.0 and SDL 2.30.12. From repository root, after preparation and SDK installation:

The downloaded SDL development archive SHA-256 is `dddafbf0705a8cbe1f97c69680886ce147ed4d38f1d04e03523681298e081b0f`. Verify a fresh download before extraction. These instructions reproduce the dependency versions and build process; generated binary timestamps and local paths can affect binary hashes.

```powershell
python -m pip install --target local/m2/build-tools cmake==3.28.3 ninja==1.11.1.1 ziglang==0.13.0
Invoke-WebRequest 'https://github.com/libsdl-org/SDL/releases/download/release-2.30.12/SDL2-devel-2.30.12-mingw.tar.gz' -OutFile local/m2/SDL2-devel.tar.gz
tar -xzf local/m2/SDL2-devel.tar.gz -C local/m2
python tools/build_m2.py desktop
python tools/m2_native_demo.py
```

Both native CTests pass. Run `local/m2/desktop-verified/ndx_fixture.exe` for the standalone fixture. `m2_native_demo.py` uses that compiled UI, SDL pointer events, synthetic pairing and real localhost TLS; it asserts one silent native-play request and refreshed state, then records thirteen framebuffer BMPs in ignored `local/m2/native-captures`. The SDL transport worker launches `m2_pipe.py`; credentials remain in the protected Python vault and never cross the pipe. A public config supplies `url`, `trust` and `state` paths; live connections require an explicit `allow_live` setting. Tests never enable it. This Windows transport is not a portable desktop release. See [M2 runbook](../docs/m2-software.md).

## Diagnostic and physical boundaries

ESP32 emits `HP01` timestamped fixture event names plus free/minimum heap. Hooks include boot, native-resolution simulation, bounded amplifier simulation, capture cancel, backlight-unbound and sleep-blocked. Add revision-specific timing/PSRAM/power markers as the board port becomes available; no token, address or user query is logged. Record serial/debug overhead and repeat power measurements detached. Physical HP-01 still needs backlight-off and verified light/deep-sleep implementations; unsupported callbacks deliberately fail rather than pretending to measure sleep.

`esp32/bridge_transport.c` implements the same v1 codec using `esp_http_client` on a FreeRTOS worker, with provisioned CA trust, hostname verification, redirect rejection, bounded 32 KiB responses, deadlines and no mutation retry. Replies from obsolete connection generations are discarded. Startup requires encrypted NVS plus runtime secure boot and flash encryption; default builds fail closed to the labelled fixture. Protected NVS namespace `controller` expects `url` (ending `/v1/request`), `credential`, `trust` (PEM), `ntp`, `ssid` and `password`. This is a provisioning interface, not a completed production provisioning tool. Do not enable irreversible security settings or provision real credentials from this recipe. The SDK compiles the worker, but default fixture builds may link out its gated network path. On-device Wi-Fi/TLS, certificate-time bootstrap, revocation, protected provisioning and power-loss behaviour remain untested. Provider credentials remain on the bridge. See [hardware-arrival checklist](../docs/m2-software.md#hardware-arrival-checklist).


## Approved native UI port — 22 September 2026

The shared renderer now implements the D020 core layout and interaction slices; see [parity/evidence](../docs/m2-ui-parity.md). Native smoke includes immediate-record voice entry, restart, explicit search, cancel, an accelerated 30-second stop without submission, independent artist-follow/track-save and consumed wake contact. `06-voice-search.bmp` supersedes the historical review-step capture; thirteen captures now document the flow. Font sizes 16/20/24/32 are explicitly enabled by the owned build overlay, retaining LVGL 8.4.0 and ESP-IDF v5.2. No new SDK/dependency download or board operation is needed.

## Authenticated artwork preview - 22 September 2026

Shared LVGL/codec accept fixed 80 x 80 RGB565 artwork previews over the authenticated bridge. No firmware image-decoder dependency or SDK pin changed. Three CTests cover controller state, strict protocol bounds and native UI cancellation/artwork failures. Desktop TLS smoke checks artwork pixels before/after a silent track change. Latest ESP32 build: `0x92c00`, 43% free; compiler evidence only. Standalone firmware fixtures have no artwork pixels yet.

The host bridge uses already-installed Pillow 12.2.0 for bounded JPEG normalization and local fixtures. Host dependencies are pinned in `tools/requirements-m2.txt` (also cryptography 46.0.7 for certificates). On a fresh host install that file with the chosen Python environment; no download was needed for this checkpoint. See [bounds and evidence](../docs/m2-artwork.md).

## Persistent local preferences - 22 September 2026

Palette/brightness intent/timeout use the shared bounded preference record and local platform storage callbacks. Windows uses SDL's per-user `NDX2/Controller` directory, or `--preferences PATH` with an existing parent. The ESP32 NVS adapter uses `display_prefs/record`, never erases on storage error and does not change credential protection gates. No hardware brightness/sleep effect is implemented.

Run `python tools/m2_preferences_demo.py` after the desktop build for isolated two-process restart evidence and native captures. All smoke tools supply temporary preference paths, preserving normal user preferences. Four CTests now include atomic storage/recovery and native save behavior. ESP32 storage remains compiled-only; physical latency/power-loss/endurance are open. See [preferences runbook](../docs/m2-preferences.md).
