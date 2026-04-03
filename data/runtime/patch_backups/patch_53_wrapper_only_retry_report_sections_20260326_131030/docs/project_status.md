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
