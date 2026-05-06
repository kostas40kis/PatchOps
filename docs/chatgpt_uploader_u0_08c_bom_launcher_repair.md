# U0.8C — composer dry-run BOM and launcher repair

U0.8B direct-manifest execution failed before PatchOps check because the generated manifest was written with a UTF-8 BOM:

```text
Manifest is not valid JSON: Unexpected UTF-8 BOM
```

U0.8C delivers the same U0.8 composer dry-run target content as a clean PatchOps zip bundle with:

```text
UTF-8 without BOM manifest JSON
accepted bundle_meta.json fields
safe run_with_patchops.ps1 root resolution using $PSScriptRoot / $PSCommandPath fallback
```

Boundary remains:

```text
no upload
no send/submit
no Selenium/WebDriver
no DOM automation
no CAPTCHA/Cloudflare bypass
real Edge gated
actual paste gated
```
