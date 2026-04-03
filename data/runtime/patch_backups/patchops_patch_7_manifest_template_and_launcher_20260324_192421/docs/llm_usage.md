# LLM Usage

Future LLMs should treat PatchOps as a wrapper that standardizes execution mechanics, not as a place to move target-repo business logic.

## Recommended flow

For a new patch task:

1. read the relevant docs
2. list available profiles
3. choose the active profile
4. inspect the manifest
5. plan the manifest
6. apply only when the preview looks correct
7. verify or rerun narrowly when the patch content is already in place

## Preferred safe command sequence

### CLI form

```powershell
py -m patchops.cli profiles
py -m patchops.cli profiles --name trader
py -m patchops.cli inspect .\examples\generic_python_patch.json
py -m patchops.cli plan .\examples\generic_python_patch.json
py -m patchops.cli apply .\examples\generic_python_patch.json
py -m patchops.cli apply .\examples\generic_backup_patch.json
py -m patchops.cli verify .\examples\generic_verify_patch.json
```

### Thin PowerShell launcher form

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1 -Name trader
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchInspect.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchPlan.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchManifest.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchVerify.ps1 -ManifestPath .\examples\generic_verify_patch.json
```

## Why profile discovery should come early

`profiles` shows the supported profile names and their default assumptions before a manifest is generated.

That means a future LLM can discover the available target shapes before guessing at:

- profile names
- default roots
- runtime location patterns
- report prefixes
- backup-root conventions

## Why inspect and plan should still come before apply

`inspect` proves that the manifest is valid and normalized.

`plan` proves the resolved profile, target root, report naming pattern, backup-root pattern, target files, and command groups before any file write happens.

That means a future LLM can review exactly what would happen before using `apply`.

## Scope discipline

PatchOps owns:

- manifest-driven execution
- profile resolution
- profile discovery
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