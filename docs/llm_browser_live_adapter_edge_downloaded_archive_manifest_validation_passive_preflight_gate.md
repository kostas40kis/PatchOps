# L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate

L22.1 starts the Microsoft Edge downloaded-archive manifest validation stream after accepted L21.7a.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair
```

Preflight authorization token:

```text
PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L22.1.
- downloaded-archive manifest validation passive preflight gate.
- manifest validation preflight authorization is readback-only.
- L21.7a archive final marker repair remains accepted.
- L21 completion means metadata-only listing of the synthetic archive fixture.
- manifest validation execution allowed: false.
- manifest validation active: false.
- manifest validation is not performed.
- downloaded manifest is not read.
- downloaded archive is not extracted.
- archive member bytes are not read.
- downloaded archive may not be opened for manifest validation in L22.1.
- downloaded archive contents are not listed for manifest validation in L22.1.
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
- no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Meaning of authorization in L22.1

L22.1 authorization only proves a future downloaded-archive manifest validation preflight gate exists.

Even with the correct flag and token:

- manifest validation execution allowed: false.
- manifest validation active: false.
- manifest validation is not performed.
- downloaded manifest is not read.
- downloaded archive may not be opened for manifest validation in L22.1.
- archive member bytes are not read.
- package-run from browser remains inactive.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no manifest validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-manifest-validation-preflight --authorization-token PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L22.1"`.
- `source_l21_7a_archive_final_marker_repair_accepted:true`.
- `l21_completion_means_metadata_only_archive_listing:true`.
- `manifest_validation_preflight_authorized:true`.
- `manifest_validation_preflight_authorization_is_readback_only_in_l22_1:true`.
- `manifest_validation_execution_allowed:false`.
- `manifest_validation_active:false`.
- `manifest_validation_performed:false`.
- `downloaded_manifest_read:false`.
- `downloaded_archive_opened_for_manifest_validation:false`.
- `downloaded_archive_contents_listed_for_manifest_validation:false`.
- `downloaded_archive_extracted:false`.
- `archive_member_bytes_read:false`.
- `downloaded_file_bytes_read:false`.
- `downloaded_file_stat_performed:false`.
- `downloaded_file_hash_performed:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `chatgpt_url_opened:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint.
