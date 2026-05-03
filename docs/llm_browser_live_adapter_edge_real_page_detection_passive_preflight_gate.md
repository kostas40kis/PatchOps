# L16.1 Microsoft Edge real-page detection passive preflight gate

L16.1 starts the real-page detection stream after the accepted L15.5 live-start handoff marker.

This patch is a passive preflight gate. It does not start Microsoft Edge, inspect any page, import Selenium, or interact with ChatGPT. It only defines the preflight/readback contract for a future real-page detection phase.

## Source commands

L16.1 is layered on the L15.5 source command:

```text
browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection
```

L15.5 was layered on L15.4:

```text
browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint
```

L15.4 was layered on L15.3:

```text
browser-start-supervised-launch-edge-first-controlled-open-proof
```

L15.3 was layered on L15.2:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback
```

L15.2 was layered on L15.1:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate
```

The new L16.1 command is:

```text
browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate
```

## CLI command

Passive default readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate --repo-root C:\dev\patchops --json --compact
```

Authorized preflight readback, still passive:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate --repo-root C:\dev\patchops --allow-real-page-detection-preflight --authorization-token PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_PREFLIGHT_AUTHORIZED --target-url https://chatgpt.com/ --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L16.1.
- passive preflight gate only.
- L15.1 through L15.4 accepted through L15.5.
- real-page detection is not active yet.
- target URL allowlist is enforced.
- ChatGPT URL may be selected but not opened.
- no Microsoft Edge start.
- no Selenium import.
- no ChatGPT interaction.
- no page inspection.
- no artifact detection.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Expected readback fields

The compact JSON readback should confirm:

- `source_l15_5_handoff_marker_accepted:true`.
- `l15_live_start_stream_complete:true`.
- `real_page_detection_active:false`.
- `real_page_detection_allowed:false`.
- `page_inspection_performed:false`.
- `target_url_allowlist_enforced:true`.
- `chatgpt_url_opened:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `selenium_imported_by_readback:false`.
- `artifact_detection_performed:false`.
- `download_performed:false`.
- `send_or_submit_performed:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L16.2 Microsoft Edge real-page detection CLI/readback checkpoint.
