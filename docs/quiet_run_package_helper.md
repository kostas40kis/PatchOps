# Quiet run-package helper

`Invoke-QuietRunPackage.ps1` is the single canonical operator-facing helper for `run-package` when you want less live console noise but still want one canonical Desktop txt report.

It exists alongside the older `Invoke-RunPackage.ps1`, which is now only a compatibility shim.

## Why this helper exists

Use this helper when you want:

- `run-package` behavior with less live console noise
- a stable summary surface after the run
- the report path treated as the source of truth
- a thin PowerShell entrypoint that does not reinterpret PatchOps results

## Maintained operator model

- `Invoke-QuietRunPackage.ps1` is the single canonical operator-facing helper.
- `Invoke-RunPackage.ps1` remains a compatibility shim only.
- Keep PowerShell thin.
- Keep reusable mechanics in Python.
- Keep one canonical Desktop txt report.

## What the helper surfaces

The helper runs `patchops.cli run-package`, then prints a compact summary including:

- patch name
- result
- exit code
- failure category
- report path

When PatchOps prints a canonical report path or report path in stdout, treat that path as the source of truth.

## Copy-paste-safe usage

```powershell
Set-Location C:\dev\patchops
.\powershell\Invoke-QuietRunPackage.ps1 -PackagePath "D:\some_patch_bundle.zip" -WrapperRepoRoot "C:\dev\patchops"
```

Optional switches:

- `-PassThruRawOutput`
- `-VerboseConsole`

## Boundary note

Keep PowerShell thin. The helper is an operator-facing shim, not a second implementation of PatchOps package execution.
Treat the canonical report as the final source of truth.
The quiet helper is a compatibility shim around the maintained runner path.
