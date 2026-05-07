# U3 C30 Chrome status message send test

Patch `u3_c30_chrome_status_message_send_test` adds the Chrome PASS status send path.

## Repair note

Repair `u3_c30_chrome_status_message_send_test_repair_01` fixes gate priority so a missing `--live-browser` flag returns `BLOCKED_SEND_RISK` before message-shape checks. This keeps live safety gates dominant and prevents a non-live run from being misclassified as `BLOCKED_STATUS_MESSAGE_MISMATCH`.

## Purpose

C30 sends the exact PASS status message only after the local no-send probe succeeds:

```text
<patch_name> has passed
```

## Required live command

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_status_message_send_test.py `
  --live-browser `
  --confirm-no-send-text PATCHOPS_CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND `
  --confirm-send-text PATCHOPS_CONFIRM_CHROME_STATUS_MESSAGE_SEND `
  --provider pywinauto
```

## Required gates

```text
live-browser gate must pass first
no-send rehearsal must pass before send
send confirmation must exactly equal PATCHOPS_CONFIRM_CHROME_STATUS_MESSAGE_SEND
selected_action must be post_status_message
browser_lane must be chrome
pass_status_message must exactly equal <patch_name> has passed
```

## Acceptance labels

```text
PASS_CHROME_STATUS_MESSAGE_SENT
BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_REQUIRED
BLOCKED_CHROME_STATUS_SEND_CONFIRMATION_MISMATCH
BLOCKED_CHROME_STATUS_SEND_NOT_VERIFIED
BLOCKED_CHROME_STATUS_TARGET_NOT_READY
BLOCKED_STATUS_MESSAGE_MISMATCH
BLOCKED_SEND_RISK
```

## Safety boundary

This patch may perform a real ChatGPT submit only when the operator supplies both live confirmations and the no-send rehearsal passes.

It must not upload an operator report, inspect DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_status_message_send_test.json
data/runtime/copilot_handoff/latest_chrome_status_message_send_test.txt
```

Successful send evidence records:

```text
chatgpt_submit_performed:true
status_message_posted:true
operator_report_uploaded:false
raw_conversation_text_available:false
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
```

Target titles are stored as hash/length only.