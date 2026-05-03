# L20.6 Microsoft Edge downloaded-file filesystem validation broad checkpoint

L20.6 is the broad checkpoint for the Microsoft Edge downloaded-file filesystem validation stream.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-broad-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-existence-proof
```

L20.5 existence proof authorization token:

```text
PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_EXISTENCE_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.6.
- downloaded-file filesystem validation broad checkpoint.
- broad filesystem validation checkpoint.
- L20.1 through L20.5 remain accepted.
- existence-only filesystem validation proof remains accepted.
- default existence proof readback remains passive.
- authorized existence proof readback remains existence-only.
- unsafe candidate remains rejected without filesystem access.
- only the synthetic PatchOps runtime fixture existence check is allowed.
- real file existence check is allowed only for the synthetic fixture.
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

## What L20.6 proves

L20.6 consolidates:

1. L20.1 filesystem validation passive preflight gate.
2. L20.2 filesystem validation CLI/readback checkpoint.
3. L20.3 filesystem validation passive plan checkpoint.
4. L20.4 filesystem validation controlled authorization gate.
5. L20.5 first controlled existence-only proof.

L20.6 validates that the source default readback remains passive, the source authorized readback remains existence-only, and an unsafe candidate is rejected before filesystem access.

The only successful filesystem validation operation allowed by the L20 stream so far is the existence-only check against:

```text
data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip
```

L20.6 does not permit file stat, file hash, byte reading, archive opening/listing/extraction, manifest reading, browser downloads, pasteback, or package-run.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-broad-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L20.6"`.
- `l20_1_through_l20_5_remain_accepted:true`.
- `existence_only_filesystem_validation_proof_remains_accepted:true`.
- `default_existence_proof_readback_remains_passive:true`.
- `authorized_existence_proof_readback_remains_existence_only:true`.
- `unsafe_candidate_remains_rejected_without_filesystem_access:true`.
- `only_synthetic_fixture_existence_check_is_allowed:true`.
- `filesystem_validation_scope:"existence_only_synthetic_patchops_runtime_fixture"`.
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

L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker.
