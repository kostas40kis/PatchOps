# L18.4 Microsoft Edge download workflow controlled live authorization gate

L18.4 adds the controlled live authorization gate after the accepted L18.3 passive plan checkpoint.

Command:

```text
browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate
```

Source command:

```text
browser-start-supervised-launch-edge-download-workflow-passive-plan-checkpoint
```

Authorization token:

```text
PATCHOPS_L18_EDGE_DOWNLOAD_WORKFLOW_LIVE_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.4.
- download workflow controlled live authorization gate.
- passive/readback-only in L18.4.
- L18.3 passive plan checkpoint remains accepted.
- explicit future live download authorization token.
- live download authorization is readback-only.
- live download execution allowed: false.
- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- download staging directory is not created.
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

## Meaning of authorization in L18.4

In L18.4, authorization only proves that the future live download gate can distinguish default readback from explicitly authorized readback.

Even with the correct flag and token:

- live download execution allowed: false.
- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- no browser is started.
- no download control is clicked.
- no package is run.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-live-download-authorization --authorization-token PATCHOPS_L18_EDGE_DOWNLOAD_WORKFLOW_LIVE_AUTHORIZED_READBACK_ONLY --json --compact
```

## Future gate plan

The L18.4 plan is planned but not executed:

1. Confirm the L18.3 passive plan checkpoint remains accepted.
2. Require the explicit live download authorization flag.
3. Require the exact live download authorization token.
4. Require the dedicated Microsoft Edge runtime profile and reject the default Microsoft Edge profile.
5. In L18.5 or later only, a future live phase may click download after operator review.
6. L18.4 readback does not execute download workflow, click, download, read downloaded file bytes, paste, send, or package run.

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L18.4"`.
- `source_l18_3_passive_plan_checkpoint_accepted:true`.
- `live_download_authorized_for_future_phase:true`.
- `live_download_authorization_is_readback_only_in_l18_4:true`.
- `live_download_execution_allowed:false`.
- `download_workflow_execution_allowed:false`.
- `download_workflow_active:false`.
- `download_allowed:false`.
- `download_performed:false`.
- `downloaded_file_bytes_read:false`.
- `download_staging_directory_created:false`.
- `click_download_performed:false`.
- `artifact_content_reading_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.
- `default_microsoft_edge_profile_allowed:false`.

## Next patch

L18.5 Microsoft Edge first controlled download metadata proof.
