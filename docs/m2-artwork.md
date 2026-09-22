# M2 authenticated artwork integration - 22 September 2026

Continued from clean `5bf0c8a` on main, preserving the approved UI, frozen feasibility tag and hardware work. Artwork is a read through the existing authenticated TLS `/v1/request` envelope. Only references registered by snapshot/native browse metadata are eligible; controller-supplied URLs and unknown/expired references cannot trigger a fetch. No unauthenticated image route was added.

## Bounds and lifecycle

The bridge reuses the existing URL allowlist/registration and bounded JPEG fetch, then Pillow **12.2.0** (already installed) to normalize an at-most-1-MiB JPEG with dimensions no larger than 1024 x 1024. Dimensions are checked before decoding: at most 1,048,576 source pixels. Source/conversion/codec working memory is additional to the output cache and has not been profiled on a deployment host. Raw compressed bytes are discarded after normalization. Four normalized previews and 32 registrations have 60-second validity; corrupt images are negatively cached. Host dependencies are pinned in `tools/requirements-m2.txt`; firmware SDK/LVGL pins are unchanged.

The initial format is **80 x 80 RGB565**, 12,800 pixel bytes encoded as 25,600 lowercase hex characters, within the existing 32-KiB response. Shared LVGL scales it into the unchanged 240-px Playing and 200-px detail spaces. The native decoder rejects wrong dimensions, format, identity, length, hex and validity. Its fixed reply pixel array is 12,800 bytes; the single renderer buffer is 12,800 bytes at 16-bit colour (25,600 at 32-bit). Existing transport/fixture reply copies each include that fixed array. No JPEG decoder is added to firmware. This preview is a bounded integration choice, not final photographic-quality or physical-memory acceptance.

Artwork stays on the existing network worker, with snapshots ahead of new artwork reads. Missing/corrupt/expired artwork remains unavailable; optional failure does not disconnect playback. Navigation, stale authoritative state, changed references and disconnect clear the displayed buffer. Obsolete generations and late/wrong-target replies cannot restore discarded covers. Requests are reads only; playback and D011 adapters are unchanged. A detail left open past registration expiry may need re-browsing to obtain a fresh registration.

Inspection also fixed a native voice recovery defect: Restart invalidates an in-flight transcript read and remains available while it is pending. Late replies after Restart or Cancel cannot search with discarded input. Native LVGL event tests exercise this plus artwork identity changes, missing/invalid replies, stale state, disconnect and retry suppression.

## Actual validation

- **77 Python tests**, including artwork normalization bounds/corruption, registration/URL refusal, expiry/eviction and authenticated/revoked TLS artwork access.
- **Five JavaScript tests** and the **five-stage silent TLS demo** passed.
- Desktop build and **three CTests** passed: controller, strict codec and native UI recovery.
- Native LVGL/TLS smoke passed. Actual 800 x 480 captures in ignored `local/m2/native-captures/` show initial artwork, detail artwork and a different cover after the one silent fixture play. Key captures were visually inspected; smoke also checks artwork pixels.
- ESP32 build passed: image **`0x92c00`**, **43%** application partition free. Compiler evidence only; gated on-device networking and physical memory have not been exercised.

The initial restricted desktop compiler attempt stalled and was stopped; normal permitted execution passed. No ACL/TLS check was weakened. Installed tools were used; no dependency download was needed. Approved HTML SHA-256 remains `1886dfe3f6bea33d8206bbe27b0c799a45964c995144131ef02a9619a3c68bbc`; the frozen tag still resolves to `aa070fc0af4a616f769a7c0f15790831c90c112c`.

## Remaining boundaries

Live metadata/artwork validation and deployment-host decode/resource profiling, higher-resolution delivery if justified, persistent preferences, production provisioning/admin, and physical display/touch/wake/microphone/power acceptance remain open. The standalone in-memory firmware fixture still shows unavailable artwork; authenticated desktop fixtures and the shared native regression harness exercise pixels.

No live/audio command, flashing, efuse operation, real credential provisioning or Pi installation occurred. HP-01 and physical P3/P4/P5 remain open; the ten-step hardware checklist is unchanged. Native Naim playback, no mutation replay, D011, protected persistence and provisioned TLS trust remain mandatory.
