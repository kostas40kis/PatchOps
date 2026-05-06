# U0.4A ChatGPT Uploader Report Parser Metadata Repair

## Purpose

U0.4A repairs the failed U0.4 bundle authoring shape and applies the intended U0.4 report parser.

The failed U0.4 bundle did not start launcher execution because `bundle_meta.json` used the older metadata key shape and omitted the currently required fields:

```text
bundle_schema_version
wrapper_project_root
```

U0.4A uses the accepted metadata shape proven by U0.2 and U0.3A.

## Scope

Allowed:

```text
apply local report parser module
apply focused parser tests
apply local smoke runner
apply parser documentation
repair bundle metadata shape
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
