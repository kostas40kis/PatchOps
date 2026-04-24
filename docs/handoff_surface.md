# Handoff surface

This document records the maintained continuation surfaces for already-running PatchOps work.

## Core continuation packet

For already-running PatchOps work, start with:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`
4. `docs/project_status.md`
5. `docs/patch_ledger.md`

Then perform the exact next recommended action from the maintained evidence.

## Wrapper proof linkage

The canonical report now carries wrapper-exercised proof fields directly in the report header.

Future readers should treat the canonical report as the primary continuity anchor for wrapper execution truth, especially when checking:

- `Manifest Path`
- `Active Profile`
- `Runtime Path`
- `Wrapper Project Root`
- `Target Project Root`
- `File Write Origin`

This note links the handoff surface to the wrapper proof layer so a maintainer can tell, from one canonical report, whether the wrapper engine was really the path that executed the run.

This note is a linkage note only. It does not redesign the handoff bundle.

<!-- PATCHOPS_PATCH128_HANDOFF_SURFACE:START -->
## Patch 128 - active-work continuation proof

Patch 128 re-exports the handoff bundle from a real green maintenance report and treats the generated `handoff/` outputs as maintained proof surfaces.

The active-work continuation path should now be interpreted like this:

1. read `handoff/current_handoff.md`,
2. read `handoff/current_handoff.json`,
3. read `handoff/latest_report_copy.txt`,
4. restate current state briefly,
5. perform the exact next recommended action.

This remains separate from onboarding for brand-new target work.
Handoff is the first resume surface for already-running PatchOps work.
<!-- PATCHOPS_PATCH128_HANDOFF_SURFACE:END -->

<!-- PATCHOPS_J1_HANDOFF_LLM_USAGE_CURRENT_TRUTH_DOCS:HANDOFF:START -->
## Handoff patch history anchors

Patch 65 added the handoff export launcher surface.
Patch 67 established `docs/llm_usage.md` as the LLM start page and linked it to `handoff/current_handoff.md`.
Patch 69 is the documentation stop for the handoff-first UX.
Patch 128 - active-work continuation proof remains the active-work continuation proof anchor.

The handoff surface points to `handoff/current_handoff.md`, `handoff/current_handoff.json`, `handoff/latest_report_copy.txt`, `handoff/next_prompt.txt`, and `handoff/final_future_llm_source_bundle.txt`.

PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:START
Final handoff stop: use the handoff bundle before scanning scattered docs.
PATCHOPS_F7_FINAL_DOC_STOP_HANDOFF:END
<!-- PATCHOPS_J1_HANDOFF_LLM_USAGE_CURRENT_TRUTH_DOCS:HANDOFF:END -->

<!-- PATCHOPS_J1A_FINISH_HANDOFF_LLM_USAGE_DOC_CONTRACT:HANDOFF:START -->
## J1A handoff documentation stop completion

Patch 67 keeps `docs/llm_usage.md` visible as the orientation page while `handoff/current_handoff.md` remains the first continuation artifact.

Patch 69 is the documentation stop for the handoff-first UX.

The handoff documentation stop keeps these surfaces visible:

- `README.md`
- `docs/project_status.md`
- `docs/examples.md`
- `docs/llm_usage.md`

Future onboarding should now start from the handoff artifact for already-running PatchOps work.
The handoff surface is now a maintained continuation contract.
Use `export-handoff` to refresh it and then use `handoff/next_prompt.txt`.
<!-- PATCHOPS_J1A_FINISH_HANDOFF_LLM_USAGE_DOC_CONTRACT:HANDOFF:END -->

<!-- PATCHOPS_L1_CURRENT_FRONTIER_DOC_CONTRACT:HANDOFF:START -->

## Patch 65 - handoff launcher surface

Patch 65 keeps the operator-facing handoff launcher visible:
`Invoke-PatchHandoff.ps1`.

<!-- PATCHOPS_L1_CURRENT_FRONTIER_DOC_CONTRACT:HANDOFF:END -->

<!-- PATCHOPS_L1A_FINISH_TWO_DOC_PHRASES:HANDOFF:START -->

## Patch L1A - maintained continuation surface wording

This is the maintained continuation surface for already-running PatchOps work.

<!-- PATCHOPS_L1A_FINISH_TWO_DOC_PHRASES:HANDOFF:END -->

<!-- PATCHOPS_L1B_FINISH_TWO_DOC_PHRASES:HANDOFF:START -->
## L1B handoff replacement boundary

The maintained continuation surface for already-running PatchOps work does not replace the README, project packets, manifests, reports, operator quickstart, or finalization docs.
<!-- PATCHOPS_L1B_FINISH_TWO_DOC_PHRASES:HANDOFF:END -->
