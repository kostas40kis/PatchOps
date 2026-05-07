# Repair 07: Chrome slash-picker path, self-report attach, no send

Patch `pseudo_self_report_upload_no_send_repair_07_slash_picker_path` stops using file-drop `Ctrl+V` because strict verification proved it did not create a visible attachment in Chrome.

## Previous failure

```text
file_clipboard_written: true
ctrl_v_pressed: true
attachment_verified: false
issues:
- new visible lower-composer attachment was not verified after Ctrl+V file paste; before_matches=0; after_matches=0
```

## New path

This patch uses the Edge-derived picker trigger path adapted to Chrome:

```text
focus visible Chrome ChatGPT/PatchOps target
one calculated safe focus click in the main page area
send /
send Enter once only to select the upload command
wait for one native Windows file picker
write the exact generated self-report path
click the native Open button
verify a new visible attachment appears in the lower composer area
stop before Send
```

## Why Enter appears here

The only Enter is for selecting the ChatGPT upload command after `/`. The patch does **not** press Enter in the chat composer to submit and does **not** press Enter in the file picker. It clicks the native Open button instead.

Evidence distinguishes:

```text
upload_command_enter_pressed:true
enter_key_pressed_in_chat_composer:false
enter_key_pressed_in_picker:false
send_button_pressed:false
chatgpt_submit_performed:false
```

## Expected success label

```text
PASS_CHROME_SELF_REPORT_SLASH_PICKER_ATTACHED_NO_SEND
```

## Safety boundary

No Selenium, no WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.