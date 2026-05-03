# L20.7 Microsoft Edge downloaded-file filesystem validation final acceptance marker

L20.7 is the final acceptance marker for the Microsoft Edge downloaded-file filesystem validation stream.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-final-acceptance-marker
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-broad-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.7.
- downloaded-file filesystem validation final acceptance marker.
- L20.1 through L20.6 remain accepted.
- L20 downloaded-file filesystem validation stream complete.
- L20 completion means synthetic-fixture existence-only validation.
- existence-only filesystem validation proof remains accepted.
- only the synthetic PatchOps runtime fixture existence check is accepted.
- real file existence check is accepted only for the synthetic fixture.
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
- archive validation remains a separate future stream.
- hash validation remains a separate future stream.
- file-byte read remains a separate future stream.
- manifest read remains a separate future stream.
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

## Meaning of completion

L20 completion means PatchOps has accepted a Microsoft Edge downloaded-file filesystem validation stream that is limited to an existence-only proof against the synthetic PatchOps runtime fixture:

```text
data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip
```

This completion does not allow real browser downloads, file stat, file hash, byte reading, archive opening, archive listing, archive extraction, manifest reading, pasteback, send/submit, or package-run.

Archive validation must start as a separate future stream.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-final-acceptance-marker --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The final marker should confirm:

- `ok:true`.
- `patch:"L20.7"`.
- `source_l20_6_broad_checkpoint_accepted:true`.
- `l20_1_through_l20_6_remain_accepted:true`.
- `l20_downloaded_file_filesystem_validation_stream_complete:true`.
- `l20_completion_means_synthetic_fixture_existence_only_validation:true`.
- `existence_only_filesystem_validation_proof_remains_accepted:true`.
- `only_synthetic_patchops_runtime_fixture_existence_check_is_accepted:true`.
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
- `archive_validation_remains_separate_future_stream:true`.
- `hash_validation_remains_separate_future_stream:true`.
- `file_byte_read_remains_separate_future_stream:true`.
- `manifest_read_remains_separate_future_stream:true`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L21.1 Microsoft Edge downloaded-archive validation passive preflight gate.
