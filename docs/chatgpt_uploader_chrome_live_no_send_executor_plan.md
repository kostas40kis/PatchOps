# Chrome live no-send executor plan

This component consumes the Chrome live no-send preflight contract and writes a no-action executor plan for a future live no-send executor.

Input preflight contract path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_preflight_contract.json
```

Default executor plan path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_plan.json
```

Default marker path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_plan.txt
```

A passing plan must emit:

```text
PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED
plan_kind: chrome_uploader_live_no_send_executor_plan
expected_browser: chrome
contract_kind: chrome_uploader_live_no_send_preflight_contract
contract_result: PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED
executor_plan_ready: true
no_send_verified: true
attachment_verified: true
safe_for_downstream_planning: true
executor_plan_performs_browser_action: false
executor_plan_performs_chatgpt_submit: false
executor_plan_reads_conversation_text: false
browser_action_performed: false
chatgpt_submit_performed: false
send_allowed: false
raw_conversation_text_available: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
conversation_text_logged: false
raw_conversation_text_logged: false
```

This patch still performs no browser action. It does not open Chrome, click, type, press Enter, inspect the DOM, use WebDriver, bypass Cloudflare/CAPTCHA, read conversation text, or submit a ChatGPT message.

The ordered future execution plan is descriptive only: confirm visible Chrome, confirm correct target conversation, confirm no Cloudflare/CAPTCHA or modal, focus existing Chrome, open the file picker, type the canonical path into the picker, press Enter in the picker, verify the attachment chip, and stop before Send.