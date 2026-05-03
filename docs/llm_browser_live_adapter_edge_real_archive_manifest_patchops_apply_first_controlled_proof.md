# L25.29 Microsoft Edge controlled runtime archive manifest PatchOps apply first proof

L25.29 follows accepted L25.28 and performs the first controlled PatchOps apply proof over a synthetic archive manifest.

Allowed in L25.29:

- read back accepted L25.28 PatchOps-apply authorization;
- create a controlled ZIP fixture during validator setup;
- open the isolated controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- parse that synthetic manifest only to enforce a zero-write and zero-validation guard;
- write those bytes to a bounded runtime temporary manifest file under `data/runtime/browser_downloads/l25_29_patchops_apply/`;
- invoke exactly one bounded PatchOps apply command: `py -m patchops.cli apply <temp_manifest>`;
- record the PatchOps apply exit code, timeout flag, PASS marker, and synthetic patch name marker;
- keep PatchOps run-package, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The isolated controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive manifest PatchOps apply is allowed only with explicit flag and token.
- The only applied payload is the synthetic controlled member `bundle/manifest.json`.
- The synthetic manifest must be zero-write and zero-validation before PatchOps apply is invoked.
- PatchOps apply is the only new PatchOps CLI command invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The applied synthetic manifest is not used for package execution.
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

L25.29 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_APPLY_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.29"`.
- `source_l25_28_summary.ok:true`.
- `source_l25_28_summary.future_patchops_apply_authorized:true`.
- default passive readback has `patchops_manifest_apply_performed:false`.
- authorized readback has `archive_manifest_patchops_apply_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_payload_json_parsed:true`.
- authorized readback has `manifest_zero_write_zero_validation:true`.
- authorized readback has `manifest_temp_file_written_for_apply:true`.
- authorized readback has `patchops_manifest_apply_performed:true`.
- authorized readback has `patchops_manifest_validation_performed:false`.
- authorized readback has `patchops_cli_apply_invoked_for_archive_manifest:true`.
- authorized readback has `patchops_cli_apply_exit_code:0`.
- authorized readback has `patchops_cli_apply_timed_out:false`.
- authorized readback has `patchops_cli_apply_stdout_result_pass:true`.
- authorized readback has `patchops_cli_apply_patch_name:"synthetic_l25_29_patchops_apply_fixture"`.
- `patchops_apply_scope:"controlled_runtime_manifest_patchops_apply_only_zero_write_zero_validation_no_run_package_no_package_execution"`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_run_package_added_by_l25_29:true`.

Next patch: L25.30 Microsoft Edge controlled runtime archive manifest PatchOps apply broad checkpoint.
