# LLM usage

A future LLM should normally use PatchOps in this order:

1. `profiles`
2. `template`
3. if useful, `template --output-path ...`
4. edit the generated manifest
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

### Inspect the saved manifest before using it

```powershell
py -m patchops.cli inspect .\data\runtime\generated_templates\generic_verify_template.json
```

### Preview what would happen

```powershell
py -m patchops.cli plan .\data\runtime\generated_templates\generic_verify_template.json --mode verify
```

### Run verify-only flow

```powershell
py -m patchops.cli verify .\data\runtime\generated_templates\generic_verify_template.json
```

## Why `--output-path` matters

Future LLMs often need a starter manifest they can immediately edit, save, inspect, and hand off. Writing the template straight to a file removes one manual copy/paste step while keeping the manifest explicit and reviewable.