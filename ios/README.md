# Still Water iPhone client

Brief B source checkpoint, 25 September 2026. **Not built, signed or run on iOS yet.** The implementation host is Windows and has neither Xcode nor Swift. D030 remains the hardware decision; D031 records this task's implementation choices. See the [implementation and review report](../docs/ios-still-water.md).

## Build and review on a Mac

Open `ios/StillWater.xcodeproj`. The shared scheme is **StillWater**. The project has an application target, unit/snapshot tests and UI tests; there are no Swift package dependencies. It targets iPhone on iOS 17 or later. Install a compatible iPhone 11 simulator runtime in Xcode.

From the repository root:

```sh
python tools/m2_ios_fixtures.py --check
python tools/generate_ios_project.py --check
xcodebuild test -project ios/StillWater.xcodeproj -scheme StillWater \
  -destination 'platform=iOS Simulator,name=iPhone 11' \
  -resultBundlePath ios/build/StillWater.xcresult
```

The explicit `-project` is needed from the repository root; inside `ios/`, the brief's shorter `xcodebuild test -scheme StillWater ...` command works. Use a new result-bundle path for a subsequent run. Select a signing team in Xcode for the physical phone; no team identifier, provisioning profile or signing secret is checked in. Simulator tests do not require device signing.

The shared test action sets `STILL_WATER_FIXTURE=1` for the application host, so saved pairing cannot start a live bridge client during unit/snapshot tests. Fixture launches do not register the background reporting task; the UI tests also launch explicitly with `--fixture`.

Add **`--fixture`** to the scheme's Run arguments for the first visual trial. This uses bundled synthetic responses in process: no server, LAN, pairing, microphone capture or NDX is needed. `--fixture --review-state touched` opens a deterministic review composition; other state names are listed in `StillWater/Core/ReviewStates.swift`. Remove `--review-state` to exercise the real timers and navigation in the silent fixture. Review mode freezes timers, so it is not a wake or power measurement.

Open the `.xcresult` in Xcode to inspect retained screenshots. Native captures target **1510 × 692 pixels**. Compare each with the corresponding reference in `docs/still-water/reference/`, applying the 1048-unit canvas anchoring rule rather than stretching the old 800-unit image. The UI test captures the actual system keyboard separately. No native capture has been produced or approved on Windows.

## Pair a real display later

Use the existing provisioned HTTPS bridge and its one-use pairing workflow. On the phone, reveal controls, hold the artist line for 700 ms, then choose **Connection → Pairing**. Import the independently supplied PEM/DER trust certificate, verify its displayed SHA-256 fingerprint through a trusted independent channel, enter the origin and one-use code, and approve that specific pairing. Trust is never learned from the first network response. Keep private certificates/configuration out of committed fixtures.

Enrollment is recorded as pending in Keychain **before** sending the code. A lost response cannot automatically redeem it again. Resolve uncertain enrollment and revoke any orphan using the existing bridge administration procedure before explicitly forgetting the local record. Forgetting locally does not revoke the bridge credential. Replacing trust keeps the origin and credential; it only installs the candidate trust after an authenticated, fresh snapshot succeeds. A failed probe retains the old binding.

The application uses only existing `/v1/pair` and authenticated `/v1/request`. It has no direct NDX address, provider credential, artwork URL route or embedded web server. The private-artifact/throwaway-static-server rule for web trials is unchanged.

## Device configuration and limits

- Fixed landscape-right interface, status bar hidden, home indicator requested hidden, 755 × 346 pt centered window with black outside. Physical notch/inlay alignment still needs checking. OS alerts, keyboard, document picker and lock screen remain system UI.
- Start brightness is 35%; Display saves palette, brightness and idle-hold timeout locally. Actual lock is owned by iOS Auto-Lock. Set and test Auto-Lock on the device; the app does not force-lock the phone or simulate screen-off with a black view.
- Enable microphone and Speech permissions for Ask. Recognition requires the selected locale to support on-device recognition; otherwise use typing. No server speech fallback or audio upload is implemented.
- Keep the phone connected to the selected UGREEN bank for phase 1 and enable Optimised Battery Charging in iOS. There is no app-controlled charge switch and no promised 75% cutoff. The built-in cable/phone connection must be verified against the actual bank.
- Foreground battery reports are attempted on activation and every 15 minutes while active. An external-power/network-required background processing task makes one fresh report when iOS grants execution. Its earliest start is not a deadline or a 15-minute guarantee. Protected enrollment is available after the first unlock following a reboot; no secrets are moved to less protected storage to bypass that requirement.

## Repository checks and generated files

```sh
python -m unittest discover -s tests -v
node --test tests/test_navigation.cjs
python tools/m2_demo.py
```

`tools/m2_ios_fixtures.py` generates public synthetic vectors through the actual Python contract. `tools/generate_ios_project.py` regenerates the project, shared scheme and Info.plist from the source files. Both accept `--check`. Run the generators after changing their inputs. Font source revisions, hashes and the two OFL notices are bundled in `StillWater/Resources/Fonts/`. Local builds, results and signing artifacts are ignored.
