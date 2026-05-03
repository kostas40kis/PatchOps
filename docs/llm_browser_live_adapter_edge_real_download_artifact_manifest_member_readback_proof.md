# L25.37 Microsoft Edge controlled runtime real-download artifact manifest member readback proof

L25.37 follows accepted L25.36 and performs the first controlled manifest-member readback from a controlled artifact ZIP.

Allowed in L25.37:

- create a controlled ZIP artifact under `data/runtime/browser_downloads/l25_37_real_artifact_manifest/` during validator setup;
- require the explicit L25.37 manifest-readback token;
- verify the accepted L25.36 artifact-readback source payload;
- open the controlled artifact path;
- read the artifact bytes and compute artifact SHA-256;
- open the ZIP only to read `bundle/manifest.json`;
- read and hash only the manifest member bytes;
- parse manifest JSON metadata;
- confirm the manifest is zero-write and zero-validation.

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
- No archive extraction.
- No archive member is extracted to the project.
- No artifact member is written to the project.
- No package execution.
- No PatchOps run-package against the artifact.
- No click/download/paste/send side effect.
- No localhost PatchOps server.
- No browser extension.
- No git commit or git push.

Expected compact JSON signals:

- `ok:true`.
- `patch:"L25.37"`.
- `manifest_member_readback_proof:true`.
- `manifest_readback_allowed:true`.
- `candidate_artifact_under_runtime_downloads:true`.
- `real_downloaded_artifact_read:true`.
- `real_downloaded_artifact_path_opened:true`.
- `real_downloaded_artifact_bytes_read:true`.
- `real_downloaded_artifact_hash_computed:true`.
- `real_downloaded_manifest_read:true`.
- `real_downloaded_manifest_member_opened:true`.
- `real_downloaded_manifest_member_name:"bundle/manifest.json"`.
- `real_downloaded_manifest_bytes_read:true`.
- `real_downloaded_manifest_hash_computed:true`.
- `real_downloaded_manifest_json_parsed:true`.
- `manifest_patch_name:"synthetic_l25_37_manifest_readback_fixture"`.
- `manifest_version:"1"`.
- `manifest_files_to_write_count:0`.
- `manifest_validation_commands_count:0`.
- `real_archive_candidate_extracted:false`.
- `adapter_archive_extraction_performed:false`.
- `archive_member_extracted_to_project:false`.
- `artifact_member_written_to_project:false`.
- `browser_started:false`.
- `package_execution_allowed:false`.
- `package_run:false`.
- `patchops_cli_run_package_invoked_for_real_artifact:false`.
- `pasteback_workflow_active:false`.
- `git_commit_performed:false`.
- `git_push_performed:false`.

Next patch: L25.38 Microsoft Edge controlled runtime real-download artifact manifest validation checkpoint.
