# L19.5 Microsoft Edge first controlled downloaded-file metadata validation proof

L19.5 proves the first controlled downloaded-file validation decision from metadata only after the accepted L19.4 controlled authorization gate.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-controlled-authorization-gate
```

Downloaded-file metadata validation proof authorization token:

```text
PATCHOPS_L19_EDGE_DOWNLOADED_FILE_METADATA_VALIDATION_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L19.5.
- controlled downloaded-file metadata validation proof.
- metadata-only downloaded-file validation decision.
- L19.4 controlled authorization gate remains accepted.
- downloaded-file metadata validation proof authorization token.
- downloaded-file metadata validation may classify synthetic metadata only.
- downloaded-file metadata validation does not check whether a file exists.
- downloaded-file metadata validation does not stat a file.
- downloaded-file metadata validation does not hash a file.
- downloaded-file metadata validation does not open a downloaded archive.
- downloaded-file metadata validation does not list downloaded archive contents.
- downloaded-file metadata validation does not extract a downloaded archive.
- downloaded-file metadata validation does not read a downloaded manifest.
- downloaded-file metadata validation does not read downloaded file bytes.
- downloaded-file metadata validation does not run a package.
- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded manifest is not read.
- download workflow remains inactive.
- real browser download remains inactive.
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
- no click/download/file-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## What L19.5 can do

L19.5 may classify downloaded-file validation metadata supplied by tests, fixtures, or the operator. It can decide whether that metadata is sufficient for a future file validation action in a later phase.

Allowed metadata keys are limited to:

- candidate path metadata.
- candidate filename metadata.
- candidate pattern.
- candidate extension metadata.
- candidate path is metadata-only boolean.
- downloaded-file validation authorization from L19.4 metadata.
- download metadata proof from L18.5 metadata.
- download workflow complete from L18.7 metadata.
- target URL allowlist metadata.
- candidate count.
- already validated boolean.
- already processed boolean.
- operator reviewed metadata boolean.

Forbidden metadata remains:

- file exists.
- file stat.
- file size bytes from disk.
- file hash.
- file bytes.
- downloaded file bytes.
- downloaded file content.
- archive members.
- archive bytes.
- manifest content.
- manifest JSON.
- artifact content.
- artifact source code.
- conversation text.
- prompt text.
- account data.
- cookies.
- tokens.
- local storage.
- DOM HTML.
- download href.

## CLI commands

Default readback, no classification:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized metadata-only positive fixture proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-downloaded-file-metadata-validation-proof --authorization-token PATCHOPS_L19_EDGE_DOWNLOADED_FILE_METADATA_VALIDATION_PROOF_AUTHORIZED --candidate-path-metadata data/runtime/browser_downloads/patch_999_example_patchops_bundle.zip --candidate-filename-metadata patch_999_example_patchops_bundle.zip --candidate-extension-metadata .zip --candidate-path-is-metadata-only --downloaded-file-validation-authorization-from-l19-4 --download-metadata-proof-from-l18-5 --download-workflow-complete-from-l18-7 --target-url-allowed-metadata --operator-reviewed-metadata --json --compact
```

## Positive metadata decision requirements

A positive downloaded-file metadata validation decision requires:

1. explicit downloaded-file metadata validation proof authorization.
2. candidate path declared metadata-only.
3. candidate filename ending in `.zip`.
4. candidate filename matching `patch_*_patchops_bundle.zip`.
5. candidate path metadata ending with the candidate filename.
6. L19.4 validation authorization metadata confirmed.
7. L18.5 download metadata proof confirmed.
8. L18.7 download workflow completion metadata confirmed.
9. target URL allowlist metadata confirmed.
10. operator reviewed metadata confirmed.
11. not already validated.
12. not already processed.
13. exactly one candidate.
14. no forbidden metadata keys.

## Expected compact JSON fields

The authorized positive fixture readback should confirm:

- `ok:true`.
- `patch:"L19.5"`.
- `source_l19_4_controlled_authorization_gate_accepted:true`.
- `downloaded_file_metadata_validation_proof_authorized:true`.
- `downloaded_file_metadata_validation_classification_performed:true`.
- `downloaded_file_metadata_validation_ready:true`.
- `downloaded_file_metadata_validation_scope:"synthetic_or_operator_supplied_metadata_only"`.
- `controlled_downloaded_file_validation_execution_allowed:false`.
- `downloaded_file_validation_execution_allowed:false`.
- `downloaded_file_validation_active:false`.
- `downloaded_file_validation_performed:false`.
- `downloaded_file_exists_check_performed:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L19.6 Microsoft Edge downloaded-file validation broad checkpoint.
