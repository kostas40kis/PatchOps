# L25.47 Microsoft Edge controlled runtime real-download artifact package-execution run-package final acceptance marker

L25.47 follows accepted L25.46A and marks the controlled run-package ladder final accepted.

L25.47 does not advance to browser control. It does not run another controlled package. It validates source-payload evidence representing the accepted L25.46A repair and the accepted L25.46 broad checkpoint, then emits the final acceptance marker for the controlled run-package ladder.

## Accepted ladder finalized by L25.47

- L25.41 authorized future package execution only.
- L25.42 rendered a would-run command only.
- L25.43 broad-checked dry-run behavior.
- L25.44 final-accepted the dry-run ladder.
- L25.45 performed one controlled `run-package` against a synthetic no-write artifact.
- L25.45A repaired PASS detection and proved exit-code-0 plus controlled marker is enough.
- L25.46 broad-checked the accepted controlled `run-package` proof.
- L25.46A repaired the L25.46 validator import bootstrap and passed.

## Boundary

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- Source-payload-only final acceptance.
- No `run-package` invocation is performed by L25.47.
- No browser start.
- No real browser download.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No archive extraction by the browser adapter.
- No archive member is extracted to the target project.
- No artifact member is written to the target project.
- No target-project writes from the controlled package.
- No pasteback.
- No send/submit.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

## Expected compact JSON signals

- `ok:true`.
- `patch:"L25.47"`.
- `controlled_run_package_final_acceptance_marker:true`.
- `controlled_run_package_ladder_final_acceptance:true`.
- `controlled_run_package_final_acceptance_from_source_payload_only:true`.
- `accepted_l25_41_package_execution_authorization_gate:true`.
- `accepted_l25_42_package_execution_dry_run_proof:true`.
- `accepted_l25_43_package_execution_dry_run_broad_checkpoint:true`.
- `accepted_l25_44_package_execution_dry_run_final_marker:true`.
- `accepted_l25_45_first_controlled_run_package_proof:true`.
- `accepted_l25_45a_pass_detection_repair:true`.
- `accepted_l25_46_controlled_run_package_broad_checkpoint:true`.
- `accepted_l25_46a_validator_import_bootstrap_repair:true`.
- `controlled_run_package_exit_code:0`.
- `controlled_run_package_exit_zero_plus_marker_pass_observed:true`.
- `controlled_run_package_marker_observed:true`.
- `controlled_run_package_run_scope:"validator_patchops_path_only"`.
- `real_archive_candidate_extraction_scope:"patchops_owned_runtime_only"`.
- `adapter_archive_extraction_performed:false`.
- `archive_member_extracted_to_project:false`.
- `artifact_member_written_to_project:false`.
- `target_project_file_write_performed_by_controlled_package:false`.
- `browser_started:false`.
- `real_browser_download_triggered:false`.
- `selenium_used:false`.
- `cdp_used:false`.
- `dom_scraping_used:false`.
- `pasteback:false`.
- `send_submit_performed:false`.
- `localhost_server_started:false`.
- `browser_extension_used:false`.
- `git_commit_performed:false`.
- `git_push_performed:false`.
- `run_package_invoked_by_l25_47:false`.
- `source_payload_only_final_acceptance:true`.

Next patch after acceptance: L25.48 only after the operator uploads a PASS report and L25.47 is explicitly accepted.

