# Examples

Start from examples and adapt them.

## Maintained examples

### trader code patch example
- `examples/trader_code_patch.json`

### trader verification-only example
- `examples/trader_first_verify_patch.json`
- `powershell/invoke-patchverify.ps1`

### generic python example
- `examples/generic_python_patch.json`

### documentation-only example
- `examples/trader_first_doc_patch.json`

### extra maintained examples
- `examples/generic_verify_patch.json`
- `examples/generic_allowed_exit_patch.json`
- `examples/generic_smoke_audit_patch.json`
- `examples/generic_content_path_patch.json`

## Handoff-first continuation examples

Handoff-first continuation examples belong beside the maintained examples.
project packet guidance complements examples; examples remain the baseline.
Do not fall back to stale example or starter-surface names.
- emit-operator-script remains a current maintained surface when operator-facing launcher emission is needed.

## content_path resolution rule

content_path resolution rule:
files_to_write entries use wrapper-relative paths from the wrapper project root.

## Pythonization maintenance alignment

pythonization maintenance alignment remains a documentation note, not a redesign request.

Current operator/bootstrap surfaces also include setup-windows-env alongside emit-operator-script.

Treat historical zip-first/Python-heavier stream summaries as background context, not as the current live frontier.

## Start narrower

Prefer the smallest example that proves the seam you are exercising.

Current maintained examples include:
- `examples/generic_python_powershell_patch.json`
- `examples/trader_first_verify_patch.json`

Treat examples as operator guidance, not as a second command surface.
- Show `allowed_exit_codes` where a validation command is expected to tolerate more than exit `0`.
- Keep examples aligned with the wrapper-relative `content_path` rule.
- `examples/generic_allowed_exit_patch.json` shows `allowed_exit_codes`.
- `examples/generic_smoke_audit_patch.json` shows smoke and audit command grouping.
- `examples/generic_content_path_patch.json` stages `generic_content_path_note.txt` to prove wrapper-relative content sources.
- Examples should describe the modular package layout rather than implying a flat single-file surface.
Use wrapper-relative paths from the wrapper project root for `content_path`.
If the runtime is reading older material, it falls back to manifest-local resolution, but wrapper-relative paths from the wrapper project root are the maintained rule.
If you are uncertain, start narrower.
That is the intended starting surface for practical PatchOps usage.
The compatibility fallback, not the primary authoring rule, is only for older material that still expects manifest-local resolution.
Examples should reinforce the one canonical truth rule.
Examples should follow a code-first / docs-last process rather than letting docs lead code changes.

Examples are no longer the first state-reconstruction surface.
Start from examples and adapt them.
If you are uncertain, start narrower.
That is the intended starting surface for practical PatchOps usage.

PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:START
Examples remain maintained examples, not the only state-reconstruction surface.
Use recommend-profile --target-root to pick the nearest safe starting point.
Then use starter --profile for generic patchops orientation before deeper target-specific work.
PATCHOPS_PATCH84_EXAMPLES_STARTER_GUIDANCE:END

### Starter guidance wording lock
Use examples as the baseline before deeper target-specific customization.

PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:START

## Handoff-first continuation examples
Use `py -m patchops.cli export-handoff` when handing off already-running PatchOps work.

## Onboarding bootstrap examples
- onboarding/current_target_bootstrap.md
- onboarding/current_target_bootstrap.json
- onboarding/next_prompt.txt
- onboarding/starter_manifest.json
- handoff = continuation of already-running patchops work

## Examples boundary
- project packet
- docs/projects/
- examples remain the baseline
- check
- inspect
- plan
- run-package
- pythonization maintenance alignment
- opt-in

<!-- PATCHOPS_E4A_EXAMPLES_GENERIC_POWERSHELL_VERIFY_REFRESH_20260423 -->
examples/generic_python_powershell_verify_patch.json

PATCHOPS_F7_FINAL_DOC_STOP_EXAMPLES:END

## Targeted examples additions
handoff/current_handoff.md
maintenance-facing

<!-- PATCHOPS_E4B_EXAMPLES_GENERIC_APPLY_BUNDLE_PATH_LOCK_20260423 -->
examples/bundles/generic_apply_bundle/

<!-- PATCHOPS_E4C_EXAMPLES_GENERIC_VERIFY_BUNDLE_PATH_LOCK_20260423 -->
examples/bundles/generic_verify_bundle/

<!-- PATCHOPS_E6_EXAMPLES_PROJECT_PACKET_AND_ONBOARDING_LOCK_20260423 -->
onboarding bootstrap examples
onboarding/current_target_bootstrap.md
onboarding/current_target_bootstrap.json
onboarding/next_prompt.txt
onboarding/starter_manifest.json
handoff = continuation of already-running patchops work
examples/bundles/generic_apply_bundle/
examples/bundles/generic_verify_bundle/

<!-- PATCHOPS_E7_EXAMPLES_ONBOARDING_HELPER_DOCS_LOCK_20260423 -->
## Onboarding bootstrap examples addendum

onboarding bootstrap examples
onboarding/current_target_bootstrap.md
onboarding/current_target_bootstrap.json
onboarding/next_prompt.txt
onboarding/starter_manifest.json
handoff = continuation of already-running PatchOps work
examples/bundles/generic_apply_bundle/
examples/bundles/generic_verify_bundle/

<!-- PATCHOPS_G3_EXAMPLES_PYTHONIZATION_ALIGNMENT_20260423 -->
## Pythonization maintenance alignment note

pythonization maintenance alignment
opt-in
maintenance-facing
low-risk

<!-- PATCHOPS_G3A_EXAMPLES_DEFAULT_BEHAVIOR_PHRASE_LOCK_20260423 -->
## Pythonization maintenance alignment default-behavior addendum

not a mandatory default behavior

<!-- PATCHOPS_H2_HANDOFF_EXAMPLES_JSON_SURFACE_LOCK_20260423 -->
## Handoff-first continuation examples addendum

handoff/current_handoff.json

<!-- PATCHOPS_H2B_EXAMPLES_HANDOFF_LATEST_REPORT_COPY_LOCK_20260423 -->
## Handoff-first continuation examples latest-report addendum

handoff/latest_report_copy.txt

<!-- PATCHOPS_H2C_EXAMPLES_LATEST_REPORT_INDEX_LOCK_20260423 -->
## Handoff-first continuation examples latest-report index addendum

handoff/latest_report_index.json

<!-- PATCHOPS_H2D_EXAMPLES_NEXT_PROMPT_LOCK_20260423 -->
## Handoff-first continuation examples next-prompt addendum

handoff/next_prompt.txt

<!-- PATCHOPS_H2E_EXAMPLES_HANDOFF_BUNDLE_CURRENT_LOCK_20260423 -->
## Handoff-first continuation examples bundle-current addendum

handoff/bundle/current/

<!-- PATCHOPS_H2F_EXAMPLES_NEW_TARGET_BOUNDARY_LOCK_20260423 -->
## Handoff-first continuation examples brand-new-target boundary addendum

Do **not** use handoff as the first step when the job is to onboard a brand-new target project.

<!-- PATCHOPS_H2G_EXAMPLES_PROJECT_PACKET_CONTRACT_LOCK_20260423 -->
## Handoff-first continuation examples project-packet contract addendum

project packet = maintained target-facing contract

<!-- PATCHOPS_H2H_EXAMPLES_REPORT_EVIDENCE_LOCK_20260423 -->
## Handoff-first continuation examples report-evidence addendum

report = evidence of what happened.
