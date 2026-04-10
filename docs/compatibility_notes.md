# Compatibility notes

## Windows PowerShell 5.1

PatchOps must remain compatible with Windows PowerShell 5.1 where the project still depends on it as an operator boundary.

Important current rule:

- do **not** rely on `ProcessStartInfo.ArgumentList` in Windows PowerShell 5.1 helper scripts,
- prefer `ProcessStartInfo.Arguments` with a compatibility-safe argument-string builder.

This matters because standalone helper scripts can reintroduce old bugs even when the core repo has already been repaired.

## Saved launcher shape

Saved PowerShell launchers should preserve a normal top-level `param(...)` script-file shape.

The canonical root launcher contract also now requires:

- the launcher begins directly with `param(` on the first line,
- there is no stray leading character before `param(...)`,
- the launcher delegates to bundle-entry instead of becoming a second workflow engine.

## Report discipline

Compatibility work should still preserve one canonical Desktop txt report per run.

That report is the evidence artifact operators and future LLMs should trust first.

## Design compatibility rules

- keep PowerShell thin,
- keep reusable mechanics in Python,
- prefer narrow compatibility repair over widening scope,
- do not move target-project business logic into PatchOps.

## Operator reminder

If a patch fails, repair the first failing layer only.
Do not widen scope just because the repo is already open.
