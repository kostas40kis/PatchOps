# L16.6 Microsoft Edge real-page metadata detection broad checkpoint

L16.6 is the broad checkpoint for the Microsoft Edge real-page metadata detection stream.

It consolidates L16.1 through L16.5 and can run one explicit live metadata checkpoint through the accepted L16.5 proof. It preserves the metadata-only boundary and avoids DOM, CDP, Selenium, conversation text, artifacts, downloads, paste, send, package-running, commit, and push.

## Source commands

L16.6 is layered on the L16.5 source command:

```text
browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof
```

L16.5 was layered on L16.4:

```text
browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate
```

L16.4 was layered on L16.3:

```text
browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint
```

L16.3 was layered on L16.2:

```text
browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint
```

L16.2 was layered on L16.1:

```text
browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate
```

The new L16.6 command is:

```text
browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint
```

## CLI command

Dry checkpoint:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint --repo-root C:\dev\patchops --json --compact
```

Explicit live metadata checkpoint:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint --repo-root C:\dev\patchops --execute-live-checkpoint --close-after-seconds 6 --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L16.6.
- broad checkpoint over L16.1 through L16.5 accepted surfaces.
- dry metadata checkpoint must not start Edge.
- explicit live metadata checkpoint may briefly open ChatGPT through L16.5.
- target URL allowlist remains enforced.
- ChatGPT URL may be opened only during explicit live checkpoint.
- metadata-only page detection.
- OS/window/process metadata only.
- no DOM scraping.
- no prompt text extraction.
- no conversation reading.
- no Selenium import.
- no CDP use.
- no browser extension.
- no artifact detection.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no git commit or git push.

## Expected explicit live checkpoint fields

When run with `--execute-live-checkpoint`, the compact JSON should confirm:

- `l16_3_passive_plan_checkpoint_still_green:true`.
- `l16_4_authorization_gate_still_green:true`.
- `l16_5_dry_metadata_detection_readback_still_green:true`.
- `l16_5_live_metadata_detection_green_when_requested:true`.
- `l16_1_through_l16_5_accepted:true`.
- `page_detection_execution_allowed:true`.
- `real_page_detection_active:true`.
- `browser_started:true`.
- `edge_process_started:true`.
- `chatgpt_url_opened:true`.
- `page_metadata_detection_performed:true`.
- `page_metadata_detection_proven:true`.
- `page_identity_metadata_detected:true`.
- `selenium_imported_by_readback:false`.
- `cdp_used:false`.
- `dom_scraping_performed:false`.
- `conversation_reading_performed:false`.
- `artifact_detection_performed:false`.
- `download_performed:false`.
- `send_or_submit_performed:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L16.7 Microsoft Edge real-page metadata detection final acceptance marker.
