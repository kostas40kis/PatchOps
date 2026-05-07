# CLU-03 Chrome operator report attach no-send probe

Patch `clu_03_chrome_operator_report_attach_no_send_probe` adds the first Chrome live upload probe that selects an operator report file and verifies attachment evidence while stopping before Send.

## Purpose

This patch proves Chrome can attach the exact operator report for a FAIL/BLOCKED route without submitting the chat message.

It checks:

```text
status_chat.enabled == true
browser_lane == chrome
target URL/hash valid
selected_action == upload_operator_report
operator_report_path exists
operator_report_sha256 matches if supplied
single visible Chrome ChatGPT/PatchOps target window
single attachment control candidate
file picker opens
operator report path is written
attachment readiness is detected
attachment is verified
no ChatGPT submit
no Send
```

## Focused test command

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_chatgpt_uploader_chrome_operator_report_attach_no_send_current.py
```

## Live command

Open the configured target link in Chrome first, then run:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_operator_report_attach_no_send_probe.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_NO_SEND `
  --stop-before-send `
  --provider pywinauto `
  --operator-report-path C:\path\to\operator_report.txt
```

Optional hash gate:

```powershell
  --operator-report-sha256 <sha256>
```

## Acceptance labels

```text
PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND
BLOCKED_OPERATOR_REPORT_MISSING
BLOCKED_OPERATOR_REPORT_HASH_MISMATCH
BLOCKED_CHROME_ATTACH_CONFIG_MISSING
BLOCKED_CHROME_ATTACH_BROWSER_MISMATCH
BLOCKED_CHROME_ATTACH_URL_INVALID
BLOCKED_CHROME_ATTACH_CONFIRMATION_REQUIRED
BLOCKED_CHROME_ATTACH_CONFIRMATION_MISMATCH
BLOCKED_CHROME_TARGET_NOT_READY
BLOCKED_CHROME_AMBIGUOUS_TARGET
BLOCKED_CHROME_ATTACHMENT_CONTROL_NOT_FOUND
BLOCKED_CHROME_FILE_PICKER_NOT_READY
BLOCKED_ATTACHMENT_NOT_VERIFIED
BLOCKED_SEND_RISK
```

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_operator_report_attached_no_send.json
data/runtime/copilot_handoff/latest_chrome_operator_report_attached_no_send.txt
```

## Success evidence

```text
result_label: PASS_CHROME_OPERATOR_REPORT_ATTACHED_NO_SEND
selected_action: upload_operator_report
browser_lane: chrome
file_upload_attempted: true
file_picker_used: true
file_path_written: true
attachment_ready: true
attachment_verified: true
operator_report_uploaded: false
chatgpt_submit_performed: false
status_message_posted: false
send_button_pressed: false
raw_conversation_text_available: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
```

## Safety boundary

CLU-03 may focus Chrome, click the single verified attachment control, use the native file picker, write the operator report path to the picker, and verify a file attachment indicator through UIA.

It must not press Send, submit ChatGPT input, post a status message, inspect DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.