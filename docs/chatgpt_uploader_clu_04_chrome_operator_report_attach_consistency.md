# CLU-04 Chrome operator report attach consistency runner

Patch `clu_04_chrome_operator_report_attach_consistency_runner` adds the Chrome attach consistency runner.

## Purpose

CLU-04 repeatedly runs the CLU-03 attach no-send behavior and only passes when the required number of consecutive runs all verify a Chrome operator report attachment without Send/submission evidence.

Default consistency bar:

```text
3 requested runs
3 completed runs
3 passed runs
3 consecutive passes
attachment_verified_all_runs:true
file_upload_attempted_all_runs:true
file_picker_used_all_runs:true
file_path_written_all_runs:true
operator_report_uploaded_any_run:false
chatgpt_submit_performed_any_run:false
status_message_posted_any_run:false
send_button_pressed_any_run:false
raw_conversation_text_available_any_run:false
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
```

## Focused test command

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_chatgpt_uploader_chrome_operator_report_attach_consistency_current.py
```

## Live command

Open the configured target link in Chrome first, then run:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_operator_report_attach_consistency.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENCY `
  --stop-before-send `
  --provider pywinauto `
  --operator-report-path C:\path\to\operator_report.txt `
  --runs 3
```

Optional base hash gate:

```powershell
  --operator-report-sha256 <sha256>
```

By default, the runner creates fresh per-run file copies under:

```text
data/runtime/copilot_handoff/chrome_attach_consistency_workdir
```

This avoids duplicate-file-name ambiguity during repeated attachment probes.

## Evidence outputs

Final summary:

```text
data/runtime/copilot_handoff/latest_chrome_operator_report_attach_consistency.json
data/runtime/copilot_handoff/latest_chrome_operator_report_attach_consistency.txt
```

Per-run child evidence:

```text
data/runtime/copilot_handoff/chrome_attach_consistency_runs/clu04_attach_run_01.json
data/runtime/copilot_handoff/chrome_attach_consistency_runs/clu04_attach_run_02.json
data/runtime/copilot_handoff/chrome_attach_consistency_runs/clu04_attach_run_03.json
```

Matching `.txt` files are also written.

## Acceptance labels

```text
PASS_CHROME_OPERATOR_REPORT_ATTACH_CONSISTENT
BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_REQUIRED
BLOCKED_CHROME_ATTACH_CONSISTENCY_CONFIRMATION_MISMATCH
BLOCKED_CHROME_ATTACH_CONSISTENCY_LIVE_BROWSER_REQUIRED
BLOCKED_CHROME_ATTACH_CONSISTENCY_STOP_BEFORE_SEND_REQUIRED
BLOCKED_CHROME_ATTACH_CONSISTENCY_INSUFFICIENT_RUNS
BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_MISSING
BLOCKED_CHROME_ATTACH_CONSISTENCY_OPERATOR_REPORT_HASH_MISMATCH
BLOCKED_CHROME_ATTACH_CONSISTENCY_FLAKY
BLOCKED_CHROME_ATTACH_CONSISTENCY_SEND_RISK
BLOCKED_CHROME_ATTACH_CONSISTENCY_EVIDENCE_MISSING
```

## Safety boundary

CLU-04 may repeat the CLU-03 no-send attach probe. It may focus Chrome, open the native file picker, write report paths, and verify attachment indicators.

It must not press Send, submit ChatGPT input, post a status message, use DOM automation, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run unbounded loops.

The run count is bounded:

```text
minimum: 3
maximum: 10
```