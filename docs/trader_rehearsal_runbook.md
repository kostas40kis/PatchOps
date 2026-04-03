# Trader rehearsal runbook

This runbook is for rehearsing the first real trader-facing PatchOps usage before any meaningful trader-side change is attempted.

## Rehearsal goal

Practice the exact wrapper sequence with a low-risk manifest so that:
- the operator flow is familiar,
- the report shape is expected,
- wrapper-only issues are discovered before higher-value usage.

## Recommended rehearsal sequence

1. Confirm PatchOps baseline:
   - `py -m pytest -q`
   - `py -m patchops.cli doctor --profile trader`
   - `py -m patchops.cli examples`

2. Pick the starter:
   - `examples/trader_first_verify_patch.json` for the safest first rehearsal
   - `examples/trader_first_doc_patch.json` after the verify rehearsal feels comfortable

3. Review-before-run:
   - `py -m patchops.cli check <manifest>`
   - `py -m patchops.cli inspect <manifest>`
   - `py -m patchops.cli plan <manifest>`
   - for verify rehearsal:
     - `py -m patchops.cli plan <manifest> --mode verify`

4. Execute only the appropriate flow:
   - `py -m patchops.cli verify <manifest>` for the first rehearsal
   - `py -m patchops.cli apply <manifest>` only after the verify path is comfortable and the manifest is still low-risk

## Rehearsal success signals

- the manifest is clear without reading source,
- the report path is understood,
- the result is easy to classify as wrapper-only vs trader-side,
- the command sequence is reproducible by another human or future LLM.

<!-- PATCHOPS_PATCH30_TRADER_READINESS_INDEX:START -->
## Readiness index cross-reference

This rehearsal runbook is not intended to stand alone.

Start with `docs/trader_readiness_index.md` so the rehearsal guidance stays connected to the trader starter manifests, execution sequence, first real run checklist, and Stage 2 entry criteria.
<!-- PATCHOPS_PATCH30_TRADER_READINESS_INDEX:END -->
