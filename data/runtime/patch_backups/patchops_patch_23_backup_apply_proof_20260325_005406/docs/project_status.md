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


## Patch 21 addition

Patch 21 adds apply-flow tests proving that command-group examples using `smoke_commands`, `audit_commands`, `cleanup_commands`, and `archive_commands` all execute through the normal reporting path with the expected sections present.


## Patch 22 addition

Patch 22 adds an apply-flow test proving that `report_dir`, `report_name_prefix`, and `write_to_desktop: false` can produce a PASS run with the report written into a custom directory under a custom prefix.
