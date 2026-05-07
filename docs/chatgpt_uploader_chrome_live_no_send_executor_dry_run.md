# Chrome live no-send executor dry run

This component consumes the Chrome live no-send executor plan and writes a dry-run readiness handoff for a future live executor.

Input executor plan path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_plan.json
```

Default dry-run path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_dry_run.json
```

Default marker path:

```text
data/runtime/copilot_handoff/latest_uploader_live_no_send_executor_dry_run.txt
```

A passing dry run must emit:

```text
PASS_CHROME_LIVE_NO_SEND_EXECUTOR_DRY_RUN_VALIDATED
dry_run_kind: chrome_uploader_live_no_send_executor_dry_run
expected_browser: chrome
plan_kind: chrome_uploader_live_no_send_executor_plan
plan_result: PASS_CHROME_LIVE_NO_SEND_EXECUTOR_PLAN_VALIDATED
dry_run_ready: true
executor_plan_ready: true
no_send_verified: true
attachment_verified: true
safe_for_downstream_planning: true
dry_run_performs_browser_action: false
dry_run_performs_chatgpt_submit: false
dry_run_reads_conversation_text: false
executor_dry_run_performed_live_action: false
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

The dry-run checklist requires an operator to confirm that Chrome is visible, the correct target conversation is already open, there is no Cloudflare/CAPTCHA or unexpected modal, the canonical attachment path is available, and the future executor stops before Send.