# L18.3 Microsoft Edge download workflow passive plan checkpoint

L18.3 defines the safe future download workflow plan after the accepted L18.2 CLI/readback checkpoint.

Command:

```text
browser-start-supervised-launch-edge-download-workflow-passive-plan-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-download-workflow-cli-readback-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.3.
- download workflow passive plan checkpoint.
- passive plan checkpoint.
- L18.2 CLI/readback checkpoint remains accepted.
- safe future download workflow plan.
- download candidate means metadata-only evidence for a PatchOps zip artifact selected by the accepted L17 stream.
- download plan does not click a download control.
- download plan does not download a file.
- download plan does not read downloaded file bytes.
- download plan does not read artifact content.
- download plan does not run a package.
- download workflow execution allowed: false.
- download workflow active: false.
- download is not performed.
- downloaded file bytes are not read.
- download staging path is planned metadata only.
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

## Download candidate definition

In L18.3, a download candidate means metadata-only evidence for a PatchOps zip artifact selected by the accepted L17 stream.

A download candidate does not mean:

- clicking a download control.
- downloading a file.
- reading downloaded file bytes.
- reading artifact content.
- running a package.
- pasting into a browser.
- sending or submitting a message.

Future candidate filename rules remain:

- extension must be `.zip`.
- recommended pattern is `patch_*_patchops_bundle.zip`.
- reject non-zip candidates.
- reject ambiguous multiple candidates.

## Future passive plan

The safe future download workflow plan is planned but not executed in L18.3:

1. Confirm the L18.2 CLI/readback checkpoint is accepted.
2. Require an L18.4-or-later explicit download authorization token.
3. Reuse the L17 metadata-selected PatchOps zip candidate.
4. Plan a download staging path without creating directories or reading files.
5. In a later live phase only, click a download control after operator review.
6. Emit a download completion metadata readback before any file-byte validation stream.

Download workflow remains inactive in L18.3.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-workflow-passive-plan-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L18.3"`.
- `source_l18_2_cli_readback_checkpoint_accepted:true`.
- `download_candidate_definition_blocks_download_file_read_package_run:true`.
- `future_download_plan_is_planned_not_executed:true`.
- `future_download_plan_blocks_click_download_file_read_paste_send_package_run:true`.
- `download_workflow_execution_allowed:false`.
- `download_workflow_active:false`.
- `download_allowed:false`.
- `download_performed:false`.
- `downloaded_file_bytes_read:false`.
- `download_staging_path_metadata_only:true`.
- `download_staging_directory_created:false`.
- `click_download_performed:false`.
- `artifact_content_reading_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L18.4 Microsoft Edge download workflow controlled live authorization gate.
