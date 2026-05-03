# L19.3 Microsoft Edge downloaded-file validation passive plan checkpoint

L19.3 defines the safe future downloaded-file validation plan after the accepted L19.2 CLI/readback checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-passive-plan-checkpoint
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-file-validation-cli-readback-checkpoint
```

## Boundary

- Microsoft Edge first.
- Opera second.
- Opera is not the active implementation target in L19.3.
- downloaded-file validation passive plan checkpoint.
- passive plan checkpoint.
- L19.2 CLI/readback checkpoint remains accepted.
- safe future downloaded-file validation plan.
- downloaded-file validation candidate means metadata-only path evidence for a future downloaded PatchOps zip artifact.
- validation plan does not check whether a file exists.
- validation plan does not stat a file.
- validation plan does not hash a file.
- validation plan does not read downloaded file bytes.
- validation plan does not open a downloaded archive.
- validation plan does not list downloaded archive contents.
- validation plan does not extract a downloaded archive.
- validation plan does not read a downloaded manifest.
- validation plan does not run a package.
- downloaded-file validation execution allowed: false.
- downloaded-file validation active: false.
- downloaded-file validation is not performed.
- downloaded file bytes are not read.
- downloaded archive is not opened.
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

## Downloaded-file validation candidate definition

In L19.3, a downloaded-file validation candidate means metadata-only path evidence for a future downloaded PatchOps zip artifact.

A candidate does not mean:

- checking whether a file exists.
- stating a file.
- hashing a file.
- reading downloaded file bytes.
- opening a downloaded archive.
- listing downloaded archive contents.
- extracting a downloaded archive.
- reading a downloaded manifest.
- running a package.
- pasting into a browser.
- sending or submitting a message.

Future candidate path rules remain:

- extension must be `.zip`.
- recommended pattern is `patch_*_patchops_bundle.zip`.
- path must be metadata-only in L19.3.
- reject non-zip candidates.
- reject ambiguous multiple candidates.

## Future passive plan

The safe future downloaded-file validation plan is planned but not executed in L19.3:

1. Confirm the L19.2 CLI/readback checkpoint is accepted.
2. Require an L19.4-or-later explicit downloaded-file validation authorization token.
3. Accept future downloaded-file path metadata only.
4. In a later phase, check file existence without reading bytes.
5. In a later phase, stat/hash after operator review.
6. Gate archive opening/listing/extraction and manifest read separately.
7. Keep package-run, pasteback, and auto-send blocked.

Downloaded-file validation remains inactive in L19.3.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-file-validation-passive-plan-checkpoint --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

The readback should confirm:

- `ok:true`.
- `patch:"L19.3"`.
- `source_l19_2_cli_readback_checkpoint_accepted:true`.
- `downloaded_file_validation_candidate_definition_blocks_file_read_archive_package_run:true`.
- `future_downloaded_file_validation_plan_is_planned_not_executed:true`.
- `future_downloaded_file_validation_plan_blocks_file_checks_file_read_archive_package_run:true`.
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

L19.4 Microsoft Edge downloaded-file validation controlled authorization gate.
