# L16.4 Microsoft Edge real-page detection controlled live plan authorization gate

L16.4 adds the controlled live-plan authorization gate for the future first real-page metadata detection proof.

This is still passive. The execution authorization is readback-only in L16.4. It does not start Microsoft Edge, inspect ChatGPT, import Selenium, detect artifacts, click, download, paste, send, run a package from the browser, commit, or push.

## Source commands

L16.4 is layered on the L16.3 source command:

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

L16.1 was layered on L15.5:

```text
browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection
```

The new L16.4 command is:

```text
browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate
```

## CLI command

Passive default readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate --repo-root C:\dev\patchops --json --compact
```

Authorized readback, still passive:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate --repo-root C:\dev\patchops --allow-real-page-detection-execution --authorization-token PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED --target-url https://chatgpt.com/ --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L16.4.
- controlled live plan authorization gate only.
- execution authorization is readback-only in L16.4.
- real-page detection is still not active.
- target URL allowlist remains enforced.
- ChatGPT URL may be authorized but not opened.
- page detection execution allowed: false.
- metadata-only detection contract.
- current URL, page title, ready state, and window count only.
- no DOM scraping.
- no prompt text extraction.
- no conversation reading.
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

- `source_l16_3_passive_plan_checkpoint_accepted:true`.
- `real_page_detection_execution_authorized:true` only when the flag and token are supplied.
- `execution_authorization_is_readback_only_in_l16_4:true`.
- `page_detection_execution_allowed:false`.
- `real_page_detection_active:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `page_inspection_performed:false`.
- `chatgpt_url_opened:false`.
- `selenium_imported_by_readback:false`.
- `artifact_detection_performed:false`.
- `download_performed:false`.
- `send_or_submit_performed:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L16.5 Microsoft Edge first controlled real-page metadata detection proof.
