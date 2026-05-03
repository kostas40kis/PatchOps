# L20.5 Microsoft Edge first controlled downloaded-file filesystem validation proof

L20.5 performs the first controlled downloaded-file filesystem validation proof after the accepted L20.4 controlled authorization gate.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-existence-proof
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-controlled-authorization-gate
```

Source L20.4 authorization token:

```text
PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
```

L20.5 existence proof authorization token:

```text
PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_EXISTENCE_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.5.
- first controlled downloaded-file filesystem validation proof.
- existence-only filesystem validation proof.
- synthetic PatchOps runtime fixture only.
- L20.4 controlled authorization gate remains accepted.
- explicit L20.5 existence proof authorization token.
- controlled filesystem validation execution is limited to existence-only proof.
- real file existence check may be performed only against the explicit synthetic fixture.
- real file stat remains inactive.
- real file hash remains inactive.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- archive validation remains inactive.
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
- no click/download/stat/hash/archive/manifest/byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## What is allowed in L20.5

L20.5 may perform one existence-only check against this explicit synthetic PatchOps runtime fixture:

```text
data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip
```

The path is treated as prior metadata until the existence-only proof is authorized with the exact L20.5 token. The proof may answer whether the path exists. It must not collect file size, timestamps, permissions, hashes, bytes, archive entries, manifest contents, package contents, or any browser content.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-existence-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized existence-only proof:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-existence-proof --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-filesystem-existence-proof --authorization-token PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_EXISTENCE_PROOF_AUTHORIZED --candidate-path-metadata data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L20.5"`.
- `source_l20_4_controlled_authorization_gate_accepted:true`.
- `filesystem_validation_authorized_by_l20_4_for_future_phase:true`.
- `filesystem_existence_proof_authorized:true`.
- `candidate_safety.candidate_safe_for_l20_5_existence_only_proof:true`.
- `existence_validation_result.existence_only_validation_performed:true`.
- `existence_validation_result.candidate_exists:true`.
- `filesystem_validation_performed:true`.
- `real_file_exists_check_performed:true`.
- `downloaded_file_exists_check_performed:true`.
- `real_file_stat_performed:false`.
- `real_file_hash_performed:false`.
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

L20.6 Microsoft Edge downloaded-file filesystem validation broad checkpoint.
