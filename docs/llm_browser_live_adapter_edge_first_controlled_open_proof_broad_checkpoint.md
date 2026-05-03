# L15.4 Microsoft Edge first controlled open proof broad checkpoint

L15.4 is a broad checkpoint over the accepted L15.1, L15.2, and L15.3 Microsoft Edge live-start surfaces.

It verifies the full live-start gate stack before moving toward real-page detection. It can run as a dry checkpoint or an explicit live checkpoint.

## Source commands

L15.4 is layered on the L15.3 source command:

```text
browser-start-supervised-launch-edge-first-controlled-open-proof
```

L15.3 is layered on L15.2:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback
```

L15.2 is layered on L15.1:

```text
browser-start-supervised-launch-edge-live-start-authorization-execution-gate
```

The new L15.4 command is:

```text
browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint
```

## CLI command

Dry checkpoint:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint --repo-root C:\dev\patchops --json --compact
```

Explicit live checkpoint:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint --repo-root C:\dev\patchops --execute-live-checkpoint --close-after-seconds 3 --json --compact
```

## Contract

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L15.4.
- broad checkpoint over L15.1, L15.2, and L15.3.
- dry checkpoint must not start Edge.
- explicit live checkpoint may briefly start Edge.
- about:blank only.
- dedicated L14 profile only.
- default Microsoft Edge profile rejected.
- Selenium is not imported.
- no ChatGPT interaction.
- no artifact detection.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Expected explicit live checkpoint fields

When run with `--execute-live-checkpoint`, the compact JSON should confirm:

- `l15_1_authorization_gate_still_green:true`.
- `l15_2_cli_readback_still_green:true`.
- `l15_3_dry_readback_still_green:true`.
- `l15_3_live_checkpoint_green_when_requested:true`.
- `launch_execution_allowed:true`.
- `browser_started:true`.
- `edge_process_started:true`.
- `live_open_smoke_proven:true`.
- `browser_close_attempted:true`.
- `selenium_imported_by_readback:false`.
- `chatgpt_url_opened:false`.
- `download_performed:false`.
- `send_or_submit_performed:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L15.5 Microsoft Edge live-start handoff marker before real-page detection.
