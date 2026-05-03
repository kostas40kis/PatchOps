# L21.1 Microsoft Edge downloaded-archive validation passive preflight gate

L21.1 starts the Microsoft Edge downloaded-archive validation stream after accepted L20.7.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-passive-preflight-gate
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-final-acceptance-marker
```

Preflight authorization token:

```text
PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L21.1.
- downloaded-archive validation passive preflight gate.
- archive validation preflight authorization is readback-only.
- L20.7 filesystem validation final marker remains accepted.
- L20 completion means synthetic-fixture existence-only validation.
- archive validation execution allowed: false.
- archive validation active: false.
- archive validation is not performed.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- downloaded file bytes are not read.
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
- no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Meaning of authorization in L21.1

L21.1 authorization only proves a future downloaded-archive validation preflight gate exists.

Even with the correct flag and token:

- archive validation execution allowed: false.
- archive validation active: false.
- archive validation is not performed.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- downloaded file bytes are not read.
- package-run from browser remains inactive.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no archive validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-archive-validation-preflight --authorization-token PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L21.1"`.
- `source_l20_7_final_marker_accepted:true`.
- `l20_downloaded_file_filesystem_validation_stream_complete:true`.
- `l20_completion_means_synthetic_fixture_existence_only_validation:true`.
- `archive_validation_preflight_authorized:true`.
- `archive_validation_preflight_authorization_is_readback_only_in_l21_1:true`.
- `archive_validation_execution_allowed:false`.
- `archive_validation_active:false`.
- `archive_validation_performed:false`.
- `downloaded_archive_opened:false`.
- `downloaded_archive_contents_listed:false`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L21.2 Microsoft Edge downloaded-archive validation CLI/readback checkpoint.
