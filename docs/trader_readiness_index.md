# Trader Readiness Index

This document is the **single operator map** for the trader-first usage wave.

Use it as the **single jumping-off document** before drafting, reviewing, rehearsing, or running trader-facing PatchOps manifests.

It ties together the starter manifests, the trader-first guidance docs, the rehearsal flow, and the Stage 2 boundary so the first real trader-facing usage path is obvious and repeatable.

---

## 1. Start here

Read these in order when you are preparing a trader-first PatchOps run:

1. `docs/trader_first_usage.md`
2. `docs/trader_manifest_authoring_checklist.md`
3. `docs/trader_safe_first_patch_types.md`
4. `docs/trader_execution_sequence.md`
5. `docs/trader_rehearsal_runbook.md`
6. `docs/first_real_trader_run_checklist.md`
7. `docs/stage2_entry_criteria.md`

That sequence moves from orientation, to manifest authoring, to safe patch selection, to execution, to rehearsal, to the first real run boundary, and finally to the Stage 2 gate.

---

## 2. Trader starter manifests and examples

Use the examples directory as the manifest starting surface for trader work.

Primary trader-first starter assets:

- `examples/trader_first_doc_starter.json`
- `examples/trader_first_verify_patch.json`

Broader trader examples that remain useful for adaptation and comparison:

- `examples/trader_doc_patch.json`
- `examples/trader_verify_patch.json`
- `examples/trader_code_patch.json`

Recommended rule:
start from the smallest trader-first example that matches the job, then adapt only what is necessary.

---

## 3. Safe first patch categories for trader work

The preferred first wave is still conservative.

Use `docs/trader_safe_first_patch_types.md` to stay inside low-risk categories such as:

- documentation-first changes,
- review-before-apply paths,
- verification-first runs,
- narrowly scoped maintenance or validation work.

Avoid treating the trader profile as permission to jump immediately into broader operational change.

---

## 4. Execution path

Use the trader-first docs together, not in isolation:

- `docs/trader_execution_sequence.md` explains the end-to-end operator order.
- `docs/trader_rehearsal_runbook.md` explains how to rehearse that path safely.
- `docs/first_real_trader_run_checklist.md` defines the final go-live-style readiness checks.

If you only remember one thing, remember this order:

1. orient with this index,
2. select or draft the manifest,
3. review the manifest against the trader checklist,
4. rehearse,
5. run the first real trader-facing patch only after the checklist and rehearsal are both green.

---

## 5. Stage boundary

Patch 30 does **not** begin Stage 2.

This index exists to make late Stage 1 / pre-Stage 2 trader readiness easier to operate.

Use `docs/stage2_entry_criteria.md` as the explicit gate for deciding whether the project can move beyond the trader-first preparation wave.

Use `docs/project_status.md` to confirm the currently shipped readiness surface and the intended boundary of the current stage.

---

## 6. Recommended operator sequence

For the first trader-facing usage wave, the clean operator path is:

1. Read this readiness index.
2. Read `docs/trader_first_usage.md`.
3. Draft or adapt a starter manifest from `examples/`.
4. Review it with `docs/trader_manifest_authoring_checklist.md`.
5. Confirm the requested work is inside `docs/trader_safe_first_patch_types.md`.
6. Follow `docs/trader_execution_sequence.md`.
7. Rehearse with `docs/trader_rehearsal_runbook.md`.
8. Use `docs/first_real_trader_run_checklist.md` before the first real trader-facing run.
9. Use `docs/stage2_entry_criteria.md` to decide whether to escalate beyond the initial readiness wave.

---

## 7. What this document is for

This document exists so the trader-first usage phase has one obvious starting point instead of many useful docs scattered across the repo.

If someone asks where to begin the trader-first PatchOps path, the answer should be:

**Start with `docs/trader_readiness_index.md`.**
