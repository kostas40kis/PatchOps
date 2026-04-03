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
