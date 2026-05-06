# U1.1A — ChatGPT uploader chunked content pasteback

U1.1A repairs the U1.1 bundle-shape failure and adds the local chunked content pasteback builder.

It accepts a local PatchOps report and writes numbered chunk files using markers:

```text
PATCHOPS_REPORT_CHUNK 1/N
...
END_PATCHOPS_REPORT_CHUNK 1/N
```

Safety behavior:

```text
safe report within max_total_chars -> chunked report payload files
secret-looking report -> compact summary only
oversized report -> compact summary only
missing report -> blocked
empty report -> blocked
```

U1.1A is local-only. It does not touch browser, clipboard, paste, upload, send, Selenium/WebDriver, DOM automation, CAPTCHA/Cloudflare bypass, or conversation text.

The previous U1.1 builder produced a zip shape that PatchOps reviewed as `content` rather than the bundle root. This repair ships the standard root bundle shape:

```text
README.txt
bundle_meta.json
manifest.json
run_with_patchops.ps1
content/...
```
