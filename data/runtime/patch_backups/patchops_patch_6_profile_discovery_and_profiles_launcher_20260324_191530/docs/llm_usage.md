# LLM Usage

Future LLMs should treat PatchOps as a wrapper that standardizes execution mechanics, not as a place to move target-repo business logic.

## Recommended flow

For a new patch task:

1. read the relevant docs
2. choose the active profile
3. inspect the manifest
4. plan the manifest
5. apply only when the preview looks correct
6. verify or rerun narrowly when the patch content is already in place

## Preferred safe command sequence

### CLI form

```powershell
py -m patchops.cli inspect .\examples\generic_python_patch.json
py -m patchops.cli plan .\examples\generic_python_patch.json
py -m patchops.cli apply .\examples\generic_python_patch.json
py -m patchops.cli apply .\examples\generic_backup_patch.json
py -m patchops.cli verify .\examples\generic_verify_patch.json
```

### Thin PowerShell launcher form

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchInspect.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchPlan.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchManifest.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchVerify.ps1 -ManifestPath .\examples\generic_verify_patch.json
```

## Why inspect and plan should come first

`inspect` proves that the manifest is valid and normalized.

`plan` proves the resolved profile, target root, report naming pattern, backup-root pattern, target files, and command groups before any file write happens.

That means a future LLM can review exactly what would happen before using `apply`.

## Scope discipline

PatchOps owns:

- manifest-driven execution
- profile resolution
- backups
- file writing
- command execution
- canonical report rendering
- wrapper-only rerun and repair mechanics

Target repos still own:

- architecture
- business logic
- domain behavior
- safety policy
- test semantics
- patch meaning