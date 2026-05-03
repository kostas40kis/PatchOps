# L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate

L21.4 adds the controlled authorization gate after the accepted L21.3 passive plan checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint
```

Authorization token:

```text
PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
```

## Boundary

- L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate
- browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate
- browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint
- PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
- Microsoft Edge first
- Opera second
- downloaded-archive validation controlled authorization gate
- controlled authorization gate
- L21.3 passive plan checkpoint remains accepted
- explicit future archive validation authorization token
- archive validation authorization is readback-only
- archive validation execution allowed: false
- archive validation active: false
- archive validation is not performed
- downloaded archive is not opened
- downloaded archive contents are not listed
- downloaded archive is not extracted
- downloaded manifest is not read
- downloaded file bytes are not read
- downloaded file stat is not performed
- downloaded file hash is not performed
- hash validation remains inactive
- manifest read remains inactive
- download workflow remains inactive
- real browser download remains inactive
- pasteback remains inactive
- package-run from browser remains inactive
- PatchOps remains source of truth
- target URL allowlist remains enforced
- ChatGPT URL may be selected but not opened
- dedicated Microsoft Edge runtime profile remains required for future live phases
- never use the default Microsoft Edge profile
- no Microsoft Edge start
- no Selenium import
- no CDP use
- no DOM scraping
- no prompt text extraction
- no conversation reading
- no artifact content reading
- no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect
- no localhost PatchOps server
- no browser extension
- no git commit or git push
- L21.5 Microsoft Edge first controlled downloaded-archive validation proof

## Meaning of authorization in L21.4

L21.4 authorization only proves that the future archive validation gate can distinguish default readback from explicitly authorized readback.

Even with the correct flag and token, archive validation execution remains false. No archive is opened, no contents are listed, no archive is extracted, no manifest is read, no file bytes are read, no browser is started, and no package is run.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no archive validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-controlled-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-archive-validation-authorization --authorization-token PATCHOPS_L21_EDGE_DOWNLOADED_ARCHIVE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY --json --compact
```

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L21.4"`.
- `source_l21_3_passive_plan_checkpoint_accepted:true`.
- `archive_validation_authorized_for_future_phase:true`.
- `archive_validation_authorization_is_readback_only_in_l21_4:true`.
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

L21.5 Microsoft Edge first controlled downloaded-archive validation proof.
