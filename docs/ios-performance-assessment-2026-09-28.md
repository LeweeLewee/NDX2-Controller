# Live iPhone beta performance assessment — 28 September 2026

## Verdict

The iPhone → authenticated bridge → native Naim architecture remains viable. The current artwork delivery and client scheduling/rendering implementation is not suitable for this UI. Do not call build 15.1.0 usable or release-ready. Passing fixture/snapshot tests did not establish integrated live performance or provider setup.

This assessment does **not** validate a replacement artwork protocol on a physical phone. It identifies measured bottlenecks and a concrete remediation design. Library, exact metadata navigation and reliable controls are separate release gates.

## Measurements

Read-only Windows-host assessment of the current NDX queue and its returned TIDAL cover; no playback/volume/collection writes. Two complete 320-preview passes, five snapshots. Raw outputs stay in ignored `local/ios/live-trial/artwork-performance-*.json`.

| Measurement | Observed |
|---|---:|
| Native bridge snapshot, in-process median (5) | 54 ms |
| Authenticated loopback TLS snapshot median (5) | 92 ms |
| Complete cover, in-process, two passes | 913 / 834 ms |
| Complete cover, authenticated loopback TLS, two passes | 1,225 / 1,156 ms |
| Requests per 320 cover | 16 |
| Source fetches per cover, both passes | 16 / 16 |
| Encoded response bytes per complete cover | 417,993 |
| Queue items / distinct artwork identities in first page | 12 / 1 |
| Isolated source decode, resize, one chunk | about 11 ms |
| Experimental 320 JPEG, quality 80 | 11,331 bytes |
| Experimental JPEG encoded as base64 | 15,108 bytes, before envelope |

These are Windows/loopback observations, not iPhone/Wi-Fi latency, p95 estimates or a broad catalogue benchmark. The JPEG experiment covers one real image; arbitrary covers still require an enforced byte ceiling and bounded quality/downsize policy. It changes the codec, not resolution, and is not deployed. The experiment suggests roughly 28× less response payload and 16→1 artwork requests for this image, not a demonstrated 28× end-to-end speedup.

The current page can require 192 chunk reads and about 5 MB of artwork responses for 12 entries even though all share one cover. At measured sequential cover cost that is roughly 14 seconds, **before** phone rendering and intervening polls. This is an estimate, not a measured phone page load.

## Findings

1. `ArtworkDelivery` caches chunks by reference/side/offset with only four entries. A 320 cover has 16 chunks. Each miss explicitly removes the source image cache, fetches and decodes again, then drops it. A second whole-cover pass misses again. This follows the original constrained-memory tradeoff; it is unsuitable for a cover-heavy iPhone UI.
2. Queue previews are keyed by track reference. Identical album artwork is downloaded separately for every track. NOW and queue previews also have separate reuse paths.
3. `Preview.uiImage` builds a new 320 RGBA image for every call. It also recalculates the fallback palette's contrast search. SwiftUI body evaluation calls this repeatedly as observable request/player state changes. This is a code finding; its physical-phone CPU contribution remains unmeasured.
4. `BridgeClient.receive` consumes response bytes one at a time in a main-actor class. Each cover entails approximately 418,000 such iterations. It needs bounded buffered receipt off the UI actor, retaining early 32-KiB rejection, pinned trust and cancellation semantics.
5. A single request path carries polling, metadata and artwork. Cancelling an iPhone read cannot cancel a source fetch already running in the bridge's single worker. Source delays can hold up subsequent controls. The phone clears all artwork when player freshness expires; artwork also expires after 60 seconds. These rules explain possible blank/reload cycles, but the exact failed phone event has not been traced.
6. Library is not configured: the private trial blocks `library_page`, and `Bridge(NaimClient(...))` has no catalogue/library adapter or connected user collection. Readback reports account disconnected. Empty Library is not an artwork defect. Native favourites can be investigated as a read-only alternative; it must not silently be substituted for authenticated TIDAL My Collection.
7. Exact Artist/Album links rely on the catalogue `related` adapter. It is absent in this trial; the live snapshot has neither reference. Track/artist/album names are not enough to guess exact IDs. Current UI makes these unavailable destinations too easy to mistake for working controls.
8. Pause/resume remain permitted in the private trial, but the current log has no transport submission for the reported failure. Its cause is **not yet established**: freshness, the initial contact gate and persisted uncertain-command state are possible client gates. Earlier successful Pause is not proof of current reliability. Do not clear unknown outcomes automatically or replay commands.

## Recommended coordinated remediation

- Add an **optional iPhone artwork encoding** through the existing authenticated `artwork` action, keeping legacy 80/RGB565 and existing routes intact. A bounded 320 JPEG/base64 response should fit below 32 KiB; reject overflow before transmission. Keep allowlisted registered sources, dimension/decode bounds, identity, original validity and revocation. This protocol extension is a proposal, not an adopted decision.
- Normalize once per artwork identity and cache bounded encoded bytes, by identity/size/encoding. A four-entry, at-most-24-KiB-per-entry encoded cache can stay within the existing 102,400-byte pixel-payload budget. Source/working-memory peaks require measurement; no silent increase in source bounds.
- Share completed valid previews across NOW, Library and queue by artwork identity; share repeated album covers among tracks. Cache tinted images by pixel identity and selected palette with an explicit iPhone memory budget. Recolour only when either changes.
- Use a bounded response collector off the main actor. Keep control dispatch ahead of optional artwork and keep background metadata/cover work out of the authoritative snapshot's critical path. Retain single-dispatch, no replay and unknown-outcome protections.
- Revalidate visible artwork before its deadline, allowing the same image to remain on screen only while original validity/freshness still holds. Refresh must be authorized by a new response; do not merely prolong client TTL or hide disconnects.
- Configure and verify the actual catalogue and user collection, or explicitly select/document native favourites. Enable required authenticated **read** actions in the private trial only after their dependency and error behaviour is verified. Show configuration errors instead of an apparently empty valid library.
- Trace one user-initiated Pause from tap eligibility through authenticated bridge result and subsequent native state; make blocked/uncertain states visible. Repeat under artwork load. No blind retry.

## Acceptance gates before another usability claim

Proposed targets, not achieved measurements: cached screen/cover revisit ≤100 ms; first visible cold cover ≤1.5 s and warm cover ≤250 ms on the target LAN; responsive touch/scroll while loading; user-initiated Pause acknowledged and native state observed within 500 ms at p95 on the target network (record at least 20 trials with user-authorized audible scope). Explain any network outliers rather than weakening no-replay protections. Measure both idle and cover-loading cases.

Use distinct and repeated covers, a full queue/library page, screen changes during transfers, at least five minutes across multiple 60-second expiries, lost Wi-Fi/reconnect, revoked trust, oversized/corrupt images and a slow CDN. Track request counts, source fetch counts, response bytes, peak bridge/client memory, main-thread time and authoritative freshness gaps. Verify real Library, Artist and Album destinations before calling this an integrated live beta.

## Changes in this assessment

- Added an explicit read-only performance diagnostic with fixture default and an optional isolated authenticated TLS mode; it never issues control actions or changes the running bridge enrollment.
- Added track names beneath Up Next covers. Shortened the decorative reflection to leave a separate two-line title band without changing the outer safe area.
- Added offline diagnostic coverage, a queue-label geometry assertion and a native rendering timing baseline. Native validation is recorded in evidence when complete.
- No production artwork codec, account setup, transport security, bridge route, firmware or live write capability was changed. Do not present this assessment/label change as a fix for all reported failures.


## Remediation measurements — 28 September

An isolated authenticated loopback TLS run of the implemented `jpeg-base64` path against the same live cover measured **98.6 ms cold / 12.6 ms repeat**, **15,568 response bytes** per whole cover and **1 / 0 source downloads**, compared with the earlier 1,225 / 1,156 ms, 417,993 bytes and 16 / 16 source downloads. Response traffic fell about 96%. Snapshot median remained 93.5 ms. This was read-only; the running trial bridge and physical phone enrollment were unchanged. Private results: `local/ios/live-trial/artwork-performance-compressed-tls.json`.

The completed pre-cache native baseline measured 488.2 ms for twelve 320px palette render calls on the simulator. The remediation reuses rendered images by immutable preview identity and selected palette, bounded to twelve entries (at most 4.9 MB of RGBA pixels), and memoizes the three fallback palettes. Native post-change results are pending. Shared queue covers reuse the original preview/deadline; expired or invalidated images remain unusable. These host/simulator observations do not establish physical-phone acceptance.

TIDAL My Collection is now the user-selected Library source. It is not configured yet: project developer credentials and account consent are required. Empty/disconnected/error states must not be conflated. Artist/Album links and integrated transport behavior remain acceptance work; no replacement release has been distributed.


**Native remediation checkpoint:** source `2e4d53f` passed 45 iOS 18.6 simulator tests (41 unit/snapshot plus four UI), four iOS26.2 TLS tests and the unsigned device archive in [run36410715309](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36410715309). Twelve warm palette-render calls measured 0.67 ms versus the earlier 488.2 ms uncached baseline; this is simulator evidence, not iPhone timing. Follow-up `d250acf` adds complete JPEG fixture coverage, source-orientation checking, metadata registration renewal for paged covers and explicit disconnected/error Library states. Its final native validation is running at [run36411702204](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36411702204). All 160 Python tests, five navigation tests and six fixture stages pass. No TestFlight upload, running bridge restart or assistant-issued NDX mutation. TIDAL developer-app credentials and user consent are still required; never paste secrets into chat.
