# U1.2 — ChatGPT uploader assisted file-upload helper

U1.2 adds a local assisted file-upload helper for PatchOps Co-Pilot.

This is **not** an automatic uploader. It prepares a local packet that an operator can review and manually upload through the normal ChatGPT UI if needed.

The helper can:

```text
validate local file paths
reject missing/empty/oversized files
reject secret-looking files by default
copy safe files into a packet folder
write assisted_upload_manifest.json
write ASSISTED_UPLOAD_INSTRUCTIONS.txt
record hashes and sizes
```

Safety boundary:

```text
no browser control
no upload click
no file dialog automation
no clipboard write
no paste
no send/submit
no Selenium/WebDriver
no DOM automation
no CAPTCHA/Cloudflare bypass
no conversation text logging
```

This patch intentionally remains manual/assisted because the primary uploader path is text pasteback through the already gated Edge composer flow.

Later optional probes may test file-input upload behavior, but only under explicit gates and never as an unbounded upload/send loop.
