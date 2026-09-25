# iPhone functional parity remediation

**D032 safe-area update available — 25 September 2026:** internal TestFlight **0.1.0 (3.1.0)** is assigned to the existing Naim NDX2 Controller TestFlight group and Apple shows **Testing**. Source `6f0b9afa49da5e6953c17664bdc5987e312a9524`, [run 36178335036](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36178335036), passed all 23 native tests and archive/sign/upload checks. The background fills the screen, content respects the system safe area plus an 8 pt inactive inset in the existing locked orientation, Like is compact beside the album, and secondary screens have one plain Back control. Other review suggestions were not adopted. Gallery: `local/ios/review-safe-area/review.html`. Mounted-phone/user acceptance remains open; this is still a silent preview.

25 September 2026, D032. The user reported usability and function gaps in internal build 0.1.0 (1.2.0). The prior automated pass did not establish full functional parity or seated readability.

| Agreed capability | Remediation and acceptance check |
| --- | --- |
| Landscape display | Fit available display with an inactive border of at least eight points; artwork stays square. Functional interior margins clear the iPhone 11 notch. Check full-phone captures and target bounds. |
| Legible typography | Increase NOW artist to 26 design units, album to 28, list secondary text to 22, filter/navigation labels to 24–26. Verify actual device presentation rather than a reference-sized crop. |
| Transport | Previous/Next 96-unit targets and 48-unit glyphs; Play/Pause 104-unit target and 52-unit glyph. Physical iPhone 11 tests require at least 72-point Previous/Next and 80-point Play/Pause. |
| Volume | Speaker-minus/plus icons, accessible Volume down/up names; no Amp label. Existing bounded action and uncertain-outcome guard retained. |
| NOW relationships | Tap exact artist and album references into detail; no guessed relationships when absent. First wake contact still reveals only. |
| Track Like/Unlike | NOW button and track detail use observed membership; unknown state cannot write. Refresh after writes. |
| Album library | Add to library / Remove from library reflect observed state on detail. |
| Artist follow | Follow / Unfollow reflect observed state on artist detail. |
| Back and browsing | Preserve bounded history, query/filter/scroll, Find, Library, detail children and More; explicit Back to now retained. |
| Queue and progress | Read-only Up next, upcoming title, elapsed/duration and playback progress retained. |
| Settings and Ask | Settings gets a separate button; Ask remains synthetic in the distributed preview. |
| Unknown and pending actions | No replay or optimistic success. An unrelated membership read cannot clear an uncertain write. |

The offline fixture stores membership separately for each reference. Native model tests cover track, album and artist state isolation and both directions of each action; a full-phone UI test follows the public navigation and toggles the controls. Existing native geometry, contrast, keyboard, lifecycle and no-replay tests remain gates. Native results and reviewed captures must be recorded after the run; Windows source checks alone do not prove compilation.

Phone review: install the replacement, confirm the border and notch clearance, read it from the intended seated distance, exercise all rows above, and report screenshots plus the action leading to any failure. No live playback or physical acceptance is implied.

## Validation outcome

**D032 remediation available in TestFlight — 25 September 2026:** version **0.1.0 (2.1.0)** was signed and uploaded from `dbd5c379c0c57e58bdab6a360a01e214f80d65bd` in [run 36174233828](https://github.com/LeweeLewee/NDX2-Controller/actions/runs/36174233828). All **23 native tests** passed, none failed or skipped; unsigned device archive and signed internal export succeeded. The phone-fit layout, larger type/transport, volume icons, exact artist/album navigation, track likes, album library controls, artist follow controls and row-specific membership actions are implemented. Fixture Library reflects per-item additions/removals. Apple processing completed; the build is assigned to **Naim NDX2 Controller TestFlight** and shows **Testing**. The existing tester can update through TestFlight; group distribution remains manual. Read [the parity checklist](ios-remediation.md). Physical readability and user acceptance of this replacement remain open; it is still a silent fixture preview.

The result-list membership indicators are actionable and reference-specific. Library fixtures are rebuilt from saved membership; no production bridge mutation was needed. The 31-image review gallery is retained under ignored `local/ios/review-remediation/`.
