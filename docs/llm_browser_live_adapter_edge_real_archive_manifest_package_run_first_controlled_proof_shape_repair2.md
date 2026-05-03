# L25.32b Microsoft Edge controlled runtime package-run bundle shape proof

L25.32b repairs the failed L25.32a proof.

L25.32a failed before reaching the package-run shape proof because its validator depended on a brittle upstream source-chain `ok:true` assertion. The accepted L25.31 checkpoint is still the authorization source by uploaded report evidence; this repair keeps the proof gated by the explicit L25.32 package-run proof token and by direct supported bundle-shape checks.

Repair scope:

- do not rerun L25.32 or L25.32a broken logic;
- create a controlled synthetic ZIP under `data/runtime/browser_downloads/l25_32b_package_run/`;
- require these ZIP members before run-package:
  - `bundle/run_with_patchops.ps1`
  - `bundle/bundle_meta.json`
  - `bundle/README.txt`
  - `bundle/manifest.json`
  - `bundle/content/.keep`
- invoke exactly one bounded PatchOps run-package command against that controlled ZIP:
  `py -m patchops.cli run-package <controlled_zip> --wrapper-root <repo>`.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- This proof uses only a controlled synthetic package ZIP.
- It is not a real downloaded artifact and not a ChatGPT-produced package.
- PatchOps run-package is allowed only with explicit flag, token, and supported synthetic bundle shape.
- The controlled package launcher writes only a proof report and exits zero.
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
- `patch:"L25.32b"`.
- `repairs_patches:["L25.32","L25.32a"]`.
- `bundle_review_expected_shape_present:true`.
- `patchops_cli_run_package_invoked_for_archive_manifest:true`.
- `patchops_cli_run_package_exit_code:0`.
- `patchops_cli_run_package_timed_out:false`.
- `patchops_cli_run_package_review_rejected:false`.
- `controlled_package_launcher_executed:true`.
- `package_run:true`.
- `patchops_run_package_scope:"controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"`.
- `package_manifest_used_for_execution:false`.
- `adapter_archive_extraction_performed:false`.
- `real_downloaded_artifact_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.

Next patch: L25.33 Microsoft Edge controlled runtime archive manifest package-run broad checkpoint.
