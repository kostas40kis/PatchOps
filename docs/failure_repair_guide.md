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
