# D0.1 — Co-Pilot downloader artifact detector

D0.1 starts the downloader side of PatchOps Co-Pilot.

The active Co-Pilot process has two components:

```text
Downloader -> detects scripts/bundles, validates them, runs PatchOps, creates report
Uploader   -> delivers report evidence to the configured target
```

Uploader work came first. D0.1 begins the downloader with **local artifact detection only**.

## What D0.1 does

```text
scan configured local folders/files
detect candidate .zip/.ps1/.txt/.md artifacts
classify patchops zip bundles and scripts
check non-empty/stable-by-age status
write JSON/TXT detection evidence
select the newest stable candidate
```

## What D0.1 does not do

```text
does not execute artifacts
does not run PatchOps
does not invoke browser
does not write clipboard
does not upload files
does not send/submit to ChatGPT
does not use Selenium/WebDriver
does not automate DOM
does not bypass CAPTCHA/Cloudflare
```

Later downloader patches can add validation and PatchOps invocation. D0.1 only proves the safe intake/detection layer.
