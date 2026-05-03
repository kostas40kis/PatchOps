# L25.27 Microsoft Edge controlled runtime archive manifest PatchOps plan broad checkpoint

L25.27 follows accepted L25.26 and acts as a broad checkpoint over the archive manifest PatchOps plan-only ladder.

Accepted L25 PatchOps-plan ladder so far:

- L25.25 archive manifest PatchOps plan authorization gate.
- L25.26 first controlled synthetic archive manifest PatchOps plan-only proof.

Allowed in L25.27:

- read back accepted L25.26 default passive path;
- read back accepted L25.26 authorized plan-only PatchOps proof;
- confirm the plan fixture is isolated from the shared preflight and inspect fixtures;
- confirm the only planned payload is `bundle/manifest.json`;
- confirm the plan command is exactly PatchOps plan-only: `py -m patchops.cli plan <temp_manifest>`;
- confirm the bounded PatchOps plan exited `0`, did not time out, returned a JSON object, and returned the expected synthetic `patch_name`, `manifest_version`, `active_profile`, `mode`, empty `target_files`, and empty `validation_commands`;
- confirm PatchOps apply, run-package, package execution, extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The isolated controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive manifest PatchOps plan remains limited to the synthetic controlled member `bundle/manifest.json`.
- PatchOps plan is the only new PatchOps CLI command invoked against the archive manifest copy.
- PatchOps apply is not invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The planned manifest is not used for package execution.
- Candidate archive is not extracted.
- No browser activity.
- No Microsoft Edge start.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No real download workflow.
- No real browser download.
- No click/download/archive-extract/PatchOps-apply/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.27"`.
- `broad_checkpoint:true`.
- `archive_manifest_patchops_plan_ladder_checkpoint:true`.
- `l25_archive_manifest_patchops_plan_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_26_default_summary.patchops_manifest_plan_performed:false`.
- `source_l25_26_authorized_summary.patchops_plan_allowed:true`.
- `source_l25_26_authorized_summary.manifest_payload_read:true`.
- `source_l25_26_authorized_summary.manifest_temp_file_written_for_plan:true`.
- `source_l25_26_authorized_summary.patchops_manifest_plan_performed:true`.
- `source_l25_26_authorized_summary.patchops_manifest_validation_performed:false`.
- `source_l25_26_authorized_summary.patchops_cli_plan_invoked_for_archive_manifest:true`.
- `source_l25_26_authorized_summary.patchops_cli_plan_exit_code:0`.
- `source_l25_26_authorized_summary.patchops_cli_plan_timed_out:false`.
- `source_l25_26_authorized_summary.patchops_cli_plan_json_object:true`.
- `source_l25_26_authorized_summary.patchops_cli_plan_patch_name:"synthetic_l25_26_patchops_plan_fixture"`.
- `accepted_patchops_plan_scope:"controlled_runtime_manifest_patchops_plan_only_no_apply_run_package_no_execution"`.
- `accepted_plan_fixture_isolated_from_preflight_and_inspect_fixtures:true`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_apply_run_package_added_by_l25_27:true`.

Next patch: L25.28 Microsoft Edge controlled runtime archive manifest PatchOps apply authorization gate.
