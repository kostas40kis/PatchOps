# PatchOps examples

This document lists the shipped manifest examples and what each one is meant to prove.

## Core starter examples

- `examples/generic_python_patch.json`
  - Minimal generic apply example.
- `examples/generic_backup_patch.json`
  - Shows backup behavior when overwriting an existing file.
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
- `examples/generic_python_powershell_verify_patch.json`
  - Example using the `generic_python_powershell` profile for verify flow.

## Report preference examples

- `examples/generic_report_prefix_patch.json`
  - Demonstrates `report_name_prefix` with Desktop evidence enabled.
- `examples/generic_report_dir_patch.json`
  - Demonstrates `report_dir` placement and Desktop evidence disabled.

## Command-group examples

- `examples/generic_smoke_audit_patch.json`
  - Demonstrates a manifest that includes both `smoke_commands` and `audit_commands`.
- `examples/generic_cleanup_archive_patch.json`
  - Demonstrates a manifest that includes both `cleanup_commands` and `archive_commands`.

## Content-source examples

- `examples/generic_content_path_patch.json`
  - Demonstrates a manifest that writes file content from `content_path` instead of embedding the payload inline.
  - The referenced content lives at `examples/content/generic_content_path_note.txt`.

## Allowed-exit-code examples

- `examples/generic_allowed_exit_patch.json`
  - Demonstrates a validation command that intentionally exits non-zero while remaining acceptable because `allowed_exit_codes` includes that value.
  - Use this when a command has a meaningful non-zero success convention and the wrapper should treat it as allowed rather than failed.

## Example authoring notes

These examples are intentionally simple and deterministic. They are not meant to encode target-repo business logic. They exist to help future LLMs and operators pick a close manifest shape before authoring a real patch.
