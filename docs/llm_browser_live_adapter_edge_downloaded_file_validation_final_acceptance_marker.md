# L19.7 Microsoft Edge downloaded-file validation final acceptance marker

L19.7 is the final acceptance marker for the Microsoft Edge downloaded-file validation stream.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-final-acceptance-marker
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-broad-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L19.7.
- downloaded-file validation final acceptance marker.
- L19.1 through L19.6 remain accepted.
- L19 downloaded-file validation stream complete.
- downloaded-file validation stream completion is metadata/readback-only.
- metadata-only downloaded-file validation proof accepted.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
- archive validation remains inactive.
- manifest read remains inactive.
- file-byte read remains inactive.
- pasteback remains inactive.
- package-run from browser remains inactive.
- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
- downloaded file existence check is not performed.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- download workflow remains inactive.
- real browser download remains inactive.
- PatchOps remains source of truth.
- target URL allowlist remains enforced.
- ChatGPT URL may be selected but not opened.
- dedicated Microsoft Edge runtime profile remains required for future live phases.
- never use the default Microsoft Edge profile.
- no Microsoft Edge start.
- no Selenium import.
- no CDP use.
- no DOM scraping.
- no prompt text extraction.
- no conversation reading.
- no artifact content reading.
- no click/download/file-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Meaning of completion

L19 completion means PatchOps has accepted the Microsoft Edge downloaded-file validation control surface up to metadata-only readiness classification and passive readbacks.

It does not mean PatchOps can validate a real downloaded file on disk. It does not mean PatchOps can stat or hash a file. It does not mean PatchOps can open or list a zip archive. It does not mean PatchOps can read a manifest. It does not mean PatchOps can read downloaded file bytes. It does not mean pasteback is active. It does not mean a browser-provided package can be run.

The next stream is filesystem validation and must start with a separate passive preflight gate.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-final-acceptance-marker --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The final marker readback should confirm:

- `ok:true`.
- `patch:"L19.7"`.
- `l19_1_through_l19_6_remain_accepted:true`.
- `l19_downloaded_file_validation_stream_complete:true`.
- `downloaded_file_validation_stream_completion_is_metadata_readback_only:true`.
- `metadata_only_downloaded_file_validation_proof_accepted:true`.
- `downloaded_file_metadata_validation_ready_from_positive_metadata:true`.
- `real_filesystem_validation_remains_inactive:true`.
- `real_file_existence_check_remains_inactive:true`.
- `real_file_stat_remains_inactive:true`.
- `real_file_hash_remains_inactive:true`.
- `archive_validation_remains_inactive:true`.
- `real_filesystem_validation_active:false`.
- `real_file_existence_check_active:false`.
- `real_file_stat_active:false`.
- `real_file_hash_active:false`.
- `archive_validation_active:false`.
- `downloaded_file_validation_execution_allowed:false`.
- `downloaded_file_validation_active:false`.
- `downloaded_file_validation_performed:false`.
- `downloaded_file_exists_check_performed:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L20.1 Microsoft Edge downloaded-file filesystem validation passive preflight gate.
