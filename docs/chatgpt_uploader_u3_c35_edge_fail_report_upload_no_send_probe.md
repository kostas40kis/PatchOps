# U3 C35 Edge fail report upload no-send probe

Patch `u3_c35_edge_fail_report_upload_no_send_probe` adds the Microsoft Edge lane FAIL/BLOCKED operator-report attachment rehearsal.

## Purpose

For failed or blocked patches, the uploader must attach the operator report instead of posting a PASS status message. C35 validates the explicit Edge lane upload path and stops before Send.

## Required live command

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_edge_fail_report_upload_no_send_probe.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_EDGE_FAIL_REPORT_UPLOAD_NO_SEND `
  --stop-before-send `
  --provider pywinauto `
  --operator-report-path C:\path\to\operator_report.txt
```

When the armed gate already contains the report route, the script can read:

```text
data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json
```

## Required gates

```text
selected_action must be upload_operator_report
browser_lane must be edge
operator_report_path must exist
operator_report_sha256 must match if supplied
--live-browser must be supplied
confirmation must exactly equal PATCHOPS_CONFIRM_EDGE_FAIL_REPORT_UPLOAD_NO_SEND
--stop-before-send must be supplied
```

## Acceptance labels

```text
PASS_EDGE_FAIL_REPORT_ATTACHED_NO_SEND
BLOCKED_OPERATOR_REPORT_MISSING
BLOCKED_OPERATOR_REPORT_HASH_MISMATCH
BLOCKED_EDGE_TARGET_NOT_READY
BLOCKED_ATTACHMENT_NOT_VERIFIED
BLOCKED_EDGE_UPLOAD_CONFIRMATION_REQUIRED
BLOCKED_EDGE_UPLOAD_CONFIRMATION_MISMATCH
BLOCKED_EDGE_UPLOAD_ROUTE_MISMATCH
BLOCKED_SEND_RISK
```

## Safety boundary

This patch may focus the visible Microsoft Edge ChatGPT target and attach the operator report under explicit live flags.

It must not press Send, submit ChatGPT input, post a status message, inspect the DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_edge_fail_report_upload_no_send_probe.json
data/runtime/copilot_handoff/latest_edge_fail_report_upload_no_send_probe.txt
```

Successful no-send attachment evidence records:

```text
attachment_verified:true
file_upload_attempted:true
operator_report_uploaded:false
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