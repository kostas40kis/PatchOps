# U3 C32 core router matrix

Patch `u3_c32_core_router_matrix` adds the core uploader routing matrix that produces:

```text
data/runtime/copilot_handoff/latest_uploader_status_report_policy.json
data/runtime/copilot_handoff/latest_uploader_status_report_policy.txt
```

## Matrix

```text
PASS + status chat configured -> post_status_message
PASS + no status chat configured -> record_pass_locally_no_upload
FAIL/BLOCKED -> upload_operator_report
```

## PASS status message

```text
<patch_name> has passed
```

## Browser lanes

Allowed explicit lanes:

```text
chrome
edge
```

Rejected/generic lanes stay blocked:

```text
any
auto
all
default
firefox
brave
opera
vivaldi
chromium
safari
```

## Required output fields

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
required_next_gate
```

## Safety boundary

This core router does not open a browser, click, type, paste, upload, send, inspect the DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.

It only computes the next policy consumed by the armed gate and named browser-lane executors.

## CLI examples

PASS with configured Chrome status chat:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_report_router_matrix.py `
  --patch-name demo_patch `
  --patch-result PASS `
  --status-chat-configured `
  --status-chat-url https://chatgpt.com/c/example `
  --browser-lane chrome
```

PASS with no status chat:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_report_router_matrix.py `
  --patch-name demo_patch `
  --patch-result PASS
```

FAIL/BLOCKED upload route:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_status_report_router_matrix.py `
  --patch-name demo_patch `
  --patch-result FAIL `
  --operator-report-path C:\path\to\operator_report.txt `
  --browser-lane chrome
```