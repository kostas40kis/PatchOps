# L16.5 Microsoft Edge first controlled real-page metadata detection proof

L16.5 is the first controlled real-page metadata detection proof for Microsoft Edge.

This is the first patch in the L16 stream that may open an allowlisted ChatGPT page, but only with explicit execution authorization. It uses the dedicated PatchOps runtime profile and observes OS/window/process metadata only.

## Source commands

L16.5 is layered on the L16.4 source command:

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

The new L16.5 command is:

```text
browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof
```

## CLI command

Dry readback, no Edge start:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof --repo-root C:\dev\patchops --json --compact
```

Explicit live metadata proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof --repo-root C:\dev\patchops --allow-real-page-detection-execution --authorization-token PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED --execute-page-metadata-detection --target-url https://chatgpt.com/ --close-after-seconds 6 --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L16.5.
- first controlled real-page metadata detection proof.
- explicit execution authorization required.
- target URL allowlist remains enforced.
- ChatGPT URL may be opened only with explicit authorization.
- dedicated PatchOps runtime profile only.
- default Microsoft Edge profile rejected.
- metadata-only page detection.
- OS/window/process metadata only.
- requested URL, process count, window count, and window title only.
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

## Expected live proof fields

When run with the explicit live proof flags, compact JSON should confirm:

- `source_l16_4_authorization_gate_accepted:true`.
- `real_page_detection_execution_authorized:true`.
- `page_detection_execution_allowed:true`.
- `real_page_detection_active:true`.
- `browser_started:true`.
- `edge_process_started:true`.
- `chatgpt_url_opened:true`.
- `page_metadata_detection_performed:true`.
- `page_metadata_detection_proven:true`.
- `page_identity_metadata_detected:true`.
- `metadata_only_detection_contract.observation_source:"os_window_process_metadata_only"`.
- `current_url_observed:false` because L16.5 avoids CDP, Selenium, and DOM access.
- `selenium_imported_by_readback:false`.
- `cdp_used:false`.
- `remote_debugging_port_used:false`.
- `dom_scraping_performed:false`.
- `prompt_text_extraction_performed:false`.
- `conversation_reading_performed:false`.
- `artifact_detection_performed:false`.
- `download_performed:false`.
- `send_or_submit_performed:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L16.6 Microsoft Edge real-page metadata detection broad checkpoint.
