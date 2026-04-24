# Failure repair guide

## Purpose

This document is the maintained operator guide for deciding what failed first.

## classification-guided repair choice

The guide uses classification-guided repair choice.

### Content failure
content failure / target_project_failure means the target-side change or expectation is wrong.

### Wrapper failure
wrapper failure means PatchOps or its wrapper mechanics failed.

### Verification-only rerun
writes are skipped and expected target files are re-checked.

### Wrapper-only repair
writes are skipped and expected target files are re-checked.

## Quick decision table

- Content failure -> repair content, not wrapper mechanics
- Wrapper failure -> repair wrapper, not target logic
- Verification-only rerun -> verify-only rerun
- Wrapper-only repair -> wrapper-only repair

## suspicious-run support

required command evidence contradicting the rendered summary is a suspicious-run case.
Other conservative suspicious-run cases should also be treated carefully.

## Main maintained classes

- target_project_failure
- wrapper_failure
- suspicious_run

## Wrapper boundary and launcher artifacts

Use the repair guide to keep the boundary explicit: wrapper failure versus target-content failure.

PatchOps should remain a wrapper and reporting layer, not a second apply engine.

Launcher artifacts are part of the operator surface and should be treated as maintained evidence carriers, not throwaway glue. A concrete example is stray leading characters in `run_with_patchops.ps1`, which can make the launcher fail before the real validation target is even reached.

Current operator-visible launcher and helper surfaces include:
- `emit-operator-script`
- `maintenance-gate`
- `Push-PatchOpsToGitHub.ps1`

When these surfaces drift, repair the wrapper/operator layer first, then rerun the narrowest truthful proof.
- Distinguish wrapper failure versus target-content failure before retrying.
- `bootstrap-repair` is not a second apply engine.
- Watch for stray leading characters in `run_with_patchops.ps1`.
- `emit-operator-script`, `maintenance-gate`, and `Push-PatchOpsToGitHub.ps1` are maintained operator surfaces.
- Distinguish wrapper failure versus target-content failure before widening the investigation.
- Watch for stray leading characters in `run_with_patchops.ps1` and other launcher artifacts.
- `emit-operator-script`, `maintenance-gate`, and `run-package` are maintained operator-support surfaces.

## Escalation rules
1. Identify the first failing layer.
2. Repair only that layer.
3. Preserve wrapper failure versus target-content failure classification.
4. Escalate only after the current layer is green.
Use the `ExitCode` / `Result` pair together when deciding what failed first.
What failed, and what is the narrowest trustworthy recovery path?

## classification-guided repair choice
- verify-only
- wrapper-only repair
- repair target content
- target_project_failure
- wrapper_failure
- patch_authoring_failure

## suspicious-run support
This is a wrapper health aid.
Conservative suspicious-run cases include:
- required command evidence contradicting the rendered summary
- critical provenance fields missing after wrapper execution

## Targeted suspicious-run additions
ambiguous_or_suspicious_run
not a target-content feature
copied latest-report surface missing after a handoff export path

<!-- PATCHOPS_E5_FAILURE_REPAIR_SUSPICIOUS_SUPPORT_LOCK_20260423 -->
## Suspicious-run support addendum

starts opt-in

report structure missing required core fields

<!-- PATCHOPS_E5A_SUSPICIOUS_RUN_MACHINE_AID_LOCK_20260423 -->
## Suspicious-run support addendum

starts opt-in
read it as a small machine-readable aid
required command evidence contradicting the rendered summary
critical provenance fields missing after wrapper execution
copied latest-report surface missing after a handoff export path
report structure missing required core fields
