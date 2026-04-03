# PatchOps Examples

PatchOps examples exist for two different purposes:

1. real example manifests you can inspect or apply safely
2. starter template commands that generate new manifests for you

## Included example manifests

### `examples\generic_python_patch.json`
Use this for the first safe apply proof against a throwaway repo such as `C:\dev\some_other_project`.

### `examples\generic_backup_patch.json`
Use this after the first generic apply to prove that backup behavior is explicit when the target file already exists.

### `examples\generic_verify_patch.json`
Use this to prove verify-only flow against the same throwaway repo.

### `examples\trader_code_patch.json`
Trader-profile example for inspect / plan review.

### `examples\trader_doc_patch.json`
Documentation-oriented trader example.

### `examples\trader_verify_patch.json`
Trader verify-only example for narrow rerun behavior.

## Safe proving sequence

Before touching trader, use this order:

1. `inspect` a generic example
2. `profiles`
3. `template`
4. `plan` a generic example
5. `apply` the generic example
6. `apply` the generic backup example
7. `verify` the generic verify example
8. only then inspect or plan trader examples

## Template generation examples

### Trader apply starter

```powershell
py -m patchops.cli template --profile trader --mode apply --patch-name trader_patch_draft
```

### Generic verify starter

```powershell
py -m patchops.cli template --profile generic_python --mode verify --patch-name generic_verify_draft
```

### Launcher form

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchTemplate.ps1 -Profile trader -Mode apply -PatchName trader_patch_draft
```

Remember: templates are scaffolds. Replace placeholder paths, placeholder content, and starter commands before running `apply`.