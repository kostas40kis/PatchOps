# PatchOps

PatchOps is a standalone wrapper / harness project for manifest-driven patch execution.

It exists to standardize the repetitive mechanics that keep getting rebuilt across projects:

- repo-root resolution
- runtime / interpreter selection
- backup creation
- deterministic file writing
- command execution
- stdout/stderr capture
- one-report evidence generation
- verification-only reruns
- wrapper-only repair discipline

PatchOps is **not** target-repo business logic.

It should help the trader repo first, but the core remains project-agnostic.

## Core design rules

- keep **what a patch changes** separate from **how a patch is executed and evidenced**
- use an explicit **manifest** as the central contract
- resolve repo-specific behavior through **profiles**
- keep **PowerShell thin** and place reusable logic in Python
- produce **one canonical report** per run with explicit runtime, roots, backups, commands, stdout/stderr, and final summary

Stage 1 ships a usable first version with:

- manifest loading and validation
- profile resolution
- trader and generic Python profiles
- deterministic backups and file writing
- process execution with stdout/stderr capture
- human-readable report rendering
- apply, verify-only, inspect, plan, and profiles flows
- thin PowerShell launchers
- examples and harness tests

## Safe first proving sequence

Before touching a real target repo, prove the wrapper in this order:

1. inspect a generic manifest
2. list available profiles
3. plan a generic manifest
4. apply a generic manifest to a throwaway repo
5. apply the generic backup-proof manifest
6. verify the same throwaway repo
7. only then inspect/plan trader-profile manifests

## Thin PowerShell entrypoints

PatchOps now exposes these thin launcher scripts under `powershell\`:

- `Invoke-PatchInspect.ps1`
- `Invoke-PatchPlan.ps1`
- `Invoke-PatchManifest.ps1`
- `Invoke-PatchVerify.ps1`
- `Invoke-PatchProfiles.ps1`

These scripts are intentionally small. They only resolve the wrapper root, choose `py` or `python`, and forward to `patchops.cli`.

## Discovering profiles before writing manifests

Use the CLI:

```powershell
py -m patchops.cli profiles
py -m patchops.cli profiles --name trader
```

Or use the thin launcher:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchProfiles.ps1 -Name trader
```

This makes it easier for future LLMs and humans to discover:

- which profiles exist
- default target-root assumptions
- runtime path assumptions
- backup-root conventions
- report prefixes
- one-report discipline defaults

See `docs/` for architecture and usage details.