# Primary hardware: iPhone 11 with Ugreen battery pack

25 September 2026. D030 is the controlling hardware decision. The Waveshare implementation is retained as a fallback; the software-feasibility tag and subsequent M2/Still Water bridge work are preserved.

## Selected direction and evidence

| Item | Current record | Still to establish |
| --- | --- | --- |
| Display/touch | iPhone 11 selected by user for a significantly nicer screen | Actual device/iOS configuration, usable viewport, wake/unlock and seated interaction |
| Voice | Use phone's built-in microphone | Permission/capture flow, review/cancel, and speech quality from the table with music playing |
| Power | UGREEN Nexode 20000mAh PD 20W QC Power Bank Built-in Cable, identified by user; user judges standby sufficient | Exact SKU, labelled Wh/ports, built-in cable connector, cable arrangement, inventory, recharge behavior and measured usage profile/runtime |
| Enclosure | Substantial bespoke River Stone retained | Phone/pack measurements, inlay, microphone access, connector bends, heat and service access |
| Fallback | Waveshare 4.3B, embedded firmware and ordered components retained | Physical validation remains pending; HP-01 resumes only if fallback is activated |

Product name and 20000mAh / PD 20W / QC wording above are user-supplied, not independently checked specifications. Do not infer usable output energy, the built-in cable connector or phone charging compatibility from the title alone.

No new measurements are claimed. Do not infer that the Ugreen is the custom 20 Ah pack in the Still Water draft, or combine it with the ordered bare-cell charger/boost circuit. Procurement records for the old build remain historical facts, not active primary-build requirements.

## Architecture and implementation boundary

The phone is the display, touch and voice-capture client. The bridge retains provider credentials, catalogue/collection/AI integration and native Naim control; the NDX 2 retains native TIDAL audio retrieval and playback. Preserve D011 and no automatic replay after uncertain mutations. Phone selection does not make the existing bridge production-ready on the Pi or prove iOS client parity.

Still Water is the revised design source. Its supplied iPhone architecture and Brief B are implementation proposals, not instructions executed merely by this hardware update. Native app versus web delivery needs a concrete assessment of available build/distribution tooling, trusted HTTPS/authentication, microphone capture, wake/lock behavior and lifecycle recovery. No provider secrets on the phone, new unauthenticated bridge endpoint or playback via the phone.

**Subsequent explicit Brief B, 25 September 2026:** the user authorized action on the concrete native-app brief. The source project now exists at `ios/StillWater.xcodeproj`; [implementation/evidence limits](../ios-still-water.md) supersede the delivery-route question above for this slice. Native compilation and all 17 simulator tests passed through the private GitHub Mac runner; [the current report](../ios-still-water.md) links exact evidence and the Windows gallery. No device validation has occurred. The earlier hardware-only authorization remains correctly scoped in D030.

### Actual app configuration to validate

- iPhone running iOS 17 or later; Xcode with a compatible iPhone 11 simulator runtime for automated review, supplied by the private GitHub Mac runner when developing on Windows (see [cloud build guide](../ios-cloud-build.md)). Device installation needs an appropriate signing team/profile; no account or signing identifier is embedded in the repository.
- Landscape-right interface, centered 755 × 346 pt mask, hidden status bar and requested hidden home indicator. Verify notch/inlay alignment on the actual phone. System keyboard, trust document picker, permission prompts and lock screen remain iOS-controlled surfaces.
- Start at 35% brightness; app preferences store fallback palette, brightness and idle-hold timeout. Configure and test iOS Auto-Lock. The app releases its idle hold; it cannot enforce an exact panel-off deadline. Guided Access/lock/unlock behavior must be tested before choosing a permanent kiosk configuration; no passcode removal or device reset was performed.
- Permit local-network access and provision the existing HTTPS bridge's independently verified PEM/DER trust plus a one-use pairing code. The credential and trust binding use Keychain, available after first unlock following reboot. No TIDAL/Naim/provider credential belongs on the phone.
- Permit microphone and Speech access for explicit Ask. The selected locale must support on-device recognition; missing support/permissions leaves typing available. The silent fixture captures no audio.
- Phase 1 keeps the phone attached to the identified UGREEN bank, with Optimised Battery Charging enabled in iOS. Verify the actual cable/connector and pack behavior. The app does not drive a switch or enforce 35–75% charging. Its external-power/network-required background task reports only when iOS grants execution; a 15-minute earliest start is not a schedule guarantee. Wake and active reporting remain separate.

Follow [the build and setup guide](../../ios/README.md). Do not describe these source settings as measured power, wake or kiosk results. Preserve all existing fallback procurement and firmware records.

The existing D029 battery report/charge query is implemented bridge behavior. It does not prove remote switching of a commercial Ugreen pack or require adding a custom power-control MCU. Select any charge-control hardware only if the actual pack and measured behavior require it.

## Next practical validation

1. Record exact phone/iOS and confirm the identified UGREEN product's SKU, labelled Wh, ports, built-in cable connector, inventory and cable arrangement privately where identifiers are involved. Review model-specific documentation before making charging or runtime claims.
2. On the actual phone, run a reversible silent Still Water visual trial using the permitted private artifact/static-fixture route. Check seated readability, touch targets, window edges, wake/lock and return to the interface. This is not live bridge integration proof.
3. Log a representative 48-hour screen-off/normal-use trial with the intended pack connection. Record brightness, Wi-Fi, active minutes, wake count, start/end charge and charging interruptions. Percentage changes are screening evidence; USB energy includes phone recharge and cannot alone establish internal standby consumption. Do not extrapolate weeks without a defensible energy basis.
4. Test built-in microphone capture, Stop/Cancel/timeout and transcript review on the selected client route; repeat quiet and music-playing queries. Preserve typing when capture is unavailable. No background listening or automatic playback.
5. Exercise Wi-Fi loss, bridge outage, phone/app restart and pack disconnect/reconnect. Restore authoritative state, show stale/unavailable honestly and never replay pending commands. These tests are separate from audible playback tests.
6. Repackage around measured phone/pack, connector and service envelopes. Check heat during normal use and charging in a representative enclosure; do not assume the earlier Waveshare fit geometry remains valid.

Deliver a sanitized report distinguishing user assessment, documentary facts, fixture behavior and physical results. The product name is recorded; exact SKU and connector/port configuration are the next hardware information dependencies. No new purchase, firmware deletion, phone reset or custom charging circuit is authorized by this plan.

## Parallel physical design

The newer [rear-loaded mounting proposal](river-stone/iphone-mount/README.md) and D030 govern the physical layout. Original 01 River Stone is the sole body/screen interface reference; preserve all microphone acoustic paths. The app build does not approve provisional aperture dimensions or replace the ongoing mounting work.


### B1 kiosk configuration

Enable Guided Access and turn **Volume Buttons off** in its session options. Apple documents this as preventing use of those buttons: https://support.apple.com/en-ie/111795. This is the configuration intended to prevent physical volume presses from raising the iOS volume overlay while Still Water is locked to the app. Leave Touch and Software Keyboards available for the controller. Configure the side button and auto-lock deliberately for the mounted trial. Verify suppression on the actual iPhone/iOS combination; merely enabling Guided Access is not proof that all buttons or overlays are disabled.

The implemented phone layout uses the full-screen colour field and system safe area plus 8 pt from D032. Earlier fixed-window/black-mask wording above is historical and does not govern B1.
