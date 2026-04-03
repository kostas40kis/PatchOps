# Safe first trader patch types

These are the recommended first real trader-facing PatchOps usage categories.

## Best first choices
- documentation-only patch
- validation-only patch
- report-only patch
- tiny non-domain code patch with existing tests
- manifest dry-run and verify-only rehearsals

## Avoid first
- complex multi-file architecture changes
- anything that touches live trading behavior
- large refactors
- anything that mixes trader safety policy into PatchOps
- large patch bundles where wrapper vs trader failure would be hard to separate

## Why this matters
The goal of the first trader-facing PatchOps run is not maximum project impact.
The goal is to prove that PatchOps can serve as the normal wrapper around a real trader repo change while preserving:
- explicit backups,
- deterministic reports,
- full stdout/stderr capture,
- clear failure classification.
