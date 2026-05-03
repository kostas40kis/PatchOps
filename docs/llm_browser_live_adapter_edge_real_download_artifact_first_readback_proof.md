# L25.36 Microsoft Edge controlled runtime real-download artifact first readback proof

L25.36 follows accepted L25.35 and performs the first controlled artifact readback proof.

Allowed in L25.36:

- create a controlled ZIP artifact under `data/runtime/browser_downloads/l25_36_real_artifact/` during validator setup;
- require the explicit L25.36 readback token;
- verify the accepted L25.35 authorization source payload;
- open the controlled artifact path;
- read the artifact bytes;
- compute SHA-256 for the artifact bytes;
- open the ZIP only to list member names;
- confirm the expected bundle-shape member names are present without extraction.

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
- No real downloaded manifest member is opened.
- No real downloaded manifest bytes are read.
- No manifest JSON is parsed.
- No archive extraction.
- No archive member is extracted to the project.
- No package execution.
- No PatchOps run-package against the artifact.
- No click/download/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.36"`.
- `first_real_download_artifact_readback_proof:true`.
- `artifact_readback_allowed:true`.
- `candidate_artifact_under_runtime_downloads:true`.
- `real_downloaded_artifact_read:true`.
- `real_downloaded_artifact_path_opened:true`.
- `real_downloaded_artifact_bytes_read:true`.
- `real_downloaded_artifact_hash_computed:true`.
- `artifact_zip_opened_for_member_names_only:true`.
- `artifact_zip_member_names_read:true`.
- `artifact_required_member_names_present:true`.
- `real_downloaded_manifest_read:false`.
- `real_downloaded_manifest_member_opened:false`.
- `real_downloaded_manifest_bytes_read:false`.
- `real_downloaded_manifest_json_parsed:false`.
- `real_archive_candidate_extracted:false`.
- `adapter_archive_extraction_performed:false`.
- `browser_started:false`.
- `package_execution_allowed:false`.
- `package_run:false`.
- `patchops_cli_run_package_invoked_for_real_artifact:false`.
- `pasteback_workflow_active:false`.
- `git_commit_performed:false`.
- `git_push_performed:false`.

Next patch: L25.37 Microsoft Edge controlled runtime real-download artifact manifest member readback gate.
