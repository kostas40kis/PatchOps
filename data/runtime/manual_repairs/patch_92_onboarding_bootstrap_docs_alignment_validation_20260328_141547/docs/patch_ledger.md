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

## Patch 56B

Patch 56B repairs the release-readiness launcher contract and the green-fixture test.

The launcher now contains the explicit `"release-readiness"` token expected by the text-contract test, and the launcher execution test now seeds the release launchers that the readiness command actually requires before it can honestly return green.

## Patch 57

Patch 57 adds the release-readiness evidence surface.

It teaches the release-readiness command how to render deterministic report lines and optionally write a stable text artifact through `--report-path`. The matching readiness PowerShell launcher now forwards `-ReportPath`, and the tests verify both the JSON surface and the evidence file path.

## Patch 57B

Patch 57B repairs the release-readiness CLI insertion from Patch 57.

The failure was a malformed `--report-path` parser insertion in `patchops/cli.py`, which caused an `IndentationError` and blocked test collection. This repair rewrites the release-readiness parser block and handler block cleanly and reruns the suite.

## Patch 57C

Patch 57C repairs the broken release-readiness CLI surface by fully rewriting `patchops/cli.py` from a known-good baseline and then reapplying the intended release-readiness command surface cleanly.

This avoids another failed regex-style surgery against syntactically broken Python and restores a deterministic command surface before rerunning the full test suite.

## Patch 57D

Patch 57D is a narrow release-readiness launcher text repair.

The launcher already worked, but the test required the literal `-ReportPath` substring to appear in the file text. This patch adds a usage example line containing `-ReportPath` and preserves the existing thin launcher behavior.

## Patch 58

Patch 58 protects the release-readiness surface from drift.

It adds explicit required release-test checks to `patchops/readiness.py`, expands the readiness command tests and readiness launcher tests, and refreshes the release/freeze docs so the supported release contract now includes the maintained release-test surface.

## Patch 58B

Patch 58B repairs the readiness module after Patch 58 removed backward-compatible initial-milestone exports.

The fix restores:
- `REQUIRED_INITIAL_MILESTONE_*` constants
- `InitialMilestoneReadiness`
- `build_initial_milestone_readiness(...)`
- `render_initial_milestone_readiness_lines(...)`
- `readiness_is_green(...)`
- `readiness_as_dict(...)`

while preserving the newer release-readiness and release-test-surface checks.

## Patch 59

Patch 59 adds the manifest version policy surface.

It makes the current manifest contract more explicit by:
- formalizing current and supported manifest versions in `patchops/manifest_validator.py`,
- exposing stable version-policy fields in `patchops/manifest_reference.py`,
- documenting the policy in `docs/manifest_schema.md`,
- and adding tests that prove unsupported versions fail cleanly and schema output stays readable.

<!-- PATCHOPS_PATCH85_LEDGER:START -->
## Patch 85

Patch 85 adds a combined onboarding-helper roundtrip validation surface.

It proves that `recommend-profile`, `init-project-doc`, `starter`, and `refresh-project-doc` remain aligned for a conservative generic-target flow.

The goal is to protect the helper-first onboarding story as one maintained operator flow without widening the PatchOps architecture.
<!-- PATCHOPS_PATCH85_LEDGER:END -->

<!-- PATCHOPS_PATCH86_LEDGER:START -->
## Patch 86

Patch 86 adds handoff failure-mode validation for self-hosted continuation.

It proves that handoff export fails closed for a missing report path, recreates missing bundle artifacts on re-export, recreates a missing top-level index on re-export, and refreshes a stale generated prompt when the report result changes.

The patch stays validation-first and does not widen the handoff engine.
<!-- PATCHOPS_PATCH86_LEDGER:END -->

<!-- PATCHOPS_PATCH86C_LEDGER:START -->
## Patch 86C

Patch 86C repairs the Patch 86B repair attempt by switching from fragile literal-block matching to function-level replacement for the failing handoff failure-mode test.

The content repair remains the same:
the test now asserts `latest_report_copy_path` through `handoff/latest_report_index.json` instead of incorrectly expecting it in the direct `export_handoff_bundle()` return payload.

This stays a narrow test-contract repair and does not widen the handoff engine.
<!-- PATCHOPS_PATCH86C_LEDGER:END -->

<!-- PATCHOPS_PATCH87_LEDGER:START -->
## Patch 87

Patch 87 is the handoff operator docs stop after the repaired handoff failure-mode validation wave.

It refreshes the main operator-facing docs so they describe current handoff reality instead of sounding like handoff export is still pending future work.

It also adds one doc-contract test that keeps the handoff-first continuation wording aligned across README, llm usage, quickstart, status, and handoff-surface docs.
<!-- PATCHOPS_PATCH87_LEDGER:END -->

<!-- PATCHOPS_PATCH88_LEDGER:START -->
## Patch 88

Patch 88 refreshes the handoff-first example usage surfaces after the operator-docs stop.

It updates `docs/examples.md` so continuation examples now show the current export-handoff flow, the expected handoff artifacts, and the distinction between handoff-first continuation and brand-new target onboarding.

It also adds one doc-contract test so example usage wording stays aligned with the shipped handoff surfaces.
<!-- PATCHOPS_PATCH88_LEDGER:END -->

<!-- PATCHOPS_PATCH88B_LEDGER:START -->
## Patch 88B

Patch 88B repairs the Patch 88 docs refresh by restoring older tested wording in `README.md`, `docs/project_status.md`, and `docs/llm_usage.md`.

The repair is intentionally additive:
it keeps the newer handoff-first continuation wording while reintroducing the legacy phrases that the maintained doc-contract tests still enforce.

This is a narrow documentation contract repair, not a surface redesign.
<!-- PATCHOPS_PATCH88B_LEDGER:END -->
\n\n<!-- PATCHOPS_PATCH89_LEDGER:START -->
## Patch 89

Patch 89 adds a narrow validation surface for the project-packet workflow boundary.

It proves the maintained docs still keep the intended separation explicit:
- handoff first for continuation of already-running PatchOps work,
- generic onboarding packet plus project packet for a brand-new target project.

This is a maintenance validation patch, not a workflow redesign.
<!-- PATCHOPS_PATCH89_LEDGER:END -->\n

<!-- PATCHOPS_PATCH89B_LEDGER:START -->
## Patch 89B

Patch 89B repairs the single wording gap exposed by Patch 89.

It restores the exact operator-quickstart phrase `already-running PatchOps work` so the onboarding-versus-continuation boundary test matches the maintained docs.

This is a narrow documentation contract repair.
<!-- PATCHOPS_PATCH89B_LEDGER:END -->

<!-- PATCHOPS_PATCH90_LEDGER:START -->
## Patch 90

Patch 90 adds a narrow validation surface for project-packet update discipline.

It keeps the stable-vs-mutable packet distinction explicit and test-protected, and it preserves the rule that packet refreshes should stay grounded in reports and handoff rather than broad speculative rewrites.

This is a maintenance validation patch, not a workflow redesign.
<!-- PATCHOPS_PATCH90_LEDGER:END -->
\n\n<!-- PATCHOPS_PATCH91_LEDGER:START -->
## Patch 91

Patch 91 adds a maintenance validation surface for onboarding-helper docs alignment.

It keeps the helper-first onboarding story explicit across workflow, quickstart, and status docs, and it preserves the rule that these helpers are for brand-new target onboarding rather than already-running continuation.

This is a narrow validation patch, not a CLI redesign.
<!-- PATCHOPS_PATCH91_LEDGER:END -->\n