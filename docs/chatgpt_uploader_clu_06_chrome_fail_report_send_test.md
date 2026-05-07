# CLU-06 Chrome fail-report send test

Patch `clu_06_chrome_fail_report_send_test` adds the optional real Chrome fail-report upload/send test.

## Purpose

CLU-06 is the first planned patch in this mini-process that may actually submit the attached operator report in Chrome.

It is intentionally gated and refuses to run unless CLU-05 produced a passing send-gate evidence file.

## Required preconditions

```text
CLU-05 evidence exists
CLU-05 result_label == PASS_CHROME_FAIL_REPORT_SEND_GATE_READY
CLU-05 gate_ready == true
selected_action == upload_operator_report
browser_lane == chrome
operator report path/hash carried forward
operator report file still matches hash
```

## Focused test command

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_chatgpt_uploader_chrome_fail_report_send_test_current.py
```

## Live command

Open the configured target in Chrome first, then run:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_fail_report_send_test.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_SEND `
  --provider pywinauto
```

Optional explicit report path/hash override:

```powershell
  --operator-report-path C:\path\to\operator_report.txt `
  --operator-report-sha256 <sha256>
```

## Acceptance labels

```text
PASS_CHROME_FAIL_REPORT_SENT
BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_REQUIRED
BLOCKED_CHROME_FAIL_REPORT_SEND_CONFIRMATION_MISMATCH
BLOCKED_CHROME_FAIL_REPORT_SEND_LIVE_BROWSER_REQUIRED
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_MISSING
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_INVALID
BLOCKED_CHROME_FAIL_REPORT_SEND_HASH_MISMATCH
BLOCKED_CHROME_FAIL_REPORT_SEND_ATTACH_FAILED
BLOCKED_CHROME_FAIL_REPORT_SEND_BUTTON_NOT_READY
FAIL_CHROME_FAIL_REPORT_SEND_NOT_PROVEN
BLOCKED_SEND_RISK
```

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_fail_report_sent.json
data/runtime/copilot_handoff/latest_chrome_fail_report_sent.txt
```

## Success evidence

```text
result_label: PASS_CHROME_FAIL_REPORT_SENT
selected_action: upload_operator_report
browser_lane: chrome
send_gate_ready: true
operator_report_hash_verified_on_disk: true
attachment_verified: true
file_upload_attempted: true
file_picker_used: true
file_path_written: true
send_button_ready: true
send_button_pressed: true
chatgpt_submit_performed: true
operator_report_uploaded: true
status_message_posted: false
raw_conversation_text_available: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
cloudflare_bypass_attempted: false
captcha_bypass_attempted: false
```

## Safety boundary

CLU-06 may focus Chrome, attach the operator report through the native file picker, and press the single enabled Send control only after the explicit live confirmation is supplied.

It must not use DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation text logging, random clicks, or unbounded loops.

This patch does not hide or bypass any UI. It performs only operator-confirmed UI actions in the visible Chrome session.