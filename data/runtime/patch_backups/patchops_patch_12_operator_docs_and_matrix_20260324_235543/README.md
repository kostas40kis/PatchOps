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

It helps the trader repo first, but the core remains project-agnostic.

## Core design rules

- keep **what a patch changes** separate from **how a patch is executed and evidenced**
- use an explicit **manifest** as the central contract
- resolve repo-specific behavior through **profiles**
- keep **PowerShell thin** and place reusable logic in Python
- produce **one canonical report** per run with explicit runtime, roots, backups, commands, stdout/stderr, and final summary

## Safe first proving sequence

Before touching a real target repo, prove the wrapper in this order:

1. inspect a generic manifest
2. list available profiles
3. generate a starter manifest template for the chosen profile
4. optionally write that template directly to a JSON file
5. inspect the saved template
6. check the saved template for placeholders before using it
7. plan a generic manifest
8. apply a generic manifest to a throwaway repo
9. apply the generic backup-proof manifest
10. verify the same throwaway repo
11. only then inspect/plan trader-profile manifests

## Thin PowerShell entrypoints

PatchOps exposes these thin launcher scripts under `powershell\`:

- `Invoke-PatchInspect.ps1`
- `Invoke-PatchPlan.ps1`
- `Invoke-PatchManifest.ps1`
- `Invoke-PatchVerify.ps1`
- `Invoke-PatchProfiles.ps1`
- `Invoke-PatchTemplate.ps1`
- `Invoke-PatchCheck.ps1`

`Invoke-PatchTemplate.ps1` supports `-OutputPath` so a starter manifest can be written directly to disk instead of only printing to stdout.

`Invoke-PatchCheck.ps1` makes the pre-apply manifest review path explicit by surfacing likely placeholder values before `plan` or `apply`.

## Discovering profiles before writing manifests

List all profiles:

```powershell
py -m patchops.cli profiles
```

Generate a template to stdout:

```powershell
py -m patchops.cli template --profile trader --mode apply --patch-name trader_template
```

Generate a template directly to a file:

```powershell
py -m patchops.cli template --profile generic_python --mode verify --patch-name generic_verify_template --output-path .\data\runtime\generated_templates\generic_verify_template.json
```

Check the written manifest for starter placeholders:

```powershell
py -m patchops.cli check .\data\runtime\generated_templates\generic_verify_template.json
```

Then review it with:

```powershell
py -m patchops.cli inspect .\data\runtime\generated_templates\generic_verify_template.json
```

## Doctor command

Use `py -m patchops.cli doctor --profile trader` before template, check, or apply when you want a quick environment and profile readiness snapshot. The command reports the requested profile, visible profiles, working directory, workspace guess, desktop availability, Python/PowerShell discovery, target-root resolution, and any issues.

## Bundled example manifest discovery

PatchOps now includes an `examples` command so a future LLM or operator can discover bundled starter manifests before generating a new one.

Typical discovery-first flow:

1. `py -m patchops.cli profiles`
2. `py -m patchops.cli doctor --profile trader`
3. `py -m patchops.cli examples`
4. `py -m patchops.cli template --profile trader --mode apply`
5. `py -m patchops.cli check <manifest>`
6. `py -m patchops.cli inspect <manifest>`
7. `py -m patchops.cli plan <manifest>`
8. `py -m patchops.cli apply <manifest>`
