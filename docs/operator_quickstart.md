# Operator Quickstart

## Purpose
This file is the fastest maintained reading surface for running PatchOps on the wrapper repo itself.

Repo root:
- `C:\dev\patchops`

## Current operator rule
Read the canonical report, not partial console output.

PatchOps now keeps one truthful outcome per run:
- fatal launcher stderr with no detected inner report is a failure
- if an inner report exists, it becomes the canonical report after outer context is merged
- do not treat a visually green outer wrapper layer as success when the inner path failed

## Fast health check
```powershell
& {
    Set-Location "C:\dev\patchops"
    py -m pytest -q
    py -m patchops.cli maintenance-gate
}
```

## Normal bundle workflow
```powershell
& {
    Set-Location "C:\dev\patchops"
    py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"
}
```

Expected behavior:
1. PatchOps extracts the zip.
2. PatchOps validates bundle shape and metadata before launcher execution.
3. PatchOps runs the bundled launcher through the maintained bundle-entry path.
4. PatchOps preserves one canonical Desktop txt report.

## Review surfaces before risky execution
Use these when the bundle is suspicious or newly authored:
- `py -m patchops.cli check-bundle <bundle-or-zip>`
- `py -m patchops.cli inspect-bundle <bundle-or-zip>`
- `py -m patchops.cli plan-bundle <bundle-or-zip>`
- `py -m patchops.cli bundle-doctor <bundle-or-zip>`

## Package-authoring preflight
The current bundle preflight rejects common authoring failures before launcher execution, including:
- malformed or incomplete `bundle_meta.json`
- missing staged content paths
- invalid generated Python helper files
- unsafe mixed-language prep helper patterns
- launcher shapes that drift away from the maintained thin launcher contract

Transport or demo bundles that do not advertise the full staged-authoring contract still retain the legacy compatibility path where appropriate.

## Generated-helper syntax gate
If a bundle carries generated Python helpers or generated tests, PatchOps syntax-checks them before launcher execution.
This is meant to fail early on authoring mistakes rather than produce late false-pass confusion.

## Emitted operator scripts
`emit-operator-script` is maintained for thin operator-facing scripts only.

Current expectations:
- scripts stay thin
- reusable mechanics stay in Python
- emitted/operator scripts should stay boring and thin

## If a run fails
1. Read the canonical Desktop txt report.
2. Identify the first failing layer.
3. Repair only that layer.
4. Continue patch by patch from evidence.
