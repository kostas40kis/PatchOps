# Examples

See the `examples/` folder for Stage 1 manifests:

- `generic_python_patch.json`
- `generic_backup_patch.json`
- `generic_verify_patch.json`
- `trader_code_patch.json`
- `trader_doc_patch.json`
- `trader_verify_patch.json`

## Safe proving order

Use examples in this order:

1. `generic_python_patch.json`
   - safe first inspect/plan/apply run against a throwaway local project
2. `generic_backup_patch.json`
   - apply after the first generic patch to prove backup behavior before using trader-profile manifests
3. `generic_verify_patch.json`
   - proves verification-only flow without rewriting files
4. `trader_code_patch.json`
   - first trader-shaped example after the wrapper itself is already proven
5. `trader_doc_patch.json`
   - documentation-oriented trader example
6. `trader_verify_patch.json`
   - trader verify-only example

## Safe entrypoints before apply

Before a real apply run, prefer this sequence:

```powershell
py -m patchops.cli inspect .\examples\generic_python_patch.json
py -m patchops.cli plan .\examples\generic_python_patch.json
```

Equivalent thin launchers also exist:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchInspect.ps1 -ManifestPath .\examples\generic_python_patch.json
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\powershell\Invoke-PatchPlan.ps1 -ManifestPath .\examples\generic_python_patch.json
```

These examples are intentionally simple. They demonstrate manifest shape, profile selection, report structure, launcher parity, and how validation commands attach to a run.