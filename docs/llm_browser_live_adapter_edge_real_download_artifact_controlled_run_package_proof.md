# L25.45 Microsoft Edge controlled runtime real-download artifact package-execution first controlled run-package proof

L25.45 follows accepted L25.44 and performs the first controlled PatchOps `run-package` proof.

L25.45A repaired the PASS detection after the first run showed that `run-package` exited `0` and emitted the controlled launcher marker, while the exact `Result : PASS` text pattern was not present in the captured stdout. The accepted success signal is now:

- `run-package` exit code is `0`;
- the controlled launcher marker `PATCHOPS_L25_45_CONTROLLED_RUN_PACKAGE_MARKER` is observed;
- the controlled no-target-write, no-browser, and no-pasteback markers are observed.

Allowed in L25.45:

- verify the accepted L25.44 dry-run final marker source payload;
- create one synthetic no-write ZIP artifact under `data/runtime/browser_downloads/l25_45_controlled_run_package/` during validator setup;
- invoke `py -m patchops.cli run-package <controlled-artifact.zip> --wrapper-root <repo>` exactly once from the validator;
- require exit code `0`;
- require the controlled launcher marker `PATCHOPS_L25_45_CONTROLLED_RUN_PACKAGE_MARKER`;
- accept either explicit PASS text or exit-code-0 plus the controlled launcher marker as the controlled run-package PASS signal;
- require the controlled launcher markers proving no target write, browser start, or pasteback;
- allow only PatchOps-owned package extraction/runtime activity required by `run-package`.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- This proof does not start Microsoft Edge.
- No browser activity.
- No real browser download is triggered.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No artifact member is written to the target project.
- No controlled package target project write.
- No adapter-driven archive extraction into the target project.
- No package execution by the browser adapter; the controlled run is executed only by the validator through PatchOps `run-package`.
- No click/download/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.45"`.
- `controlled_run_package_first_proof:true`.
- `controlled_run_package_pass_detection_repaired_by_l25_45a:true`.
- `controlled_run_package_proof_from_l25_44_final_acceptance:true`.
- `controlled_artifact_under_l25_45_runtime:true`.
- `controlled_artifact_suffix_zip:true`.
- `controlled_run_package_invoked:true`.
- `controlled_run_package_exit_code:0`.
- `controlled_run_package_result_pass:true`.
- `controlled_run_package_exit_zero_plus_marker_pass_observed:true`.
- `controlled_run_package_marker_observed:true`.
- `controlled_package_target_write_marker_false:true`.
- `controlled_package_browser_marker_false:true`.
- `controlled_package_pasteback_marker_false:true`.
- `package_execution_allowed:true`.
- `controlled_package_run_performed_by_validator:true`.
- `package_run:true`.
- `patchops_cli_run_package_invoked_for_controlled_artifact:true`.
- `patchops_cli_run_package_invoked_for_real_artifact:true`.
- `real_archive_candidate_extracted:true` for PatchOps-owned package runtime extraction only.
- `adapter_archive_extraction_performed:false`.
- `archive_member_extracted_to_project:false`.
- `artifact_member_written_to_project:false`.
- `target_project_file_write_performed_by_controlled_package:false`.
- `browser_started:false`.
- `pasteback_workflow_active:false`.
- `git_commit_performed:false`.
- `git_push_performed:false`.

Next patch: L25.46 Microsoft Edge controlled runtime real-download artifact package-execution run-package broad checkpoint.
