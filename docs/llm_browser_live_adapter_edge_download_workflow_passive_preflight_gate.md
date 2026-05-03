# L18.1 Microsoft Edge download workflow passive preflight gate

L18.1 starts the Microsoft Edge download workflow stream after the accepted L17.7 artifact detection final marker.

Command:

```text
browser-start-supervised-launch-edge-download-workflow-passive-preflight-gate
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-detection-final-acceptance-marker
```

Download preflight token:

```text
PATCHOPS_L18_EDGE_DOWNLOAD_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.1.
- download workflow passive preflight gate.
- L17.7 artifact detection final marker remains accepted.
- download workflow preflight authorization is readback-only.
- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- artifact content reading performed: false.
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
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Meaning of authorization in L18.1

L18.1 only proves that a future download workflow preflight authorization surface exists.

Even with the correct flag and token:

- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- no browser is started.
- no download control is clicked.
- no artifact content is read.
- no package is run.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no download execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-download-workflow-preflight --authorization-token PATCHOPS_L18_EDGE_DOWNLOAD_PREFLIGHT_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L18.1"`.
- `source_l17_7_artifact_detection_final_marker_accepted:true`.
- `l17_artifact_detection_stream_complete:true`.
- `download_workflow_preflight_authorized:true`.
- `download_workflow_preflight_authorization_is_readback_only_in_l18_1:true`.
- `download_workflow_execution_allowed:false`.
- `download_workflow_active:false`.
- `download_allowed:false`.
- `download_performed:false`.
- `downloaded_file_bytes_read:false`.
- `click_download_performed:false`.
- `artifact_content_reading_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L18.2 Microsoft Edge download workflow CLI/readback checkpoint.
