# Chrome explicit live-action boundary

This component consumes the Chrome downstream ready contract and creates an explicit human-confirmation boundary for any future live Chrome action.

Input ready contract path:

```text
data/runtime/copilot_handoff/latest_uploader_ready_contract.json
```

Default boundary path:

```text
data/runtime/copilot_handoff/latest_uploader_live_action_boundary.json
```

Without the exact confirmation text, the boundary writes a safe blocked proof:

```text
BLOCKED_LIVE_BOUNDARY_CONFIRMATION_REQUIRED
live_action_allowed:false
browser_action_performed:false
chatgpt_submit_performed:false
send_allowed:false
```

The required confirmation text is:

```text
PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_ACTION
```

With the exact confirmation text, the boundary may emit:

```text
PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED
boundary_kind: chrome_uploader_explicit_live_action_boundary
expected_browser: chrome
live_action_allowed: true
send_allowed: false
browser_action_performed: false
chatgpt_submit_performed: false
raw_conversation_text_available: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
conversation_text_logged: false
raw_conversation_text_logged: false
```

This patch still performs no browser action. It only creates the boundary contract. Always-forbidden actions include sending a ChatGPT message, reading conversation text, DOM automation, WebDriver, Cloudflare/CAPTCHA bypass, random clicking, and hidden browser use.