# L17.6 Microsoft Edge artifact detection broad checkpoint

L17.6 is the broad passive checkpoint for the current Microsoft Edge artifact detection stream.

Command:

```text
browser-start-supervised-launch-edge-artifact-detection-broad-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-presence-metadata-proof
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.6.
- broad passive checkpoint.
- L17.1 through L17.5 remain accepted.
- metadata-only artifact-presence proof remains accepted.
- metadata-only broad checkpoint.
- live browser artifact detection remains inactive.
- artifact detection execution allowed: false.
- real page inspection performed: false.
- artifact content reading performed: false.
- download workflow active: false.
- download workflow remains inactive.
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

This checkpoint consolidates the completed artifact-detection stream so far:

1. L17.1 passive preflight gate.
2. L17.2 CLI/readback checkpoint.
3. L17.3 passive artifact-presence plan.
4. L17.4 controlled live authorization gate.
5. L17.5 metadata-only artifact-presence proof.

The checkpoint may validate the L17.5 default and authorized metadata-only readbacks, but it does not inspect a real page and does not activate live browser artifact detection.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-broad-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The broad readback should confirm:

- `ok:true`.
- `patch:"L17.6"`.
- `l17_1_through_l17_5_remain_accepted:true`.
- `metadata_only_artifact_presence_proof_remains_accepted:true`.
- `metadata_only_broad_checkpoint:true`.
- `artifact_presence_metadata_classification_validated:true`.
- `artifact_detection_execution_allowed:false`.
- `real_page_inspection_performed:false`.
- `live_browser_artifact_detection_active:false`.
- `live_browser_artifact_detection_performed:false`.
- `artifact_content_reading_performed:false`.
- `download_workflow_active:false`.
- `download_performed:false`.
- `click_download_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L17.7 Microsoft Edge artifact detection final acceptance marker.
