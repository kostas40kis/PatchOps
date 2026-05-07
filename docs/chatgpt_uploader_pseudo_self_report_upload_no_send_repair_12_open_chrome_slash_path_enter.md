# Repair 12: open Chrome target, slash Enter, paste full path, Enter

Patch `pseudo_self_report_upload_no_send_repair_12_open_chrome_slash_path_enter` follows the requested manual sequence exactly.

## Previous result

Repair 11 clicked upload/paperclip candidates and even clicked one upload menu item, but no native picker opened. That means the button/menu UIA path is not reliable for this target.

## New flow

```text
open Chrome at the configured target ChatGPT URL
focus the Chrome target window
no mouse click
press /
press Enter
wait for the native Windows file picker
paste the full Desktop path: C:\Users\vicky\Desktop\<self-report>.txt
press Enter in the native picker
verify a new visible attachment appears
stop before Send
```

## Evidence contract

```text
chrome_open_invoked:true
mouse_clicks_used:false
slash_key_pressed:true
upload_command_enter_pressed:true
picker_opened:true
full_path_pasted_to_picker:true
ctrl_v_pressed_in_picker:true
picker_enter_pressed:true
open_button_clicked:false
enter_key_pressed_in_chat_composer:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

## Expected success label

```text
PASS_CHROME_SELF_REPORT_OPEN_SLASH_PATH_ENTER_ATTACHED_NO_SEND
```

No mouse clicks, no Tab trigger, no Open button click, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.