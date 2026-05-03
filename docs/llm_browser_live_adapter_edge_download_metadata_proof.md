# L18.5 Microsoft Edge first controlled download metadata proof

L18.5 proves the first controlled download-readiness decision from metadata only after the accepted L18.4 controlled live authorization gate.

Command:

```text
browser-start-supervised-launch-edge-download-metadata-proof
```

Source command:

```text
browser-start-supervised-launch-edge-download-workflow-controlled-live-authorization-gate
```

Download metadata proof authorization token:

```text
PATCHOPS_L18_EDGE_DOWNLOAD_METADATA_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L18.5.
- controlled download metadata proof.
- metadata-only download readiness classification.
- L18.4 controlled live authorization gate remains accepted.
- download metadata proof authorization token.
- download metadata proof may classify synthetic metadata only.
- download metadata proof does not inspect a real page.
- download metadata proof does not click a download control.
- download metadata proof does not download a file.
- download metadata proof does not create a staging directory.
- download metadata proof does not read downloaded file bytes.
- download metadata proof does not read artifact content.
- download metadata proof does not run a package.
- live browser download workflow remains inactive.
- download workflow active: false.
- download workflow execution allowed: false.
- download is not performed.
- downloaded file bytes are not read.
- download staging directory is not created.
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

## What L18.5 can do

L18.5 may classify metadata supplied by tests, fixtures, or the operator. It can decide whether that metadata is sufficient for a future download action in a later phase.

Allowed metadata keys are limited to:

- candidate filename.
- candidate visible filename metadata.
- candidate pattern.
- artifact presence from L17 metadata.
- download control visible/enabled metadata.
- download authorization from L18.4 metadata.
- target URL allowlist metadata.
- staging path metadata.
- staging path is metadata-only boolean.
- candidate count.
- already downloaded boolean.
- already processed boolean.

Forbidden metadata remains:

- conversation text.
- prompt text.
- account data.
- artifact content.
- artifact source code.
- downloaded file bytes.
- downloaded file content.
- cookies.
- tokens.
- local storage.
- older conversation messages.
- DOM HTML.
- download href.

## CLI commands

Default readback, no classification:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-metadata-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized metadata-only positive fixture proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-download-metadata-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-download-metadata-proof --authorization-token PATCHOPS_L18_EDGE_DOWNLOAD_METADATA_PROOF_AUTHORIZED --candidate-filename patch_999_example_patchops_bundle.zip --artifact-presence-from-l17-metadata --download-control-visible-metadata --download-control-enabled-metadata --download-authorization-from-l18-4 --target-url-allowed-metadata --staging-path-is-metadata-only --json --compact
```

## Positive metadata decision requirements

A positive download-readiness metadata decision requires:

1. explicit download metadata proof authorization.
2. candidate filename ending in `.zip`.
3. candidate filename matching `patch_*_patchops_bundle.zip`.
4. visible filename metadata matching the candidate filename.
5. L17 metadata-only artifact presence confirmed.
6. L18.4 download authorization metadata confirmed.
7. target URL allowlist metadata confirmed.
8. visible and enabled download-control metadata.
9. staging path metadata declared metadata-only.
10. not already downloaded.
11. not already processed.
12. exactly one candidate.
13. no forbidden metadata keys.

## Expected compact JSON fields

The authorized positive fixture readback should confirm:

- `ok:true`.
- `patch:"L18.5"`.
- `source_l18_4_controlled_live_authorization_gate_accepted:true`.
- `download_metadata_proof_authorized:true`.
- `download_metadata_classification_performed:true`.
- `download_readiness_confirmed_from_metadata:true`.
- `download_metadata_scope:"synthetic_or_operator_supplied_metadata_only"`.
- `download_workflow_execution_allowed:false`.
- `download_workflow_active:false`.
- `download_allowed:false`.
- `download_performed:false`.
- `downloaded_file_bytes_read:false`.
- `download_staging_directory_created:false`.
- `click_download_performed:false`.
- `artifact_content_reading_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L18.6 Microsoft Edge download workflow broad checkpoint.
