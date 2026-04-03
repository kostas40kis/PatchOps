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

<!-- PATCHOPS_PATCH36_VERIFY_ONLY_DAILY_USE:START -->
## Daily-use trust checks for verify-only reruns

Patch 36 tightens the verify-only trust surface with test coverage that checks practical operator cases:

- deduplicated expected file resolution stays stable,
- rerun scope lines remain explicit,
- zero-target verification passes do not escalate by accident,
- and wrapper-only retry stays a distinct narrow path rather than a hidden write-capable rerun.

This keeps the rerun surface usable for daily operations instead of only for idealized examples.
<!-- PATCHOPS_PATCH36_VERIFY_ONLY_DAILY_USE:END -->

<!-- PATCHOPS_PATCH51_WRAPPER_RETRY_PLAN:START -->
## Wrapper-only retry planning preview

Patch 51 adds a planning preview for wrapper-only retry before the dedicated launcher exists.

Use:

- `py -m patchops.cli plan <manifest> --mode wrapper_retry --retry-reason "report writer failed after likely validation success"`

The wrapper-only retry planning surface stays narrow:

- writes are skipped,
- the retry reason is recorded,
- expected target files are surfaced,
- missing target files force attention or escalation,
- and the preview does not widen silently into a full apply pass.

This is the planning and inspection surface only.
The thin PowerShell launcher belongs to the next patch.
<!-- PATCHOPS_PATCH51_WRAPPER_RETRY_PLAN:END -->

<!-- PATCHOPS_PATCH52_WRAPPER_RETRY_LAUNCHER:START -->
## Wrapper-only retry launcher

Patch 52 adds `powershell/Invoke-PatchWrapperRetry.ps1` as the thin operator surface for wrapper-only retry.

Use preview first when appropriate:

- `.\powershell\Invoke-PatchWrapperRetry.ps1 -ManifestPath <manifest> -Preview -RetryReason "report writer failed after validation"`

Run the narrow wrapper-only retry through the same launcher family when the intent is clear:

- `.\powershell\Invoke-PatchWrapperRetry.ps1 -ManifestPath <manifest> -RetryReason "report writer failed after validation"`

The launcher stays thin and forwards into Python-owned logic rather than recreating retry behavior in PowerShell.
<!-- PATCHOPS_PATCH52_WRAPPER_RETRY_LAUNCHER:END -->

<!-- PATCHOPS_PATCH53_WRAPPER_RETRY_REPORT_MATRIX:START -->
## Report evidence for wrapper-only retry

Patch 53 adds canonical report wording for wrapper-only retry.

A good wrapper-only retry report now makes these fields explicit inside the report body:

- retry kind,
- retry reason,
- writes skipped,
- expected/existing/missing targets,
- escalation state.

This keeps wrapper-only retry distinct from verify-only and from a normal apply report.
<!-- PATCHOPS_PATCH53_WRAPPER_RETRY_REPORT_MATRIX:END -->
