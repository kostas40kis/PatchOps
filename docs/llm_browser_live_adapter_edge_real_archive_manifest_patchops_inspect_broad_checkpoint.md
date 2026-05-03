# L25.24 Microsoft Edge controlled runtime archive manifest PatchOps inspect broad checkpoint

L25.24 follows accepted L25.23 plus L25.23a and acts as a broad checkpoint over the archive manifest PatchOps inspect-only ladder.

Accepted L25 PatchOps-inspect ladder so far:

- L25.22 archive manifest PatchOps inspect authorization gate.
- L25.23 first controlled synthetic archive manifest PatchOps inspect-only proof.
- L25.23a isolated inspect fixture repair.

Allowed in L25.24:

- read back accepted L25.23 default passive path;
- read back accepted L25.23 authorized inspect-only PatchOps proof;
- confirm the inspect fixture is isolated from the shared L25.20/L25.21 preflight fixture;
- confirm the only inspected payload is `bundle/manifest.json`;
- confirm the inspect command is exactly PatchOps inspect-only: `py -m patchops.cli inspect <temp_manifest>`;
- confirm the bounded PatchOps inspect exited `0`, did not time out, returned a JSON object, and returned the expected synthetic `patch_name`, `manifest_version`, and `active_profile`;
- confirm PatchOps plan, apply, run-package, package execution, extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The isolated controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive manifest PatchOps inspect remains limited to the synthetic controlled member `bundle/manifest.json`.
- PatchOps inspect is the only new PatchOps CLI command invoked against the archive manifest copy.
- PatchOps plan is not invoked against the archive manifest copy.
- PatchOps apply is not invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The inspected manifest is not used for package execution.
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
- No click/download/archive-extract/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.24"`.
- `broad_checkpoint:true`.
- `archive_manifest_patchops_inspect_ladder_checkpoint:true`.
- `l25_archive_manifest_patchops_inspect_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_23_default_summary.patchops_manifest_inspect_performed:false`.
- `source_l25_23_authorized_summary.patchops_inspect_allowed:true`.
- `source_l25_23_authorized_summary.manifest_payload_read:true`.
- `source_l25_23_authorized_summary.manifest_temp_file_written_for_inspect:true`.
- `source_l25_23_authorized_summary.patchops_manifest_inspect_performed:true`.
- `source_l25_23_authorized_summary.patchops_manifest_validation_performed:false`.
- `source_l25_23_authorized_summary.patchops_cli_inspect_invoked_for_archive_manifest:true`.
- `source_l25_23_authorized_summary.patchops_cli_inspect_exit_code:0`.
- `source_l25_23_authorized_summary.patchops_cli_inspect_timed_out:false`.
- `source_l25_23_authorized_summary.patchops_cli_inspect_json_object:true`.
- `source_l25_23_authorized_summary.patchops_cli_inspect_patch_name:"synthetic_l25_23_patchops_inspect_fixture"`.
- `accepted_patchops_inspect_scope:"controlled_runtime_manifest_patchops_inspect_only_no_plan_apply_run_package_no_execution"`.
- `accepted_inspect_fixture_isolated_from_preflight_fixture:true`.
- `patchops_cli_plan_invoked_for_archive_manifest:false`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_plan_apply_run_package_added_by_l25_24:true`.

Next patch: L25.25 Microsoft Edge controlled runtime archive manifest PatchOps plan authorization gate.
