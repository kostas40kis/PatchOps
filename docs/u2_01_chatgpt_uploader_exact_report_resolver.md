# U2.1 ChatGPT uploader exact report resolver

This patch adds the exact report resolver for the ChatGPT uploader stream.

## Added

- `patchops/chatgpt_uploader/report_resolver.py`
- `scripts/run_uploader_resolve_report.py`
- `tests/test_chatgpt_uploader_u2_01_exact_report_resolver_current.py`

## Selection order

The resolver uses this order:

1. explicit `--report-path`
2. `Report Path : ...` parsed from supplied output text
3. latest report fallback only when `--recovery-latest` is explicitly enabled

## Rejections

The resolver rejects reports that are:

- missing
- not files
- empty
- too recent to be stable
- too large when a max size is configured

## Safety boundary

This patch does not upload a file and does not send a ChatGPT message.

The live proof resolves a real PatchOps Desktop report, records SHA256/size/path, then verifies the configured normal Microsoft Edge target with the existing U2.0 preflight.

Next patch: U2.2 Windows file-picker detector and stale modal cleanup.