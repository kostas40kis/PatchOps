# L25.33a Microsoft Edge controlled runtime package-run broad checkpoint key repair

L25.33a repairs the failed L25.33 broad checkpoint.

L25.33 did **not** fail because the controlled run-package proof failed. The controlled synthetic run-package launcher still executed and passed. L25.33 failed because the broad checkpoint expected L25.32b validator-summary key names while the source module returned module-payload key names.

Repair scope:

- normalize both L25.32b source payload shapes:
  - validator-summary shape, for example `package_run_allowed`, `pasteback`, and `runpkg_fixture_names_include_expected_bundle_shape`;
  - module-payload shape, for example `archive_manifest_package_run_allowed`, `pasteback_workflow_active`, and `bundle_review_expected_shape_present`;
- preserve the accepted L25.32b controlled synthetic run-package proof;
- keep the proof limited to the supported synthetic bundle shape and one bounded PatchOps run-package command.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- This checkpoint uses only the controlled synthetic package-run proof.
- It is not a real downloaded artifact and not a ChatGPT-produced package.
- The package manifest is not used for target-project execution.
- Adapter code does not extract the archive manually.
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
- No click/download/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.33a"`.
- `repairs_patch:"L25.33"`.
- `broad_checkpoint:true`.
- `archive_manifest_package_run_ladder_checkpoint:true`.
- `l25_archive_manifest_package_run_ladder_complete:true`.
- `failed_checks:[]`.
- `source_l25_32b_summary.ok:true`.
- `source_l25_32b_summary.patch:"L25.32b"`.
- `source_l25_32b_summary.repairs_patches:["L25.32","L25.32a"]`.
- `source_l25_32b_summary.bundle_review_expected_shape_present:true`.
- `source_l25_32b_summary.runpkg_fixture_names_include_expected_bundle_shape:true`.
- `source_l25_32b_summary.package_run_allowed:true`.
- `source_l25_32b_summary.patchops_cli_run_package_invoked_for_archive_manifest:true`.
- `source_l25_32b_summary.patchops_cli_run_package_exit_code:0`.
- `source_l25_32b_summary.patchops_cli_run_package_timed_out:false`.
- `source_l25_32b_summary.patchops_cli_run_package_review_rejected:false`.
- `source_l25_32b_summary.controlled_package_launcher_executed:true`.
- `source_l25_32b_summary.package_run:true`.
- `accepted_patchops_run_package_scope:"controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"`.
- `package_manifest_used_for_execution:false`.
- `adapter_archive_extraction_performed:false`.
- `real_downloaded_artifact_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.

Next patch: L25.34 Microsoft Edge controlled runtime package-run final acceptance marker.
