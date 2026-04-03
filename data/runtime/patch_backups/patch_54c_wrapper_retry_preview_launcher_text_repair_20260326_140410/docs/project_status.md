# PatchOps project status

## Current state snapshot

This document distinguishes stable now from future work.

PatchOps is in late Stage 1 / pre-Stage 2 and should be treated as a maintained wrapper utility.

## Stable now

What is stable now and exists in the repo today:

- manifest loading and validation
- profile resolution
- deterministic reporting
- backup and write helpers
- apply / verify / inspect / check / plan flows
- verification-only reruns
- wrapper-vs-target failure separation
- cleanup and archive workflow support
- example manifests
- documentation handoff surface

## Exists in the repo today

The current stable surface includes the trader, generic_python, and generic_python_powershell profiles plus the PowerShell launchers and bundled example manifests.

Patch 41 extended the mixed-profile surface.
Patch 48 added the formal initial milestone gate.

## Future work, not yet shipped behavior

This section is about future work, not yet shipped behavior.

Possible future work includes richer profiles, stronger dry-run introspection, richer summaries, broader language/repo support, and stronger fixture repos.

## What remains future work rather than current behavior

What remains future work rather than current behavior should be treated as additive enhancement work, not evidence that the initial product failed.

## Git / traceability note

A missing .git directory or unavailable Git metadata should be treated as a traceability / environment hygiene warning.

It should not be mistaken for evidence that the PatchOps core is broken.

## Repairability note

The stable surface also includes wrapper-only retry classification support so narrow reruns stay explicit and auditable.

## Verification launcher note

Use `powershell/Invoke-PatchVerify.ps1` when the right move is a narrow verification rerun rather than a full apply rerun.

## CLI visibility note

Useful stable discovery surfaces include:

- `patchops.cli profiles`
- `patchops.cli examples`
- `patchops.cli doctor --profile trader`

<!-- PATCHOPS_PATCH51_WRAPPER_RETRY_PLAN_STATUS:START -->
## Stage 2 note: Patch 51

Patch 51 begins the first intentional Stage 2 wave with a wrapper-only retry planning surface.

A future operator or LLM can now preview a narrow wrapper-only retry with:

- `py -m patchops.cli plan <manifest> --mode wrapper_retry --retry-reason "..."`

This is a planning and inspection surface only.
The dedicated thin PowerShell launcher is intentionally reserved for the next patch.
<!-- PATCHOPS_PATCH51_WRAPPER_RETRY_PLAN_STATUS:END -->

<!-- PATCHOPS_PATCH52_WRAPPER_RETRY_LAUNCHER_STATUS:START -->
## Stage 2 note: Patch 52

Patch 52 adds the thin wrapper-only retry launcher:

- `powershell/Invoke-PatchWrapperRetry.ps1`

It supports preview-first operation through the Stage 2 wrapper-only retry planning surface and keeps the recovery logic Python-owned.
<!-- PATCHOPS_PATCH52_WRAPPER_RETRY_LAUNCHER_STATUS:END -->

<!-- PATCHOPS_PATCH53_WRAPPER_RETRY_REPORT_STATUS:START -->
## Stage 2 note: Patch 53

Patch 53 makes wrapper-only retry unmistakable in the canonical report.

The report now includes a dedicated `WRAPPER-ONLY RETRY` section so the evidence artifact itself records retry kind, retry reason, writes-skipped state, target counts, and escalation state.
<!-- PATCHOPS_PATCH53_WRAPPER_RETRY_REPORT_STATUS:END -->

<!-- PATCHOPS_PATCH53B_WRAPPER_RETRY_IMPORT_REPAIR:START -->
## Stage 2 note: Patch 53B repair

Patch 53B repairs an import cycle introduced while adding wrapper-only retry report sections.

The reporting surface from Patch 53 remains the same, but `patchops.workflows.wrapper_retry` now resolves verify-only helpers lazily so:

- report rendering can import cleanly,
- verify-only can still own the core execution path,
- and wrapper-only retry remains a narrow overlay rather than a second reporting stack.
<!-- PATCHOPS_PATCH53B_WRAPPER_RETRY_IMPORT_REPAIR:END -->

<!-- PATCHOPS_PATCH53C_VERIFY_ALIAS_REPAIR:START -->
## Patch 53C note

Patch 53C repairs the wrapper-only retry execution surface after Patch 53B.

The narrow import-cycle repair in Patch 53B removed the module-level `verify_only` symbol that an existing wrapper-retry test monkeypatches.
Patch 53C restores that compatibility point while keeping the lazy-import behavior that avoids the earlier circular import.
<!-- PATCHOPS_PATCH53C_VERIFY_ALIAS_REPAIR:END -->

<!-- PATCHOPS_PATCH53D_WRAPPER_ONLY_RETRY_MODE_LABEL_REPAIR:START -->
## Patch 53D note

Patch 53D repairs the wrapper-only retry workflow result label.

`execute_wrapper_only_retry(...)` now relabels delegated verify results to `wrapper_only_retry`, matching the workflow intent and the existing test surface.
<!-- PATCHOPS_PATCH53D_WRAPPER_ONLY_RETRY_MODE_LABEL_REPAIR:END -->

<!-- PATCHOPS_PATCH54_WRAPPER_RETRY_TESTS_STATUS:START -->
## Stage 2 note: Patch 54

Patch 54 hardens the wrapper-only retry test surface so the contract stays enforceable:

- writes stay skipped,
- reason normalization stays explicit,
- missing expected files escalate,
- wrapper-only retry stays distinct from verify-only,
- and the launcher/preview path stays aligned with the Python-owned rerun surface.
<!-- PATCHOPS_PATCH54_WRAPPER_RETRY_TESTS_STATUS:END -->

<!-- PATCHOPS_PATCH54B_WRAPPER_RETRY_PREVIEW_FIX:START -->
## Patch 54B note

Patch 54B repairs the thin wrapper-only retry launcher so it exposes `-Preview` and forwards preview requests into `patchops.cli plan --mode wrapper_retry` instead of forcing operators to compose that command manually.

This keeps the launcher aligned with Stage 2 retry-plan semantics while still leaving recovery logic in Python.
<!-- PATCHOPS_PATCH54B_WRAPPER_RETRY_PREVIEW_FIX:END -->
