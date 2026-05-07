# Chrome acceptance handoff reader

This component is a read-only downstream consumer guard for the Chrome-only uploader acceptance handoff.

Input handoff path:

```text
data/runtime/copilot_handoff/latest_uploader_acceptance.json
```

Default consumed proof path:

```text
data/runtime/copilot_handoff/latest_uploader_acceptance_consumed.json
```

A passing read must emit:

```text
PASS_CHROME_ACCEPTANCE_HANDOFF_CONSUMED_NO_BROWSER
consumed_kind: chrome_uploader_acceptance_consumed_no_browser
handoff_kind: chrome_uploader_acceptance_no_send
expected_browser: chrome
acceptance_result: PASS_CHROME_UPLOAD_ACCEPTED_NO_SEND
no_send_verified: true
attachment_verified: true
browser_opened_by_reader: false
no_browser_action_performed: true
chatgpt_submit_performed: false
selenium_used: false
webdriver_used: false
browser_dom_automation_used: false
conversation_text_logged: false
raw_conversation_text_logged: false
```

The reader must not open Chrome, press keys, click buttons, submit ChatGPT messages, inspect the DOM, invoke WebDriver, or read conversation text. It only validates JSON contract fields, hashes the source handoff file, and writes a downstream-safe consumed proof.