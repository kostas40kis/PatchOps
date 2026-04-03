# PatchOps project status

## Stage 1 status

PatchOps now has a working Stage 1 harness with:

- manifest loading and validation
- profile resolution
- deterministic reporting
- backup and write helpers
- apply / verify / inspect / plan flows
- discovery commands:
  - profiles
  - examples
  - schema
  - doctor
  - check
  - template
- thin PowerShell launchers
- self-tests for the harness
- bundled examples covering:
  - generic apply
  - backup proof
  - verify-only
  - trader examples
  - report preference examples
  - generic Python + PowerShell examples
  - command-group examples
  - content-path examples
  - allowed-exit examples

## Current position

PatchOps is now in late Stage 1 / pre-Stage 2.

The core wrapper surface exists, multiple manifest authoring patterns have been proven end to end, and the next sensible milestone is deliberate consolidation followed by first real trader-facing usage through PatchOps as the normal wrapper path.

## Patch 25_26 addition

Patch 25_26 adds consolidation docs plus first trader-facing usage prep docs so Stage 1 can be treated as a freezeable baseline before the first deliberate trader-facing PatchOps usage wave.

## Patch 27 addition

Patch 27 adds trader-first starter manifests and authoring docs so the first deliberate trader-facing usage wave can start from concrete low-risk assets.

## Patch 28 addition

Patch 28 adds a trader execution sequence doc and proves the starter manifests through `plan`, so the first trader-facing review-before-apply path is explicit and tested.

## Patch 29 addition

Patch 29 adds trader rehearsal and first-real-run checklists so the first trader-facing PatchOps usage can move from documentation into a more operator-ready execution path.

<!-- PATCHOPS_PATCH30_TRADER_READINESS_INDEX:START -->
## Patch 30 — trader readiness index

Patch 30 adds `docs/trader_readiness_index.md` and `tests/test_trader_readiness_index.py`.

This patch does not start Stage 2.
It strengthens the late Stage 1 / pre-Stage 2 operator surface by introducing one explicit trader-first map that links the key docs, starter manifests, rehearsal path, and Stage 2 boundary in one place.

The intent is to reduce operator drift during the first trader-facing usage wave and make the starting sequence obvious to both humans and future LLMs.
<!-- PATCHOPS_PATCH30_TRADER_READINESS_INDEX:END -->

<!-- PATCHOPS_PATCH32_VERIFY_ONLY_FLOW:START -->
## Patch 32 — verify-only flow contract

Patch 32 formalizes a verification-only rerun contract in `patchops/workflows/verify_only.py` and adds `tests/test_verify_only_flow.py`.

The focus is narrow and explicit:

- verification-only reruns should skip writes,
- expected target files should be re-checked from manifest data,
- rerun scope should be renderable as explicit report lines,
- and missing expected files should surface as an attention condition rather than being hidden.

This patch is part of the Stage 1 repairability surface rather than a broad CLI redesign.
<!-- PATCHOPS_PATCH32_VERIFY_ONLY_FLOW:END -->

<!-- PATCHOPS_PATCH33_VERIFY_LAUNCHER:START -->
## Patch 33 — Invoke-PatchVerify launcher

Patch 33 adds `powershell/Invoke-PatchVerify.ps1` as the thin Windows-native launcher for verification-only reruns.

The launcher remains deliberately narrow:

- resolve the wrapper root,
- resolve a Python runtime for PatchOps,
- accept a manifest path,
- call the PatchOps CLI,
- and preserve the CLI exit code.

A `-Preview` switch is also included so operators can safely preview the verify-only plan path before running a real verification pass.
<!-- PATCHOPS_PATCH33_VERIFY_LAUNCHER:END -->

<!-- PATCHOPS_PATCH34_WRAPPER_RETRY:START -->
## Patch 34 — wrapper-only retry support

Patch 34 adds `patchops/workflows/wrapper_retry.py` and `tests/test_wrapper_retry.py`.

The goal is to make wrapper-only recovery explicit when patch content likely succeeded but wrapper/reporting mechanics failed.

The contract stays deliberately narrow:

- wrapper-only retry is treated as a verification-shaped recovery path,
- writes remain skipped,
- expected target files are re-checked,
- rerun scope can be rendered as explicit report lines,
- and missing expected files trigger escalation instead of silently widening back into a full apply pass.
<!-- PATCHOPS_PATCH34_WRAPPER_RETRY:END -->

<!-- PATCHOPS_PATCH35_FAILURE_REPAIR_GUIDE:START -->
## Patch 35 — failure repair guide

Patch 35 adds `docs/failure_repair_guide.md` and `tests/test_failure_repair_guide.py`.

The guide explains how to distinguish:

- content failure,
- wrapper failure,
- verification-only rerun cases,
- and wrapper-only repair cases.

The goal is to let operators and future LLMs choose the narrowest trustworthy recovery path confidently instead of widening into blind reruns.
<!-- PATCHOPS_PATCH35_FAILURE_REPAIR_GUIDE:END -->

<!-- PATCHOPS_PATCH36_VERIFY_ONLY_DAILY_USE:START -->
## Patch 36 — verify-only daily-use tests

Patch 36 deepens `tests/test_verify_only_flow.py` so the verify-only and wrapper-only retry surfaces are proven trustworthy enough for daily use.

The added coverage focuses on the acceptance criteria from the development plan:

- verification-only paths still skip writes,
- rerun scope lines stay explicit and readable,
- no-target-file reruns stay narrow instead of escalating by accident,
- and wrapper-only recovery remains distinct from verification-only while still staying write-free and narrow.
<!-- PATCHOPS_PATCH36_VERIFY_ONLY_DAILY_USE:END -->

<!-- PATCHOPS_PATCH37_LLM_USAGE:START -->
## Patch 37 — LLM usage manual

Patch 37 adds `docs/llm_usage.md` and `tests/test_llm_usage_doc.py`.

This is the core handoff manual for future coding LLMs.
It explains how to read the project, how to choose a profile, how to build or adapt manifests, how to choose between apply and verify-only, how to classify failure, and how to preserve the wrapper-versus-target boundary.

The intent is to make a future model useful quickly without depending on tribal memory.
<!-- PATCHOPS_PATCH37_LLM_USAGE:END -->

<!-- PATCHOPS_PATCH38_TRADER_PROFILE:START -->
## Patch 38 — trader profile manual

Patch 38 adds `docs/trader_profile.md` and `tests/test_trader_profile_doc.py`.

This patch makes trader usage explicit without turning trader assumptions into core PatchOps identity.
It documents the expected roots, expected runtime, backup conventions, report expectations, and the wrapper-versus-target boundary for `C:\dev\trader`.
<!-- PATCHOPS_PATCH38_TRADER_PROFILE:END -->
