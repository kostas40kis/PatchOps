# L21.7a Microsoft Edge downloaded-archive validation final acceptance marker repair

L21.7a is a narrow repair for the L21 final marker after the previous L21.7 bundle reached `apply` but failed as target content. The repair keeps the final-marker source checks less brittle and uses L21.6a as the accepted detailed broad checkpoint.

Command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair
```

Source command:

```text
browser-start-supervised-launch-edge-downloaded-archive-validation-broad-checkpoint-repair
```

## Boundary

- Microsoft Edge first.
- Opera second.
- L21.6a archive broad checkpoint repair remains accepted.
- L21 downloaded-archive validation stream complete.
- L21 completion means metadata-only listing of the synthetic archive fixture.
- metadata-only archive listing remains accepted.
- downloaded archive may be opened only for metadata listing of the synthetic fixture.
- downloaded archive contents may be listed as metadata only.
- downloaded archive is not extracted.
- downloaded manifest is not read.
- archive member bytes are not read.
- downloaded file bytes are not read.
- downloaded file stat is not performed.
- downloaded file hash is not performed.
- archive extraction remains a separate future stream.
- manifest read remains a separate future stream.
- archive member-byte read remains a separate future stream.
- package-run from browser remains a separate future stream.
- no Microsoft Edge start.
- no browser download.
- no prompt text extraction.
- no conversation reading.
- no pasteback.
- no send/submit.
- no package-run from browser.
- no localhost PatchOps server.
- no browser extension.
- no git commit or git push.

## Why this is L21.7a

The previous L21.7 repaired bundle passed package preflight, check, inspect, and plan, but `apply` returned exit code 1. L21.7a keeps the same safety contract and final status meaning, but avoids brittle exact-field assertions against the L21.6a source payload.

## CLI command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair --repo-root C:\dev\patchops --target-url https://chatgpt.com/ --json --compact
```

## Expected compact JSON fields

- `ok:true`.
- `patch:"L21.7a"`.
- `source_l21_6a_broad_checkpoint_repair_accepted:true`.
- `l21_downloaded_archive_validation_stream_complete:true`.
- `l21_completion_means_metadata_only_synthetic_archive_listing:true`.
- `metadata_only_archive_listing_remains_accepted:true`.
- `archive_validation_scope:"metadata_only_synthetic_patchops_runtime_archive_fixture"`.
- `downloaded_archive_opened:true`.
- `downloaded_archive_contents_listed:true`.
- `downloaded_archive_extracted:false`.
- `downloaded_manifest_read:false`.
- `archive_member_bytes_read:false`.
- `downloaded_file_bytes_read:false`.
- `browser_started:false`.
- `edge_process_started:false`.
- `package_run_performed_by_adapter:false`.

## Next patch

L22.1 Microsoft Edge downloaded-archive manifest validation passive preflight gate.
