# L25.38 Microsoft Edge controlled runtime real-download artifact manifest validation checkpoint

L25.38 follows accepted L25.37 and validates already-read manifest metadata from the L25.37 source payload.

Allowed in L25.38:

- require the explicit L25.38 manifest-validation token;
- verify the accepted L25.37 manifest-member readback source payload;
- validate that the read manifest member was `bundle/manifest.json`;
- validate that the manifest patch name is `synthetic_l25_37_manifest_readback_fixture`;
- validate that the manifest version is `1`;
- validate that the manifest is zero-write and zero-validation;
- validate that extraction, execution, run-package, browser, pasteback, localhost, extension, commit, and push are still closed.

Boundary:

- Microsoft Edge first.
- Opera second, not active.
- PatchOps remains the source of truth.
- This checkpoint does not open an artifact path.
- This checkpoint does not read artifact bytes.
- This checkpoint does not open ZIP members.
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
- `patch:"L25.38"`.
- `manifest_validation_checkpoint:true`.
- `manifest_validation_from_source_payload_only:true`.
- `manifest_validation_allowed:true`.
- `accepted_manifest_member_name:"bundle/manifest.json"`.
- `accepted_manifest_patch_name:"synthetic_l25_37_manifest_readback_fixture"`.
- `accepted_manifest_version:"1"`.
- `accepted_manifest_files_to_write_count:0`.
- `accepted_manifest_validation_commands_count:0`.
- `accepted_manifest_zero_writes:true`.
- `accepted_manifest_zero_validation_commands:true`.
- `artifact_path_opened_by_l25_38:false`.
- `artifact_bytes_read_by_l25_38:false`.
- `zip_member_opened_by_l25_38:false`.
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

Next patch: L25.39 Microsoft Edge controlled runtime real-download artifact manifest validation broad checkpoint.
