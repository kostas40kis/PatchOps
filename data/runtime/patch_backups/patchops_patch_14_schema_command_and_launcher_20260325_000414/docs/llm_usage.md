# LLM usage

A future LLM should normally use PatchOps in this order:

1. `profiles`
2. `template`
3. if useful, `template --output-path ...`
4. `check`
5. `inspect`
6. `plan`
7. `apply` or `verify`
8. review the one canonical Desktop txt report

## Example flow

### Discover the available profiles

```powershell
py -m patchops.cli profiles
```

### Scaffold a trader apply template to stdout

```powershell
py -m patchops.cli template --profile trader --mode apply --patch-name trader_patch_template
```

### Scaffold a generic verify template directly to disk

```powershell
py -m patchops.cli template --profile generic_python --mode verify --patch-name generic_verify_template --output-path .\data\runtime\generated_templates\generic_verify_template.json
```

### Check the saved manifest before using it

```powershell
py -m patchops.cli check .\data\runtime\generated_templates\generic_verify_template.json
```

### Inspect the saved manifest before using it

```powershell
py -m patchops.cli inspect .\data\runtime\generated_templates\generic_verify_template.json
```

### Preview what would happen

```powershell
py -m patchops.cli plan .\examples\generic_backup_patch.json
```

### Run verify-only flow

```powershell
py -m patchops.cli verify .\examples\generic_verify_patch.json
```

## Why `check` matters

Starter templates are intentionally explicit, but they still contain placeholder values. `check` gives the next LLM or human operator a simple gate that says whether the manifest still looks like scaffolding instead of real patch intent.

## Doctor first

Recommended discovery flow for a fresh session: `profiles`, `doctor`, `template`, edit manifest, `check`, `inspect`, `plan`, then `apply` or `verify`. `doctor` gives the next LLM a fast readiness snapshot before it starts writing manifests.

## Use bundled examples before generating a new manifest

Before generating a new manifest from scratch, list the bundled examples with:

- `py -m patchops.cli examples`
- `powershell\Invoke-PatchExamples.ps1`

This gives a future LLM a quick inventory of realistic manifests that already match supported profiles.

## Recommended operator flow

When you are using PatchOps as a future LLM, prefer this order:

1. `profiles`
2. `doctor`
3. `examples`
4. `template`
5. edit the manifest
6. `check`
7. `inspect`
8. `plan`
9. `apply` or `verify`

This keeps manifest generation explicit and reduces wrapper-only failure loops.
