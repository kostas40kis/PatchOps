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
  - content-path examples
  - allowed-exit-code examples

## Patch 18 addition

Patch 18 expands example coverage so future LLMs can see a concrete `allowed_exit_codes` authoring shape for command entries. This improves manifest authoring guidance without changing target-repo logic or the wrapper-core execution contract.
