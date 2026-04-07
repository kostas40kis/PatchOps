# PatchOps Summary-Integrity Repair Stream
## Current-state truth reset after Patch 133, Patch 133A, and the failed Patch 134 attempt

## Purpose

This note makes the current summary-integrity repair stream visible from the repo itself.

It exists so the next LLM can continue the stream without depending on prior chat history.

This is not a redesign note.
It is a narrow maintenance / repair note for a repo that is already in a maintenance / refinement posture.

---

## Current interpreted posture

PatchOps should still be treated as:

- a maintained wrapper / harness,
- substantially complete as an initial product,
- and currently doing narrow repair / validation work rather than broad architecture work.

The important remaining risk in this stream is truth drift in the rendered report summary, not a missing subsystem.

---

## Observed repair-stream chain

### Patch 133

Patch 133 did **not** reach the summary-integrity bug.

It failed first as a wrapper/content-path authoring problem.

Observed failure shape:

- classification: `wrapper_failure`
- error class: `FileNotFoundError`
- symptom: duplicated patch-root path under the manual-repair content path

Meaning:

- the first failure in this stream was not the reporting engine,
- it was the self-hosted manifest/content-path authoring shape.

### Patch 133A

Patch 133A repaired the manifest-local content-path problem and reached the real bug.

The repro test confirmed the contradiction we were looking for:

- the report body showed a required validation command with a non-zero exit,
- but the rendered summary still ended with:
  - `ExitCode : 0`
  - `Result   : PASS`

This is the confirmed product bug in the stream.

### Attempted Patch 134

The attempted Patch 134 run then failed earlier as a malformed-manifest authoring problem.

Observed failure shape:

- malformed manifest / invalid JSON
- patch-authoring failure
- the repair logic did not get a fair execution path

Meaning:

- Patch 134 did not yet prove or disprove the engine fix,
- because the manifest failed before the reporting logic could be exercised.

---

## Failure classification for this stream

Keep these failure classes separate:

1. **Patch 133**
   - wrapper/content-path authoring failure

2. **Patch 133A**
   - confirmed product bug in summary derivation

3. **Attempted Patch 134**
   - patch-authoring / malformed-manifest failure

The most important rule is:

> Patch 133A is the confirmed product bug.

Do not let Patch 133 or the attempted Patch 134 failure distract the next repair patch into the wrong layer.

---

## What is actually wrong

The confirmed product bug is:

- a required validation failure can still coexist with a rendered summary that says `PASS`.

The likely technical implication is:

- truthful final summary state is not being derived strictly enough before rendering,
- or stale success state is still able to survive into the final summary block.

That bug should be repaired in Python-owned workflow / reporting state derivation, not by widening PowerShell.

---

## Immediate next action

Proceed to the second patch in the six-patch repair circle:

1. repair the self-hosted authoring path narrowly,
2. keep `content_path` manifest-local and stable,
3. repair the malformed JSON generation issue from the attempted Patch 134 run,
4. rerun the real summary-integrity repair path only after the authoring path is clean.

Do not redesign PatchOps during this stream.

---

## Boundary reminder

Preserve the current architecture rules:

- keep PowerShell thin,
- keep reusable workflow logic in Python,
- keep PatchOps project-agnostic,
- keep one canonical report per run,
- prefer narrow repair over broad rewrite.

<!-- PATCHOPS_PATCH134B_STREAM:START -->
## Patch 134B â€” authoring unblocker after the truth reset

Patch 134A established the maintained truth-reset note and recorded the observed failure chain.

Patch 134B keeps the next move narrow.
It does not attempt the summary derivation repair yet.
Instead it locks the current self-hosted authoring contract that the repair stream should use:

- self-hosted manual-repair manifests in this stream should be emitted as valid JSON from structured data,
- self-hosted `content_path` values should remain manifest-local and relative to the manifest file,
- the stream now carries a regression test that drives `check`, `inspect`, `plan`, and `apply` against a temporary self-hosted manual-repair patch root.

This directly addresses the two authoring-side problems seen around the stream:

1. Patch 133 used the wrong `content_path` shape and duplicated the patch root.
2. Patch 134 failed before execution because the generated manifest was not valid JSON.

The real product bug is still separate:
a required command failure must not coexist with a rendered summary that says `PASS`.
<!-- PATCHOPS_PATCH134B_STREAM:END -->

<!-- PATCHOPS_PATCH134C_STREAM:START -->
## Patch 134C â€” real summary-integrity repair

Patch 134C repairs the confirmed product bug from Patch 133A.

Confirmed contradiction from Patch 133A:
- the command evidence showed a required command with non-zero exit,
- but the inner rendered report summary still ended with `ExitCode : 0` and `Result   : PASS`.

Patch 134C keeps the repair narrow:
- it does not redesign the workflow model,
- it does not widen PowerShell,
- it does not redesign the manifest contract.

Instead it fixes the immediate reporting truth problem by deriving the rendered summary from required validation and smoke command evidence before `render_summary(...)` is called.

Current behavior locked by tests:
1. required validation failure outside `allowed_exit_codes` renders `FAIL`,
2. earlier required failure stays sticky even if later required commands succeed,
3. explicitly tolerated non-zero exits still render `PASS`.

The broader fail-closed workflow hardening remains a later patch.
<!-- PATCHOPS_PATCH134C_STREAM:END -->

<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:START -->
## Patch 134F - maintained doc refresh

Patch 134F refreshes the maintained reading surfaces so future LLMs and operators can understand the stream from repo files alone.

It records the now-maintained interpretation:
- Patch 133 = wrapper / patch-authoring failure,
- Patch 133A = confirmed product bug repro,
- Patch 134 = malformed-manifest authoring failure,
- Patch 134B = authoring unblocker,
- Patch 134C = rendered-summary derivation repair,
- Patch 134D / 134E = workflow-facing fail-closed hardening.

This patch intentionally keeps the story narrow and maintenance-oriented.
The remaining stream work is proof / freeze validation rather than redesign.
<!-- PATCHOPS_PATCH134F_SUMMARY_INTEGRITY_DOCS:END -->

<!-- PATCHOPS_PATCH134G_STREAM:START -->
## Patch 134G - final proof and handoff refresh

Patch 134G is the closing proof patch for the six-patch summary-integrity repair circle.

### What it proves
- the rendered report summary no longer claims `PASS` when required validation or smoke evidence failed outside `allowed_exit_codes`,
- CLI-facing and handoff-facing workflow surfaces also fail closed when required command evidence contradicts stale success state,
- the maintained handoff bundle can be refreshed from a green current report after the repair stream.

### Acceptance reached
- Patch 134A truth reset: complete.
- Patch 134B authoring unblocker: complete.
- Patch 134C report-summary derivation repair: complete.
- Patch 134E workflow hardening repair: complete.
- Patch 134F maintained docs refresh: complete.
- Patch 134G proof and handoff refresh: complete.

### Current closure statement
Treat the summary-integrity repair stream as complete unless later repo evidence shows another contradiction between required command evidence and final reported status.
<!-- PATCHOPS_PATCH134G_STREAM:END -->

<!-- PATCHOPS_PATCH134H_REPORT_DIR_REPAIR:START -->
## Patch 134H â€” apply-flow report-directory creation repair

Patch 134G exposed a narrow apply-flow bug: `patchops.workflows.apply_patch.apply_manifest(...)` could respect a custom `report_dir` in planning output yet still fail at report-write time when that directory did not already exist.

The repair is intentionally narrow:
- create the parent directory for the resolved report path before writing the canonical report,
- keep the existing `report_preferences.report_dir` contract,
- add a regression test that proves a missing custom report directory is created automatically.

This is a wrapper/content repair, not a summary-integrity redesign.
<!-- PATCHOPS_PATCH134H_REPORT_DIR_REPAIR:END -->

<!-- PATCHOPS_PATCH134I_REPORT_DIR_PROOF:START -->
## Patch 134I â€” report-dir proof repair

Patch 134H most likely repaired the apply-flow bug itself, because `patchops apply` progressed far enough to emit a normal run summary instead of crashing on report creation.

The remaining failure looked like proof-layer drift, not a second report-path crash.
This repair therefore keeps the code fix, narrows the proof surface, and hardens report-preference tests to use an explicit Python runtime instead of relying on the bare `python` command.

This remains a narrow wrapper/content repair.
<!-- PATCHOPS_PATCH134I_REPORT_DIR_PROOF:END -->

<!-- PATCHOPS_PATCH134J_REPORT_DIR_PROOF:START -->
## Patch 134J â€” report-dir proof pytest repair

Patch 134H most likely fixed the underlying apply-flow bug by creating the report directory before writing the canonical report.
The remaining failures were inside the proof layer itself.

This patch keeps the apply-flow repair, updates the maintained report-preference proof test to use an explicit Python runtime, and proves the repair with focused pytest coverage only.
<!-- PATCHOPS_PATCH134J_REPORT_DIR_PROOF:END -->

## Patch 134K - report-dir proof layer repair

Patch 134K repairs the remaining proof-layer drift left after Patch 134H through Patch 134J.

What it changes:
- the maintained report-preference apply-flow proof is rewritten as valid current tests,
- the proof now uses structured manifests and `sys.executable` for the validation command,
- the underlying apply-flow code repair from Patch 134H remains unchanged.

Interpretation:
- Patch 134H fixed the missing-report-dir creation bug in live code,
- Patch 134K repaired the proof layer around that fix,
- the remaining work after Patch 134K is the final proof / handoff refresh step only.

## Patch 134L - final proof and handoff refresh retry

Patch 134L reruns the maintained summary-integrity proof layer after Patch 134K returned the report-dir proof surface to green.

It then refreshes the maintained handoff bundle from the current green report and records the closure state in maintained docs.

Acceptance reached:
- Patch 134A truth reset: complete.
- Patch 134B authoring unblocker: complete.
- Patch 134C report-summary derivation repair: complete.
- Patch 134E workflow hardening repair: complete.
- Patch 134F maintained docs refresh: complete.
- Patch 134H apply-flow report-directory creation repair: complete.
- Patch 134K report-dir proof-layer repair: complete.
- Patch 134L final proof and handoff refresh: complete.

## Closure statement

Treat the summary-integrity repair stream as complete unless later repo evidence shows:
- a new contradiction between required command evidence and final reported status,
- or a new report-preference regression in the same apply-flow report-directory area.

## Patch 134O - exact-current repair manifest authoring fix

Patch 134O keeps the exact-current apply report-write hardening payload and repairs only the manifest authoring shape that blocked Patch 134N.

What it means:
- the apply-flow report write hardening is now live in the current repo,
- the stream now returns to the original final proof / handoff refresh goal,
- there is no need to widen the repair stream into a broader reporting redesign.

## Patch 134P - final proof and handoff refresh retry

Patch 134P reruns the maintained summary-integrity proof layer after Patch 134O landed the exact-current apply report-write hardening.

It then refreshes the maintained handoff bundle from the current green report and records the closure state in maintained docs.

Acceptance reached:
- Patch 134A truth reset: complete.
- Patch 134B authoring unblocker: complete.
- Patch 134C report-summary derivation repair: complete.
- Patch 134E workflow hardening repair: complete.
- Patch 134F maintained docs refresh: complete.
- Patch 134K report-dir proof-layer repair: complete.
- Patch 134O apply-flow report write hardening / manifest authoring fix: complete.
- Patch 134P final proof and handoff refresh retry: complete.

## Final proof / closure after 134Y and 134Z

The stream finished in two truthful steps:

1. `p134y_report_dir_pre_mkdir_fallback_fix` repaired the last live Windows-hostile report-dir blocker by delaying custom report_dir creation until a safe candidate path was selected.
2. `p134z_final_proof_handoff_refresh` reran the maintained proof layer from that green report-path frontier and refreshed handoff from the resulting green report.

Final interpretation:
- the original summary-integrity contradiction remains fixed,
- tolerated explicit nonzero exits remain allowed,
- workflow-facing surfaces fail closed,
- the Windows-hostile custom report-path issue is repaired,
- the stream is complete unless new contrary evidence appears.

## Maintained fail-closed rules locked by current tests

- required validation failure outside llowed_exit_codes forces rendered summary FAIL
- required smoke failure outside llowed_exit_codes forces rendered summary FAIL
- the first required failure remains sticky even if later required commands succeed
- explicitly tolerated non-zero exits still remain PASS
## exact fail-closed phrase alignment

- required validation failure outside `allowed_exit_codes` forces rendered summary `fail`
- required smoke failure outside `allowed_exit_codes` forces rendered summary `fail`
- the first required failure remains sticky even if later required commands succeed
- explicitly tolerated non-zero exits still remain `pass`
