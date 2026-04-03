# PatchOps

PatchOps is a standalone, project-agnostic patch execution harness.

It is **not** the trader engine, target-repo business logic, strategy logic, or portfolio logic. It exists to standardize the repetitive mechanics around patch application and evidence generation across repositories.

Core intent:

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
- apply, verify-only, inspect, and plan flows
- thin PowerShell launchers
- examples and harness tests

## Safe first proving sequence

Before touching a real target repo, prove the wrapper in this order:

1. inspect a generic manifest
2. plan a generic manifest
3. apply a generic manifest to a throwaway repo
4. apply the generic backup-proof manifest
5. verify the same throwaway repo
6. only then inspect/plan trader-profile manifests

## Thin PowerShell entrypoints

PatchOps now exposes these thin launcher scripts under `powershell\`:

- `Invoke-PatchInspect.ps1`
- `Invoke-PatchPlan.ps1`
- `Invoke-PatchManifest.ps1`
- `Invoke-PatchVerify.ps1`

These scripts are intentionally small. They only resolve the wrapper root, choose `py` or `python`, and forward to `patchops.cli`.

See `docs/` for architecture and usage details.