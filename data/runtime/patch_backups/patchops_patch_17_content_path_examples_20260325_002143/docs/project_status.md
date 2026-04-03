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

## Patch 16 addition

Patch 16 expands example coverage so future LLMs can see concrete command-group shapes for:

- `smoke_commands`
- `audit_commands`
- `cleanup_commands`
- `archive_commands`

This improves manifest authoring guidance without changing target-repo logic or the wrapper-core execution contract.
