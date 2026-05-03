# L25.46 Microsoft Edge controlled runtime real-download artifact package-execution run-package broad checkpoint

L25.46 follows accepted L25.45A and creates a source-payload-only broad checkpoint over the controlled `run-package` proof.

L25.46 does not advance to browser control. It does not run another controlled package. It validates that the accepted L25.45/L25.45A evidence contains the repaired success signal:

- controlled `run-package` was invoked in the validator / PatchOps path;
- exit code was `0`;
- the controlled launcher marker was observed;
- exit-code-0 plus the controlled marker is accepted as PASS;
- no-target-write, no-browser, and no-pasteback markers were observed;
- PatchOps-owned runtime extraction is the only accepted extraction scope.

## Ladder confirmed

- L25.41 authorized future package execution only.
- L25.42 rendered a would-run command only.
- L25.43 broad-checked dry-run behavior.
- L25.44 final-accepted the dry-run ladder.
- L25.45 performed one controlled `run-package` against a synthetic no-write artifact.
- L25.45A repaired PASS detection and proved exit-code-0 plus controlled marker is enough.

## Boundary

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- No browser start.
- No real browser download.
- No Selenium import.
- No CDP use.
- No DOM scraping.
- No page inspection.
- No prompt text extraction.
- No conversation reading.
- No pasteback.
- No send/submit.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.
- No target-project writes from the controlled package.
- No adapter-driven extraction into the target project.
- No `run-package` invocation is performed by L25.46.

## Expected compact JSON signals

- `ok:true`.
- `patch:"L25.46"`.
- `controlled_run_package_broad_checkpoint:true`.
- `controlled_run_package_ladder_valid:true`.
- `controlled_run_package_pass_detection_repaired_by_l25_45a:true`.
- `controlled_run_package_exit_code:0`.
- `controlled_run_package_exit_zero_plus_marker_pass_observed:true`.
- `controlled_run_package_marker_observed:true`.
- `controlled_run_package_run_scope:"validator_patchops_path_only"`.
- `adapter_archive_extraction_performed:false`.
- `archive_member_extracted_to_project:false`.
- `artifact_member_written_to_project:false`.
- `target_project_file_write_performed_by_controlled_package:false`.
- `browser_started:false`.
- `selenium_used:false`.
- `cdp_used:false`.
- `dom_scraping_used:false`.
- `pasteback:false`.
- `send_submit_performed:false`.
- `localhost_server_started:false`.
- `browser_extension_used:false`.
- `git_commit_performed:false`.
- `git_push_performed:false`.
- `run_package_invoked_by_l25_46:false`.
- `source_payload_only_broad_checkpoint:true`.

Next patch after acceptance: L25.47 only after the operator uploads a PASS report and L25.46 is explicitly accepted.

## L25.46A repair note

The first L25.46 attempt wrote the intended module, doc, and validator, and `py_compile` passed. The validator failed because the manifest launched it as `py scripts/patch_l25_46_brief_validate.py`, which places `scripts/` on `sys.path` instead of the repository root. L25.46A adds a narrow repo-root import bootstrap before importing `patchops.*`.

L25.46A does not change the checkpoint boundary, does not invoke `run-package`, and does not advance to browser control.

Expected repair signal: `validator_import_bootstrap_repaired:true`.
