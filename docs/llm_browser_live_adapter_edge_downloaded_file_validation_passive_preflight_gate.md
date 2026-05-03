# L19.1 Microsoft Edge downloaded-file validation passive preflight gate

L19.1 starts the Microsoft Edge downloaded-file validation stream after the accepted L18.7 download workflow final marker.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-passive-preflight-gate
```

Source command:

```text
browser-start-supervised-launch-edge-download-workflow-final-acceptance-marker
```

Downloaded-file validation preflight token:

```text
PATCHOPS_L19_EDGE_DOWNLOADED_FILE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L19.1.
- downloaded-file validation passive preflight gate.
- L18.7 download workflow final marker remains accepted.
- downloaded-file validation preflight authorization is readback-only.
- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
- downloaded file existence check is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
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

## Meaning of authorization in L19.1

L19.1 only proves that a future downloaded-file validation authorization surface exists.

Even with the correct flag and token:

- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
- downloaded file existence check is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- no browser is started.
- no download control is clicked.
- no package is run.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no downloaded-file validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-file-validation-preflight --authorization-token PATCHOPS_L19_EDGE_DOWNLOADED_FILE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L19.1"`.
- `source_l18_7_download_workflow_final_marker_accepted:true`.
- `l18_download_workflow_stream_complete:true`.
- `downloaded_file_validation_preflight_authorized:true`.
- `downloaded_file_validation_preflight_authorization_is_readback_only_in_l19_1:true`.
- `downloaded_file_validation_execution_allowed:false`.
- `downloaded_file_validation_active:false`.
- `downloaded_file_validation_performed:false`.
- `downloaded_file_exists_check_performed:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `download_workflow_active:false`.
- `download_performed:false`.
- `click_download_performed:false`.
- `artifact_content_reading_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L19.2 Microsoft Edge downloaded-file validation CLI/readback checkpoint.
