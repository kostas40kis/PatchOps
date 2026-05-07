# Repair 09: Slash, Enter, Enter-if-needed picker path

Patch `pseudo_self_report_upload_no_send_repair_09_slash_enter_enter` removes the Tab trigger path and uses the requested Chrome trigger sequence:

```text
type /
press Enter
wait for native picker
if no picker appears, press Enter once more
wait for native picker
```

After the picker opens, the helper writes the exact generated self-report path, clicks the native Open button, verifies a new visible lower-composer attachment, and stops before Send.

## Why this repair exists

The Tab/Enter path appeared to succeed in evidence but did not visibly attach/upload in the operator view. This patch keeps strict visible attachment verification and changes only the picker trigger sequence.

## Evidence expectations

```text
keyboard_shortcuts_used: /,ENTER_FOR_UPLOAD_COMMAND_ONLY,SECOND_ENTER_FOR_UPLOAD_COMMAND_ONLY_IF_NEEDED
enter_key_pressed_in_chat_composer:false
enter_key_pressed_in_picker:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

The two Enter presses are only for selecting/opening the upload command path. The patch must still stop before Send.

## Expected success label

```text
PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND
```

No Selenium, no WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.