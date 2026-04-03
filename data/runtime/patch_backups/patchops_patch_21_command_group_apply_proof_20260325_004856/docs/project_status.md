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
  - allowed-exit examples

## Patch 20 addition

Patch 20 adds a dedicated apply-flow test proving that a manifest using `allowed_exit_codes` can treat an expected non-zero validation result as acceptable and still finish with a normal PASS report. This makes the allowed-exit pattern a real end-to-end tested authoring shape, not only an inspectable example.
