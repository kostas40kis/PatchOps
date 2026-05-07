# Chrome acceptance handoff

This document describes the downstream handoff produced after the Chrome-only uploader has passed repeatability acceptance.

The handoff is intentionally Chrome-only and no-send. It must not introduce a generic browser abstraction, a browser registry, Selenium, WebDriver, DOM automation, Cloudflare/CAPTCHA bypass, random clicking, or conversation-text logging.

Default handoff path:

```text
data/runtime/copilot_handoff/latest_uploader_acceptance.json
```

Required handoff fields include:

```text
handoff_kind: chrome_uploader_acceptance_no_send
expected_browser: chrome
acceptance_result: PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
no_send_verified: true
attachment_verified: true
chatgpt_submit_performed: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
conversation_text_logged: false
raw_conversation_text_logged: false
```

The handoff records source acceptance basename and SHA-256 only. It does not expose raw conversation text or require direct browser access.