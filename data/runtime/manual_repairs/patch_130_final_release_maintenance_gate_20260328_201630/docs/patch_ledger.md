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
<!-- PATCHOPS_PATCH91_LEDGER:END -->\n\n<!-- PATCHOPS_PATCH92_LEDGER:START -->
## Patch 92

Patch 92 adds a maintenance validation surface for onboarding bootstrap docs alignment.

It keeps the bootstrap artifact story explicit across workflow, examples, quickstart, and status docs, and it preserves the rule that onboarding bootstrap is for brand-new target onboarding rather than already-running continuation.

This is a narrow validation patch, not an onboarding redesign.
<!-- PATCHOPS_PATCH92_LEDGER:END -->\n\n<!-- PATCHOPS_PATCH93_LEDGER:START -->
## Patch 93

Patch 93 adds a maintenance validation surface for the maintained project-packet examples.

It keeps `docs/projects/trader.md` and `docs/projects/wrapper_self_hosted.md` aligned with the packet contract and the current onboarding-versus-continuation interpretation.

This is a narrow validation patch, not a project-packet redesign.
<!-- PATCHOPS_PATCH93_LEDGER:END -->\n\n<!-- PATCHOPS_PATCH94_LEDGER:START -->
## Patch 94

Patch 94 adds a maintenance validation surface for the actual onboarding bootstrap artifacts.

It proves that the generated bootstrap markdown, JSON payload, next prompt, and starter manifest still match the current contract already described by the onboarding docs and current project-packet rollout.

This is a narrow validation patch, not an onboarding redesign.
<!-- PATCHOPS_PATCH94_LEDGER:END -->\n

<!-- PATCHOPS_PATCH94B_LEDGER:START -->
## Patch 94B

Patch 94B repairs the new onboarding bootstrap artifact test to match the current path-format contract.

The starter manifest currently preserves the Windows target root form for `target_project_root`, so the repair updates the test expectation rather than widening bootstrap behavior.

This is a narrow test-contract repair, not an onboarding redesign.
<!-- PATCHOPS_PATCH94B_LEDGER:END -->

<!-- PATCHOPS_PATCH94C_LEDGER:START -->
## Patch 94C

Patch 94C repairs the onboarding bootstrap artifact test so it matches the current direct payload contract.

The direct return payload is asserted through `written` plus the returned artifact paths, while profile identity remains asserted through the generated bootstrap markdown and JSON artifact surfaces.

This is a narrow test-contract repair, not an onboarding redesign.
<!-- PATCHOPS_PATCH94C_LEDGER:END -->

<!-- PATCHOPS_PATCH95_LEDGER:START -->
## Patch 95

Patch 95 adds a maintenance validation surface for the `refresh-project-doc` CLI contract.

It proves the operator-facing help still exposes the intended artifact-grounded refresh inputs:
`--handoff-json-path`, `--report-path`, and the mutable-state override flags that keep packet refresh explicit rather than hidden.

This is a narrow validation patch, not a refresh redesign.
<!-- PATCHOPS_PATCH95_LEDGER:END -->

<!-- PATCHOPS_PATCH95B_LEDGER:START -->
## Patch 95B

Patch 95B repairs the new `refresh-project-doc` help contract test so it matches the live CLI help surface.

The local help output currently proves the usage line and the live flags, including `--risk`.
This repair keeps the validation narrow and avoids widening the CLI just to satisfy a newer-than-live expectation.

This is a narrow test-contract repair.
<!-- PATCHOPS_PATCH95B_LEDGER:END -->

<!-- PATCHOPS_PATCH96_LEDGER:START -->
## Patch 96

Patch 96 adds a maintenance validation surface for the live help contracts of the helper-first onboarding commands.

It proves the current CLI help for `recommend-profile` and `starter` still exposes the small live flag surface that the onboarding helper layer depends on.

This is a narrow validation patch, not a helper redesign.
<!-- PATCHOPS_PATCH96_LEDGER:END -->

<!-- PATCHOPS_PATCH97_LEDGER:START -->
## Patch 97

Patch 97 adds a maintenance validation surface for the live help contract of `init-project-doc`.

It proves the current CLI help still exposes the first-use packet scaffold inputs:
`--project-name`, `--target-root`, `--profile`, `--runtime-path`, `--initial-goal`, `--output-path`, and `--wrapper-root`.

This is a narrow validation patch, not a scaffold redesign.
<!-- PATCHOPS_PATCH97_LEDGER:END -->

<!-- PATCHOPS_PATCH98_LEDGER:START -->
## Patch 98

Patch 98 adds a maintenance validation surface for the live help contract of `export-handoff`.

It proves the current CLI help still exposes the handoff-export inputs:
`--report-path`, `--wrapper-root`, `--current-stage`, and `--bundle-name`.

This is a narrow validation patch, not a handoff redesign.
<!-- PATCHOPS_PATCH98_LEDGER:END -->

<!-- PATCHOPS_PATCH99_LEDGER:START -->
## Patch 99

Patch 99 adds a maintenance validation surface for the live help contract of `bootstrap-target`.

It proves the current CLI help still exposes the first-use onboarding bootstrap inputs:
`--project-name`, `--target-root`, `--profile`, `--wrapper-root`, and repeated `--initial-goal`.

This is a narrow validation patch, not an onboarding redesign.
<!-- PATCHOPS_PATCH99_LEDGER:END -->

<!-- PATCHOPS_PATCH100_LEDGER:START -->
## Patch 100

Patch 100 adds a maintenance validation surface for the live help contract of `template`.

It proves the current CLI help still exposes the profile-aware starter-manifest inputs:
`--profile`, `--mode`, `--patch-name`, `--target-root`, `--output-path`, and `--wrapper-root`.

This is a narrow validation patch, not a template redesign.
<!-- PATCHOPS_PATCH100_LEDGER:END -->

<!-- PATCHOPS_PATCH101_LEDGER:START -->
## Patch 101

Patch 101 adds a maintenance validation surface for the live help contract of `doctor`.

It proves the current CLI help still exposes the profile-readiness inspection inputs:
`--profile` and `--target-root`.

This is a narrow validation patch, not a doctor-command redesign.
<!-- PATCHOPS_PATCH101_LEDGER:END -->

<!-- PATCHOPS_PATCH102_LEDGER:START -->
## Patch 102

Patch 102 adds a maintenance validation surface for the live help contract of `examples`.

It proves the current CLI help still exposes the bundled-example discovery input:
`--profile`.

This is a narrow validation patch, not an examples-surface redesign.
<!-- PATCHOPS_PATCH102_LEDGER:END -->

<!-- PATCHOPS_PATCH103_LEDGER:START -->
## Patch 103

Patch 103 adds a maintenance validation surface for the live help contract of `schema`.

It proves the current CLI help still exposes the stable manifest-reference surface for the `schema` command.

This is a narrow validation patch, not a schema-surface redesign.
<!-- PATCHOPS_PATCH103_LEDGER:END -->

<!-- PATCHOPS_PATCH104_LEDGER:START -->
## Patch 104

Patch 104 adds a maintenance validation surface for the live help contract of `release-readiness`.

It proves the current CLI help still exposes the readiness-report inputs:
`--wrapper-root`, `--profile`, `--core-tests-green`, and `--report-path`.

This is a narrow validation patch, not a readiness redesign.
<!-- PATCHOPS_PATCH104_LEDGER:END -->

<!-- PATCHOPS_PATCH105_LEDGER:START -->
## Patch 105

Patch 105 adds a maintenance validation surface for the `release-readiness` report artifact contract.

It proves the live command still writes a deterministic UTF-8 text artifact through `--report-path` and returns the resolved `report_path` in the JSON payload.

This is a narrow validation patch, not a readiness redesign.
<!-- PATCHOPS_PATCH105_LEDGER:END -->

<!-- PATCHOPS_PATCH106_LEDGER:START -->
## Patch 106

Patch 106 adds a maintenance validation surface for the live help contract of `profiles`.

It proves the current CLI help still exposes the profile-summary discovery inputs:
`--name` and `--wrapper-root`.

This is a narrow validation patch, not a profiles-surface redesign.
<!-- PATCHOPS_PATCH106_LEDGER:END -->

<!-- PATCHOPS_PATCH107_LEDGER:START -->
## Patch 107

Patch 107 adds a maintenance validation surface for the live help contract of `check`.

It proves the current CLI help still exposes the manifest-validation surface for `check`,
including the starter-placeholder warning before apply or verify flows.

This is a narrow validation patch, not a manifest-check redesign.
<!-- PATCHOPS_PATCH107_LEDGER:END -->

<!-- PATCHOPS_PATCH108_LEDGER:START -->
## Patch 108

Patch 108 adds a maintenance validation surface for the live help contract of `inspect`.

It proves the current CLI help still exposes the stable operator-help surface for the `inspect` command without guessing extra flags not grounded in the current uploaded sources.

This is a narrow validation patch.
<!-- PATCHOPS_PATCH108_LEDGER:END -->

<!-- PATCHOPS_PATCH109_LEDGER:START -->
## Patch 109

Patch 109 adds a maintenance validation surface for the live help contract of `plan`.

It proves the current CLI help still exposes the manifest-preview inputs:
positional `manifest`, `--wrapper-root`, `--mode`, and `--retry-reason`.

This is a narrow validation patch, not a planning-surface redesign.
<!-- PATCHOPS_PATCH109_LEDGER:END -->

<!-- PATCHOPS_PATCH110_LEDGER:START -->
## Patch 110

Patch 110 adds a maintenance validation surface for the live help contract of `apply`.

It proves the current CLI help still exposes the core execution-entry surface:
positional `manifest` and optional `--wrapper-root`.

This is a narrow validation patch, not an apply-flow redesign.
<!-- PATCHOPS_PATCH110_LEDGER:END -->

<!-- PATCHOPS_PATCH111_LEDGER:START -->
## Patch 111

Patch 111 adds a maintenance validation surface for the live help contract of `verify`.

It proves the current CLI help still exposes the core verify-only entry surface:
positional `manifest` and optional `--wrapper-root`.

This is a narrow validation patch, not a verify-flow redesign.
<!-- PATCHOPS_PATCH111_LEDGER:END -->

<!-- PATCHOPS_PATCH112_LEDGER:START -->
## Patch 112

Patch 112 adds a maintenance validation surface for the live help contract of `wrapper-retry`.

It proves the current CLI help still exposes the narrow wrapper-only retry entry surface:
positional `manifest`, optional `--wrapper-root`, and optional `--retry-reason`.

This is a narrow validation patch, not a wrapper-retry redesign.
<!-- PATCHOPS_PATCH112_LEDGER:END -->

<!-- PATCHOPS_PATCH113_LEDGER:START -->
## Patch 113

Patch 113 adds a narrow inventory validation surface for the core execution help-contract wave.

It proves the shipped CLI still exposes the three live execution-entry commands:
`apply`, `verify`, and `wrapper-retry`,
and it locks the expectation that the matching help-contract tests remain present.

This is a narrow maintenance validation patch, not a command-surface redesign.
<!-- PATCHOPS_PATCH113_LEDGER:END -->

<!-- PATCHOPS_PATCH114_LEDGER:START -->
## Patch 114

Patch 114 adds a narrow help-contract test for the root `patchops --help` surface.

It proves the top-level CLI entry still exposes the maintained operator-facing command map,
including the core execution commands, the onboarding helpers, and the planning / validation surfaces.

This is a narrow validation patch, not a CLI redesign.
<!-- PATCHOPS_PATCH114_LEDGER:END -->

<!-- PATCHOPS_PATCH115_LEDGER:START -->
## Patch 115

Patch 115 adds a narrow inventory validation surface for the maintained PowerShell launcher layer.

It proves the main thin launcher set still exists for the shipped authoring, discovery, execution,
retry, and readiness flows.

This is a narrow maintenance validation patch, not a launcher redesign.
<!-- PATCHOPS_PATCH115_LEDGER:END -->

<!-- PATCHOPS_PATCH116_LEDGER:START -->
## Patch 116

Patch 116 adds a narrow inventory validation surface for the remaining thin PowerShell launcher surfaces
that support handoff export, inspect, and schema discovery.

It proves the maintained secondary launcher set still exists:
- `Invoke-PatchHandoff.ps1`
- `Invoke-PatchInspect.ps1`
- `Invoke-PatchSchema.ps1`

This is a narrow maintenance validation patch, not a launcher redesign.
<!-- PATCHOPS_PATCH116_LEDGER:END -->

<!-- PATCHOPS_PATCH117_LEDGER:START -->
## Patch 117

Patch 117 adds a narrow parser-inventory validation surface for the maintained operator subcommand map.

It proves the shipped CLI still exposes the current operator-facing subcommands across:
execution, planning, discovery, onboarding helpers, handoff export, and release readiness.

This is a narrow maintenance validation patch, not a CLI redesign.
<!-- PATCHOPS_PATCH117_LEDGER:END -->

<!-- PATCHOPS_PATCH118_LEDGER:START -->
## Patch 118

Patch 118 adds a narrow alignment validation surface between the maintained launcher-backed CLI commands
and the thin PowerShell launcher layer.

It proves the current shipped mapping remains explicit across:
apply, verify, wrapper-retry, discovery, inspection, schema, planning, template, handoff export, and release readiness.

This is a narrow maintenance validation patch, not a CLI or launcher redesign.
<!-- PATCHOPS_PATCH118_LEDGER:END -->

<!-- PATCHOPS_PATCH119_LEDGER:START -->
## Patch 119

Patch 119 adds a narrow boundary validation surface for the maintained Python-only helper command layer.

It proves the shipped helper-first commands still exist:
- `bootstrap-target`
- `recommend-profile`
- `starter`
- `init-project-doc`
- `refresh-project-doc`

It also keeps explicit that these helper surfaces remain Python-owned rather than growing new PowerShell launchers.

This is a narrow maintenance validation patch, not an onboarding redesign.
<!-- PATCHOPS_PATCH119_LEDGER:END -->

<!-- PATCHOPS_PATCH120_LEDGER:START -->
## Patch 120

Patch 120 adds a narrow partition validation surface for the maintained operator command map.

It proves the shipped operator-facing commands still split cleanly into two explicit groups:
- launcher-backed commands,
- Python-only helper commands.

It also keeps the combined maintained operator map explicit without widening behavior.

This is a narrow maintenance validation patch, not an operator-surface redesign.
<!-- PATCHOPS_PATCH120_LEDGER:END -->

<!-- PATCHOPS_PATCH121_LEDGER:START -->
## Patch 121

Patch 121 adds a narrow validation surface for the exact thin PowerShell launcher set.

It proves the maintained launcher layer remains exactly:
- manifest
- verify
- wrapper retry
- profiles
- doctor
- examples
- schema
- check
- inspect
- plan
- template
- handoff
- readiness

This is a narrow maintenance validation patch, not a launcher redesign.
<!-- PATCHOPS_PATCH121_LEDGER:END -->

<!-- PATCHOPS_PATCH122_LEDGER:START -->
## Patch 122

Patch 122 adds a narrow documentation-validation surface for the recent operator-surface hardening wave.

It proves the maintained status docs still keep the latest operator-surface maintenance sequence explicit:
- CLI and PowerShell surface alignment,
- Python-only helper boundary,
- operator-surface partitioning,
- exact thin PowerShell launcher set.

This is a narrow maintenance validation patch, not a documentation redesign.
<!-- PATCHOPS_PATCH122_LEDGER:END -->

<!-- PATCHOPS_PATCH123_LEDGER:START -->
## Patch 123

Patch 123 adds a narrow validation surface for the exact shipped CLI subcommand set.

It proves the maintained operator-facing command surface remains exactly:
- the launcher-backed operator commands,
- plus the Python-only helper commands,
- with no unexpected CLI command drift.

This is a narrow maintenance validation patch, not a CLI redesign.
<!-- PATCHOPS_PATCH123_LEDGER:END -->

<!-- PATCHOPS_PATCH124_LEDGER:START -->
## Patch 124

Patch 124 adds a narrow documentation-validation surface for the recent exact-boundary operator-surface wave.

It proves the maintained status docs still keep the latest exact-boundary maintenance sequence explicit:
- exact thin PowerShell launcher set,
- operator-surface status documentation validation,
- exact shipped CLI subcommand set.

This is a narrow maintenance validation patch, not a documentation redesign.
<!-- PATCHOPS_PATCH124_LEDGER:END -->

<!-- PATCHOPS_PATCH125A_LEDGER:START -->
## Patch 125A

Patch 125A repairs the narrow documentation regressions exposed by the truth-reset audit.

It restores:
- the `README.md` consolidation-status wording,
- the `docs/project_status.md` late Stage 1 / pre-Stage 2 posture and exact operator-surface phrasing,
- the `docs/llm_usage.md` rule that target-repo business logic must remain outside PatchOps.

This is a narrow maintenance repair patch, not a redesign.
<!-- PATCHOPS_PATCH125A_LEDGER:END -->
<!-- PATCHOPS_PATCH125B_LEDGER:START -->
## Patch 125B

Patch 125B completes the remaining truth-reset wording repair.

It restores:
- the exact `prefer narrow repair over broad rewrite` phrase in `docs/llm_usage.md`,
- the explicit `docs/patch_ledger.md` reference in `README.md`.

This remains a narrow documentation repair patch.
<!-- PATCHOPS_PATCH125B_LEDGER:END -->

<!-- PATCHOPS_PATCH126_LEDGER:START -->
## Patch 126

Patch 126 refreshes the final self-contained documentation set that can survive loss of prior chat history.

It adds or refreshes:

- `docs/finalization_master_plan.md`
- `README.md`
- `docs/project_status.md`
- `docs/llm_usage.md`
- `docs/operator_quickstart.md`

This is an F2 documentation patch.
It is meant to restate the repo as a maintenance-mode wrapper whose remaining work is finalization, proof, and freeze rather than redesign.
<!-- PATCHOPS_PATCH126_LEDGER:END -->

<!-- PATCHOPS_PATCH127_LEDGER:START -->
## Patch 127

Patch 127 is the final contract-lock validation sweep from the rushed finalization plan.

It adds narrow tests that protect the maintenance-mode final docs introduced in Patch 126:
- `README.md`
- `docs/llm_usage.md`
- `docs/operator_quickstart.md`
- `docs/project_status.md`
- `docs/finalization_master_plan.md`

This is a validation-first maintenance patch.
It exists to lock shipped truth rather than widen behavior.
<!-- PATCHOPS_PATCH127_LEDGER:END -->

<!-- PATCHOPS_PATCH128_LEDGER:START -->
## Patch 128

Patch 128 is the F4 proof patch from the rushed finalization plan.

It does three things:
- re-exports the current handoff bundle from a real green report,
- records the generated `handoff/` outputs as maintained continuation artifacts,
- adds one narrow validation layer that proves the active-work continuation flow remains mechanical.

This is a proof-and-refresh patch, not a handoff redesign patch.
<!-- PATCHOPS_PATCH128_LEDGER:END -->

<!-- PATCHOPS_PATCH128A_LEDGER:START -->
## Patch 128A

Patch 128A repairs the two stale maintenance-doc assertions left behind after Patch 128 moved the green head from Patch 127 to Patch 128.

This patch does not change the continuation flow itself.
It only updates `tests/test_final_maintenance_mode_docs.py` so the maintenance-doc test layer matches the current post-F4 state.
<!-- PATCHOPS_PATCH128A_LEDGER:END -->

<!-- PATCHOPS_PATCH129_LEDGER:START -->
## Patch 129

Patch 129 is the F5 proof patch from the rushed finalization plan.

It proves the already-shipped new-target onboarding flow by running a current helper-first rehearsal:
- `recommend-profile`
- `init-project-doc`
- `starter`
- onboarding bootstrap artifact generation

It also adds current-state tests for the proof packet and onboarding artifacts.
<!-- PATCHOPS_PATCH129_LEDGER:END -->

<!-- PATCHOPS_PATCH129A_LEDGER:START -->
## Patch 129A

Patch 129A repairs the narrow bootstrap-artifact failure left by Patch 129.

The onboarding proof itself was already mostly successful:
- `recommend-profile` passed,
- `init-project-doc` passed,
- `starter` passed.

The only broken step was the ad hoc helper used to call bootstrap generation.
Patch 129A replaces that ad hoc proof step with the built-in `bootstrap-target` CLI surface and leaves the broader onboarding design unchanged.
<!-- PATCHOPS_PATCH129A_LEDGER:END -->

<!-- PATCHOPS_PATCH129B_LEDGER:START -->
## Patch 129B

Patch 129B repairs the narrow `bootstrap-target` CLI branch bug revealed by the onboarding proof wave.

The failure was not in onboarding design or bootstrap generation.
The failure was that the `bootstrap-target` branch tried to parse `argv[1:]` even when `main()` had been entered with `argv=None`.

Patch 129B changes that branch to use `sys.argv[1:]` in the `argv is None` case and then reruns the current onboarding proof.
<!-- PATCHOPS_PATCH129B_LEDGER:END -->

<!-- PATCHOPS_PATCH129C_LEDGER:START -->
## Patch 129C

Patch 129C completes the narrow `bootstrap-target` CLI repair.

Patch 129B fixed the `argv is None` crash.
Patch 129C fixes the remaining subcommand-token issue by ensuring the bootstrap-target branch uses `sys.argv[2:]` for module-entry invocation while preserving `argv[1:]` for direct `main([...])` calls.

This patch still does not redesign onboarding.
It only repairs the CLI argument slicing so the current onboarding artifacts can be generated through the maintained command surface.
<!-- PATCHOPS_PATCH129C_LEDGER:END -->

<!-- PATCHOPS_PATCH129D_LEDGER:START -->
## Patch 129D

Patch 129D repairs the final payload-shape mismatch in the `bootstrap-target` onboarding proof path.

The maintained onboarding bootstrap contract expects fields such as:
- `profile_name`
- `project_packet_path`
- `current_stage`
- `recommended_commands`

Patch 129D aligns the `bootstrap-target` CLI output with that existing helper contract and then reruns the onboarding proof.
<!-- PATCHOPS_PATCH129D_LEDGER:END -->

<!-- PATCHOPS_PATCH129E_LEDGER:START -->
## Patch 129E

Patch 129E completes the narrow onboarding-proof repair by routing the `bootstrap-target` CLI branch through the maintained `build_onboarding_bootstrap(...)` helper.

This avoids further payload drift between:
- the helper contract already proven in onboarding tests,
- the CLI branch used by `python -m patchops.cli bootstrap-target ...`,
- and the onboarding artifacts written under `onboarding/`.

This is still a narrow CLI repair, not an onboarding redesign.
<!-- PATCHOPS_PATCH129E_LEDGER:END -->

<!-- PATCHOPS_PATCH129F_LEDGER:START -->
## Patch 129F

Patch 129F collapses the duplicate `bootstrap-target` branches in `patchops/cli.py` into one canonical branch.

This resolves the real root cause behind the repeated onboarding-proof failures:
- one older branch still used `bootstrap_target_onboarding(...)`,
- one later branch imported `build_onboarding_bootstrap(...)`,
- the duplicated in-function import created a local-name scoping conflict,
- and the two branches drifted in payload shape.

Patch 129F keeps only one `bootstrap-target` branch and routes it through `build_onboarding_bootstrap(...)`.
<!-- PATCHOPS_PATCH129F_LEDGER:END -->

<!-- PATCHOPS_PATCH129H_LEDGER:START -->
## Patch 129H

Patch 129H aligns the new F5 proof tests with the actual current `bootstrap-target` contract already emitted by the repo.

This is a narrow test-alignment patch.
It does not change onboarding behavior.
It records that the current maintained bootstrap-target contract is sufficient to prove the onboarding flow without forcing a stronger payload schema than the shipped CLI currently guarantees.
<!-- PATCHOPS_PATCH129H_LEDGER:END -->

<!-- PATCHOPS_PATCH129I_LEDGER:START -->
## Patch 129I

Patch 129I restores the intended helper-backed onboarding bootstrap contract for the `bootstrap-target` command.

It replaces the current branch with a direct `build_onboarding_bootstrap(...)` call and restores the F5 proof tests to the intended contract:
- `profile_name`
- `project_packet_path`
- `current_stage`
- `recommended_commands`
- starter manifest `patch_name = bootstrap_verify_only`
<!-- PATCHOPS_PATCH129I_LEDGER:END -->

<!-- PATCHOPS_PATCH129J_LEDGER:START -->
## Patch 129J

Patch 129J refreshes the generated onboarding artifacts after the helper-contract restore work.

The remaining failure after Patch 129I was not a code-logic failure.
It was that `onboarding/current_target_bootstrap.json` and related artifacts had not been regenerated from the current `bootstrap-target` branch.

Patch 129J reruns the maintained onboarding bootstrap command against the current demo target and validates the refreshed artifacts.
<!-- PATCHOPS_PATCH129J_LEDGER:END -->

## Patch 130

Patch 130 adds the final release / maintenance gate surface.

It records the verified pre-gate posture after Patch 129K, appends an explicit F6 gate status block to `docs/project_status.md`, and adds `tests/test_final_release_maintenance_gate.py` so the maintained docs, handoff bundle files, project-packet examples, key profiles, and operator launchers have to exist together before the repo can be described as maintenance-ready.

This patch is intentionally narrow.
It is a gate patch, not a redesign patch.
