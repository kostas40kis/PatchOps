# PatchOps patch ledger

## High-level status

PatchOps is in maintenance mode after the initial buildout circle and Documentation Stop H.

## Patch 24

Patch 24 covered failure-classification tests and made the wrapper-vs-target distinction enforceable.

## Patch 25

Patch 25 documented compatibility notes for Windows / PowerShell / runtime pitfalls.

## Patch 26

Patch 26 created the main manifest-driven apply workflow.

## Patch 25-26

Together, Patch 25-26 established the execution-integrity bridge from compatibility posture into real end-to-end apply behavior.

## Patch 41

Patch 41 extended the generic_python_powershell profile surface.

## Patch 48

Patch 48 added the final initial-milestone gate.

## Patch 49

Patch 49 was the Documentation Stop H refresh intent.

## Patch 50

Patch 50 covered Git / traceability hygiene intent.

## Patch 50C

Patch 50C restored required tested wording in the maintained docs after an over-minimal doc rewrite removed phrases that the doc tests intentionally enforce.

## Patch 25_26

Patch 25_26 is the maintained shorthand for the compatibility-to-apply bridge across the Patch 25 and Patch 26 transition.

## Patch 51

Patch 51 adds the wrapper-only retry planning surface.

It extends the `plan` command so wrapper-only retry can be previewed as a first-class rerun shape with an explicit retry reason, expected and missing target files, a writes-skipped guarantee, and escalation visibility.

This patch intentionally improves planning and inspection only.
The thin PowerShell launcher remains the next patch.

## Patch 52

Patch 52 adds the thin wrapper-only retry launcher.

It introduces `powershell/Invoke-PatchWrapperRetry.ps1`, adds a small Python-owned execution surface through `wrapper-retry`, and keeps preview support aligned with the wrapper-only retry planning surface added in Patch 51.

## Patch 53

Patch 53 adds explicit wrapper-only retry report sections.

It updates the canonical report renderer so wrapper-only retry shows up as its own report section with retry kind, retry reason, writes-skipped state, expected/existing/missing target counts, and escalation state.

This keeps wrapper-only retry parseable and visibly distinct from verify-only or full apply reports.

## Patch 53B

Patch 53B repairs the import cycle introduced by Patch 53.

The fix keeps the wrapper-only retry report surface but removes eager imports from `patchops.workflows.wrapper_retry` into `verify_only`, so `renderer.py`, `sections.py`, `wrapper_retry.py`, and `verify_only.py` no longer deadlock during module import.

## Patch 53C

Patch 53C repairs the wrapper-only retry execution compatibility surface.

It restores a module-level `verify_only` shim inside `patchops/workflows/wrapper_retry.py` and makes `execute_wrapper_only_retry()` delegate through that shim before relabeling the workflow mode to `wrapper_retry`.

This keeps the import-cycle repair from Patch 53B while preserving the existing monkeypatch/test contract.

## Patch 53D

Patch 53D repairs the wrapper-only retry mode label.

The delegated verify result is now relabeled to `wrapper_only_retry` instead of `wrapper_retry`, which matches the intended workflow name and existing regression test expectation.

## Patch 54

Patch 54 expands the wrapper-only retry tests.

It deepens coverage across the Python helper surface, the plan/preview surface, and the PowerShell launcher layer so wrapper-only retry remains explicit, narrow, and distinct from verify-only.

## Patch 54B

Patch 54B repairs `powershell/Invoke-PatchWrapperRetry.ps1` so the launcher exposes `-Preview` and routes preview calls into the Python-owned `plan --mode wrapper_retry` surface.

This is a thin launcher repair only.

## Patch 54C

Patch 54C rewrites `powershell/Invoke-PatchWrapperRetry.ps1` so the launcher text explicitly includes `-Preview` and forwards preview requests into `patchops.cli plan --mode wrapper_retry` while keeping the non-preview branch thin.

## Patch 54D

Patch 54D is a thin launcher contract repair for wrapper-only retry.

It does not widen workflow behavior. It only makes the PowerShell launcher text and forwarding shape match the locked Stage 2 expectations for preview and repo-root resolution.

## Patch 54E

Patch 54E repairs the wrapper retry PowerShell launcher contract.

It rewrites `powershell/Invoke-PatchWrapperRetry.ps1` so the launcher contains the exact thin-surface text the tests assert and so preview execution resolves wrapper root safely when the script is invoked with `-File`.

## Patch 54F

Patch 54F repairs the final wrapper retry launcher text contract by making the literal `-Preview` string appear in `powershell/Invoke-PatchWrapperRetry.ps1` without widening the launcher beyond thin forwarding into `patchops.cli`.

## Patch 55

Patch 55 adds a `release-readiness` CLI surface.

It summarizes release/freeze readiness from repo-visible evidence, exposes required docs/examples/workflow/launcher surfaces in structured JSON, supports optional profile focus, and avoids guessing hidden state by keeping core test status explicit.

## Patch 55C

Patch 55C repairs `patchops/cli.py` after Patch 55 by removing the redundant inner `profile_summary` import inside the `release-readiness` handler.

That import shadowed the module-level `get_profile_summary` and `list_profile_summaries` names and broke the existing `profiles` command.

## Patch 55D

Patch 55D repairs the `release-readiness` command handler after Patch 55C left the handler body incomplete.

The fix restores payload construction in `patchops/cli.py` and preserves the earlier scope-shadow repair by reusing the existing module-level profile summary imports.

## Patch 56

Patch 56 adds the thin PowerShell launcher for release readiness.

It introduces `powershell/Invoke-PatchReadiness.ps1` so operators can invoke the existing `release-readiness` command surface without custom shell composition. The launcher remains thin, forwards optional profile and core-test state flags, and keeps the readiness logic in Python.
