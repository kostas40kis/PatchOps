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

<!-- PATCHOPS_PATCH39_EXAMPLES_WALKTHROUGHS:START -->
## Patch 39 — examples walkthroughs

Patch 39 expands `docs/examples.md` into a real walkthrough guide and adds `tests/test_examples_doc.py`.

The document now gives a clear starting surface for:

- one trader code patch example,
- one trader verification-only example,
- one generic Python example,
- and one documentation-only example.

This makes the example layer teachable for both humans and future LLMs instead of leaving usage implied by raw JSON alone.
<!-- PATCHOPS_PATCH39_EXAMPLES_WALKTHROUGHS:END -->

<!-- PATCHOPS_PATCH40_STATUS_SNAPSHOT:START -->
## Current state snapshot

### Stable now

The following surfaces are now considered stable enough for handoff and daily use:

- manifest loading and validation,
- profile resolution for `generic_python`, `generic_python_powershell`, and `trader`,
- deterministic reporting with one canonical evidence artifact,
- example manifest discovery through `patchops.cli examples`,
- verification-only reruns,
- wrapper-only retry classification support,
- the thin PowerShell verify launcher `powershell/Invoke-PatchVerify.ps1`,
- LLM-first onboarding docs and trader-specific profile documentation,
- example walkthrough documentation with both starter and specialized examples.

### Exists in the repo today

PatchOps now has these major user-facing surfaces in place:

- CLI commands for planning, applying, verifying, checking, inspecting, examples, schema, profiles, and doctor flows,
- manifest examples for trader, generic Python, generic Python plus PowerShell, allowed-exit patterns, content-path patterns, and report preference patterns,
- docs that explain manifest structure, profile behavior, failure repair, LLM usage, trader usage, and examples,
- tests that keep example manifests, rerun behavior, launcher behavior, and documentation contracts current.

### Future work, not yet shipped behavior

The following items remain future work from the development plan and should not be described as already shipped:

- Patch 41 — broaden reuse with `profiles/generic_python_powershell.py` hardening as a dedicated next step,
- Patch 42 — first-class cleanup workflow support,
- Patch 43 — first-class archive workflow support,
- Patch 44 — cleanup/archive integration tests,
- Patch 45 — optional `docs/operational_patch_types.md`,
- Patch 46 — readiness check surface,
- Patch 47 — end-to-end sample suite,
- Patch 48 — final initial-milestone gate.

### Handoff meaning

This status document should help a future LLM or operator answer three questions without guesswork:

1. what is already stable now,
2. what exists in the repo today,
3. what remains future work rather than current behavior.
<!-- PATCHOPS_PATCH40_STATUS_SNAPSHOT:END -->

<!-- PATCHOPS_PATCH41_MIXED_PROFILE:START -->
## Patch 41 — generic Python plus PowerShell profile hardening

Patch 41 hardens `patchops/profiles/generic_python_powershell.py` and adds `tests/test_generic_python_powershell_profile.py`.

This patch treats the mixed profile as an explicit reuse surface instead of leaving its runtime assumptions implied.
The goal is to broaden support beyond pure Python repos while keeping PowerShell behavior profile-scoped and conservative.
<!-- PATCHOPS_PATCH41_MIXED_PROFILE:END -->

<!-- PATCHOPS_PATCH42_CLEANUP_WORKFLOW:START -->
## Patch 42 — cleanup workflow support

Patch 42 adds `patchops/workflows/cleanup.py` and `tests/test_cleanup_workflow.py`.

This patch makes cleanup a first-class workflow surface with explicit report sections and a deterministic scope description.
The goal is to support maintenance-style manifests without hiding cleanup actions as invisible side effects.
<!-- PATCHOPS_PATCH42_CLEANUP_WORKFLOW:END -->

<!-- PATCHOPS_PATCH43_ARCHIVE_WORKFLOW:START -->
## Patch 43 — archive workflow support

Patch 43 adds `patchops/workflows/archive.py` and `tests/test_archive_workflow.py`.

This patch makes archive actions a first-class workflow surface with explicit archive sections and traceable scope lines.
The goal is to support archive-style manifests without hiding archive behavior as invisible side effects.
<!-- PATCHOPS_PATCH43_ARCHIVE_WORKFLOW:END -->

<!-- PATCHOPS_PATCH44_CLEANUP_ARCHIVE_INTEGRATION:START -->
## Patch 44 — cleanup/archive integration tests

Patch 44 adds `tests/test_cleanup_archive_integration.py`.

This patch proves PatchOps supports maintenance-style manifests, not only code-writing workflows.
The integration surface checks the bundled cleanup/archive example manifest and verifies that cleanup and archive remain distinct, explicit, and deterministic when used together.
<!-- PATCHOPS_PATCH44_CLEANUP_ARCHIVE_INTEGRATION:END -->

<!-- PATCHOPS_PATCH45_OPERATIONAL_TYPES:START -->
## Patch 45 — operational patch types

Patch 45 adds `docs/operational_patch_types.md` and `tests/test_operational_patch_types_doc.py`.

This patch creates one explicit guide for choosing between code, documentation, validation, cleanup, archive, and verify-only workflows.
It turns the supported patch classes into a practical decision surface for operators and future LLMs.
<!-- PATCHOPS_PATCH45_OPERATIONAL_TYPES:END -->

<!-- PATCHOPS_PATCH46_READINESS_SURFACE:START -->
## Patch 46 — readiness check surface

Patch 46 adds `patchops/readiness.py` and `tests/test_readiness_surface.py`.

This patch creates a named readiness surface for the initial PatchOps milestone.
It verifies required docs, required examples, required workflows, required profiles, and whether the core test surface is green, then reports a clear `green` or `not_ready` status.
<!-- PATCHOPS_PATCH46_READINESS_SURFACE:END -->
