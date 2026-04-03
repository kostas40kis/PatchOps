# PatchOps repair and rerun matrix

## Use apply when

- files need to be written or rewritten
- backups should be taken again
- validation and smoke commands must run as part of a full patch

## Use verify-only when

- the patch content is already correct
- you only need validation commands rerun
- you want a narrower evidence pass without rewriting target files

## Treat it as a wrapper-only failure when

- quoting breaks a valid command
- the report generation layer fails
- launcher argument forwarding breaks
- a compatibility issue exists in PowerShell or .NET behavior

## Treat it as a target-project failure when

- target tests fail because the repo code is wrong
- a target policy blocks the requested action by design
- the manifest points at the wrong target root or wrong files for the repo

## Best practice

Keep repairs narrow. Prefer fixing the wrapper evidence layer without disturbing target-repo business logic when the target commands already passed.

<!-- PATCHOPS_PATCH32_VERIFY_ONLY_FLOW:START -->
## Verify-only rerun contract

Use the verification-only path when the files are already on disk and the goal is to produce a clean rerun report without widening back into a full rewrite pass.

The rerun contract should stay explicit:

- writes are skipped,
- expected target files are re-checked,
- validation commands are rerun,
- and missing expected files are surfaced clearly.

Patch 32 adds helper logic and tests for that narrow contract in `patchops/workflows/verify_only.py` and `tests/test_verify_only_flow.py`.
<!-- PATCHOPS_PATCH32_VERIFY_ONLY_FLOW:END -->

<!-- PATCHOPS_PATCH33_VERIFY_LAUNCHER:START -->
## PowerShell verification-only launcher

Use `powershell/Invoke-PatchVerify.ps1` when the goal is to run a verification-only rerun from a thin PowerShell entrypoint.

Recommended sequence:

1. use `-Preview` first to confirm the resolved verify-only plan,
2. then run the launcher without `-Preview` when the manifest and target look correct.

The launcher is intentionally thin so rerun behavior stays owned by the Python core rather than being duplicated in shell logic.
<!-- PATCHOPS_PATCH33_VERIFY_LAUNCHER:END -->

<!-- PATCHOPS_PATCH34_WRAPPER_RETRY:START -->
## Wrapper-only retry contract

Use the wrapper-only retry path when the patch content likely succeeded but wrapper mechanics did not produce trustworthy evidence.

Typical examples:

- report writer failed after files were already written,
- a launcher or quoting issue happened after the target repo work probably succeeded,
- process output capture or summary rendering failed even though the target validation likely completed.

The wrapper-only retry path must stay explicit and narrow:

- writes are skipped,
- the reason for the wrapper-only retry is recorded,
- expected target files are re-checked,
- validation-oriented reruns stay verification-shaped,
- and missing expected files force escalation instead of silently widening into a blind full apply pass.
<!-- PATCHOPS_PATCH34_WRAPPER_RETRY:END -->
