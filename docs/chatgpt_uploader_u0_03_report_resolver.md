# U0.3 ChatGPT Uploader Report Resolver

Patch `u0_03_chatgpt_uploader_report_resolver` adds the next conservative uploader layer after U0.2.

## Purpose

U0.3 resolves one local PatchOps report file so later uploader patches can parse it and build pasteback summaries.

The resolver can:

- resolve an explicit report path;
- choose the newest matching `.txt` report from a directory;
- record byte-exact size and SHA256;
- write JSON/TXT resolver evidence;
- return BLOCKED instead of crashing for missing or invalid paths.

## Boundary

This patch does not parse the report result. U0.4 owns report parsing.

This patch does not build `PATCHOPS_LLM_PASTEBACK`. U0.5 owns pasteback summary creation.

This patch does not open a browser, upload a file, paste text, send a message, use Selenium, use WebDriver, or attempt any CAPTCHA/Cloudflare bypass.

## Runnable smoke surface

```powershell
py -m patchops.chatgpt_uploader.report_resolver `
  --report-path "C:\Users\kostas\Desktop\some_patchops_report.txt" `
  --output-dir "data/runtime/u0_03_chatgpt_uploader_report_resolver" `
  --json
```

Directory mode:

```powershell
py -m patchops.chatgpt_uploader.report_resolver `
  --report-dir "C:\Users\kostas\Desktop" `
  --prefix "u0_" `
  --output-dir "data/runtime/u0_03_chatgpt_uploader_report_resolver" `
  --json
```

## Safety expectations

```text
webdriver_used:false
selenium_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
file_upload_attempted:false
chatgpt_submit_performed:false
conversation_text_logged:false
random_page_click_performed:false
```
