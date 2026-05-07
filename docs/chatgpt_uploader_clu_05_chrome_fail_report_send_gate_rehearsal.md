# CLU-05 Chrome fail-report send gate rehearsal

Patch `clu_05_chrome_fail_report_send_gate_rehearsal` adds the planned send-gate rehearsal after CLU-04 consistency has passed.

## Purpose

CLU-05 verifies that the final report-send step is gated and ready, without performing any browser action.

This patch is intentionally local-only:

```text
no Chrome focus
no file picker
no upload
no ChatGPT submit
no Send
no DOM automation
no Selenium/WebDriver
```

## What it validates

```text
CLU-04 consistency evidence exists
CLU-04 result_label == PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT
selected_action == upload_operator_report
browser_lane == chrome
runs_completed >= 3
runs_passed >= 3
consecutive_passes >= 3
attachment_verified_all_runs == true
file_upload_attempted_all_runs == true
file_picker_used_all_runs == true
file_path_written_all_runs == true
operator_report_uploaded_any_run == false
chatgpt_submit_performed_any_run == false
status_message_posted_any_run == false
send_button_pressed_any_run == false
operator report hash is carried forward
operator report file still matches the carried-forward hash
real send confirmation is reserved for the optional CLU-06 patch
```

## Focused test command

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_chatgpt_uploader_chrome_fail_report_send_gate_rehearsal_current.py
```

## Operator command

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_fail_report_send_gate_rehearsal.py `
  --confirm-send-gate-rehearsal-text PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_SEND_GATE_REHEARSAL
```

Optional explicit hash carry-forward:

```powershell
  --operator-report-path C:\path\to\operator_report.txt `
  --operator-report-sha256 <sha256>
```

## Acceptance labels

```text
PASS_CHROME_FAIL_REPORT_SEND_GATE_READY
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_REQUIRED
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_CONFIRMATION_MISMATCH
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_MISSING
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_EVIDENCE_INVALID
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_HASH_MISMATCH
BLOCKED_CHROME_FAIL_REPORT_SEND_GATE_ATTACHMENT_MISSING
BLOCKED_SEND_RISK
```

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_fail_report_send_gate_ready.json
data/runtime/copilot_handoff/latest_chrome_fail_report_send_gate_ready.txt
```

## Success evidence

```text
result_label: PASS_CHROME_FAIL_REPORT_SEND_GATE_READY
gate_ready: true
selected_action: upload_operator_report
browser_lane: chrome
attachment_verified_from_prior_evidence: true
operator_report_hash_carried_forward: true
operator_report_hash_verified_on_disk: true
real_send_confirmation_required_for_next_patch: PATCHOPS_CONFIRM_CHROME_FAIL_REPORT_SEND
real_send_confirmation_accepted_by_this_patch: false
browser_action_performed: false
file_upload_attempted: false
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

CLU-05 only reads CLU-04 evidence and verifies the carried report hash. It does not open, focus, click, type, paste, upload, or send.

Supplying the real send confirmation to CLU-05 is treated as `BLOCKED_SEND_RISK`. The real send confirmation is reserved for the optional CLU-06 send test.