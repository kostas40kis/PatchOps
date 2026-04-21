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
