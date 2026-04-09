# Operator quickstart

## Current maintained posture
PatchOps is in maintenance mode after the completed zip-first and Python-heavier streams. The default local workflow remains:

1. review or author a bundle,
2. run the bundle through `run-package`,
3. read the one canonical Desktop txt report,
4. continue only from report truth.

## Existing maintained recovery and operator helper surfaces
Keep using the already-maintained helper surfaces when they are the truthful fit for the situation:

- `py -m patchops.cli emit-operator-script ...`
- emitted script kinds such as `run-package-zip` and `maintenance-gate`
- `py -m patchops.cli bootstrap-repair ...`
- direct module recovery via `py -m patchops.bootstrap_repair ...`

When bootstrap recovery is needed because the normal CLI import path is broken, **Return to the normal `check` / `inspect` / `plan` / `apply` / `verify`** flow as soon as recovery succeeds.

## Optional GitHub publish helper
When the repo is already green locally and you have reviewed the final report, you can use the maintained helper script:

- `powershell/Push-PatchOpsToGitHub.ps1`

This helper is operator-facing and manual.
It is **not** an automatic post-patch step and it is **not** a second workflow engine.

### Example
```powershell
& {
    Set-Location "C:\dev\patchops"
    powershell -NoProfile -ExecutionPolicy Bypass -File ".\powershell\Push-PatchOpsToGitHub.ps1"
}
```

### What the helper does
- checks Git availability and configured identity,
- ensures or updates `origin`,
- stages the maintained PatchOps repo surfaces,
- applies local/runtime-safe `.gitignore` exclusions such as `data/runtime/`,
- removes a stale `.git\index.lock` when needed,
- commits,
- pushes to `main`.

### Compatibility note
The helper keeps Windows PowerShell 5.1 compatibility by using `ProcessStartInfo.Arguments` via `Convert-ToWindowsArgumentString` instead of relying on `ArgumentList`.
