# U3 C34 Edge status message send test

Patch `u3_c34_edge_status_message_send_test` adds the first real Microsoft Edge PASS status-message send test.

## Purpose

When a patch passes and the Edge status target is configured, the uploader should post exactly:

```text
<patch_name> has passed
```

For this patch, the exact live message is:

```text
u3_c34_edge_status_message_send_test has passed
```

## Required live command

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_edge_status_message_send_test.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_EDGE_STATUS_MESSAGE_SEND `
  --confirm-exact-message "u3_c34_edge_status_message_send_test has passed" `
  --provider pywinauto
```

## Required gates

```text
--live-browser must be supplied
confirmation must exactly equal PATCHOPS_CONFIRM_EDGE_STATUS_MESSAGE_SEND
--confirm-exact-message must exactly equal u3_c34_edge_status_message_send_test has passed
selected_action must be post_status_message
browser_lane must be edge
pass_status_message must exactly equal <patch_name> has passed
```

## Acceptance labels

```text
PASS_EDGE_STATUS_MESSAGE_SENT
BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISSING
BLOCKED_EDGE_EXACT_MESSAGE_CONFIRMATION_MISMATCH
BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_REQUIRED
BLOCKED_EDGE_STATUS_SEND_CONFIRMATION_MISMATCH
BLOCKED_EDGE_STATUS_TARGET_NOT_READY
BLOCKED_EDGE_STATUS_MESSAGE_MISMATCH
BLOCKED_EDGE_SEND_RISK
FAIL_EDGE_STATUS_MESSAGE_SEND_NOT_PROVEN
```

## Safety boundary

This patch may send exactly one Edge ChatGPT PASS status message only under the explicit live gate and exact-message confirmation.

It must not upload a report on PASS, inspect the DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_edge_status_message_send_test.json
data/runtime/copilot_handoff/latest_edge_status_message_send_test.txt
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