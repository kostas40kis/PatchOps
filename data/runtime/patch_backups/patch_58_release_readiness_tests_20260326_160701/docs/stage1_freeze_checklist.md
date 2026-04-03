# Stage 1 freeze checklist

This checklist is for deciding whether PatchOps Stage 1 is stable enough to freeze as a baseline.

## Core behavior
- [x] Manifest loading works.
- [x] Manifest validation works.
- [x] Profile resolution works.
- [x] Deterministic report rendering works.
- [x] Backup helpers work.
- [x] File writing helpers work.
- [x] Apply flow works.
- [x] Verify-only flow works.
- [x] Inspect flow works.
- [x] Plan flow works.

## Discovery / authoring surface
- [x] `profiles`
- [x] `doctor`
- [x] `examples`
- [x] `schema`
- [x] `template`
- [x] `check`

## Launcher surface
- [x] PowerShell launchers exist for the main authoring and discovery flows.
- [x] Saved-script execution policy issues are documented and understood.

## Report discipline
- [x] Canonical single-report discipline exists.
- [x] Final `SUMMARY` block is part of the contract.
- [x] `ExitCode` and `Result` lines are explicit.
- [x] Wrapper-only failure handling is part of the documented workflow.

## Proven authoring patterns
- [x] Generic apply
- [x] Verify-only
- [x] Backup overwrite
- [x] `content_path`
- [x] `allowed_exit_codes`
- [x] command-group sections
- [x] report preferences
- [x] `generic_python_powershell` mixed profile flow

## Freeze decision
Stage 1 can be treated as frozen enough for deliberate usage when:
1. the test suite is green,
2. the docs match the current command surface,
3. a human or future LLM can follow the documented flow without reading the source,
4. one real target-repo flow is ready to be exercised through PatchOps.
