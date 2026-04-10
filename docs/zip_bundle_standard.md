# Zip bundle standard

## Purpose

This file describes the maintained PatchOps bundle shape after the post-publish refresh wave.

Use it when you need the exact zip layout, launcher rule, and review sequence for the modern bundle workflow.

## Maintained bundle tree

```text
<bundle-root>/
  manifest.json
  bundle_meta.json
  README.txt
  run_with_patchops.ps1
  content/
    ...
```

## Root launcher rule

- Use exactly one saved root launcher: `run_with_patchops.ps1`.
- Keep the saved launcher in top-level `param(...)` script-file form.
- Do not prepend stray leading `/` or `\` characters before `param(...)`.
- Do not hand-author the saved launcher when a Python helper is available.
- The root launcher is a thin compatibility shim that delegates to `bundle-entry` or the maintained manifest review/apply path.

## Maintained review sequence

Use the same maintained order every time:

1. `py -m patchops.cli make-bundle ...`
2. `py -m patchops.cli check-bundle ...`
3. `py -m patchops.cli inspect-bundle ...`
4. `py -m patchops.cli plan-bundle ...`
5. `py -m patchops.cli bundle-doctor ...`
6. `py -m patchops.cli build-bundle ...`
7. `py -m patchops.cli run-package ...`

## Packaging rule

Package the bundle root itself so the zip expands to one top-level bundle directory containing the maintained root files.

## Operator boundary

PowerShell stays thin and operator-facing.
Reusable mechanics stay in Python.
