# Repair guidance

This document explains the maintained repair-choice guidance after failure classification is stable.

## Repair choice guide

Use the classified evidence from the canonical report, the handoff bundle, and the maintained helper-owned fields.

### Use verify-only rerun when

- the failure class is `wrapper_failure`,
- expected target files already exist,
- target content likely succeeded,
- and the narrow goal is to re-check and re-evidence existing target files.

### Use wrapper-only repair or retry when

- the failure class is `wrapper_failure`,
- content likely succeeded or partially succeeded,
- verify-only is not the right narrow path,
- and the wrapper/report/launcher mechanics need recovery without widening into a full content repair.

### Repair target content when

- the failure class is `target_project_failure`,
- required validation failed for real target reasons,
- or verify-only surfaced a real content defect.

### Stop because the run is suspicious when

- the failure class is `ambiguous_or_suspicious_run`,
- evidence is contradictory,
- or the repo state is too unclear for a safe narrow rerun.

### Repair patch authoring when

- the failure class is `patch_authoring_failure`,
- the manifest, staged content, or patch packaging is malformed,
- and the target project should not be treated as the first repair surface.

## Maintained principle

Keep the repair narrow, follow the helper-owned classification, and continue patch by patch from evidence.
