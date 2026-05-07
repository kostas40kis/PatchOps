# Chrome live no-send preflight contract

This component consumes the no-action Chrome live instruction packet and writes a preflight contract for a future live no-send executor.

Input packet path:

```text
data/runtime/copilot_handoff/latest_uploader_live_instruction_packet.json
```

Default preflight contract path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_preflight_contract.json
```

A passing contract must emit:

```text
PASS_CHROME_LIVE_NO_SEND_PREFLIGHT_CONTRACT_VALIDATED
contract_kind: chrome_uploader_live_no_send_preflight_contract
expected_browser: chrome
packet_kind: chrome_uploader_live_instruction_packet_no_action
packet_result: PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED
boundary_kind: chrome_uploader_explicit_live_action_boundary
boundary_result: PASS_CHROME_EXPLICIT_LIVE_ACTION_BOUNDARY_VALIDATED
preflight_contract_ready: true
no_send_verified: true
attachment_verified: true
packet_performs_browser_action: false
packet_performs_chatgpt_submit: false
packet_reads_conversation_text: false
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

The future executor may only proceed when a visible existing Chrome window is confirmed, the correct target conversation is already open, the file picker is not open initially, the send button is not focused, no Cloudflare/CAPTCHA is present, and no unexpected modal is visible.