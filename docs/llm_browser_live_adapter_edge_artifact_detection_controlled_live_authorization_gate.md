# L17.4 Microsoft Edge artifact detection controlled live authorization gate

L17.4 adds the controlled live authorization gate after the accepted L17.3 passive plan checkpoint.

Command:

```text
browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint
```

Authorization token:

```text
PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_LIVE_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.4.
- controlled live authorization gate.
- passive/readback-only in L17.4.
- L17.3 passive plan checkpoint remains accepted.
- explicit future live authorization token.
- live artifact detection authorization is readback-only.
- live artifact detection execution allowed: false.
- artifact detection execution allowed: false.
- artifact detection is not performed.
- artifact presence detection is not performed.
- download workflow active: false.
- download workflow remains inactive.
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
- no artifact detection.
- no artifact content reading.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-live-artifact-detection-authorization --authorization-token PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_LIVE_AUTHORIZED_READBACK_ONLY --json --compact
```

## Meaning of authorization in L17.4

In L17.4, authorization only proves that the future live authorization gate can distinguish default readback from explicitly authorized readback.

Even with the correct flag and token:

- live artifact detection execution allowed: false.
- artifact detection execution allowed: false.
- artifact presence detection is not performed.
- no browser is started.
- no page is inspected.
- no artifact is detected.
- no download workflow is activated.
- no package is run.

## Future gate plan

The L17.4 plan is planned but not executed:

1. Confirm the L17.3 passive plan checkpoint remains accepted.
2. Require the explicit live artifact detection authorization flag.
3. Require the exact live artifact detection authorization token.
4. Require the dedicated Microsoft Edge runtime profile and reject the default Microsoft Edge profile.
5. In L17.5 or later only, a future live phase may open the allowlisted ChatGPT URL after operator review.
6. L17.4 readback does not execute live artifact detection, click, download, paste, send, or package run.

Download workflow remains inactive and remains a separate future stream.

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L17.4"`.
- `source_l17_3_passive_plan_checkpoint_accepted:true`.
- `live_artifact_detection_authorization_is_readback_only_in_l17_4:true`.
- `live_artifact_detection_execution_allowed:false`.
- `artifact_presence_detection_execution_allowed:false`.
- `artifact_detection_execution_allowed:false`.
- `artifact_detection_active:false`.
- `artifact_detection_performed:false`.
- `artifact_presence_detection_performed:false`.
- `download_workflow_active:false`.
- `download_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `requires_dedicated_edge_runtime_profile_in_future_live_phase:true`.
- `default_microsoft_edge_profile_allowed:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L17.5 Microsoft Edge first controlled artifact-presence metadata proof.
