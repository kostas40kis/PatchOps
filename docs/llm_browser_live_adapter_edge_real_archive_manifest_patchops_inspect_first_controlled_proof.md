# L25.23 Microsoft Edge controlled runtime archive manifest PatchOps inspect first proof

L25.23 follows accepted L25.22 and performs the first controlled PatchOps inspect proof over a synthetic archive manifest.

L25.23a repairs fixture isolation. The inspect proof now uses its own isolated controlled archive fixture path under `data/runtime/browser_downloads/l25_23_patchops_inspect/`, while the shared L25.20/L25.21 preflight fixture remains separate for L25.22 source-chain readback.

Allowed in L25.23:

- read back accepted L25.22 PatchOps-inspect authorization;
- create a controlled ZIP fixture during validator setup;
- open the isolated controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- write those bytes to a bounded runtime temporary manifest file under `data/runtime/browser_downloads/l25_23_patchops_inspect/`;
- invoke exactly one bounded PatchOps inspect command: `py -m patchops.cli inspect <temp_manifest>`;
- record the PatchOps inspect exit code, timeout flag, parsed JSON-object marker, `patch_name`, `manifest_version`, and `active_profile`;
- keep PatchOps plan, PatchOps apply, PatchOps run-package, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The isolated controlled runtime ZIP fixture is the only archive path used by this proof.
- The inspect fixture is isolated from the shared L25.20/L25.21 preflight fixture.
- Archive manifest PatchOps inspect is allowed only with explicit flag and token.
- The only inspected payload is the synthetic controlled member `bundle/manifest.json`.
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

L25.23 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_INSPECT_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.23"`.
- `repair_patch:"L25.23a"`.
- `inspect_fixture_isolated_from_preflight_fixture:true`.
- `source_l25_22_summary.ok:true`.
- `source_l25_22_summary.future_patchops_inspect_authorized:true`.
- default passive readback has `patchops_manifest_inspect_performed:false`.
- authorized readback has `archive_manifest_patchops_inspect_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_temp_file_written_for_inspect:true`.
- authorized readback has `patchops_manifest_inspect_performed:true`.
- authorized readback has `patchops_manifest_validation_performed:false`.
- authorized readback has `patchops_cli_inspect_invoked_for_archive_manifest:true`.
- authorized readback has `patchops_cli_inspect_exit_code:0`.
- authorized readback has `patchops_cli_inspect_timed_out:false`.
- authorized readback has `patchops_cli_inspect_json_object:true`.
- authorized readback has `patchops_cli_inspect_patch_name:"synthetic_l25_23_patchops_inspect_fixture"`.
- `patchops_inspect_scope:"controlled_runtime_manifest_patchops_inspect_only_no_plan_apply_run_package_no_execution"`.
- `patchops_cli_plan_invoked_for_archive_manifest:false`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_plan_apply_run_package_added_by_l25_23:true`.

Next patch: L25.24 Microsoft Edge controlled runtime archive manifest PatchOps inspect broad checkpoint.
