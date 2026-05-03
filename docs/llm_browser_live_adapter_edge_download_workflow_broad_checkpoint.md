# L18.6 Microsoft Edge download workflow broad checkpoint

L18.6 is the broad passive checkpoint for the current Microsoft Edge download workflow stream.

Command:

```text
browser-start-supervised-launch-edge-download-workflow-broad-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-download-metadata-proof
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.6.
- broad passive checkpoint.
- L18.1 through L18.5 remain accepted.
- metadata-only download readiness proof remains accepted.
- metadata-only broad checkpoint.
- live browser download workflow remains inactive.
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

## Scope

This checkpoint consolidates the completed download workflow stream so far:

1. L18.1 passive download workflow preflight gate.
2. L18.2 CLI/readback checkpoint.
3. L18.3 passive download workflow plan.
4. L18.4 controlled live authorization gate.
5. L18.5 metadata-only download readiness proof.

The checkpoint may validate the L18.5 default and authorized metadata-only readbacks, but it does not inspect a real page and does not activate a live browser download workflow.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-broad-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The broad readback should confirm:

- `ok:true`.
- `patch:"L18.6"`.
- `l18_1_through_l18_5_remain_accepted:true`.
- `metadata_only_download_readiness_proof_remains_accepted:true`.
- `metadata_only_broad_checkpoint:true`.
- `download_metadata_classification_validated:true`.
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

## Next patch

L18.7 Microsoft Edge download workflow final acceptance marker.
