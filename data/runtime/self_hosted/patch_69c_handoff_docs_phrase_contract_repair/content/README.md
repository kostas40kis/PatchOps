# PatchOps

PatchOps is a project-agnostic patch execution harness for Windows-first patch workflows.

It keeps target-repo business logic separate from wrapper mechanics and standardizes:

- manifest-driven patch execution
- profile-aware defaults
- deterministic backups
- explicit file writes
- process execution with stdout/stderr capture
- canonical single-report evidence
- wrapper-vs-target failure separation
- narrow reruns such as verify-only and wrapper-only repair paths

## What PatchOps is not

PatchOps is not target-repo business logic.
It should not become trader strategy logic, application-domain logic, or target-side workflow ownership.

Trader is the first serious profile, not the identity of the wrapper.

## Consolidation status

PatchOps is now in late Stage 1 / pre-Stage 2 maintenance posture for the original buildout circle, and the handoff-first Stage 2 buildout has now been completed through Patch 69.

The practical result is that the repo should be treated as a maintained utility with an additive handoff-first continuation surface.

## Current status

If you are taking over the repo as a future LLM, do not reconstruct current state from scattered docs first.

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Then produce only the next repair patch or next planned patch.

## Operator flow

The intended operator flow is now:

1. run handoff export
2. upload the generated bundle
3. paste `handoff/next_prompt.txt`

That is the practical seamless-transition path.

## Core rules

PatchOps should preserve these rules unless evidence forces a deeper change:

- keep PowerShell thin
- keep reusable workflow logic in Python
- preserve the one-report evidence contract
- prefer narrow repair over broad rewrite
- keep the wrapper project-agnostic
- preserve existing compatible surfaces where they are still relied on

## Current command and example posture

Useful orientation surfaces still include:

- `patchops.cli examples`
- `patchops.cli profiles`
- `patchops.cli schema`
- `patchops.cli template`
- `powershell/Invoke-PatchVerify.ps1`

Generic Python + PowerShell profile examples remain part of the maintained surface.

Generic Python + PowerShell profile examples:
- `examples/generic_python_powershell_patch.json`
- `examples/generic_python_powershell_verify_patch.json`

The mixed profile name is:

- `generic_python_powershell`

## Where to look next

If you need orientation after the handoff files, read:

- `docs/llm_usage.md`
- `docs/project_status.md`
- `docs/examples.md`
- `docs/handoff_surface.md`
- `docs/manifest_schema.md`
- `docs/failure_repair_guide.md`
- `docs/patch_ledger.md`

## Summary

PatchOps is now meant to tell the next LLM exactly how to resume, not merely provide enough background for a clever model to infer the current state.