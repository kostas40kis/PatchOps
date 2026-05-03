# L17.2 Microsoft Edge artifact detection CLI/readback checkpoint

L17.2 adds a passive CLI/readback checkpoint over the accepted L17.1 Microsoft Edge artifact detection passive preflight gate.

Command:

```text
browser-start-supervised-launch-edge-artifact-detection-cli-readback-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate
```

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-cli-readback-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.2.
- passive CLI/readback checkpoint only.
- L17.1 passive preflight gate remains accepted.
- default compact readback remains passive.
- authorized compact readback remains passive.
- artifact detection preflight authorization is still readback-only.
- artifact detection execution allowed: false.
- artifact detection is not performed.
- download workflow is not active.
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

## Validation style

L17.2 deliberately avoids nested CLI validation cascades.

The L17.2 readback proves both accepted L17.1 source branches through direct module readback:

1. default compact readback remains passive and has artifact preflight authorization false.
2. authorized compact readback remains passive and has artifact preflight authorization true.

The direct-manifest validation should run one shallow L17.2 compact CLI smoke, not a large chain of nested CLI calls.

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L17.2"`.
- `l17_1_passive_preflight_gate_accepted:true`.
- `l17_1_default_compact_readback_ok:true`.
- `l17_1_authorized_compact_readback_ok:true`.
- `default_artifact_preflight_authorized:false`.
- `authorized_artifact_preflight_authorized:true`.
- `artifact_detection_preflight_is_readback_only:true`.
- `artifact_detection_execution_allowed:false`.
- `artifact_detection_active:false`.
- `artifact_detection_performed:false`.
- `download_workflow_active:false`.
- `download_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.
- `avoid_nested_cli_validation_cascades:true`.
- `one_shallow_cli_smoke_recommended:true`.

## Next patch

L17.3 Microsoft Edge artifact detection passive plan checkpoint.

## L17.2a validator import-context repair

L17.2a repairs the brief validator execution path used by the direct manifest validation command:

```powershell
py scripts/patch_l17_02_brief_validate.py --repo-root C:\dev\patchops
```

When Python executes a file by script path, `sys.path[0]` points at `scripts/` instead of the repository root. The validator therefore self-bootstraps the repository root before importing `patchops`.

This repair is still passive: no Microsoft Edge start, no Selenium import, no CDP use, no DOM scraping, no artifact detection, no artifact content reading, no click/download/paste/send/package-run side effect, no localhost PatchOps server, no browser extension, and no git commit or git push.

## L17.2b exact doc-contract phrase repair

The L17.2 validation contract includes the exact phrase:

```text
avoid nested CLI validation cascades
```

This phrase means L17.2 should prove its source readbacks through direct module checks and only one shallow compact CLI smoke. It must not expand into a long nested CLI chain.

This repair is passive: no Microsoft Edge start, no Selenium import, no CDP use, no DOM scraping, no prompt text extraction, no conversation reading, no artifact detection, no artifact content reading, no click/download/paste/send/package-run side effect, no localhost PatchOps server, no browser extension, and no git commit or git push.
