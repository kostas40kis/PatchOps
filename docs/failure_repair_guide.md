# Failure Repair Guide

This file is the maintained decision guide for interpreting failures in PatchOps runs.

Its purpose is simple:

**What failed, and what is the narrowest trustworthy recovery path?**

This guide is the classification-guided repair choice surface for the wrapper.

It should help an operator or future LLM decide between:

- direct narrow repair
- Verification-only rerun
- Wrapper-only repair
- failure-capture-first rerun
- broader escalation only when the evidence really justifies it

## Maintained failure-class vocabulary

Use these maintained categories when reading reports, CLI output, or helper surfaces:

- `target_project_failure`
- `wrapper_failure`
- `patch_authoring_failure`
- `ambiguous_or_suspicious_run`

Plain-English labels still matter too:

- Content failure
- Wrapper failure
- wrapper/reporting failure
- wrapper/authoring failure
- suspicious run
- test-contract failure

## Quick decision table

| Observed pattern | Most likely class | Narrowest trustworthy recovery path |
| --- | --- | --- |
| A required command failed against real target behavior | Content failure / `target_project_failure` | Repair the target-facing content, then rerun validation |
| The report or launcher contradicted the command evidence | Wrapper failure / `wrapper_failure` | Repair the wrapper/reporting layer first |
| The manifest, emitted test, or staged file is malformed | wrapper/authoring failure / `patch_authoring_failure` | Repair authoring output first, then rerun narrowly |
| Current files are believed correct and only validation needs rerun | Verification-only rerun | writes are skipped and expected target files are re-checked |
| Patch content likely succeeded but wrapper/reporting failed | Wrapper-only repair | keep scope narrow and avoid blind full reruns |
| Evidence is contradictory or incomplete | suspicious run / `ambiguous_or_suspicious_run` | prefer failure-capture-first rerun before wider repair |
| A wording or status surface drifted while behavior stayed correct | test-contract failure | repair the smallest doc/test contract surface |

## Main classes in plain English

### Content failure

Use this when required target-facing behavior is actually wrong.

Typical signs:

- a required validation command exits non-zero for a real target reason
- the manifest applied correctly but the resulting behavior is wrong
- a required content assertion fails after the wrapper did what it was supposed to do

This usually maps to `target_project_failure`.

Default move: repair target content, then rerun the smallest trustworthy validation path.

### Wrapper failure

Use this when the wrapper, launcher, or reporting layer failed to prove reality reliably.

Typical signs:

- the launcher died before the repo under test was actually exercised
- the report hid the failing command output
- the summary contradicted the required command evidence
- the wrapper failed even though the target content may already be correct

This usually maps to `wrapper_failure`.

### Verification-only rerun

Use this when the content on disk is believed to be correct and the safest next step is a narrow rerun.

The essential behavior is:

- writes are skipped
- expected target files are re-checked
- validation commands are rerun
- the report should make the narrow scope obvious

### Wrapper-only repair

Use this when the patch content likely succeeded but the wrapper or report layer failed.

The repair goal is narrow:

- do not silently widen execution
- do not rewrite unrelated files
- recover report truth and wrapper truth first

## Suspicious-run support

Suspicious-run support is a conservative wrapper health aid. It is meant to help operators notice when wrapper evidence looks contradictory or incomplete. It is not a target-content feature and it does not claim that the target project itself is broken.

What currently counts as suspicious should stay narrow. Examples include required command evidence contradicting the rendered summary, critical provenance fields missing after wrapper execution, a copied latest-report surface missing after a handoff export path that should have produced it, or a report structure missing required core fields.

This surface starts opt-in on purpose. The first release is meant to stay maintenance-friendly and avoid noisy false positives in every run. Operators should enable emitted suspicious-run artifacts only when they are deliberately proving or inspecting wrapper health.

When a suspicious-run artifact is emitted, read it as a small machine-readable aid rather than as a final verdict. The artifact summarizes the detection reason, failure class, report path, workflow mode, optional manifest path, and recommended follow-up so the next inspection step is easier to choose.

## wrapper/reporting failure vs wrapper/authoring failure

### wrapper/reporting failure

This is a wrapper failure where report plumbing, summary derivation, or evidence rendering is the broken layer.

Examples:

- `ExitCode` / `Result` does not match the required command evidence
- the report path exists but the important failing output is missing
- the catch path crashed and replaced the real failure with a helper failure

### wrapper/authoring failure

This is a patch-authoring failure where the emitted manifest, staged file, or generated test is malformed before the actual repo contract was exercised.

Examples:

- malformed JSON manifest
- emitted Python test with bad indentation or escaping
- exact-text surgery that failed because the live file shape drifted

## test-contract failure

A test-contract failure is usually a narrow wording or surface-drift problem rather than a deep architecture problem.

Typical signs:

- docs or status surfaces lost exact maintained phrases
- the code behavior is still right, but the exact contract wording drifted
- a proof patch advanced the repo and a narrow doc/test alignment repair is needed

Default move:

- preserve current behavior
- repair the exact contract surface
- avoid broad rewrite unless validation proves a deeper issue

## Escalation rules

1. Read the canonical report first.
2. Trust required command evidence over optimistic summaries.
3. If `ExitCode` / `Result` conflicts with the required command evidence, treat the run as a wrapper/reporting problem until proven otherwise.
4. If the failure report does not preserve the failing command’s stdout/stderr, prefer a capture-first rerun.
5. If the content is already correct, prefer Verification-only rerun over blind full reapply.
6. If the wrapper layer is clearly what failed, prefer Wrapper-only repair over widening the patch.
7. Escalate to broader redesign only when repeated evidence shows a real missing reusable surface.

## Why runner-hidden evidence matters

A failure report that hides the real failing step is not a trustworthy final artifact.

If the report only shows a null-valued expression, a helper crash, or a top-level wrapper exception, the next repair should focus on restoring evidence capture before widening the scope of the actual feature work.

## Practical reminders

- Keep PowerShell thin.
- Keep reusable logic in Python.
- Preserve one canonical report per run.
- Prefer narrow validation and repair over redesign.
- Use current repo files, tests, handoff surfaces, and reports as the source of truth.
- Keep the wrapper boring.


Use verify-only when the patch content is already correct and the goal is only to rerun validation and evidence without rewriting files.
