# U3 C33 Edge status target preflight

Patch `u3_c33_edge_status_target_preflight` adds the explicit Microsoft Edge lane status-target preflight.

## Purpose

This patch validates and rehearses the Edge status target before Edge PASS-message sending is enabled.

It consumes either:

```text
data/runtime/copilot_handoff/latest_uploader_status_target_config_validation.json
data/config/uploader_status_target_config.json
```

or an explicit path passed with:

```powershell
--status-target-path C:\path\to\edge_status_target.json
```

## Required target shape

```json
{
  "status_chat": {
    "browser_lane": "edge",
    "target_url": "https://chatgpt.com/c/...",
    "target_url_sha256": "<hash>",
    "enabled": true
  }
}
```

Hash-only target evidence is accepted when the raw target URL is not available.

## Required live command

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_edge_status_target_preflight.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_EDGE_STATUS_TARGET_PREFLIGHT `
  --provider pywinauto
```

## Acceptance labels

```text
PASS_EDGE_STATUS_TARGET_PREFLIGHT_READY
BLOCKED_EDGE_STATUS_TARGET_CONFIG_MISSING
BLOCKED_EDGE_STATUS_TARGET_BROWSER_MISMATCH
BLOCKED_EDGE_STATUS_TARGET_URL_INVALID
BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_REQUIRED
BLOCKED_EDGE_STATUS_TARGET_CONFIRMATION_MISMATCH
BLOCKED_EDGE_STATUS_TARGET_NOT_READY
BLOCKED_SEND_RISK
```

## Safety boundary

This patch may focus the visible Microsoft Edge ChatGPT target under explicit live flags.

It must not type, paste, upload, press Send, submit ChatGPT input, inspect DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_edge_status_target_preflight.json
data/runtime/copilot_handoff/latest_edge_status_target_preflight.txt
```

Successful preflight evidence records:

```text
browser_lane:edge
edge_target_ready:true
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

Target titles are stored as hash/length only.