# L25.30 Microsoft Edge controlled runtime archive manifest PatchOps apply broad checkpoint

L25.30 follows accepted L25.29 and acts as a broad checkpoint over the archive manifest PatchOps apply-only ladder.

Accepted L25 PatchOps-apply ladder so far:

- L25.28 archive manifest PatchOps apply authorization gate.
- L25.29 first controlled synthetic archive manifest PatchOps apply-only proof.

Allowed in L25.30:

- read back accepted L25.29 default passive path;
- read back accepted L25.29 authorized apply-only PatchOps proof;
- confirm the apply fixture is isolated from the shared preflight, inspect, and plan fixtures;
- confirm the only applied payload is `bundle/manifest.json`;
- confirm the manifest is zero-write and zero-validation before PatchOps apply is invoked;
- confirm the apply command is exactly PatchOps apply-only: `py -m patchops.cli apply <temp_manifest>`;
- confirm the bounded PatchOps apply exited `0`, did not time out, returned a PASS marker, and returned the expected synthetic patch name marker;
- confirm PatchOps run-package, package execution, extraction, browser, pasteback, and package-run remain inactive.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The isolated controlled runtime ZIP fixture is the only archive path used by this checkpoint.
- Archive manifest PatchOps apply remains limited to the synthetic controlled member `bundle/manifest.json`.
- The synthetic manifest must be zero-write and zero-validation before PatchOps apply is invoked.
- PatchOps apply is the only new PatchOps CLI command invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The applied manifest is not used for package execution.
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
- No click/download/archive-extract/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.30"`.
- `broad_checkpoint:true`.
- `archive_manifest_patchops_apply_ladder_checkpoint:true`.
- `l25_archive_manifest_patchops_apply_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_29_default_summary.patchops_manifest_apply_performed:false`.
- `source_l25_29_authorized_summary.patchops_apply_allowed:true`.
- `source_l25_29_authorized_summary.manifest_payload_read:true`.
- `source_l25_29_authorized_summary.manifest_payload_json_parsed:true`.
- `source_l25_29_authorized_summary.manifest_zero_write_zero_validation:true`.
- `source_l25_29_authorized_summary.manifest_temp_file_written_for_apply:true`.
- `source_l25_29_authorized_summary.patchops_manifest_apply_performed:true`.
- `source_l25_29_authorized_summary.patchops_manifest_validation_performed:false`.
- `source_l25_29_authorized_summary.patchops_cli_apply_invoked_for_archive_manifest:true`.
- `source_l25_29_authorized_summary.patchops_cli_apply_exit_code:0`.
- `source_l25_29_authorized_summary.patchops_cli_apply_timed_out:false`.
- `source_l25_29_authorized_summary.patchops_cli_apply_stdout_result_pass:true`.
- `source_l25_29_authorized_summary.patchops_cli_apply_patch_name:"synthetic_l25_29_patchops_apply_fixture"`.
- `accepted_patchops_apply_scope:"controlled_runtime_manifest_patchops_apply_only_zero_write_zero_validation_no_run_package_no_package_execution"`.
- `accepted_apply_fixture_isolated_from_preflight_inspect_and_plan_fixtures:true`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_run_package_added_by_l25_30:true`.

Next patch: L25.31 Microsoft Edge controlled runtime archive manifest package-run authorization gate.
