# L20.4 Microsoft Edge downloaded-file filesystem validation controlled authorization gate

L20.4 adds the controlled authorization gate after the accepted L20.3 passive plan checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-controlled-authorization-gate
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-plan-checkpoint
```

Authorization token:

```text
PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L20.4.
- downloaded-file filesystem validation controlled authorization gate.
- controlled authorization gate.
- L20.3 passive plan checkpoint remains accepted.
- explicit future filesystem validation authorization token.
- filesystem validation authorization is readback-only.
- filesystem validation execution allowed: false.
- filesystem validation active: false.
- filesystem validation is not performed.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
- archive validation remains inactive.
- downloaded file existence check is not performed.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
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

## Meaning of authorization in L20.4

L20.4 authorization only proves that the future filesystem validation gate can distinguish default readback from explicitly authorized readback.

Even with the correct flag and token:

- filesystem validation execution allowed: false.
- filesystem validation active: false.
- filesystem validation is not performed.
- real filesystem validation remains inactive.
- real file existence check remains inactive.
- real file stat remains inactive.
- real file hash remains inactive.
- archive validation remains inactive.
- downloaded file existence check is not performed.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
- downloaded archive contents are not listed.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- no browser is started.
- no package is run.

## CLI commands

Default passive readback:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-controlled-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no filesystem validation execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-controlled-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-filesystem-validation-authorization --authorization-token PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY --json --compact
```

## Future authorization gate plan

The L20.4 plan is planned but not executed:

1. Confirm the L20.3 passive plan checkpoint remains accepted.
2. Require the explicit filesystem validation authorization flag.
3. Require the exact filesystem validation authorization token.
4. In L20.5 or later only, check file existence without reading file bytes.
5. Keep stat, hash, file-byte read, archive opening/listing/extraction, manifest read, package-run, pasteback, and auto-send behind separate gates.
6. Keep L20.4 as readback-only.

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L20.4"`.
- `source_l20_3_passive_plan_checkpoint_accepted:true`.
- `filesystem_validation_authorized_for_future_phase:true`.
- `filesystem_validation_authorization_is_readback_only_in_l20_4:true`.
- `controlled_filesystem_validation_execution_allowed:false`.
- `filesystem_validation_execution_allowed:false`.
- `filesystem_validation_active:false`.
- `filesystem_validation_performed:false`.
- `real_filesystem_validation_active:false`.
- `real_file_exists_check_performed:false`.
- `real_file_stat_performed:false`.
- `real_file_hash_performed:false`.
- `archive_validation_performed:false`.
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

L20.5 Microsoft Edge first controlled downloaded-file filesystem validation proof.
