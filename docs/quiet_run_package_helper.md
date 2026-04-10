# Canonical run-package operator runner

## Purpose

`Invoke-QuietRunPackage.ps1` is the single canonical operator-facing PowerShell runner for applying a patch bundle through PatchOps.

It keeps the live console short and practical while preserving the full canonical Desktop txt report as the real proof artifact.

## Operator posture

- Use `Invoke-QuietRunPackage.ps1` as the canonical runner.
- Keep `Invoke-RunPackage.ps1` only as a compatibility shim for older habits.
- Do not treat the compatibility shim as a second supported runner.
- Keep PowerShell thin and keep reusable mechanics in Python.
- Preserve one canonical Desktop txt report per run.

## Output behavior

The canonical runner prints only a short summary:

- patch name,
- result,
- exit code,
- failure category when present,
- report path.

Use `-PassThruRawOutput` only when you intentionally want the full raw stdout and stderr for debugging.

## Usage

```powershell
.\powershell\Invoke-QuietRunPackage.ps1 -PackagePath "D:\some_patch_bundle.zip" -WrapperRepoRoot "C:\dev\patchops"
```

## Compatibility

`Invoke-RunPackage.ps1` remains as a compatibility shim that delegates directly to `Invoke-QuietRunPackage.ps1`.

That keeps old commands from breaking while leaving only one canonical operator-facing runner.
