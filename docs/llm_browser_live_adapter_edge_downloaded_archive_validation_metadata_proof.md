# L21.5 Microsoft Edge first controlled downloaded-archive validation proof

L21.5 performs the first controlled downloaded-archive validation proof after the accepted L21.4 controlled authorization gate.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate
```

Source L21.4 authorization token:

```text
PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
```

L21.5 archive metadata proof authorization token:

```text
PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L21.5.
- first controlled downloaded-archive validation proof.
- archive metadata-only validation proof.
- synthetic PatchOps runtime archive fixture only.
- L21.4 controlled authorization gate remains accepted.
- explicit L21.5 archive metadata proof authorization token.
- controlled archive validation execution is limited to metadata-only proof.
- downloaded archive may be opened only for metadata listing of the explicit synthetic fixture.
- downloaded archive contents may be listed as metadata only.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- archive member bytes are not read.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- package-run from browser remains inactive.
- pasteback remains inactive.
- download workflow remains inactive.
- real browser download remains inactive.
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
- no click/download/stat/hash/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## What is allowed in L21.5

L21.5 may open this explicit synthetic PatchOps runtime archive fixture and list entry names only:

```text
data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip
```

The proof may confirm the archive is openable and that its entry names include expected bundle-shaped names such as `manifest.json`. It must not extract entries, read manifest contents, read archive member bytes, calculate hashes, run the package, paste into a browser, send a message, or inspect any browser page.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized archive metadata-only proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-metadata-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-archive-metadata-proof --authorization-token PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_METADATA_PROOF_AUTHORIZED --candidate-path-metadata data/runtime/browser_downloads/patch_l21_05_synthetic_archive_patchops_bundle.zip --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L21.5"`.
- `source_l21_4_controlled_authorization_gate_accepted:true`.
- `archive_validation_authorized_by_l21_4_for_future_phase:true`.
- `archive_metadata_proof_authorized:true`.
- `candidate_safety.candidate_safe_for_l21_5_metadata_only_proof:true`.
- `archive_metadata_validation_result.archive_metadata_validation_performed:true`.
- `archive_metadata_validation_result.archive_validation_ready:true`.
- `archive_metadata_validation_result.downloaded_archive_opened:true`.
- `archive_metadata_validation_result.downloaded_archive_contents_listed:true`.
- `downloaded_archive_opened:true`.
- `downloaded_archive_contents_listed:true`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `archive_member_bytes_read:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L21.6 Microsoft Edge downloaded-archive validation broad checkpoint.
