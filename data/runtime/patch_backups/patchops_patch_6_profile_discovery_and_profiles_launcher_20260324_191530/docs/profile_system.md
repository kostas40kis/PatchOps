# Profile System

Profiles isolate target-repo assumptions from the PatchOps core.

## Stage 1 profiles

- `trader`
- `generic_python`
- `generic_python_powershell`

## A profile can define

- default target root
- runtime path resolution
- backup root convention
- report prefix
- evidence discipline defaults

## Rule

Trader is the first profile, not the identity of the system.
The core must remain project-agnostic.
