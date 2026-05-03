# L18.7 Microsoft Edge download workflow final acceptance marker

L18.7 is the final acceptance marker for the Microsoft Edge download workflow stream.

Command:

```text
browser-start-supervised-launch-edge-download-workflow-final-acceptance-marker
```

Source command:

```text
browser-start-supervised-launch-edge-download-workflow-broad-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.7.
- final acceptance marker.
- L18.1 through L18.6 remain accepted.
- L18 download workflow stream complete.
- metadata-only download readiness proof accepted.
- download workflow stream completion is metadata-only.
- real browser download remains inactive.
- downloaded-file validation is the next separate stream.
- pasteback remains inactive.
- package-run from browser remains inactive.
- live browser download workflow remains inactive.
- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- download staging directory is not created.
- artifact content reading performed: false.
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

## Meaning of completion

L18 completion means PatchOps has accepted the Microsoft Edge download workflow control surface up to metadata-only download readiness classification and passive readbacks.

It does not mean a real browser download is active. It does not mean downloaded file bytes can be read. It does not mean pasteback is active. It does not mean a browser-provided package can be run.

The next stream is downloaded-file validation and must start with a separate passive preflight gate.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-final-acceptance-marker --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The final marker readback should confirm:

- `ok:true`.
- `patch:"L18.7"`.
- `l18_1_through_l18_6_remain_accepted:true`.
- `l18_download_workflow_stream_complete:true`.
- `download_workflow_stream_completion_is_metadata_only:true`.
- `metadata_only_download_readiness_proof_accepted:true`.
- `download_metadata_classification_validated:true`.
- `downloaded_file_validation_is_next_separate_stream:true`.
- `downloaded_file_validation_active:false`.
- `downloaded_file_validation_performed:false`.
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

L19.1 Microsoft Edge downloaded-file validation passive preflight gate.
