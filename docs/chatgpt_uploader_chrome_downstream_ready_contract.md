# Chrome downstream ready contract

This component consumes the read-only Chrome acceptance handoff reader output and writes a downstream planning contract.

Input consumed proof path:

```text
data/runtime/copilot_handoff/latest_uploader_acceptance_consumed.json
```

Default ready contract path:

```text
data/runtime/copilot_handoff/latest_uploader_ready_contract.json
```

A passing ready contract must emit:

```text
PASS_CHROME_DOWNSTREAM_READY_CONTRACT_VALIDATED
ready_contract_kind: chrome_uploader_downstream_ready_contract
consumed_kind: chrome_uploader_acceptance_consumed_no_browser
expected_browser: chrome
no_send_verified: true
attachment_verified: true
safe_for_downstream_planning: true
read_only_contract: true
browser_action_performed: false
chatgpt_submit_performed: false
raw_conversation_text_available: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
conversation_text_logged: false
raw_conversation_text_logged: false
```

Allowed downstream planning actions are restricted to reading acceptance summaries, planning orchestration, preparing explicit live-test instructions, and requesting human confirmation before any browser action.

Forbidden downstream actions include opening a browser without explicit live confirmation, sending a ChatGPT message, reading conversation text, DOM automation, WebDriver, Cloudflare/CAPTCHA bypass, and random clicking.