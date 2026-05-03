# L17.1 Microsoft Edge artifact detection passive preflight gate

L17.1 starts the Microsoft Edge artifact-detection stream after the accepted L16.7 metadata final marker.

This is a passive preflight gate. It does not start Microsoft Edge, inspect a page, read ChatGPT conversation text, detect artifacts, download anything, paste, send, run a package from the browser, commit, or push.

## Source commands

L17.1 is layered on the L16.7 source command:

```text
browser-start-supervised-launch-edge-real-page-metadata-detection-final-acceptance-marker
```

L16.7 was layered on L16.6:

```text
browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint
```

L16.6 was layered on L16.5:

```text
browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof
```

The new L17.1 command is:

```text
browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate
```

## CLI command

Passive default readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate --repo-root C:\dev\patchops --json --compact
```

Authorized preflight readback, still passive:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate --repo-root C:\dev\patchops --allow-artifact-detection-preflight --authorization-token PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_PREFLIGHT_AUTHORIZED --target-url https://chatgpt.com/ --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.1.
- passive preflight gate only.
- L16 metadata detection stream complete.
- artifact detection is not active yet.
- artifact detection preflight authorization is readback-only.
- artifact detection execution allowed: false.
- download workflow is not active yet.
- PatchOps remains source of truth.
- target URL allowlist remains enforced.
- ChatGPT URL may be selected but not opened.
- no Microsoft Edge start.
- no Selenium import.
- no CDP use.
- no DOM scraping.
- no prompt text extraction.
- no conversation reading.
- no artifact detection.
- no artifact content reading.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Future artifact plan

The future artifact-detection path is planned but not executed:

1. Confirm the L16 metadata detection stream is complete.
2. Require explicit operator authorization for artifact detection.
3. Open an allowlisted ChatGPT page with the dedicated profile only in a later live phase.
4. Detect artifact presence from safe metadata only.
5. Emit an operator review readback without auto-clicking, auto-downloading, auto-pasting, or auto-sending.

## Expected readback fields

The compact JSON readback should confirm:

- `source_l16_7_final_marker_accepted:true`.
- `l16_metadata_detection_stream_complete:true`.
- `artifact_detection_preflight_authorized:true` only when the flag and token are supplied.
- `artifact_detection_preflight_is_readback_only_in_l17_1:true`.
- `artifact_detection_execution_allowed:false`.
- `artifact_detection_active:false`.
- `artifact_detection_performed:false`.
- `download_workflow_active:false`.
- `download_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L17.2 Microsoft Edge artifact detection CLI/readback checkpoint.
