# L19.6 Microsoft Edge downloaded-file validation broad checkpoint

L19.6 is the broad passive checkpoint for the Microsoft Edge downloaded-file validation stream.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-broad-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-metadata-validation-proof
```

Metadata proof token used by the source readback:

```text
PATCHOPS_L19_EDGE_DOWNLOADED_FILE_METADATA_VALIDATION_PROOF_AUTHORIZED
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L19.6.
- downloaded-file validation broad checkpoint.
- broad passive checkpoint.
- L19.1 through L19.5 remain accepted.
- metadata-only downloaded-file validation proof remains accepted.
- default metadata proof readback remains passive.
- authorized positive metadata proof readback remains passive.
- negative metadata fixture remains rejected without side effects.
- forbidden metadata keys remain rejected without side effects.
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

## Scope

This checkpoint consolidates the completed downloaded-file validation stream so far:

1. L19.1 passive downloaded-file validation preflight gate.
2. L19.2 downloaded-file validation CLI/readback checkpoint.
3. L19.3 passive downloaded-file validation plan checkpoint.
4. L19.4 controlled downloaded-file validation authorization gate.
5. L19.5 first controlled downloaded-file metadata validation proof.

L19.6 may validate the L19.5 default readback, authorized positive metadata readback, negative metadata fixture, and forbidden metadata rejection. These validations are metadata-only and do not touch the filesystem or archive content.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-broad-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L19.6"`.
- `l19_1_through_l19_5_remain_accepted:true`.
- `metadata_only_downloaded_file_validation_proof_remains_accepted:true`.
- `default_metadata_proof_readback_remains_passive:true`.
- `authorized_positive_metadata_proof_readback_remains_passive:true`.
- `negative_metadata_fixture_remains_rejected_without_side_effects:true`.
- `forbidden_metadata_keys_remain_rejected_without_side_effects:true`.
- `downloaded_file_metadata_validation_ready_from_positive_metadata:true`.
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

L19.7 Microsoft Edge downloaded-file validation final acceptance marker.
