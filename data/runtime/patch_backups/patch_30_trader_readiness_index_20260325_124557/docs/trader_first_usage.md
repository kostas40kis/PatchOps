# Trader first usage guide

This document describes the first deliberate trader-facing PatchOps usage wave.

## Goal

Use PatchOps as the normal wrapper for a real trader-side manifest flow without moving trader business logic into PatchOps.

PatchOps should own:
- manifest loading
- profile resolution
- report generation
- backup behavior
- deterministic process execution
- wrapper-only rerun discipline

The trader repo should still own:
- architecture
- domain logic
- tests
- trading behavior
- safety rules

## Recommended first flow

1. Confirm PatchOps health:
   - `py -m pytest -q`
   - `py -m patchops.cli doctor --profile trader`
   - `py -m patchops.cli examples`
   - `py -m patchops.cli schema`

2. Generate a starter manifest:
   - `py -m patchops.cli template --profile trader --mode apply --patch-name trader_first_real_patch --output-path .\data\runtime\generated_templates\trader_first_real_patch.json`

3. Replace placeholders deliberately:
   - target project root
   - backup files
   - files to write
   - validation commands
   - report preferences

4. Review before execution:
   - `py -m patchops.cli check <manifest>`
   - `py -m patchops.cli inspect <manifest>`
   - `py -m patchops.cli plan <manifest>`

5. Only then run:
   - `py -m patchops.cli apply <manifest>`
   - or `py -m patchops.cli verify <manifest>` when appropriate

## Suggested first trader manifest shape

Choose something low-risk:
- documentation-only patch
- report-only patch
- validation-only patch
- a tiny repo-safe file write with existing tests

Avoid first using PatchOps on:
- complex live-flow trader changes
- high-surface multi-file code patches
- anything that mixes trader safety decisions into PatchOps

## Success criteria

The first real trader-facing usage is successful when:
- the manifest is understandable without reading PatchOps source,
- the report is complete and deterministic,
- backups are explicit,
- validation output is fully captured,
- any failure is clearly wrapper-only or trader-side.
## Starter manifests

- `examples/trader_first_doc_patch.json`
- `examples/trader_first_verify_patch.json`

See also: `docs/trader_execution_sequence.md`

See also: `docs/trader_rehearsal_runbook.md` and `docs/first_real_trader_run_checklist.md`
