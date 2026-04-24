# PatchOps

PatchOps is a standalone wrapper / harness project for applying, verifying, packaging, and evidencing changes.

## Final maintenance posture

PatchOps is in a maintenance / additive-improvement posture.
Historical zip-first and Python-heavier completion as architecture context remain useful, but the live frontier must still be read from the latest truthful report and handoff.

This README closes the frontier discrepancy by treating historical stream-completion summaries as context only.
The post-Patch-29 recovery stream is now green through the accepted recovery frontier regression gate only when the canonical report says so.
The final pre-documentation proof stop is the point after which the docs may be refreshed.
Consolidation status remains visible here because older Stage 1 / pre-Stage 2 history still matters as context.

## Read these files in this order:

1. `handoff/current_handoff.md`
2. `docs/project_status.md`
3. `docs/operator_quickstart.md`
4. `docs/llm_usage.md`
5. `docs/examples.md`

If PatchOps work is already in progress, start from handoff/current_handoff.md first.
If the repo is being taken over fresh, also read docs/project_packet_contract.md and docs/project_packet_workflow.md.

## Current truth rules

- Keep one canonical Desktop txt report.
- Treat the canonical report as the truth surface for each run.
- Keep PowerShell thin and operator-facing.
- Keep reusable mechanics in Python.
- suspicious-run support exists as a conservative reading aid.
- verification-only reruns and wrapper-only repair remain distinct flows.

## Handoff and source bundle surfaces

- `handoff/current_handoff.md`
- `handoff/final_future_llm_source_bundle.txt`

The preferred history-compression artifact is `handoff/final_future_llm_source_bundle.txt`.
That artifact and the source bundle should describe the real modular package layout rather than stale flat-file assumptions.

## Profile and example note

### Generic Python + PowerShell profile examples

Use the maintained examples and adapt them:
- `examples/trader_code_patch.json`
- `examples/trader_first_verify_patch.json`
- `examples/generic_python_patch.json`
- `examples/trader_first_doc_patch.json`
- `examples/generic_verify_patch.json`

Patch 26, Patch 29, and later recovery wording should be interpreted carefully: Patch 29 was unresolved and required the recovery stream.

Historical zip-first and Python-heavier completion as architecture context should be treated as background only, not current frontier proof. Patch 29 was unresolved and required the later recovery stream.

handoff/final_future_llm_source_bundle.txt is the durable future-llm upload artifact.

Use the durable future-LLM upload artifact together with the current modular-package snapshot.

## Current command inventory

PatchOps currently exposes the maintained core surfaces:

- `check`
- `inspect`
- `plan`
- `apply`
- `verify`
- `run-package`
- `check-bundle`
- `inspect-bundle`
- `plan-bundle`
- `bundle-doctor`
- `build-bundle`
- `make-bundle`
- `make-proof-bundle`
- `profiles`
- `doctor`
- `schema`
- `examples`
- `maintenance-gate`
- `emit-operator-script`

Operator-facing PowerShell helpers should remain thin shims over these Python-owned command surfaces.
- Keep PowerShell thin.
PatchOps should now be treated as a maintained utility rather than an open-ended architecture buildout.
Use `handoff/current_handoff.md` when active PatchOps work is already underway.
Use `docs/finalization_master_plan.md` as the final maintenance sequence summary.
PatchOps is a maintenance-mode wrapper.
PatchOps should be treated as a maintained utility rather than an open-ended architecture buildout.
Preserve one canonical truth and one canonical Desktop txt report.
`bootstrap-repair` remains a narrow recovery surface.
The repo should be read as code-proof frontier is green before the docs wave widened.
PatchOps follows a suspicious-success blocker rule whenever a command claims success without the expected truth-bearing evidence.
Use `Push-PatchOpsToGitHub.ps1` as the maintained GitHub publish helper after maintenance-mode work is ready to publish.
The canonical Desktop txt report remains the operator-facing source of truth.
Use `post_publish_snapshot.md` to confirm the published-state snapshot after maintenance-mode work is pushed.

Read these files in this order:
1. handoff/current_handoff.md
2. handoff/current_handoff.json
3. handoff/latest_report_copy.txt
4. docs/project_status.md
5. docs/patch_ledger.md

Read these files in this order:
1. `handoff/current_handoff.md`
2. `handoff/current_handoff.json`
3. `handoff/latest_report_copy.txt`
4. `docs/project_status.md`
5. `docs/patch_ledger.md`

## Handoff refresh reminder
- run handoff export after meaningful progress so takeover artifacts stay current.

## Handoff resume reminder

After exporting the handoff packet, paste `handoff/next_prompt.txt` into the next continuation chat.

## Profile reminder

Generic Python + PowerShell profile examples use `generic_python_powershell`.

PATCHOPS_F7_FINAL_DOC_STOP_README:START

## Final doc-stop reading note
- handoff/current_handoff.md
- handoff/current_handoff.json
- handoff/latest_report_copy.txt
- handoff/next_prompt.txt
- brand-new target project
- historical anchors
- target-specific extension work
- final pre-documentation proof stop
- handoff/final_future_llm_source_bundle.txt
- patchops/reporting/
- suspicious-run support
- wrapper health aid
- post-Patch-29 recovery stream is now green through the accepted recovery frontier regression gate
- treat any outer PASS with fatal stderr and no detected inner report as a failure

PATCHOPS_F7_FINAL_DOC_STOP_README:END

## Targeted contract repair additions
patchops/failure_categories.py
opt-in suspicious-run support remains a wrapper health aid, not a target-content feature.
setup-windows-env

<!-- PATCHOPS_E4A_README_CURRENT_TRUTH_FOLLOWUP_20260423 -->
Historical Patch 29 operator-script attempts should not be treated as the accepted success state on their own.

<!-- PATCHOPS_E8_README_HISTORY_COMPRESSION_LOCK_20260423 -->
## Final pre-documentation proof stop

handoff/current_handoff.md
brand-new target project
historical anchors
target-specific extension work
historical patch 29 operator-script attempts should not be treated as the accepted success state on their own
handoff/final_future_llm_source_bundle.txt

## Pythonization stream maintenance note

PatchOps now includes helper-owned Pythonization maintenance surfaces for:
- suspicious-run rule detection,
- detector proofs,
- a compact machine-readable suspicious-run artifact model,
- optional artifact emission behind an explicit opt-in flag,
- and a short canonical report mention when an emitted artifact exists.

These are maintenance-grade wrapper-health aids.
They do not widen PatchOps into target-project policy logic and they do not turn PowerShell into a second workflow engine.
