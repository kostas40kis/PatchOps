# PatchOps LLM Usage

This document explains how a future coding LLM should use PatchOps without guessing.

## Read these first

1. `README.md`
2. `docs/profile_system.md`
3. `docs/examples.md`
4. `docs/project_status.md`

Read `docs/trader_profile.md` before working against `C:\dev\trader`.

## Recommended working order

When starting fresh, do this in order:

1. discover available profiles
2. choose the active profile
3. generate a starter manifest template
4. fill in the target files and commands
5. inspect the manifest
6. plan the manifest
7. decide between apply and verify-only
8. run the wrapper
9. inspect the single canonical report

## Discover profiles first

```powershell
py -m patchops.cli profiles
py -m patchops.cli profiles --name trader
```

This tells you:

- which profiles exist
- whether a profile has a default target root
- whether a profile has a runtime path expectation
- the report prefix convention
- whether strict one-report behavior is expected

## Generate a starter manifest template

Do not begin by hand-authoring large manifests from memory when a profile-aware starter can be generated first.

```powershell
py -m patchops.cli template --profile trader --mode apply --patch-name trader_patch_draft
py -m patchops.cli template --profile generic_python --mode verify --patch-name generic_verify_draft
```

Or through PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchTemplate.ps1 -Profile trader -Mode apply -PatchName trader_patch_draft
```

The output is intentionally conservative:

- placeholder relative file paths
- a starter validation command
- explicit report preferences
- profile-driven default target root when available
- mode-specific structure for apply vs verify-only

You must still replace placeholder values before treating the manifest as real work.

## Inspect and plan before apply

```powershell
py -m patchops.cli inspect .\examples\trader_code_patch.json
py -m patchops.cli plan .\examples\trader_code_patch.json
```

Use `plan` when you want to confirm:

- target root
- runtime path
- report path pattern
- backup path pattern
- target files
- command groups

## Decide between apply and verify-only

Use `apply` when the manifest should write files and then validate them.

Use `verify` when the patch contents already exist and you only need a narrow rerun of verification / validation behavior.

That distinction matters because wrapper-only failures should be repaired narrowly whenever possible.

## Keep PatchOps generic

Do not move target-repo business logic into PatchOps just because it is convenient.

PatchOps owns:

- manifest execution
- profile resolution
- backups
- file writing
- process execution
- output capture
- report generation
- wrapper failure classification
- rerun / verify-only behavior

Target repos still own:

- architecture
- business logic
- tests
- domain safety rules
- patch semantics

## What a good run looks like

A good run has one report that clearly shows:

- workspace root
- wrapper project root
- target project root
- active profile
- runtime path
- backup root
- report path
- files targeted
- backups performed or missing-file honesty
- commands run
- full stdout/stderr
- final `ExitCode` and `Result`