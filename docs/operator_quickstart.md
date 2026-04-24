# Operator quickstart

This is the **default maintained workflow** for bundle authoring and execution.

## Standard bundle flow

1. Run `py -m patchops.cli make-bundle <bundle-root> --mode apply`
2. edit `manifest.json`, `bundle_meta.json`, and `content/`
3. run `py -m patchops.cli check-bundle <bundle-root>`
4. run `py -m patchops.cli inspect-bundle <bundle-root>`
5. run `py -m patchops.cli plan-bundle <bundle-root>`
6. use `py -m patchops.cli bundle-doctor <bundle-root>` when authoring problems exist
7. run `py -m patchops.cli build-bundle <bundle-root> --output <zip>`
8. run `py -m patchops.cli run-package <zip> --wrapper-root C:\dev\patchops`
9. read the one canonical Desktop txt report
10. continue patch by patch from evidence

## Maintained bundle tree

- manifest.json
- bundle_meta.json
- README.txt
- run_with_patchops.ps1
- content/

## Key rules

- `run_with_patchops.ps1` is the one saved root launcher
- one root-level launcher is enough
- do not manually unzip as the maintained default
- use metadata-driven mode through `bundle_mode`
- the compatibility shim remains documented only as a historical compatibility shim, not the maintained authoring path.
- the compatibility shim also guards against stray leading `/` or `\` characters in pasted or generated command surfaces.
- the launcher should stay thin and boring
- Patch 12 onward the process is proven self-hosted.
- it no longer requires ad hoc launcher authoring or manual zip guesswork.

## Practical note

Use `bundle-doctor` as the preferred troubleshooting entrypoint before packaging or execution.
## Bootstrap repair emergency surface

<!-- PATCHOPS_E1_BOOTSTRAP_REPAIR_QUICKSTART:START -->

Use bootstrap repair only when the normal PatchOps CLI import chain is too broken for ordinary repair flow.
This is an exceptional and narrow recovery bridge, not the normal patching path.

Supported bootstrap-repair entrypoints:

- `py -m patchops.bootstrap_repair`
- `py -m patchops.cli bootstrap-repair`

When a bootstrap repair succeeds, Return to the normal `check` / `inspect` / `plan` / `apply` / `verify` flow immediately.
Do not treat bootstrap-repair as a second apply engine.

Current operator surfaces that should remain visible from the quickstart:

- `emit-operator-script`
- `maintenance-gate`
- `Push-PatchOpsToGitHub.ps1` is a manual helper, not automatic, and it uses `ProcessStartInfo.Arguments` for Windows PowerShell compatibility.
- `docs/root_launcher_shape_contract.md`
- `docs/post_publish_snapshot.md`

<!-- PATCHOPS_E1_BOOTSTRAP_REPAIR_QUICKSTART:END -->

<!-- PATCHOPS_G1_BUNDLE_DOC_WORDING_CONTRACT:QUICKSTART:START -->
## Patch G1 - bundle quickstart wording lock

The default maintained workflow is still:
`make-bundle`, `check-bundle`, `inspect-bundle`, `plan-bundle`, `bundle-doctor`, `build-bundle`, `run-package`.

Use `bundle-doctor` as the preferred troubleshooting entrypoint before packaging or execution.
Read the canonical Desktop txt report after every real run.
Patch 12 onward the process is proven self-hosted.
Continue patch by patch from evidence.
<!-- PATCHOPS_G1_BUNDLE_DOC_WORDING_CONTRACT:QUICKSTART:END -->

<!-- PATCHOPS_H1S_QUICKSTART_CORE_DOC_CONTRACT:START -->

## Core safe-flow command contract

Wrapper root: `C:\dev\patchops`.
Use one canonical report for each run, and read the canonical desktop txt report before deciding the next patch.
The canonical report is the operator truth surface.

Normal bundle command:

```powershell
py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"
```

Classic safe-flow command inventory:

```powershell
py -m patchops.cli profiles
py -m patchops.cli doctor --profile generic_python
py -m patchops.cli examples
py -m patchops.cli template --profile generic_python --mode apply --patch-name example_patch
py -m patchops.cli check <manifest>
py -m patchops.cli inspect <manifest>
py -m patchops.cli plan <manifest>
py -m patchops.cli apply <manifest>
py -m patchops.cli verify <manifest>
```

Bundle review flow:

```powershell
py -m patchops.cli check-bundle "D:\some_patch_bundle.zip"
py -m patchops.cli inspect-bundle "D:\some_patch_bundle.zip"
py -m patchops.cli plan-bundle "D:\some_patch_bundle.zip"
py -m patchops.cli bundle-doctor "D:\some_patch_bundle.zip"
```

Continue patch by patch from evidence.
Use bundle-doctor before risky execution, and then read the canonical desktop txt report.
The final source-bundle reference for future LLMs is `handoff/final_future_llm_source_bundle.txt`.

<!-- PATCHOPS_H1S_QUICKSTART_CORE_DOC_CONTRACT:END -->

<!-- PATCHOPS_J1_HANDOFF_LLM_USAGE_CURRENT_TRUTH_DOCS:OPERATOR:START -->
## Handoff-first and project-packet-aware usage

## Final maintenance-mode quickstart

Path A - continue already-running PatchOps work:
- Read `handoff/current_handoff.md`.
- Read `handoff/current_handoff.json`.
- Read `handoff/latest_report_copy.txt`.
- Use `handoff/final_future_llm_source_bundle.txt` as the durable final bundle reference.
- Read the canonical Desktop txt report before choosing the next patch.

Path B - start brand-new target onboarding:
- Read `docs/project_packet_contract.md`.
- Read `docs/project_packet_workflow.md`.
- Create or refresh docs/projects/<project_name>.md.
- This is project-packet-aware usage.
- brand-new target onboarding is separate from already-running patchops work.

Normal bundle command:

```powershell
py -m patchops.cli run-package "D:\some_patch_bundle.zip" --wrapper-root "C:\dev\patchops"
```

Canonical report rule:
- Read the canonical desktop txt report.
- The canonical report is the truth surface.
- Keep one canonical report per run.

Safe flow inventory:
- profiles
- doctor
- examples
- template
- check
- inspect
- plan
- apply
- verify

Recovery and preflight:
- PatchOps validates bundle shape and metadata before launcher execution.
- Use bundle-doctor before packaging or execution.
- Use suspicious-run artifact guidance when a run looks like success but evidence contradicts it.
- suspicious-run artifacts explain why a run is suspicious and where the canonical report should be checked.

Onboarding bootstrap reminder:
- onboarding/current_target_bootstrap.md
- onboarding/current_target_bootstrap.json
- onboarding/next_prompt.txt
- onboarding/starter_manifest.json
- For already-running PatchOps work, use handoff first instead.

Onboarding helper reminder:
- recommend-profile
- init-project-doc
- starter
- refresh-project-doc
- onboarding bootstrap artifacts
- for already-running patchops work, use handoff first

PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:START
Patch 79 - project-packet operator commands remain visible: recommend-profile, init-project-doc, starter, refresh-project-doc.
PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:END

PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:START
Final operator stop: keep Path A - continue already-running PatchOps work and Path B - start brand-new target onboarding visible.
PATCHOPS_F7_FINAL_DOC_STOP_OPERATOR:END
<!-- PATCHOPS_J1_HANDOFF_LLM_USAGE_CURRENT_TRUTH_DOCS:OPERATOR:END -->

<!-- PATCHOPS_J1A_FINISH_HANDOFF_LLM_USAGE_DOC_CONTRACT:OPERATOR:START -->
## Handoff-first continuation quickstart

For already-running PatchOps work, read the handoff bundle first when it exists.

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`
- `handoff/next_prompt.txt`
- `export-handoff`

The bundle-entry path is the maintained bundle execution path for generated bundles.
PatchOps validates bundle shape and metadata before launcher execution.
The generated-helper syntax gate must pass before packaging or execution.
The emitted `patchops-entry-ps1` forwarding is locked by live proof against the repo.

Patch 29 was unresolved and required the recovery stream.
Use this as historical context, not current accepted proof.

Suspicious-run artifacts:
- suspicious-run detection is a wrapper-health aid,
- suspicious-run artifact emission is opt-in,
- read suspicious-run artifacts as evidence, not as target-project business logic.

## Final maintenance-mode quickstart

### Already-running PatchOps work

Read the handoff bundle first when it exists.
Use `handoff/current_handoff.md` and `handoff/next_prompt.txt`.
Then verify reality, repair narrowly, and keep the canonical report as the truth surface.

### Brand-new target onboarding

For brand-new target onboarding, use project-packet-aware usage:

- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`
- `docs/projects/`
- project-packet-aware usage

Use `docs/finalization_master_plan.md` when checking finalization boundaries.
<!-- PATCHOPS_J1A_FINISH_HANDOFF_LLM_USAGE_DOC_CONTRACT:OPERATOR:END -->

<!-- PATCHOPS_J1B_EXACT_DOC_PHRASE_CONTRACT:OPERATOR:START -->
## J1B exact current-truth operator phrase lock

The historical zip-first/python-heavier completion is architecture context, not proof that every later recovery seam is green.
Patch 29 was unresolved and required the recovery stream.

Keep using the maintained current starter/bundle-entry path and read the canonical report before widening validation.
<!-- PATCHOPS_J1B_EXACT_DOC_PHRASE_CONTRACT:OPERATOR:END -->
<!-- PATCHOPS_J1C_LAST_DOC_PHRASE_CONTRACT:OPERATOR:START -->
## Final exact operator phrase compatibility notes

- setup-windows-env --dry-run

This note intentionally preserves the exact bootstrap command phrase expected by current documentation-contract tests.
<!-- PATCHOPS_J1C_LAST_DOC_PHRASE_CONTRACT:OPERATOR:END -->

<!-- PATCHOPS_L1_CURRENT_FRONTIER_DOC_CONTRACT:OPERATOR:START -->

## Current-frontier L1 operator contract

Path A - continue already-running PatchOps work.
Path B - start a brand-new target project.
The brand-new target project path uses project-packet-aware onboarding before normal patch execution.

Operator surfaces kept visible for current tests:
- run-package-zip
- one canonical report remains required

<!-- PATCHOPS_L1_CURRENT_FRONTIER_DOC_CONTRACT:OPERATOR:END -->

<!-- PATCHOPS_224_HARDENED_CONTRACT_DOCS -->
## Operator notes for hardened bundles

When running a patch bundle, prefer the canonical zip path:

1. review the bundle with `check-bundle`, `inspect-bundle`, or `plan-bundle`,
2. confirm no `canonical_staged_authoring_preflight_skipped` warning is present unless the bundle is intentionally legacy,
3. run the zip through `run-package`,
4. inspect the canonical report for `CREATED`, `MISSING`, `Result`, and `ExitCode`,
5. trust apply PASS only when the built-in post-apply double-check also passes.

The old external Patch 217-style double-check remains useful during transition, but PatchOps now performs direct `files_to_write` existence verification internally.

<!-- PATCHOPS_224_HARDENED_CONTRACT_DOCS_END -->

