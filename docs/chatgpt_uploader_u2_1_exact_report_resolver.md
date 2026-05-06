# ChatGPT Uploader U2.1 Exact Report Resolver

U2.1 adds the report resolver layer for the ChatGPT uploader.

## Goal

Before any upload attempt, the uploader must know the exact PatchOps report file to deliver.

The resolver records:

```text
selected report path
selected report filename
selected report size
selected report SHA256
modified timestamp
resolution mode
stable-file observation count
```

## Resolution policy

1. Explicit `--report-path` wins.
2. Missing, empty, directory, temporary, or unstable report files are rejected.
3. Latest Desktop fallback exists only when `--latest-desktop-recovery` is explicitly requested.
4. Resolving a report never uploads it and never sends a ChatGPT message.

## Live proof

U2.1 resolves the exact PatchOps apply report from the current patch run and then focuses the configured Edge target.

No upload, no picker, no send, no Selenium/WebDriver, no DOM automation, no URL launch.
