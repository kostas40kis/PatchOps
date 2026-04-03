# Examples

## Existing example manifests

- `examples\generic_python_patch.json`
- `examples\generic_backup_patch.json`
- `examples\generic_verify_patch.json`
- `examples\trader_code_patch.json`
- `examples\trader_doc_patch.json`
- `examples\trader_verify_patch.json`

## Safe first-use sequence

1. `py -m patchops.cli inspect .\examples\generic_python_patch.json`
2. `py -m patchops.cli profiles`
3. `py -m patchops.cli template --profile generic_python --mode verify --output-path .\data\runtime\generated_templates\generic_verify_template.json`
4. `py -m patchops.cli check .\data\runtime\generated_templates\generic_verify_template.json`
5. `py -m patchops.cli inspect .\data\runtime\generated_templates\generic_verify_template.json`
6. `py -m patchops.cli plan .\examples\generic_backup_patch.json`
7. `py -m patchops.cli apply .\examples\generic_python_patch.json`
8. `py -m patchops.cli apply .\examples\generic_backup_patch.json`
9. `py -m patchops.cli verify .\examples\generic_verify_patch.json`

Only after that should you move on to trader-profile manifests.

## Doctor examples

`py -m patchops.cli doctor --profile trader` inspects the trader profile defaults. `powershell\Invoke-PatchDoctor.ps1 -Profile generic_python` provides the same information through the thin launcher entrypoint.

## Discover examples from the CLI

PatchOps includes an `examples` command that prints bundled example manifest metadata as JSON.

Examples:

- `py -m patchops.cli examples`
- `py -m patchops.cli examples --profile generic_python`
- `powershell\Invoke-PatchExamples.ps1 -Profile trader`

## Generic Python + PowerShell examples

PatchOps now ships two examples for the `generic_python_powershell` profile:

- `examples/generic_python_powershell_patch.json`
- `examples/generic_python_powershell_verify_patch.json`

Use these when the target repo should stay project-agnostic but your proving flow wants to show both Python validation and PowerShell-native smoke commands.
These examples are still inspection-first starter artifacts. Replace placeholder paths and commands before using them for real work.
