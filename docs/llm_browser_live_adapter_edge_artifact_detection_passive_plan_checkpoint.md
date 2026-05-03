# L17.3 Microsoft Edge artifact detection passive plan checkpoint

L17.3 defines the safe future artifact-presence detection plan after the accepted L17.2 CLI/readback checkpoint.

Command:

```text
browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-detection-cli-readback-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.3.
- passive plan checkpoint only.
- L17.2 CLI/readback checkpoint remains accepted.
- safe future artifact-presence detection plan.
- artifact detection execution allowed: false.
- artifact detection is not performed.
- download workflow active: false.
- download workflow remains inactive.
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

## Artifact presence definition

In L17.3, artifact presence means metadata-only evidence that a downloadable PatchOps zip candidate exists in the latest assistant reply.

Artifact presence does not mean reading artifact content.
Artifact presence does not mean clicking a download control.
Artifact presence does not mean downloading a file.
Artifact presence does not mean running a package.

Future allowed metadata signals are limited to things like:

- latest assistant reply container identity.
- visible filename metadata ending in `.zip`.
- filename pattern metadata such as `patch_*_patchops_bundle.zip`.
- download control accessible-name metadata.
- visible/enabled state of a nearby download control.
- artifact card role or label metadata.
- whether the candidate belongs to the latest assistant reply.
- whether the candidate has already been processed by metadata key.

Forbidden observations remain:

- conversation text.
- prompt text.
- account data.
- artifact content.
- artifact source code.
- downloaded file bytes.
- cookies.
- tokens.
- local storage.
- older conversation messages.

## Future passive plan

The safe future artifact-presence detection plan is planned but not executed in L17.3:

1. Confirm the L17.2 CLI/readback checkpoint is accepted.
2. Require a future explicit live authorization token in L17.4 or later.
3. In a later live phase only, open the allowlisted ChatGPT URL with the dedicated Microsoft Edge runtime profile.
4. Observe latest-assistant-reply metadata without text extraction.
5. Classify artifact presence from metadata only.
6. Emit operator review readback without click, download, paste, send, or package run.

Download workflow remains inactive in L17.3 and remains a separate future stream.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L17.3"`.
- `source_l17_2_cli_readback_checkpoint_accepted:true`.
- `artifact_presence_definition_blocks_content_and_download:true`.
- `artifact_presence_definition_forbids_sensitive_observations:true`.
- `future_artifact_presence_plan_is_planned_not_executed:true`.
- `future_artifact_presence_plan_blocks_download_paste_send_package_run:true`.
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

L17.4 Microsoft Edge artifact detection controlled live authorization gate.

## L17.3a exact doc-contract phrase repair

The L17.3 validation contract requires these exact lowercase phrases:

```text
artifact presence does not mean reading artifact content
artifact presence does not mean clicking a download control
artifact presence does not mean downloading a file
artifact presence does not mean running a package
```

These phrases are part of the passive artifact-presence definition. They keep artifact presence separate from artifact content reading, clicking, downloading, and package execution.

This repair is passive: no Microsoft Edge start, no Selenium import, no CDP use, no DOM scraping, no prompt text extraction, no conversation reading, no artifact detection, no artifact content reading, no click/download/paste/send/package-run side effect, no localhost PatchOps server, no browser extension, and no git commit or git push.
