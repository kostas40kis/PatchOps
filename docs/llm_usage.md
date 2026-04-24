# LLM usage

When guiding bundle work, follow the maintained command order:

- `make-bundle`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `run-package`

Always continue patch by patch from evidence.

Prefer the maintained bundle workflow over ad hoc zip guessing.

<!-- PATCHOPS_H1S_LLM_USAGE_CORE_DOC_CONTRACT:START -->

## Core maintenance contract

PatchOps is maintained with thin powershell at the operator boundary and reusable mechanics in Python.
PowerShell may pass paths, invoke the Python CLI, and surface a report path, but durable workflow behavior should stay Python-owned.
Keep reusable mechanics in Python for bundle validation, extraction, command execution, reporting, and failure classification.

The suspicious-success blocker and suspicious success blocker language means a run must not be summarized as green when stderr or missing inner evidence proves failure.
This repo follows code-first / docs-last maintenance: patch the code-proof frontier first, then update docs only from shipped behavior.
Treat the canonical report as the truth surface for each run.

Current handoff and source-bundle references:

- handoff/final_future_llm_source_bundle.txt
- patchops/reporting/
- patchops/failure_categories.py
- generic_python_powershell_patch.json
- generic_python_powershell_verify_patch.json
- trader_first_doc_patch.json
- trader_first_verify_patch.json
- stale exports that mention missing flat files are historical context, not the current module layout
- post_publish_snapshot.md

<!-- PATCHOPS_H1S_LLM_USAGE_CORE_DOC_CONTRACT:END -->

<!-- PATCHOPS_J1_HANDOFF_LLM_USAGE_CURRENT_TRUTH_DOCS:LLM_USAGE:START -->
## Handoff-first current-truth orientation

This file is the orientation page for future coding LLMs.
It is not the main state-reconstruction surface anymore.
PatchOps is a **standalone wrapper / harness project**.
Do not start current-state reconstruction by scanning scattered docs when the handoff bundle exists.

Read these files in this order:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Then use `handoff/final_future_llm_source_bundle.txt` as the durable source-bundle artifact and paste `handoff/next_prompt.txt` when transferring context.

If PatchOps work is already in progress, start from the handoff files and continue patch by patch from evidence.
if patchops work is already in progress, do not rebuild state from scattered historical docs first.

Starting a brand-new target project with PatchOps uses the generic onboarding packet, `docs/project_packet_contract.md`, `docs/project_packet_workflow.md`, and `docs/projects/<project_name>.md`.
Continuing an already-running PatchOps effort uses handoff first.
starting a brand-new target project with patchops is not the same as continuing an already-running patchops effort.

briefly restate:
- the current accepted evidence,
- the first failing seam,
- the exact next patch,
- and why the patch is narrow.

Then produce only the next repair patch or next planned patch.
Do not move target-repo business logic into PatchOps.
Prefer narrow repair over broad rewrite.
Run handoff export when refreshing the handoff bundle, upload the generated bundle, and paste `handoff/next_prompt.txt`.

Treat the canonical report as the truth surface for each run.
historical stream-completion summaries as context, not current frontier proof.
post_publish_snapshot.md remains historical context, not a replacement for the current report.
thin powershell remains the rule: PowerShell is an operator shim, not the reusable workflow engine.

## Final maintenance-mode reading order

Use handoff/current_handoff.md first for active work, then handoff/current_handoff.json, then handoff/latest_report_copy.txt, then handoff/final_future_llm_source_bundle.txt.

## Self-hosted patch authoring notes for Windows PowerShell / ISE

Keep PowerShell thin. Avoid ProcessStartInfo.ArgumentList in Windows PowerShell 5.1. Prefer Python-owned helpers and one canonical report.

PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:START
For brand-new target onboarding, use recommend-profile, init-project-doc, starter, refresh-project-doc, the generic onboarding packet, and the project packet. For already-running work, use handoff first.
PATCHOPS_PATCH84_LLM_USAGE_ONBOARDING:END

PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:START
Final documentation stop: preserve handoff-first reading order, generic onboarding packet boundaries, and the current final source bundle path handoff/final_future_llm_source_bundle.txt.
PATCHOPS_F7_FINAL_DOC_STOP_LLM_USAGE:END
<!-- PATCHOPS_J1_HANDOFF_LLM_USAGE_CURRENT_TRUTH_DOCS:LLM_USAGE:END -->

<!-- PATCHOPS_J1A_FINISH_HANDOFF_LLM_USAGE_DOC_CONTRACT:LLM_USAGE:START -->
## J1A final handoff and LLM usage contract fill

This file is the orientation page for future coding LLMs.
It is not the main state-reconstruction surface anymore.

Read these current-state artifacts first:

1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`

Do not start current-state reconstruction by scanning scattered docs when the handoff bundle exists.
For operator continuation, run handoff export, upload the generated bundle, and paste `handoff/next_prompt.txt`.

PatchOps is a **standalone wrapper / harness project**.

Target repos own:
- target-project business logic,
- domain behavior,
- application-specific architecture,
- product features.

PatchOps owns:
- manifests,
- patch planning,
- wrapper-owned apply / verify orchestration,
- reporting,
- handoff,
- bundle transport,
- recovery guidance.

Default takeover flow:
- briefly restate:
  - the current evidence,
  - the first failing seam,
  - the next narrow repair.
- produce only the next repair patch or next planned patch.
- do not move target-repo business logic into PatchOps.
- prefer narrow repair over broad rewrite.

Operator handoff flow:
- run handoff export.
- upload the generated bundle.
- paste `handoff/next_prompt.txt`.

Starting a brand-new target project with PatchOps uses the generic onboarding packet and `docs/projects/<project_name>.md`.
Continuing an already-running PatchOps effort starts from `handoff/current_handoff.md`.
If PatchOps work is already in progress, start from handoff.
If you are starting a brand-new target project, start from the project packet workflow.

Use code-first / docs-last discipline.
Treat the canonical report as the truth surface for each run.
Historical stream-completion summaries as context, not current frontier proof.
Patch 29 as unresolved historical context that required the recovery stream.
Legacy launcher compatibility still exists for bare transport/demo bundles where appropriate.

## Self-hosted patch authoring notes for Windows PowerShell / ISE

When authoring a self-hosted PatchOps repair from Windows PowerShell / ISE:
- write the patch manifest as compact JSON,
- avoid shell-owned workflow logic,
- keep reusable behavior in Python,
- syntax-check generated helpers before packaging,
- keep PowerShell as a thin launcher / report surface.

## Final maintenance-mode reading order

For final maintenance-mode work:
- verify reality,
- repair narrowly,
- keep docs truthful to code,
- use `handoff/current_handoff.md`,
- use `docs/projects/<project_name>.md` for target onboarding,
- use `docs/finalization_master_plan.md` for the finalization boundary.
<!-- PATCHOPS_J1A_FINISH_HANDOFF_LLM_USAGE_DOC_CONTRACT:LLM_USAGE:END -->

<!-- PATCHOPS_J1B_EXACT_DOC_PHRASE_CONTRACT:LLM_USAGE:START -->
## J1B exact current-truth phrase lock

Never move target-repo business logic into PatchOps.
PatchOps remains the wrapper; target repositories own their own application code and domain decisions.

Current handoff/source-bundle language must describe the current modular package layout, not stale flat-file assumptions.

legacy launcher compatibility still exists for bare transport/demo bundles where appropriate.

Self-hosted patch authoring reminder: do not add a trailing newline to the patch manifest.
<!-- PATCHOPS_J1B_EXACT_DOC_PHRASE_CONTRACT:LLM_USAGE:END -->
<!-- PATCHOPS_J1C_LAST_DOC_PHRASE_CONTRACT:LLM_USAGE:START -->
## Final exact phrase compatibility notes

- Trader is the first serious profile, not the identity of the wrapper.
- validate the manifest immediately with `json.load(...)`.

These notes intentionally preserve exact legacy wording expected by the current doc-contract tests.
<!-- PATCHOPS_J1C_LAST_DOC_PHRASE_CONTRACT:LLM_USAGE:END -->
<!-- PATCHOPS_J1D_FINISH_LLM_USAGE_READING_ORDER_CONTRACT:START -->
## Final LLM reading-order completion

For the wrapper boundary and handoff-first reading order, future coding LLMs must keep these exact questions visible:

- how to read the project
- how to pick a profile
- how to build a manifest
- how to decide between apply and verify-only
- how to classify failure
- how to avoid moving target-repo logic into patchops

Required references for that reading order remain:

- docs/failure_repair_guide.md
- examples/trader_first_verify_patch.json
- powershell/invoke-patchverify.ps1

Self-hosted PowerShell authoring rule: use ProcessStartInfo.Arguments for Windows PowerShell 5.1 compatibility when ArgumentList is unavailable or unsafe.
<!-- PATCHOPS_J1D_FINISH_LLM_USAGE_READING_ORDER_CONTRACT:END -->

<!-- PATCHOPS_L1_CURRENT_FRONTIER_DOC_CONTRACT:LLM_USAGE:START -->

## Current-frontier L1 reading and helper contract

- Keep `starter --profile` visible in LLM onboarding guidance.
- Keep `bootstrap_repair.md` visible beside `post_publish_snapshot.md` for top-level published-state orientation.

<!-- PATCHOPS_L1_CURRENT_FRONTIER_DOC_CONTRACT:LLM_USAGE:END -->

<!-- PATCHOPS_L1A_FINISH_TWO_DOC_PHRASES:LLM_USAGE:START -->

## Patch L1A - published helper reference

Keep `github_publish_helper.md` visible alongside `post_publish_snapshot.md` and `bootstrap_repair.md` for top-level published-state orientation.

<!-- PATCHOPS_L1A_FINISH_TWO_DOC_PHRASES:LLM_USAGE:END -->

<!-- PATCHOPS_L1B_FINISH_TWO_DOC_PHRASES:LLM_USAGE:START -->
## L1B final publish helper phrase

Keep `Push-PatchOpsToGitHub.ps1` visible in LLM orientation because top-level post-publish docs name it as the manual GitHub publish helper.
<!-- PATCHOPS_L1B_FINISH_TWO_DOC_PHRASES:LLM_USAGE:END -->
