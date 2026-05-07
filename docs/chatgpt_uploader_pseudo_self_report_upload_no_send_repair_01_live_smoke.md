# Pseudo self-report upload no-send repair 01: live smoke command

Patch `pseudo_self_report_upload_no_send_repair_01_live_smoke` repairs the previous pseudo patch behavior by putting the live Chrome attach step inside PatchOps `smoke_commands`.

## Why this repair exists

The previous pseudo patch wrote the helper and tests, but the PatchOps Desktop report showed:

```text
SMOKE COMMANDS
--------------
(none)
```

That means PatchOps apply only ran unit validation. It did not click Chrome or attach a report.

## What changes

This repair adds:

```text
scripts/run_pseudo_self_report_upload_no_send_apply_smoke.py
```

and a PatchOps smoke command that runs it during apply.

The smoke command:

1. creates `data/runtime/copilot_handoff/pseudo_self_report_upload_no_send_apply_self_report.txt`
2. hashes it
3. opens the configured Chrome target through the existing explicit Chrome helper
4. clicks the native file picker attachment control
5. writes the report path
6. clicks the native `Open` button
7. verifies the attachment is present
8. stops before Send

## Explicit no-send/no-enter contract

```text
enter_key_pressed: false
send_button_pressed: false
chatgpt_submit_performed: false
operator_report_uploaded: false
status_message_posted: false
```

`operator_report_uploaded` remains false because the report is attached to the composer only. No ChatGPT message is submitted.

## Expected success label

```text
PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND
```

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_pseudo_self_report_upload_no_send_apply_smoke.json
data/runtime/copilot_handoff/latest_pseudo_self_report_upload_no_send_apply_smoke.txt
data/runtime/copilot_handoff/pseudo_self_report_upload_no_send_apply_self_report.txt
```

## Safety boundary

This smoke uses visible Chrome UI Automation only. It does not use DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation text logging, random clicks, generic all-browser abstractions, Enter fallback, or Send.