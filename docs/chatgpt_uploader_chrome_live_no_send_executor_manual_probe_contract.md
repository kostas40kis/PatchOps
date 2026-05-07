# Chrome live no-send executor manual-probe contract

This component consumes the Chrome live no-send executor dry-run handoff and writes a manual-probe contract for the future live executor.

Input dry-run path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_dry_run.json
```

Default manual-probe contract path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_manual_probe_contract.json
```

Default marker path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_manual_probe_contract.txt
```

A passing contract must emit:

```text
PASS_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE_CONTRACT_VALIDATED
contract_kind: chrome_uploader_live_no_send_executor_manual_probe_contract
expected_browser: chrome
dry_run_kind: chrome_uploader_live_no_send_executor_dry_run
dry_run_result: PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED
manual_probe_contract_ready: true
dry_run_ready: true
executor_plan_ready: true
no_send_verified: true
attachment_verified: true
safe_for_downstream_planning: true
explicit_confirmation_required: true
confirmation_text: PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE
manual_probe_contract_performs_browser_action: false
manual_probe_contract_performs_chatgpt_submit: false
manual_probe_contract_reads_conversation_text: false
manual_probe_contract_performed_live_action: false
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

The future executor command template is written as data only and must not be executed by this patch:

```text
python scripts/run_uploader_chrome_live_no_send_executor.py --contract-json data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_manual_probe_contract.json --live-browser --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_LIVE_NO_SEND_EXECUTOR_MANUAL_PROBE --stop-before-send
```

This patch still performs no browser action. It does not open Chrome, click, type, press Enter, inspect the DOM, use WebDriver, bypass Cloudflare/CAPTCHA, read conversation text, or submit a ChatGPT message.