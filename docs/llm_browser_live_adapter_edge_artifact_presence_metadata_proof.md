# L17.5 Microsoft Edge first controlled artifact-presence metadata proof

L17.5 proves the first controlled artifact-presence decision from metadata only after the accepted L17.4 controlled live authorization gate.

Command:

```text
browser-start-supervised-launch-edge-artifact-presence-metadata-proof
```

Source command:

```text
browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate
```

Metadata proof authorization token:

```text
PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_METADATA_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L17.5.
- controlled artifact-presence metadata proof.
- metadata-only artifact-presence classification.
- L17.4 controlled live authorization gate remains accepted.
- metadata proof authorization token.
- artifact presence metadata proof may classify synthetic metadata only.
- artifact presence metadata proof does not inspect a real page.
- artifact presence metadata proof does not read artifact content.
- artifact presence metadata proof does not click a download control.
- artifact presence metadata proof does not download a file.
- artifact presence metadata proof does not run a package.
- live browser artifact detection remains inactive.
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
- no artifact content reading.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## What L17.5 can do

L17.5 may classify metadata supplied by tests, fixtures, or the operator. It can decide whether that metadata describes a visible PatchOps zip candidate in the latest assistant reply.

Allowed metadata keys are limited to:

- filename.
- visible filename metadata.
- download control accessible-name metadata.
- download control visible/enabled booleans.
- latest assistant reply scope boolean.
- artifact card role or label metadata.
- already processed boolean.
- candidate count.

Forbidden metadata remains:

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

## CLI commands

Default readback, no classification:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-presence-metadata-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized metadata-only positive fixture proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-artifact-presence-metadata-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-artifact-presence-metadata-proof --authorization-token PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_METADATA_PROOF_AUTHORIZED --candidate-filename patch_999_example_patchops_bundle.zip --download-control-visible --download-control-enabled --latest-assistant-reply-scope --json --compact
```

## Positive metadata decision requirements

A positive artifact-presence metadata decision requires:

1. explicit metadata proof authorization.
2. filename ending in `.zip`.
3. filename matching `patch_*_patchops_bundle.zip`.
4. visible filename metadata matching the filename.
5. visible and enabled download-control metadata.
6. latest assistant reply scope.
7. not already processed.
8. exactly one candidate.
9. no forbidden metadata keys.

## Expected compact JSON fields

The authorized positive fixture readback should confirm:

- `ok:true`.
- `patch:"L17.5"`.
- `source_l17_4_controlled_live_authorization_gate_accepted:true`.
- `artifact_presence_metadata_proof_authorized:true`.
- `artifact_presence_metadata_classification_performed:true`.
- `artifact_presence_detected_from_metadata:true`.
- `artifact_presence_detection_scope:"synthetic_or_operator_supplied_metadata_only"`.
- `real_page_inspection_performed:false`.
- `live_browser_artifact_detection_active:false`.
- `live_browser_artifact_detection_performed:false`.
- `artifact_content_reading_performed:false`.
- `download_workflow_active:false`.
- `download_performed:false`.
- `click_download_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L17.6 Microsoft Edge artifact detection broad checkpoint.
