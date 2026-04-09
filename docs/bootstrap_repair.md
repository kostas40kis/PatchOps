# Bootstrap repair

## Purpose
`bootstrap-repair` is a narrow recovery surface for the specific case where normal PatchOps use is blocked by a small file-level break such as a syntax error or import-chain break.

This is **not** a second apply engine. In plain terms, this surface is not a second apply engine.
It is a maintenance helper for restoring one or a few known file paths, optionally validating those repaired Python files with `py_compile`, and then returning the operator to the normal PatchOps workflow.

## Preferred direct recovery entrypoint
Use the direct module when you do not trust the full `patchops.cli` import chain:

`py -m patchops.bootstrap_repair C:\temp\bootstrap_payload --target-root "C:\dev\patchops" --path patchops\operator_scripts.py --py-compile-path patchops\operator_scripts.py`

## CLI convenience entrypoint
If the normal CLI is still bootable, the repo also exposes a matching command surface:

`py -m patchops.cli bootstrap-repair C:\temp\bootstrap_payload --target-root "C:\dev\patchops" --path patchops\operator_scripts.py --py-compile-path patchops\operator_scripts.py`

## Payload shape
The payload root should contain replacement files in target-relative shape.

Example payload:

```text
C:\temp\bootstrap_payload\
  patchops\operator_scripts.py
```

## What the helper does
1. restores the requested relative file paths from the payload root,
2. backs up any pre-existing target files under `data/runtime/bootstrap_repairs/...`,
3. optionally runs `py_compile` against the repaired Python file paths,
4. prints one machine-readable JSON payload,
5. tells the operator to return to the normal PatchOps workflow.

## Scope guardrails
- Keep the restored path set intentionally small.
- Prefer this only for bootability repair, not routine patch application.
- Return to the maintained PatchOps flow as soon as recovery succeeds.
- Treat this surface as exceptional and narrow.
