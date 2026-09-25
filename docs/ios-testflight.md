# Still Water internal TestFlight preview

**Signing setup complete — 25 September 2026:** the approved distribution certificate, matching App Store profile and Developer-role upload key are prepared; all six signing inputs are encrypted in the private GitHub `apple-testflight` environment. The profile signature, exact app/team identity, certificate match and encrypted key storage were verified. No signed upload or phone installation is claimed yet. Private identifiers and recovery history remain in ignored `local/ios/apple-setup-status.md`.

25 September 2026. This guide prepares a private **silent design preview** for installation on the selected iPhone. The explicit App ID `com.ndx2.controller` and an iOS App Store Connect record named **NDX2 Controller** are now registered. The account-record name **Still Water** was unavailable; the on-phone display name remains **Still Water**. Team/account details stay under ignored `local/ios/`. Signing materials and the first upload remain pending. The user confirms this app will not be sold; leave banking information unchanged.

## What will be installed

A release build starts directly in the in-process fixture without launch arguments. `STILL_WATER_MODE=STILL_WATER_PREVIEW` enables a compile-time restriction: the preview refuses HTTP transport, Keychain enrollment/read/write/forget, real speech capture and background reporting. Pairing actions are disabled. The existing SILENT DEMO label remains visible. Navigation, synthetic transport, search, artwork, keyboard, palette/brightness and idle behavior can be explored on the actual phone. Voice remains synthetic; real speech and live bridge integration require a later build and trial. No firmware, bridge route or NDX behavior changes.

The app icon is an original temporary sage/water-ripple test icon, not an accepted final brand decision. The privacy manifest declares app-owned UserDefaults (`CA92.1`) and uptime-based internal timers (`35F9.1`), with no tracking or collected data in this preview. Reassess privacy disclosures before a live integration build. [Apple required-reason guidance](https://developer.apple.com/documentation/technotes/tn3183-adding-required-reason-api-entries-to-your-privacy-manifest) and [reason definitions](https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitypereasons).

## Build and upload boundaries

The simulator workflow now uses **Xcode 26.3 / iOS 26.2 SDK** on `macos-15`, retains the iPhone 11 / iOS 18 runtime test destination, and checks an unsigned Release archive for a generic physical iOS device. Building with a newer SDK does not raise the app's minimum supported iOS version from 17. [Apple requires Xcode 26 or later for current uploads](https://developer.apple.com/news/upcoming-requirements/?id=04282026a); [GitHub's runner inventory](https://github.com/actions/runner-images/blob/main/images/macos/macos-15-arm64-Readme.md) lists the selected toolchain.

`.github/workflows/ios-testflight.yml` first runs the same tests/archive checks, then signs and uploads with manual distribution signing. Its export is `app-store-connect`, `destination=upload`, **testFlightInternalTestingOnly=true**. It cannot export a public-store/external-beta candidate through this configuration. Apple processing and internal tester assignment remain separate and must be verified after upload. TestFlight builds expire after 90 days; see [Apple's internal testing guide](https://developer.apple.com/help/app-store-connect/test-a-beta-version/add-internal-testers).

The upload workflow runs only by manual dispatch or an explicitly pushed `ios-preview-*` tag; normal source pushes run unsigned validation only. GitHub's manual-dispatch UI becomes available once the workflow is on the default branch. A reviewed tag can run the workflow while it is only on the build branch. Do not create a release tag before the account setup is ready. The upload waits for validation and uses the `apple-testflight` GitHub environment, now configured to allow only branch `codex/still-water-cloud-build` and tags `ios-preview-*`. Its two app-identity variables are populated and verified; signing secrets remain pending. No pull-request event can access signing inputs. Runtime is bounded to 25 minutes per job, uploads are serialized, and an active upload is not cancelled by a newer run.

The build counter is `<workflow run number>.<attempt>.0`, allowing distinct reruns. It stops at run 9999/attempt 99 instead of silently reusing a number. An existing app with a higher build number needs an explicit version policy update first.

## Apple account setup

1. **Complete:** verify the **Team ID** and register explicit App ID `com.ndx2.controller`. This is now the source/build default; test bundles have distinct suffixes. Keep the team identifier in private configuration, not source.
2. **Complete:** create the **NDX2 Controller** iOS app record using that exact bundle ID, an unused internal SKU, English (U.K.) and Limited Access. No additional users were selected. The user resolved Apple's agreement-update blocker. This record does not publish the app. [Apple app-record instructions](https://developer.apple.com/help/app-store-connect/create-an-app-record/add-a-new-app/).
3. Reuse a suitable **Apple Distribution** certificate and its password-protected `.p12` if the team already holds one. Otherwise create a new certificate from a CSR, then download an **App Store Connect distribution profile** for the exact App ID and certificate. Development, ad-hoc, enterprise, expired, wildcard and mismatched profiles are refused by the helper. No phone UDID is needed for this TestFlight route. Existing signing certificates are never automatically revoked. The current gate also expects the App ID prefix to equal the Team ID; a legacy transferred/prefix exception needs explicit review rather than bypassing the check.
4. Under App Store Connect → Users and Access → Integrations, create a **team API key with the Developer role** for build uploads, or use an appropriate existing key. The Account Holder may need to request API access first. Record Key ID and Issuer ID and download the `.p8` once. This key is used to upload; it does not replace the signing certificate/profile. Team keys cover the team's apps, even at the Developer role, so keep this dedicated to CI and revoke it when retired. [Apple API-key guidance](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-api).
5. Create a private internal TestFlight group containing only the intended tester. Leave automatic distribution off for the initial build; add the processed build deliberately after reviewing its identity. Tester invitations send email, so select/invite only the intended account.

## Creating signing material on Windows when no P12 exists

A Mac is not required to make a CSR. This development computer has Git for Windows OpenSSL at `C:/Program Files/Git/usr/bin/openssl.exe`. The commands below create a **password-encrypted** private key and ask for passwords interactively. Keep the password in your password manager. Run from the repository root; `local/` is ignored. Do not paste keys/passwords into chat or put them in source.

```powershell
New-Item -ItemType Directory -Force local/ios/signing | Out-Null
$appleOpenSSL = 'C:/Program Files/Git/usr/bin/openssl.exe'
& $appleOpenSSL genpkey -algorithm RSA -aes-256-cbc -pkeyopt rsa_keygen_bits:2048 -out local/ios/signing/distribution-key.pem
& $appleOpenSSL req -new -key local/ios/signing/distribution-key.pem -out local/ios/signing/distribution.csr -subj '/CN=Still Water CI/'
```

Upload **only `distribution.csr`** when creating the Apple Distribution certificate. Download the issued certificate as `local/ios/signing/distribution.cer`, then package it with its matching key:

```powershell
& $appleOpenSSL x509 -inform DER -in local/ios/signing/distribution.cer -out local/ios/signing/distribution.pem
& $appleOpenSSL pkcs12 -export -inkey local/ios/signing/distribution-key.pem -in local/ios/signing/distribution.pem -name 'Apple Distribution' -out local/ios/signing/distribution.p12
```

Choose a nonempty export password; this becomes `APPLE_CERTIFICATE_PASSWORD`. Creating a new certificate uses a team certificate slot, so reuse suitable existing material where available. No certificate has been generated by this document.

## GitHub environment settings

In repository Settings → Environments, create/select **apple-testflight**. Store identifiers as environment variables and signing inputs as environment secrets. [GitHub's signing guidance](https://docs.github.com/en/actions/how-tos/deploy/deploy-to-third-party-platforms/sign-xcode-applications) describes certificate/profile handling on Mac runners.

| Type | Name | Value |
| --- | --- | --- |
| Variable | `APPLE_TEAM_ID` | Ten-character Apple team identifier |
| Variable | `APPLE_BUNDLE_ID` | Exact registered app bundle ID |
| Secret | `APPLE_CERTIFICATE_P12_BASE64` | Base64 of the matching distribution P12 |
| Secret | `APPLE_CERTIFICATE_PASSWORD` | P12 export password |
| Secret | `APPLE_PROFILE_BASE64` | Base64 of the matching App Store Connect `.mobileprovision` |
| Secret | `ASC_KEY_ID` | Upload API key identifier |
| Secret | `ASC_ISSUER_ID` | Team API issuer UUID |
| Secret | `ASC_PRIVATE_KEY` | Complete downloaded `.p8` text including BEGIN/END lines |

For a binary file, copy its Base64 directly to the clipboard without printing it:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes((Resolve-Path 'local/ios/signing/distribution.p12'))) | Set-Clipboard
```

Paste into the matching GitHub secret, then clear the clipboard. Repeat for the profile. Paste the `.p8` directly into its secret; do not Base64 that field. The upload helper writes inputs with owner-only permissions to a temporary runner folder, uses a random temporary keychain password, imports only for code-signing tools, and restores the prior keychain list and removes its profile/keychain on exit. It never uploads signing files, archives containing profiles or distribution logs as artifacts. GitHub also destroys hosted runners after the job. Provisioning setup is explicit; the workflow does not create/revoke Apple certificates or profiles. The export permits Xcode to download updates for the supplied manual profile while authenticating the upload; it does not switch to automatic signing.

## First device trial

After Apple finishes processing, verify bundle ID, version/build and internal-only status in App Store Connect, add the build to the intended internal group, then install through TestFlight on the iPhone. Keep the original prototype and gallery. Check first-touch behavior, the inlay/window edges, keyboard reach, scrolling, state feedback, idle/lock return and brightness. Capture feedback by screen. Do not treat this as live speech, bridge security, battery-life, mounted acoustic or heat proof.

## Validation checkpoint

[Run 36134704504](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36134704504) passed at `768ebece4120dae58ae8ad783f5b4bce60f18608`: **19 native tests**, 23 state captures plus three UI captures, and the unsigned physical-device Release archive. Xcode 26.3 (17C529), iOS 26.2 SDK, iPhone 11 simulator running iOS 18.6. This does not claim an iOS 26 runtime test. Archive version `0.1.0` / `7.1.0` retains minimum iOS 17, compiled preview mode, AppIcon and the privacy manifest. Its binary SHA-256 is `64962d5c21f9735c9f6768dcf148d9fca764241056c9740adebfc8731033c855`. It is unsigned and cannot be installed.

Artifact `still-water-ios-7` (ID `10864715051`) SHA-256: `7e207c37978a7b0bd98fa81ab10f99fc2ea8eb6ca18c8c53ca624f76ef8a7efd`; GitHub expiry 2 October 2026. Local gallery: `local/ios/review-testflight/review.html`; archive metadata is beside it in `archive-check.json`. Original PNG bytes are preserved. All changed native captures (Pairing, queue and after-search) were inspected; all others match the previously inspected pixels. Pairing shows the disabled preview actions; system home-indicator/keyboard limitations remain.

146 Python tests, five navigation tests, six silent TLS demo stages and generator/vector checks passed. Five new offline distribution tests reject wrong-team/bundle, expired, development, ad-hoc, enterprise and wildcard profiles, and verify internal-only export, rerun build numbering and exact signing-password preservation. Signed archive/export, Apple processing and phone installation remain **unexecuted** until account configuration is supplied. The final helper-only authenticated-export option change and gallery ZIP-layout fix do not alter the tested app or archive path; their local checks passed. A real upload reruns native validation first.

## Registered identity revalidation - 25 September 2026

[Run 36152860230](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36152860230) passed all **19 native tests**, none skipped, and the unsigned iPhone archive at `ba2d18f95778d1856ab052b4aa3d394c68ff4825`. Archive metadata confirms bundle ID `com.ndx2.controller`, version `0.1.0` / build `8.1.0`, compiled preview mode and minimum iOS 17. Xcode 26.3 / iOS 26.2 SDK; simulator execution remains iPhone 11 / iOS 18.6. Binary SHA-256: `44d26506336bf23999d5904f4d87d67ba5ab56358474e1e523ad98b763449f84`. Signed false, uploaded false.

Artifact `still-water-ios-8` (ID `10872223340`) SHA-256: `a4e3edcb195e47fc11d3330c0cfc8953abe262b013e53914a1a009f4fb92a64f`; expiry 2 October 2026. The ZIP is retained under `local/ios/` and its exact summary/archive/environment JSON under `local/ios/registered-identity-validation/`. Nine relevant offline project/distribution tests and the generator check passed. This identifier-only app change does not replace the existing gallery review or close any physical/user acceptance gate. Signing material is the remaining account setup dependency.
