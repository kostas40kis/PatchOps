# Chrome live instruction packet

This component consumes a confirmed Chrome explicit live-action boundary and writes a no-action instruction packet for a future human-supervised Chrome no-send run.

Input boundary path:

```text
data/runtime/copilot_handoff/latest_uploader_live_action_boundary.json
```

Default instruction packet path:

```text
data/runtime/copilot_handoff/latest_uploader_live_instruction_packet.json
```

A passing packet must emit:

```text
PASS_CHROME_LIVE_INSTRUCTION_PACKET_VALIDATED
packet_kind: chrome_uploader_live_instruction_packet_no_action
expected_browser: chrome
boundary_kind: chrome_uploader_explicit_live_action_boundary
boundary_confirmed: true
live_action_allowed_by_boundary: true
packet_performs_browser_action: false
packet_performs_chatgpt_submit: false
packet_reads_conversation_text: false
send_allowed: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
conversation_text_logged: false
raw_conversation_text_logged: false
```

The packet is not a live executor. It must not open Chrome, click, type, press Enter, use WebDriver, use DOM automation, bypass Cloudflare/CAPTCHA, read conversation text, or send a ChatGPT message.

Future live actions remain limited to a human-visible Chrome no-send path and must stop if the target Chrome window is missing, hidden, ambiguous, wrong-browser, blocked by Cloudflare/CAPTCHA, at risk of sending, or unable to verify the expected attachment chip.