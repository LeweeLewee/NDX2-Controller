# Portable desktop package

This Windows x64 package includes the validated native desktop controller, SDL2 and an isolated Python 3.14.3 runtime for TLS and setup. No system Python installation or bridge/provider dependencies are needed by the packaged client. It is a development-host portable build, not a signed installer or physical-controller release.

Extract the entire ZIP into a new empty directory. Keep configuration, trust, pairing and preferences outside that directory. Upgrade by extracting a new version alongside the old version and pointing it at the same external files; do not merge versions or delete user state. Windows DPAPI pairing remains tied to the same Windows user/machine. Moving the package does not migrate credentials to another computer.

From a terminal in the extracted directory:

```text
Launch.cmd --check
Fixture.cmd
Setup.cmd --config C:/private/ndx-controller/desktop.json status
Setup.cmd --config C:/private/ndx-controller/desktop.json pair
Launch.cmd --config C:/private/ndx-controller/desktop.json
```

Configuration uses the existing public JSON fields `url`, absolute `trust` and `state` paths, and optional `allow_live`. Setup code entry remains hidden and interactive. Follow the included `docs/m2-setup.md` and `docs/m2-trust.md` instructions. Close the controller before running setup; the protected pairing vault has one owner. No configuration or credential is bundled, generated or installed automatically. No bridge service is included.

`Launch.cmd --config ... --check` checks package hashes, pairing and one read-only snapshot without opening the UI. Normal launch explains transient bridge failure and opens the existing reconnecting UI; it never repeats playback commands or silently re-pairs. Missing/revoked pairing or changed trust needs explicit setup. `--fixture` runs the silent standalone UI. Pairing in package mode requires the new bound enrollment format; explicitly migrate legacy records through setup first.

Preferences use the existing per-user SDL directory by default; `--preferences` selects an existing external directory/file path. Pairing and trust must also remain outside the package. Launch and packaged setup enforce this boundary. Copying/upgrading application files never overwrites those records. The approved layout and playback/volume semantics are unchanged.

`manifest.json` records file SHA-256 values, runtime version, source checkpoint and whether the source tree had edits when assembled. Hash checks detect missing/damaged files; the manifest is not a signature or proof of publisher identity. Obtain the archive through a trusted channel. Notices are under `licenses/` and `runtime/LICENSE.txt`.

Build from the existing validated desktop output using `python tools/package_m2.py --out local/m2/packages/CHOOSE-A-NEW-NAME`. It refuses existing destinations, copies an explicit client allowlist and installed standard runtime, excludes site-packages/caches/development environments, and creates a ZIP with fixed entry timestamps. It downloads nothing. Python 3.14.3, SDL2 2.30.12, LVGL 8.4.0 and the existing native build are reused. No compiler, provider authorization, Naim address, certificates, pairing store or capture is bundled.

## Validation and limits - 22 September 2026

126 Python tests passed, including eight package/launcher cases. `python tools/m2_package_demo.py PATH-TO-ZIP` passed after extraction into two clean directories with spaces in their names. The bundled interpreter ignored deliberately invalid host PYTHONHOME/PYTHONPATH and had no site-packages path. Packaged setup/status and paired snapshot checks passed. The actual extracted native UI rendered authenticated artwork; its explicit smoke action sent one silent play. The second installation restored preferences, and external pairing/preferences stayed byte-identical. No extra playback or volume request was sent during the upgrade rehearsal. Both installations used the same archive; this establishes the replaceable-folder/state boundary, not compatibility with hypothetical future record formats.

The verified trial ZIP was about 14 MB. The package is assembled from an explicit file list and the installed Python standard runtime. Manifest hashes include all runtime/app files. Application data and certificates are excluded. Native C/ESP32 sources and the approved UI are unchanged; the prior validated desktop executable is reused, with no fresh compilation claim. Build outputs, archives and captures remain ignored under `local/m2/`. No live Naim/provider, physical hardware, Pi or user-credential operation occurred. HP-01 and physical P3/P4/P5 remain open.

This is Windows x64 development-host evidence on the current machine, not a clean-OS or cross-user deployment certification. A second machine/Windows version, signing/release optimization, runtime servicing and physical terminal hidden-entry check remain follow-ups. The desktop artifact does not install a bridge, schedule certificate renewal, migrate DPAPI credentials across machines or provision ESP32 hardware. License text and third-party notices accompany the runtime; publisher authenticity still requires a trusted distribution channel.

## Play/Pause correction

The first user trial found a silent-fixture state bug: Pause commands did not change the reported playing state. The corrected package includes a fixture fix, verified with actual native Pause -> Play -> Pause icon captures in standalone and TLS modes. The UI still follows observed state. This package remains a functional development build; a focused finish against the approved design is pending. Run `python tools/m2_transport_demo.py --package EXTRACTED-DIRECTORY` from the development repository for the silent regression.
