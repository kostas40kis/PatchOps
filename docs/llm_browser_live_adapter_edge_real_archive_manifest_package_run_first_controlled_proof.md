# L25.32 Microsoft Edge controlled runtime archive manifest package-run first proof

L25.32 follows accepted L25.31 and performs the first controlled package-run proof.

Allowed in L25.32:

- read back accepted L25.31 package-run authorization;
- create a controlled synthetic package ZIP during validator setup;
- include required bundle metadata such as `bundle_schema_version` and `wrapper_project_root`;
- invoke exactly one bounded PatchOps run-package command against that controlled ZIP:
  `py -m patchops.cli run-package <controlled_zip> --wrapper-root <repo>`;
- execute only the controlled root launcher inside that synthetic package;
- let the controlled launcher write only a tiny Desktop proof report and exit zero;
- record the run-package exit code, timeout flag, PASS/ok marker, launcher marker, and report-path marker.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Default Microsoft Edge profile is not allowed.
- Dedicated Edge runtime profile remains required for any future live phase.
- ChatGPT URL may be selected but not opened.
- This proof uses only a controlled synthetic package ZIP under `data/runtime/browser_downloads/l25_32_package_run/`.
- It is not a real downloaded artifact and not a ChatGPT-produced package.
- PatchOps run-package is allowed only with explicit flag and token.
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

L25.32 token:

```text
PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PACKAGE_RUN_FIRST_CONTROLLED_PROOF_AUTHORIZED
```

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.32"`.
- `source_l25_31_summary.ok:true`.
- `source_l25_31_summary.future_package_run_authorized:true`.
- default passive readback has `patchops_run_package_performed:false`.
- authorized readback has `archive_manifest_package_run_allowed:true`.
- authorized readback has `patchops_cli_run_package_invoked_for_archive_manifest:true`.
- authorized readback has `patchops_cli_run_package_exit_code:0`.
- authorized readback has `patchops_cli_run_package_timed_out:false`.
- authorized readback has `patchops_cli_run_package_stdout_has_pass:true` or `patchops_cli_run_package_stdout_has_ok_true:true`.
- authorized readback has `controlled_package_launcher_executed:true`.
- authorized readback has `package_run:true`.
- `patchops_run_package_scope:"controlled_runtime_package_run_only_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"`.
- `package_manifest_used_for_execution:false`.
- `adapter_archive_extraction_performed:false`.
- `real_downloaded_artifact_read:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.

Next patch: L25.33 Microsoft Edge controlled runtime archive manifest package-run broad checkpoint.
