# Build Still Water from Windows

The private GitHub repository runs Xcode on a hosted Mac. A local Mac and an Apple Developer membership are not needed for the unsigned **simulator** build. This does not produce an installable iPhone `.ipa` or configure TestFlight.

## Current workflow

`Still Water iOS simulator` runs on pushes changing iOS/build files on `codex/still-water-cloud-build`. The branch preserves the newer mounting work from `main`; the original local checkout and its uncommitted documentation are separate. There is also a manual-dispatch declaration, available in the GitHub UI once this workflow is on the default branch. Until then, push a build change or use **Re-run jobs** on an existing run.

The job uses `macos-15`, Xcode 16.4 and an available iOS 18 runtime with the **iPhone 11** device type. It records the exact environment. The 25-minute timeout bounds each run, and a newer push cancels an older run on the same branch. The workflow token can only read repository contents; checkout does not retain its credential. No provider secrets, signing material, LAN address or live bridge configuration is supplied. Test-host and UI-test launches use the in-process silent fixture, including no physical microphone capture or background battery reporting.

## Results on Windows

1. Open the repository's **Actions → Still Water iOS simulator** and select the latest run for the expected commit.
2. Check the build/test result. A green job is an automated result, not physical or user acceptance.
3. Download the `still-water-ios-<run number>` artifact. The artifact is private to repository access and retained for seven days.
4. On Windows, make a review gallery directly from the downloaded ZIP: `python tools/ios_review.py "C:/path/to/still-water-ios-<run number>.zip" --output local/ios/review`. Open `local/ios/review/review.html`. It provides state selection, original reference images and full-pixel-size inspection, plus the JSON test summary/environment. It copies the original PNG bytes without alteration and requires no server. Optionally pass `--revision <full commit SHA from the run>` to record the exact tested source alongside the ZIP SHA-256. The helper requires Python 3.11 or later.
5. Keep the original ZIP. It retains `xcodebuild.log`, the attachment manifest and the complete `.xcresult` for later Xcode inspection. Direct extraction of xcresult internals can exceed Windows path limits; the gallery command avoids those internals.
6. Compare every composition with the supplied reference and the anchored tables, using [the review matrix](ios-still-water.md#native-review-matrix-and-remaining-gate). Review actual keyboard screenshots separately. A failed assertion remains a failed gate until its cause is corrected; do not substitute browser renders for native evidence.

GitHub may charge usage beyond the account's included private-repository allowance. This setup does not change account billing, enable paid plans or purchase Apple membership. The current workflow builds and tests only; signing, real-phone installation and hardware measurements remain a separate step.

## Reproduce or inspect

`tools/ios_ci.py prepare` chooses and boots the simulator and records `environment.json`. `xcodebuild test` builds with `CODE_SIGNING_ALLOWED=NO`, using the shared StillWater scheme and serial simulator testing. `tools/ios_ci.py export` exports test JSON and native attachments using Apple's `xcresulttool`, even after test failure. Generated project and fixture checks remain available on Windows:

```powershell
python tools/generate_ios_project.py --check
python tools/m2_ios_fixtures.py --check
```

No existing bridge route or firmware was changed for cloud building. Simulator captures cannot prove physical readability, microphones, lock/wake, charging, heat or battery life.

## Design review sequence

Start with Still, Touched, long titles and no artwork, then compare queue, Find, keyboard, Detail and Library. Finish with speech, offline/pending/unknown states and settings. Record feedback by state and concrete element (for example, `queue: track labels feel too small at seated distance`). The screenshot gallery supports detailed visual comparison; it is not an interactive native app or an iPhone installation. The existing HTML design reference remains available for its own interaction trial, but is not evidence of native behavior. A signed phone build is a separate next step for real touch, mounted keyboard access, speech, lock/wake and power testing.
