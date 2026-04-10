# PatchOps

PatchOps is a standalone wrapper and patch-execution toolkit for applying, verifying, packaging, and evidencing changes without turning the wrapper into target-project business logic.

## Current operating contract

- PatchOps remains the wrapper, not target-project logic.
- PowerShell stays thin and operator-facing.
- Reusable workflow mechanics should live in Python.
- Every normal run should resolve to one canonical truth in one canonical report.
- Suspicious-success patterns are blocked rather than reported as success.
- Development stays code-first and documentation-last.

## Maintained command inventory

The maintained command inventory includes:

- `check`
- `inspect`
- `plan`
- `apply`
- `verify`
- `check-bundle`
- `run-package`

Bundle-native behavior is additive and should not silently break classic manifest-driven flows.

## Canonical report truth rules

PatchOps preserves one canonical truth rule:

- fatal setup or launcher failure must not resolve to PASS,
- missing inner-report evidence must not be hidden by a green outer artifact,
- suspicious-success patterns must be blocked,
- and the canonical report must match the effective result.

## Future-LLM continuity

The maintained future-LLM upload artifact and source bundle should describe the real modular package layout rather than stale flat-file assumptions.
