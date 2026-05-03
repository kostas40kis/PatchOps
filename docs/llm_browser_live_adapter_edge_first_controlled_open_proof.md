# L15.3 first controlled Microsoft Edge open proof

L15.3 is the first controlled Microsoft Edge open proof.

This is the first patch in this stream that may cross the browser-process boundary, but only when the operator supplies every explicit authorization argument. The controlled proof opens Microsoft Edge to `about:blank` with the dedicated L14 profile candidate, waits briefly, and attempts to close only the Edge process/profile it started.

## Source commands

L15.3 is layered on the accepted L15.2 CLI/readback command:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback
```

L15.2 read back the L15.1 gate command:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate
```

The new L15.3 command is:

```text
browser-start-supervised-launch-edge-first-controlled-open-proof
```

## CLI command

Dry readback, no Edge start:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-first-controlled-open-proof --repo-root C:\dev\patchops --json --compact
```

Live smoke proof, explicitly authorized:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-first-controlled-open-proof --repo-root C:\dev\patchops --allow-live-start --authorization-token PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED --execute-live-open --close-after-seconds 3 --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L15.3.
- explicit live-start authorization flag required.
- explicit live-start authorization token required.
- explicit live-open execution flag required.
- dedicated L14 profile candidate required.
- default Microsoft Edge profile rejected.
- open URL is about:blank.
- Selenium is not imported.
- the live proof is process-level only.
- no browser session creation through Selenium/WebDriver.
- no driver creation.
- no ChatGPT interaction.
- no artifact detection.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.
- close only the Edge process/profile it started.

## Expected live proof fields

When run with all live flags, the compact JSON readback should show:

- `launch_execution_allowed:true`.
- `live_open_smoke_executed:true`.
- `live_open_smoke_proven:true`.
- `browser_started:true`.
- `edge_process_started:true`.
- `browser_close_attempted:true`.
- `open_url:"about:blank"`.
- `selenium_imported_by_readback:false`.
- `chatgpt_url_opened:false`.
- `click_download_performed:false`.
- `download_performed:false`.
- `paste_performed:false`.
- `send_or_submit_performed:false`.
- `package_run_performed_by_adapter:false`.
- `auto_send_allowed:false`.

The dedicated profile may be created or mutated by Microsoft Edge. Default profile use remains forbidden.

## Next patch

L15.4 Microsoft Edge first controlled open proof broad checkpoint.
