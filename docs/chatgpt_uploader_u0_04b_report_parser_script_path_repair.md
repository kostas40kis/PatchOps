# U0.4B ChatGPT Uploader Report Parser Script Path Repair

## Purpose

U0.4B repairs U0.4A after the bundle applied source content but failed validation.

The failing layer was target content: the smoke runner was executed as a script path from the repository root, but it did not bootstrap the repository root onto `sys.path` before importing `patchops.chatgpt_uploader.report_parser`.

This mirrors the earlier accepted U0.3A smoke runner shape, which explicitly inserted the repo root into `sys.path` before importing PatchOps modules.

## Scope

Allowed:

```text
repair script-path import bootstrap
keep report parser implementation
keep focused parser tests
add regression proving the script runs by path from repo root
run parser smoke command
```

Forbidden:

```text
upload
send
browser start
Selenium/WebDriver
DOM automation
CAPTCHA or Cloudflare bypass
PATCHOPS_LLM_PASTEBACK generation
```

## Safety

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
