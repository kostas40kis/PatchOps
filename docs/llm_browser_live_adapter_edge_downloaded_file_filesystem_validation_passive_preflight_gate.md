# L20.1 Microsoft Edge downloaded-file filesystem validation passive preflight gate

L20.1 starts a new Microsoft Edge downloaded-file filesystem validation stream after accepted L19.7.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-preflight-gate
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-final-acceptance-marker
```

Filesystem validation preflight authorization token:

```text
PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.1.
- downloaded-file filesystem validation passive preflight gate.
- L19.7 downloaded-file validation final acceptance marker remains accepted.
- L19 downloaded-file validation stream is complete as metadata/readback-only.
- filesystem validation preflight authorization is readback-only.
- filesystem validation execution allowed: false.
- filesystem validation active: false.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
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
- pasteback remains inactive.
- package-run from browser remains inactive.
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

## Meaning of authorization in L20.1

L20.1 only proves that a future filesystem validation preflight authorization surface exists.

Even with the correct flag and token:

- filesystem validation execution allowed: false.
- filesystem validation active: false.
- filesystem validation is not performed.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
- downloaded file existence check is not performed.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- no browser is started.
- no package is run.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no filesystem validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-filesystem-validation-preflight --authorization-token PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L20.1"`.
- `source_l19_7_final_acceptance_marker_accepted:true`.
- `l19_downloaded_file_validation_stream_complete:true`.
- `l19_downloaded_file_validation_completion_metadata_readback_only:true`.
- `filesystem_validation_preflight_authorized:true`.
- `filesystem_validation_preflight_authorization_is_readback_only_in_l20_1:true`.
- `filesystem_validation_execution_allowed:false`.
- `filesystem_validation_active:false`.
- `filesystem_validation_performed:false`.
- `real_filesystem_validation_active:false`.
- `real_file_existence_check_active:false`.
- `real_file_stat_active:false`.
- `real_file_hash_active:false`.
- `real_file_exists_check_performed:false`.
- `real_file_stat_performed:false`.
- `real_file_hash_performed:false`.
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

L20.2 Microsoft Edge downloaded-file filesystem validation CLI/readback checkpoint.
