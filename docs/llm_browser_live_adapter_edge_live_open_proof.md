# L15.1 Microsoft Edge live open proof explicit authorization gate

L15.1 adds the first controlled Microsoft Edge live-open proof surface after the accepted L14.9 dedicated profile lifecycle final marker.

Command:

`browser-start-supervised-launch-edge-live-open-proof`

Source command:

`browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker`

Boundary:

- L14.9 final acceptance marker remains accepted.
- L15.1 live open proof is Microsoft Edge only.
- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target.
- real browser start requires `--execute-live-open`.
- real browser start requires `--allow-live-edge-start`.
- real browser start requires `--authorization-token PATCHOPS_L15_EDGE_LIVE_OPEN_PROOF`.
- authorization token is not echoed in JSON readback.
- dedicated profile candidate is `data/runtime/browser_profiles/edge_supervised_l14`.
- dedicated profile must stay under `data/runtime/browser_profiles`.
- default Edge profile is rejected.
- profile directory creation is allowed only during explicit live open execution.
- default CLI/readback mode is passive and starts no browser.
- no Selenium import.
- no driver creation.
- no page scraping.
- no ChatGPT interaction.
- no latest assistant reply detection.
- no artifact detection.
- no click/download/paste/send/package-run side effect.
- no auto-send.
- no git commit or git push.
- no localhost PatchOps server.
- no browser extension.

Live proof command, to be run only when the operator intentionally wants the narrow Edge smoke proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-open-proof `
  --repo-root C:\dev\patchops `
  --execute-live-open `
  --allow-live-edge-start `
  --authorization-token PATCHOPS_L15_EDGE_LIVE_OPEN_PROOF `
  --json --compact
```

The command opens Edge with the dedicated profile and `about:blank` by default. It performs no page scraping, no artifact detection, no download, no pasteback, no send/submit, and no PatchOps package run.

If accepted, continue with:

`L15.2 Microsoft Edge live open proof CLI/readback and operator report polish`

<!-- PATCHOPS_L15_01B_READBACK_STATUS_CONTRACT -->

## L15.1B readback status contract

Default JSON readback is allowed to return `PASS` when the safety contract is satisfied and no live start was requested.

In that default mode, the important proof fields are:

- `execution_mode: readback_only`
- `launch_execution_allowed: false`
- `browser_started: false`
- `edge_process_started: false`
- `send_or_submit_performed: false`

`BLOCKED` is reserved for denied or incomplete execution attempts, not for a safe no-side-effect readback.
