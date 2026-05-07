# Repair 08: Chrome tab/enter picker path, self-report attach, no send

Patch `pseudo_self_report_upload_no_send_repair_08_tab_enter_picker_path` adapts the Edge U2.4E trigger shape to Chrome.

## Why this repair exists

Repair 07 focused Chrome and sent `/` plus Enter, but no native picker opened:

```text
chrome_target_ready: true
chrome_target_focused: true
safe_focus_click_performed: true
slash_key_pressed: true
upload_command_enter_pressed: true
picker_opened: false
issues:
- native file picker did not open after slash+Enter
```

## New trigger shape

```text
focus Chrome
one calculated safe neutral click
Tab once
Enter once
if no picker appears, Enter once more
stop immediately once picker is detected
```

After the picker is detected, this patch writes the exact generated self-report path, clicks the native Open button, verifies a new visible attachment appears in the lower composer area, and stops before Send.

## Safety boundary

The second Enter is only attempted if no picker exists yet. No Enter is sent inside the picker. The picker is operated by exact path write plus native Open button click.

```text
enter_key_pressed_in_chat_composer:false
enter_key_pressed_in_picker:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

No Selenium, no WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.

## Expected success label

```text
PASS_CHROME_SELF_REPORT_TAB_ENTER_PICKER_ATTACHED_NO_SEND
```