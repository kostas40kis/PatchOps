# Run-package helper compatibility shim

`Invoke-RunPackage.ps1` is now only a compatibility shim.

The canonical operator-facing runner is `Invoke-QuietRunPackage.ps1`.

Use the canonical runner for new work:

```powershell
.\powershell\Invoke-QuietRunPackage.ps1 -PackagePath "D:\some_patch_bundle.zip" -WrapperRepoRoot "C:\dev\patchops"
```
