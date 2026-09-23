# Project instructions

- Current handover: read docs/chat-closeout-2026-09-23.md and docs/continuation-prompt.md before resuming. The user paused work and rejected the current visual direction (D028). Preserve the working prototype and newer work; do not resume design implementation without the revised direction.

- Read README.md and docs/decisions.md before changing architecture.
- Native Naim TIDAL playback is non-negotiable. Do not substitute Music Assistant-to-DLNA, AirPlay, Chromecast, Roon, a Pi audio relay or generic URL playback. TIDAL Connect is a distinct route, not an automatically accepted replacement.
- Distinguish live observations, reference-code behaviour, hypotheses and untested implementation claims. Computer-side success does not prove ESP32 firmware or battery life.
- Prefer read-only inspection before live mutations. Honour existing user authorization; do not invent additional approval gates. Announce audible tests, inspect existing playback/queue state, and verify the final state after commands. Do not equate an HTTP 200 with completed playback.
- Do not treat /levels/room as confirmed amplifier System Automation control until tested. Avoid arbitrary volume changes.
- Keep live reports, addresses, account information and captures in ignored local/. Never commit service credentials, tokens or raw responses.
- Keep development tools in tools/, tests in tests/, and documentation in docs/. Do not migrate one-off live command scripts into production without review.
- Update docs/evidence.md when a claim becomes proven or disproven, docs/decisions.md for accepted design changes, and docs/roadmap.md for milestone progress.
- Run appropriate offline tests for changes to diagnostics. Live device tests are separate and must not run automatically in unit tests or CI.
