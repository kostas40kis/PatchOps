# U3 C31 Chrome fail report upload no-send

Patch `u3_c31_chrome_fail_report_upload_no_send` adds the Chrome lane FAIL/BLOCKED report-upload no-send rehearsal.

## Purpose

For failed or blocked patches, the uploader must upload the operator report instead of posting the PASS message.

This patch prepares the Chrome upload path and stops before Send.

## Required live command

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_fail_report_upload_no_send.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_UPLOAD_NO_SEND `
  --stop-before-send `
  --provider pywinauto `
  --operator-report-path C:\path\to\operator_report.txt
```

When C27 has already written the armed gate, the script can read:

```text
data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json
```

## Required gates

```text
selected_action must be upload_operator_report
browser_lane must be chrome
operator_report_path must exist
operator_report_sha256 must match if supplied
live-browser gate must pass
confirmation must exactly equal PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_UPLOAD_NO_SEND
--stop-before-send must be supplied
```

## Acceptance labels

```text
PASS_CHROME_FAIL_REPORT_ATTACHMENT_READY_NO_SEND
BLOCKED_CHROME_REPORT_TARGET_NOT_READY
BLOCKED_CHROME_REPORT_UPLOAD_CONFIRMATION_REQUIRED
BLOCKED_CHROME_REPORT_UPLOAD_CONFIRMATION_MISMATCH
BLOCKED_OPERATOR_REPORT_MISSING
BLOCKED_OPERATOR_REPORT_HASH_MISMATCH
BLOCKED_CHROME_REPORT_UPLOAD_NOT_VERIFIED
BLOCKED_CHROME_REPORT_UPLOAD_MESSAGE_MISMATCH
BLOCKED_SEND_RISK
```

## Safety boundary

This patch may focus the visible Chrome ChatGPT target and attach the operator report under explicit live flags.

It must not press Send, submit ChatGPT input, post a status message, inspect the DOM, use Selenium/WebDriver, attempt CAPTCHA/Cloudflare bypass, log raw conversation text, random-click, or run an unbounded loop.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_fail_report_upload_no_send.json
data/runtime/copilot_handoff/latest_chrome_fail_report_upload_no_send.txt
```

Successful no-send upload evidence records:

```text
operator_report_uploaded:true
chatgpt_submit_performed:false
status_message_posted:false
send_button_pressed:false
raw_conversation_text_available:false
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
```

Target titles are stored as hash/length only.