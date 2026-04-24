# Bundle contract packet

## Purpose

This is the maintained **LLM-facing** bundle contract packet.
A fresh LLM should be able to author a correct bundle using only this packet.

## Exact bundle tree

```text
good_example_bundle/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
```

The exact bundle tree is the maintained shape.
Archive the bundle root contents directly.
Do not manually invent zip layout by hand.

## Exact launcher rule

- `run_with_patchops.ps1` is the maintained launcher path.
- The saved launcher is the bundle-entry surface.
- The saved launcher should keep the top-level `param(...)` script-file form.
- Do not hand-author the saved root launcher; emit it from Python.

## Metadata fields

Required maintained metadata fields:
- `schema_version`
- `patch_name`
- `bundle_mode`
- `recommended_profile`
- `target_project`
- `target_project_root`
- `manifest_path`
- `content_root`
- `launcher_path`

## Maintained command order

Use these commands in order:
- `make-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

continue patch by patch from evidence

## Guardrails

Keep PowerShell thin.
Keep reusable mechanics in Python.
Keep one canonical Desktop txt report.
Command/doc alignment proof should remain part of the maintained contract.

## One good example

```text
good_example_bundle/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
```

Example metadata fragment:

```json
{
  "launcher_path": "run_with_patchops.ps1"
}
```

## One bad example

```text
bad_example_bundle/
  manifest.json
  bundle_meta.json
  README.txt
  apply_with_patchops.ps1
  verify_with_patchops.ps1
  content/
```

## What not to do

- Do not create multiple launcher variants.
- Do not manually invent zip layout by hand.
- Do not skip `bundle-doctor`.
- Do not widen PowerShell into a second workflow engine.

## Documented command inventory

The maintained command/doc alignment proof should keep this documented command inventory visible:
- `check`
- `inspect`
- `plan`
- `apply`
- `verify`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `make-bundle`
- `build-bundle`
- `make-proof-bundle`
- `run-package`
- `bundle-entry`
- `maintenance-gate`
- `emit-operator-script`
- `bootstrap-repair`

<!-- PATCHOPS_E2_BUNDLE_CONTRACT_PACKET_COMPATIBILITY_SHIM_LOCK_20260423 -->
## Compatibility shim note

The maintained root launcher and bundle-entry story still preserve a compatibility shim for older transport or demo expectations when needed.
This does not replace the canonical `run_with_patchops.ps1` root-launcher contract; it explains how older expectations are bridged without changing the maintained bundle shape.

<!-- PATCHOPS_E2A_BUNDLE_PACKET_PATH_HYGIENE_PHRASE_LOCK_20260423 -->
stray leading `/` or `\` characters
