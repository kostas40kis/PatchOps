# L18.2 Microsoft Edge download workflow CLI/readback checkpoint

L18.2 adds a passive CLI/readback checkpoint over the accepted L18.1 Microsoft Edge download workflow passive preflight gate.

Command:

```text
browser-start-supervised-launch-edge-download-workflow-cli-readback-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-download-workflow-passive-preflight-gate
```

Authorization token used by the source L18.1 readback:

```text
PATCHOPS_L18_EDGE_DOWNLOAD_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.2.
- download workflow CLI/readback checkpoint.
- passive CLI/readback checkpoint.
- L18.1 passive preflight gate remains accepted.
- default compact readback remains passive.
- authorized compact readback remains passive.
- download workflow preflight authorization remains readback-only.
- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- artifact content reading performed: false.
- pasteback remains inactive.
- package-run from browser remains inactive.
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

## Validation style

L18.2 should avoid nested CLI validation cascades.

The L18.2 readback proves both accepted L18.1 source branches through direct module readback:

1. default compact readback remains passive and has download preflight authorization false.
2. authorized compact readback remains passive and has download preflight authorization true.

The direct-manifest validation should run one shallow L18.2 compact CLI smoke, not a long nested CLI chain.

One shallow L18.2 compact CLI smoke is enough for this checkpoint.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-cli-readback-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L18.2"`.
- `l18_1_passive_preflight_gate_accepted:true`.
- `l18_1_default_compact_readback_ok:true`.
- `l18_1_authorized_compact_readback_ok:true`.
- `default_download_workflow_preflight_authorized:false`.
- `authorized_download_workflow_preflight_authorized:true`.
- `download_workflow_preflight_authorization_remains_readback_only:true`.
- `download_workflow_execution_allowed:false`.
- `download_workflow_active:false`.
- `download_allowed:false`.
- `download_performed:false`.
- `downloaded_file_bytes_read:false`.
- `click_download_performed:false`.
- `artifact_content_reading_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.
- `avoid_nested_cli_validation_cascades:true`.
- `one_shallow_cli_smoke_recommended:true`.

## Next patch

L18.3 Microsoft Edge download workflow passive plan checkpoint.
