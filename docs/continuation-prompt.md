# Continuation prompt — paused prototype, revised design direction

Copy this into a new task, followed by the user's revised design brief:

---

Continue NDX2 Controller in `local/river-stone-repo`. First read `AGENTS.md`, `docs/chat-closeout-2026-09-23.md`, this prompt, `README.md`, `docs/decisions.md` (especially D028), `docs/m2-closeout.md` and `docs/m2-ui-parity.md`.

The user paused a working prototype because the visual direction was not what they wanted. Do not resume the previous polish loop or automatically pursue higher-resolution artwork. The old designer gate is not user approval. Use the revised direction supplied with this task; if none is supplied, inspect and summarize the baseline and ask for that direction before design changes.

Inspect current Git status, history and remote before editing. Last implementation is b36098d19473ae7d8b7ad1a96b16bcde632d862e; the documentation closeout follows it. Preserve all newer work, untracked materials and ignored artifacts. In particular, docs/still-water/ was local/untracked at closeout and was not reviewed or accepted by this handover. Establish its relevance from the user's instruction before adopting it. Do not reset/clean or replace the checkout with river-stone-shell-repo.

Retain the working shared C/LVGL functionality, authenticated artwork, preferences, recovery, transport fixes, protected setup/trust and package infrastructure. Visual composition may change under the new brief. Read docs/m2-object-design.md as implementation history, not aesthetic authority. Read docs/controller-contract-v1.md, docs/architecture.md, docs/deployment-design.md, docs/interaction-design.md, docs/m2-software.md and firmware/README.md before relevant changes. Runbooks m2-artwork, m2-preferences, m2-recovery, m2-provisioning, m2-setup, m2-trust and m2-package document implemented boundaries. Consult docs/roadmap.md, docs/detailed-design-plan.md and hardware records for remaining gates.

Preserve native Naim TIDAL and D011; no alternate audio route, replay of uncertain mutations, automatic re-pairing, weakened TLS/protected storage, live audible tests, physical provisioning/flashing/efuse/Pi installation or fabricated hardware/power claims. Keep silent fixtures while off the NDX network. The closeout enumerates exact command/recovery constraints, artifacts, previous validation and open physical gates. Original 5bf0c8a handover and older prompts are historical; preserve the frozen feasibility tag.

For authorized changes, work in bounded slices, render/review actual native pixels, validate affected behavior and update evidence, decisions, roadmap and continuation documents. Use installed tools; do not overwrite generated build/package directories. Prior test results are not fresh runs. Repository updates are authorized when appropriate: review and commit coherent validated work, fetch/reconcile concurrent changes, then push without force. Stage only owned changes and keep private data/generated artifacts out of Git.

The previous detailed continuation is archived in docs/m2-continuation-before-revised-direction.md for runbook history only. Its instructions to continue the old design or artwork work are superseded by this prompt and D028.
