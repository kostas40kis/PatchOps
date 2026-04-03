# Trader execution sequence

This document describes the exact sequence to use for the first real trader-facing PatchOps run.

## Goal

Use PatchOps as the normal wrapper around a low-risk trader manifest without moving trader business logic into PatchOps.

## Recommended sequence

1. Confirm PatchOps baseline:
   - `py -m pytest -q`
   - `py -m patchops.cli doctor --profile trader`
   - `py -m patchops.cli examples`
   - `py -m patchops.cli schema`

2. Start from a trader starter manifest:
   - `examples/trader_first_doc_patch.json`
   - or `examples/trader_first_verify_patch.json`

3. Review the manifest:
   - `py -m patchops.cli check <manifest>`
   - `py -m patchops.cli inspect <manifest>`
   - `py -m patchops.cli plan <manifest>`
   - for verify-only starter flows:
     - `py -m patchops.cli plan <manifest> --mode verify`

4. Only then run:
   - `py -m patchops.cli apply <manifest>`
   - or `py -m patchops.cli verify <manifest>`

## First-run discipline

- keep the first trader-facing manifest intentionally small
- prefer documentation-only, verification-only, or tiny repo-safe writes
- confirm backups are explicit
- confirm report location is understood
- do not move trader safety decisions into PatchOps

## Expected result

A successful first run should produce:
- one canonical report,
- explicit `ExitCode` and `Result`,
- clear stdout/stderr capture,
- clear separation between wrapper-only and trader-side failure.
