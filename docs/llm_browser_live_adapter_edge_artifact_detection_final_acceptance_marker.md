# L17.7 Microsoft Edge artifact detection final acceptance marker

L17.7 is the final acceptance marker for the Microsoft Edge artifact detection stream.

Command:

```text
browser-start-supervised-launch-edge-artifact-detection-final-acceptance-marker
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-detection-broad-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.7.
- final acceptance marker.
- L17.1 through L17.6 remain accepted.
- L17 artifact detection stream complete.
- metadata-only artifact-presence proof accepted.
- artifact detection stream completion is metadata-only.
- download workflow remains inactive.
- download workflow is the next separate stream.
- pasteback remains inactive.
- package-run from browser remains inactive.
- live browser artifact detection remains inactive.
- artifact detection execution allowed: false.
- real page inspection performed: false.
- artifact content reading performed: false.
- download workflow active: false.
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

L17 completion means PatchOps has accepted the Microsoft Edge artifact-detection control surface up to metadata-only artifact-presence classification. It does not mean downloads are active. It does not mean pasteback is active. It does not mean a browser-provided package can be run.

The next stream is download workflow and must start with a separate passive preflight gate.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-final-acceptance-marker --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The final marker readback should confirm:

- `ok:true`.
- `patch:"L17.7"`.
- `l17_1_through_l17_6_remain_accepted:true`.
- `l17_artifact_detection_stream_complete:true`.
- `artifact_detection_stream_completion_is_metadata_only:true`.
- `metadata_only_artifact_presence_proof_accepted:true`.
- `artifact_presence_metadata_classification_validated:true`.
- `download_workflow_is_next_separate_stream:true`.
- `download_workflow_active:false`.
- `pasteback_remains_inactive:true`.
- `package_run_from_browser_remains_inactive:true`.
- `real_page_inspection_performed:false`.
- `live_browser_artifact_detection_active:false`.
- `artifact_content_reading_performed:false`.
- `download_performed:false`.
- `click_download_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L18.1 Microsoft Edge download workflow passive preflight gate.
