# U3 C29 Chrome status message no-send probe

Patch `u3_c29_chrome_status_message_no_send_probe` adds the Chrome lane no-send rehearsal for the new PASS status behavior.

## Purpose

Input selected action:

```text
post_status_message
```

Live behavior:

```text
focus visible Chrome target
prepare exact message: <patch_name> has passed
place message into composer only if safe
verify no send happened
stop before Send
```

## Required live flags

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_status_message_no_send_probe.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_STATUS_MESSAGE_NO_SEND `
  --stop-before-send `
  --provider pywinauto
```

## Acceptance labels

```text
PASS_CHROME_STATUS_MESSAGE_COMPOSER_READY_NO_SEND
BLOCKED_CHROME_STATUS_TARGET_NOT_READY
BLOCKED_STATUS_MESSAGE_MISMATCH
BLOCKED_SEND_RISK
```

## Safety boundary

This patch may focus the visible Chrome target and place the exact PASS message into the composer under explicit live flags.

It must not press Send, submit ChatGPT input, upload an operator report, inspect the DOM, use Selenium/WebDriver, attempt CAPTCHA/Cloudflare bypass, log raw conversation text, random-click, or run an unbounded loop.

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_status_message_no_send_probe.json
data/runtime/copilot_handoff/latest_chrome_status_message_no_send_probe.txt
```

Evidence records title hash/length rather than raw target title and preserves:

```text
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

## Notes

The default fake provider supports safe unit validation without opening Chrome. The live `pywinauto` provider is only used when the operator passes the required live flags.