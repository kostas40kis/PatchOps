# ChatGPT uploader Chrome live acceptance marker

This marker records the Chrome-only uploader acceptance boundary for PatchOps.

The acceptance gate is intentionally Chrome-specific. It does not introduce an all-browser abstraction, a browser registry, a generic adapter, Selenium, WebDriver, DOM automation, hidden browser automation, or random clicking.

## Required acceptance evidence

A passing acceptance run must show:

```text
PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
chrome_executable_found:true
chrome_target_ready:true
canonical_report_found:true
picker_opened:true
exact_path_written:true
file_upload_attempted:true
attachment_verified:true
repeatability_attempts:5
repeatability_passes_at_least:4
chatgpt_submit_performed:false
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
conversation_text_logged:false
raw_conversation_text_logged:false
random_page_click_performed:false
```

## Evidence source

The gate consumes operator-safe Chrome evidence bundle JSON files created from prior upload-flow evidence. It records basenames and hashes only. It must not read ChatGPT conversation text.

## No-send boundary

This acceptance marker is for the no-send Chrome uploader path. Any evidence with `chatgpt_submit_performed:true` or `submit_action_performed:true` is blocked by the acceptance gate.