# L25.20 Microsoft Edge controlled runtime archive manifest PatchOps preflight first proof

L25.20 follows accepted L25.19 and performs the first controlled PatchOps preflight proof over a synthetic archive manifest.

L25.20a repairs the proof validator fixture. The controlled ZIP candidate is shared by the L25 source-readback chain, so the synthetic manifest must remain compatible with both the earlier L25.17 tiny internal schema and the new PatchOps check-only preflight. The repaired fixture therefore includes the tiny-schema keys `bundle_schema_version`, `manifest_version`, `patch_name`, `purpose`, and `synthetic`, plus the PatchOps manifest fields required for `py -m patchops.cli check`.

Allowed in L25.20:

- read back accepted L25.19 PatchOps-preflight authorization;
- create a controlled ZIP fixture during validator setup;
- open the controlled ZIP fixture after explicit token authorization;
- read bytes from exactly one controlled synthetic manifest member: `bundle/manifest.json`;
- write those bytes to a bounded runtime temporary manifest file under `data/runtime/browser_downloads/l25_20_patchops_preflight/`;
- invoke exactly one bounded PatchOps preflight command: `py -m patchops.cli check <temp_manifest>`;
- record the PatchOps check exit code, timeout flag, `ok`, `issue_count`, `patch_name`, and `active_profile`;
- keep PatchOps inspect, PatchOps plan, PatchOps apply, package execution, extraction, browser, pasteback, and package-run execution disabled.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- The controlled runtime ZIP fixture is the only archive path used by this proof.
- Archive manifest PatchOps preflight is allowed only with explicit flag and token.
- The only preflighted payload is the synthetic controlled member `bundle/manifest.json`.
- PatchOps check is the only PatchOps CLI command invoked against the archive manifest copy.
- PatchOps inspect is not invoked against the archive manifest copy.
- PatchOps plan is not invoked against the archive manifest copy.
- PatchOps apply is not invoked against the archive manifest copy.
- PatchOps run-package is not invoked against the archive manifest copy.
- The preflighted manifest is not used for package execution.
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
- No click/download/archive-extract/PatchOps-inspect/PatchOps-plan/PatchOps-apply/package-run/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

L25.20 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.20"`.
- `repair_patch:"L25.20a"` from the validator output.
- `fixture_contract:"dual_compatible_l25_17_schema_and_patchops_check_manifest"` from the validator output.
- `source_l25_19_summary.ok:true`.
- `source_l25_19_summary.future_patchops_preflight_authorized:true`.
- default passive readback has `patchops_manifest_preflight_performed:false`.
- authorized readback has `archive_manifest_patchops_preflight_allowed:true`.
- authorized readback has `manifest_payload_read:true`.
- authorized readback has `manifest_temp_file_written_for_preflight:true`.
- authorized readback has `patchops_manifest_preflight_performed:true`.
- authorized readback has `patchops_manifest_validation_performed:true` for PatchOps check-only preflight.
- authorized readback has `patchops_cli_check_invoked_for_archive_manifest:true`.
- authorized readback has `patchops_cli_check_exit_code:0`.
- authorized readback has `patchops_cli_check_ok:true`.
- authorized readback has `patchops_cli_check_issue_count:0`.
- `patchops_preflight_scope:"controlled_runtime_manifest_patchops_check_only_no_inspect_plan_apply_no_execution"`.
- `patchops_cli_inspect_invoked_for_archive_manifest:false`.
- `patchops_cli_plan_invoked_for_archive_manifest:false`.
- `patchops_cli_apply_invoked_for_archive_manifest:false`.
- `patchops_cli_run_package_invoked_for_archive_manifest:false`.
- `package_manifest_used_for_execution:false`.
- `package_execution_allowed:false`.
- `real_archive_candidate_extracted:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `package_run:false`.
- `no_patchops_inspect_plan_apply_added_by_l25_20:true`.

Next patch: L25.21 Microsoft Edge controlled runtime archive manifest PatchOps preflight broad checkpoint.
