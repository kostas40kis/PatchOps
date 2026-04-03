# PatchOps examples

This document lists the shipped manifest examples and what each one is meant to prove.

## Core starter examples

- `examples/generic_python_patch.json`
  - Minimal generic apply example.
- `examples/generic_backup_patch.json`
  - Shows backup behavior when overwriting an existing file.
  - This backup-overwrite shape is also covered by an apply-flow test.
- `examples/generic_verify_patch.json`
  - Minimal generic verify-only example.
- `examples/trader_code_patch.json`
  - Trader-flavored code patch example.
- `examples/trader_doc_patch.json`
  - Trader-flavored documentation patch example.
- `examples/trader_verify_patch.json`
  - Trader-flavored verify-only example.

## Profile coverage examples

- `examples/generic_python_powershell_patch.json`
  - Example using the `generic_python_powershell` profile for apply flow.
  - This profile shape is also covered by an apply-flow test.
- `examples/generic_python_powershell_verify_patch.json`
  - Example using the `generic_python_powershell` profile for verify flow.
  - The apply side of this profile is covered by a dedicated apply-flow test.

## Report preference examples

- `examples/generic_report_prefix_patch.json`
  - Demonstrates `report_name_prefix` with Desktop evidence enabled.
  - This report-preference shape is also covered by an apply-flow test.
- `examples/generic_report_dir_patch.json`
  - Demonstrates `report_dir` placement and Desktop evidence disabled.
  - This report-preference shape is also covered by an apply-flow test.

## Command-group examples

- `examples/generic_smoke_audit_patch.json`
  - Demonstrates a manifest that includes both `smoke_commands` and `audit_commands`.
  - Use this when the patch needs a primary validation step and then extra lightweight confirmation or diagnostics.
  - This shape is also covered by an apply-flow test, not just inspect.

- `examples/generic_cleanup_archive_patch.json`
  - Demonstrates a manifest that includes both `cleanup_commands` and `archive_commands`.
  - Use this when a patch intentionally leaves behind temporary artifacts or creates a handoff/archive step that should still be reported explicitly.
  - This shape is also covered by an apply-flow test, not just inspect.

## Content-source examples

- `examples/generic_content_path_patch.json`
  - Demonstrates a manifest that writes file content from `content_path` instead of embedding the payload inline.
  - The referenced content lives at `examples/content/generic_content_path_note.txt`.
  - Use this when the patch content should stay in a separate artifact but still be driven by one manifest.
  - This shape is also covered by an apply-flow test, not just inspect.

## Allowed-exit examples

- `examples/generic_allowed_exit_patch.json`
  - Demonstrates how `allowed_exit_codes` can authorize an expected non-zero command result.
  - This shape is also covered by an apply-flow test, not just inspect.

## Example authoring notes

These examples are intentionally simple and deterministic. They are not meant to encode target-repo business logic. They exist to help future LLMs and operators pick a close manifest shape before authoring a real patch.
