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
- profile notes for humans and future LLMs

## Why profiles exist

The wrapper must stay generic.

Target repos differ in:

- expected root location
- virtual environment layout
- report naming preference
- backup-root convention
- common runtime assumptions

Those differences belong in profiles rather than being hardcoded into the execution core.

## Profile discovery command

PatchOps now exposes a first-class profile discovery command:

```powershell
py -m patchops.cli profiles
py -m patchops.cli profiles --name trader
```

The output is JSON so it is easy for:

- humans to inspect
- future LLMs to consume
- documentation to quote precisely

The thin PowerShell launcher is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1 -Name trader
```

## Rule

Trader is the first profile, not the identity of the system.
The core must remain project-agnostic.