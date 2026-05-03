# L25.26 Microsoft Edge controlled runtime archive manifest PatchOps plan first proof

L25.26 follows accepted L25.25 and performs the first controlled PatchOps plan proof over a synthetic archive manifest.

Allowed in L25.26:

- read back accepted L25.25 PatchOps-plan authorization;
- create a controlled ZIP fixture during validator setup;
- open the isolated controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- write those bytes to a bounded runtime temporary manifest file under `data/runtime/browser_downloads/l25_26_patchops_plan/`;
- invoke exactly one bounded PatchOps plan command: `py -m patchops.cli plan <temp_manifest>`;
- record the PatchOps plan exit code, timeout flag, parsed JSON-object marker, `patch_name`, `manifest_version`, `active_profile`, `mode`, `target_files`, and `validation_commands`;
- keep PatchOps apply, PatchOps run-package, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The isolated controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive manifest PatchOps plan is allowed only with explicit flag and token.
- The only planned payload is the synthetic controlled member `bundle/manifest.json`.
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

L25.26 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_PLAN_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.26"`.
- `source_l25_25_summary.ok:true`.
- `source_l25_25_summary.future_patchops_plan_authorized:true`.
- default passive readback has `patchops_manifest_plan_performed:false`.
- authorized readback has `archive_manifest_patchops_plan_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_temp_file_written_for_plan:true`.
- authorized readback has `patchops_manifest_plan_performed:true`.
- authorized readback has `patchops_manifest_validation_performed:false`.
- authorized readback has `patchops_cli_plan_invoked_for_archive_manifest:true`.
- authorized readback has `patchops_cli_plan_exit_code:0`.
- authorized readback has `patchops_cli_plan_timed_out:false`.
- authorized readback has `patchops_cli_plan_json_object:true`.
- authorized readback has `patchops_cli_plan_patch_name:"synthetic_l25_26_patchops_plan_fixture"`.
- authorized readback has `patchops_cli_plan_mode:"apply"`.
- authorized readback has `patchops_cli_plan_target_files:[]`.
- authorized readback has `patchops_cli_plan_validation_commands:[]`.
- `patchops_plan_scope:"controlled_runtime_manifest_patchops_plan_only_no_apply_run_package_no_execution"`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_apply_run_package_added_by_l25_26:true`.

Next patch: L25.27 Microsoft Edge controlled runtime archive manifest PatchOps plan broad checkpoint.
