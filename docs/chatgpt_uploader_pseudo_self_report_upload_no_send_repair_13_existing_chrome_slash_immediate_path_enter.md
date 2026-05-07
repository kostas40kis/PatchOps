# Repair 13: existing Chrome, slash Enter, immediate full-path paste, picker Enter

Patch `pseudo_self_report_upload_no_send_repair_13_existing_chrome_slash_immediate_path_enter` follows the corrected workflow.

## Previous mistake

Repair 12 opened the target URL again, creating a new tab/window context. The URL was already loaded in Chrome. The important step was not opening Chrome; it was using the already-ready Windows file picker and pasting the full path.

## New flow

```text
use the already-loaded Chrome target
focus the existing Chrome window
no new tab
no mouse click
press /
press Enter
immediately check the foreground window is the native Windows file picker
paste the full Desktop path:
C:\Users\vicky\Desktop\pseudo_self_report_upload_no_send_repair_13_existing_chrome_slash_immediate_path_enter_self_report.txt
press Enter in the native picker
verify a new visible attachment appears
stop before Send
```

## Evidence contract

```text
existing_chrome_used:true
chrome_open_invoked:false
mouse_clicks_used:false
slash_key_pressed:true
upload_command_enter_pressed:true
foreground_picker_ready:true
picker_detection_wait_used:false
full_path_pasted_to_picker:true
ctrl_v_pressed_in_picker:true
picker_enter_pressed:true
open_button_clicked:false
enter_key_pressed_in_chat_composer:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

## Safety boundary

The patch refuses to paste/press Enter if the foreground window is not a Windows file picker. This prevents accidentally pasting the file path into the ChatGPT composer and submitting it.

No new Chrome tab, no mouse clicks, no Tab trigger, no Open button click, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.