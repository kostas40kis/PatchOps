# PatchOps Co-Pilot Downloader Direction

Patch `d0_01_copilot_downloader_foundation` creates the first downloader-owned package surface.

This patch is intentionally local-only. It creates the package skeleton, result labels, safety flags, evidence helpers, a foundation doctor command, and focused tests.

## Boundary

Allowed in this patch:

- write downloader package files under `patchops/copilot_downloader/`
- write downloader documentation under `docs/`
- write focused downloader tests under `tests/`
- run local PatchOps `check`, `inspect`, `plan`, and `apply`
- run local pytest and the downloader foundation doctor

Forbidden in this patch:

- browser use
- Selenium or WebDriver
- browser DOM automation
- clipboard read/write
- browser download observation
- artifact intake or artifact execution
- ChatGPT submit or file upload
- uploader imports or downloader-to-uploader calls
- git commit or git push

## Design intent

Downloader creates truth through local staged artifacts, hashes, validation evidence, PatchOps evidence, canonical reports, and later handoff JSON. Browser surfaces are intake surfaces only and never become final truth.

D0.1 does not detect or run artifacts yet. That begins in later D0 patches after config, detector, stable-size, hash/ledger, classifier, validator, and staging surfaces exist.