# PatchOps operator quickstart

This guide is the shortest safe path for using PatchOps in a real workspace.

## Recommended Stage 1 flow

1. Run `patchops profiles` or `Invoke-PatchProfiles.ps1` to see available profiles.
2. Run `patchops doctor --profile <name>` or `Invoke-PatchDoctor.ps1` to confirm the environment is ready.
3. Run `patchops examples` or `Invoke-PatchExamples.ps1` to find the closest bundled example.
4. Run `patchops template` or `Invoke-PatchTemplate.ps1` to generate a starter manifest.
5. Replace placeholder paths, content, and commands in the manifest.
6. Run `patchops check <manifest>` to catch starter placeholders before real execution.
7. Run `patchops inspect <manifest>` to see normalized JSON.
8. Run `patchops plan <manifest>` to preview target root, runtime, report path, backup path, and command groups.
9. Run `patchops apply <manifest>` for real patch execution, or `patchops verify <manifest>` for narrow validation-only reruns.

## Safer first proving order

Use a throwaway generic target before touching trader.

- Start with `examples/generic_python_patch.json`
- Then prove backups with `examples/generic_backup_patch.json`
- Then practice narrow reruns with `examples/generic_verify_patch.json`
- Only after that should you move to trader-oriented examples

## When to use verify-only reruns

Use verify-only reruns when patch content is already correct and you only need a narrower validation pass or cleaner evidence.

## When to stop and repair the wrapper

If the target repo commands already pass but the report, launcher, quoting, or wrapper plumbing fails, treat it as a wrapper-only repair instead of reworking the target patch.

<!-- PATCHOPS_PATCH76_PROJECT_PACKET_AWARE_QUICKSTART:START -->
## Project-packet-aware usage

PatchOps now has two closely related but different starting paths.

### Already-running PatchOps continuation

If work is already in progress, begin with:

- `handoff/current_handoff.md`
- `handoff/current_handoff.json`
- `handoff/latest_report_copy.txt`

Then perform the exact next recommended action.
If the work is target-specific, also read the relevant packet under `docs/projects/`.

### Brand-new target onboarding

If the target project is new, begin with the generic PatchOps packet:

- `README.md`
- `docs/overview.md`
- `docs/llm_usage.md`
- `docs/manifest_schema.md`
- `docs/profile_system.md`
- `docs/compatibility_notes.md`
- `docs/failure_repair_guide.md`
- `docs/examples.md`
- `docs/project_status.md`
- `docs/operator_quickstart.md`
- `docs/project_packet_contract.md`
- `docs/project_packet_workflow.md`

Then create or refresh `docs/projects/<project_name>.md`, choose the smallest correct profile, pick the closest example manifest, run `check`, `inspect`, and `plan`, and only then `apply` or `verify`.
<!-- PATCHOPS_PATCH76_PROJECT_PACKET_AWARE_QUICKSTART:END -->

<!-- PATCH_79_SELF_HOSTED_QUICKSTART_START -->
## Patch 79 - project-packet operator commands

Use the Python CLI for packet work. Do not duplicate reusable packet logic in PowerShell.

### Create a new target packet

```powershell
py -m patchops.cli init-project-doc --project-name "Wrapper Self Hosted" --target-root C:\dev\patchops --profile generic_python --initial-goal "Keep PowerShell thin" --initial-goal "Use the CLI for packet work"
```

### Refresh a maintained packet after a run

```powershell
py -m patchops.cli refresh-project-doc --name wrapper_self_hosted --wrapper-root C:\dev\patchops
```

### Re-export the handoff bundle after the canonical report exists

```powershell
py -m patchops.cli export-handoff --wrapper-root C:\dev\patchops
```

### Simple operator rule

- project packet = target-level memory surface
- handoff bundle = run-level resume surface
- one canonical report remains required
<!-- PATCH_79_SELF_HOSTED_QUICKSTART_END -->

<!-- PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:START -->
## Project-packet command quickstart

For project-packet work, keep the flow mechanical:

1. Use `init-project-doc` to scaffold a brand-new packet from explicit inputs.
2. Use `refresh-project-doc` to update mutable packet state after a validated run.
3. Keep `docs/projects/wrapper_self_hosted.md` as the self-hosted reference packet for PatchOps itself.
4. Still produce one canonical report for every run.
5. Treat wrapper/report failures as wrapper-only repairs rather than rewriting target content.

### Command examples

```text
py -m patchops.cli init-project-doc --project-name demo_project --target-root C:\dev\demo --profile generic_python
py -m patchops.cli refresh-project-doc --name wrapper_self_hosted
```
<!-- PATCHOPS_PATCH80_PROJECT_PACKET_COMMANDS:END -->

<!-- PATCHOPS_PATCH87_OPERATOR_QUICKSTART:START -->
## Handoff-first continuation quickstart

Use this path when PatchOps work is already in progress.

1. Run `py -m patchops.cli export-handoff --report-path <latest_report> --wrapper-root <wrapper_root>`
2. Upload the generated files under `handoff/`
3. Paste `handoff/next_prompt.txt` into the next LLM session
4. Let the next LLM continue from the exact next recommended action

This is the default continuation flow.

Use the generic onboarding packet and project packets only when the task is to start a brand-new target project with PatchOps.
<!-- PATCHOPS_PATCH87_OPERATOR_QUICKSTART:END -->

<!-- PATCHOPS_PATCH89B_QUICKSTART:START -->
### Boundary reminder

Use handoff first for **already-running PatchOps work**.

Use the generic onboarding packet first for **brand-new target onboarding**.

If the task is target-specific after continuation or onboarding, also use the relevant project packet under `docs/projects/`.
<!-- PATCHOPS_PATCH89B_QUICKSTART:END -->
\n\n<!-- PATCHOPS_PATCH91_QUICKSTART:START -->
## Onboarding helper reminder

For a brand-new target project, the operator can now use a helper-first onboarding path:

- `recommend-profile`
- `init-project-doc`
- `starter`
- onboarding bootstrap artifacts
- `refresh-project-doc`

This path is for onboarding only.
For already-running PatchOps work, use handoff first.
<!-- PATCHOPS_PATCH91_QUICKSTART:END -->\n\n<!-- PATCHOPS_PATCH92_QUICKSTART:START -->
## Onboarding bootstrap reminder

For a brand-new target project, onboarding bootstrap artifacts can shorten the first-use path.

Look for:

- `onboarding/current_target_bootstrap.md`
- `onboarding/current_target_bootstrap.json`
- `onboarding/next_prompt.txt`
- `onboarding/starter_manifest.json`

For already-running PatchOps work, use handoff first instead.
<!-- PATCHOPS_PATCH92_QUICKSTART:END -->\n