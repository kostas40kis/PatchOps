# U3 C27 uploader status reporter armed gate

Patch `u3_c27_uploader_status_reporter_armed_gate` adds the local armed gate for the uploader status/report delivery policy.

## Purpose

The gate consumes:

```text
data/runtime/copilot_handoff/latest_uploader_status_report_policy.json
```

It writes:

```text
data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.json
data/runtime/copilot_handoff/latest_uploader_status_reporter_armed_gate.txt
```

## Rules

```text
selected_action: post_status_message -> require PATCHOPS_CONFIRM_UPLOADER_STATUS_POST_MESSAGE
selected_action: upload_operator_report -> require PATCHOPS_CONFIRM_UPLOADER_STATUS_UPLOAD_REPORT
selected_action: record_pass_locally_no_upload -> no live action confirmation needed
```

## Boundaries

This patch does not open Chrome or Edge.

This patch does not type, paste, upload, send, inspect the DOM, read raw conversation text, use Selenium/WebDriver, or attempt CAPTCHA/Cloudflare bypass.

The browser lanes execute later patches only after this local gate has produced evidence.

## Evidence fields

The JSON evidence includes:

```text
patch_name
patch_result
selected_action
browser_lane
status_chat_configured
status_chat_url_hash_or_redacted
operator_report_path
operator_report_sha256
pass_status_message
confirmation_text_supplied
browser_action_performed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
status_message_posted:false
send_button_pressed:false
raw_conversation_text_available:false
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
```

## Acceptance labels

```text
PASS_UPLOADER_STATUS_REPORTER_ARMED_GATE_VALIDATED
BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_REQUIRED
BLOCKED_UPLOADER_STATUS_REPORTER_CONFIRMATION_MISMATCH
BLOCKED_UPLOADER_STATUS_REPORTER_UNSUPPORTED_BROWSER_LANE
```

## CLI

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_reporter_armed_gate.py `
  --policy-path data/runtime/copilot_handoff/latest_uploader_status_report_policy.json `
  --confirm-uploader-status-text PATCHOPS_CONFIRM_UPLOADER_STATUS_POST_MESSAGE
```