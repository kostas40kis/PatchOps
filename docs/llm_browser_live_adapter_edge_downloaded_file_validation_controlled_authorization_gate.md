# L19.4 Microsoft Edge downloaded-file validation controlled authorization gate

L19.4 adds the controlled authorization gate after the accepted L19.3 passive plan checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-controlled-authorization-gate
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-passive-plan-checkpoint
```

Authorization token:

```text
PATCHOPS_L19_EDGE_DOWNLOADED_FILE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L19.4.
- downloaded-file validation controlled authorization gate.
- passive/readback-only in L19.4.
- L19.3 passive plan checkpoint remains accepted.
- explicit future downloaded-file validation authorization token.
- downloaded-file validation authorization is readback-only.
- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
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

## Meaning of authorization in L19.4

L19.4 authorization only proves that the future downloaded-file validation gate can distinguish default readback from explicitly authorized readback.

Even with the correct flag and token:

- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
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
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-controlled-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

Authorized passive readback, still no execution:

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-controlled-authorization-gate --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --allow-downloaded-file-validation-authorization --authorization-token PATCHOPS_L19_EDGE_DOWNLOADED_FILE_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY --json --compact
```

## Future gate plan

The L19.4 plan is planned but not executed:

1. Confirm the L19.3 passive plan checkpoint remains accepted.
2. Require the explicit downloaded-file validation authorization flag.
3. Require the exact downloaded-file validation authorization token.
4. In L19.5 or later only, validate path metadata without reading file bytes or opening archives.
5. Keep real file existence/stat/hash behind a later explicit gate.
6. Keep archive opening/listing/extraction, manifest reads, package-run, pasteback, and auto-send blocked.

## Expected compact JSON fields

The authorized readback should confirm:

- `ok:true`.
- `patch:"L19.4"`.
- `source_l19_3_passive_plan_checkpoint_accepted:true`.
- `downloaded_file_validation_authorized_for_future_phase:true`.
- `downloaded_file_validation_authorization_is_readback_only_in_l19_4:true`.
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

L19.5 Microsoft Edge first controlled downloaded-file metadata validation proof.
