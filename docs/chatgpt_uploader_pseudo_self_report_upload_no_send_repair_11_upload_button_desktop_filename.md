# Repair 11: upload button + Desktop filename + picker Enter

Patch `pseudo_self_report_upload_no_send_repair_11_upload_button_desktop_filename` stops using command shortcuts to open the file picker.

## Previous failure

Repair 10c reached live smoke, created the Desktop self-report, focused Chrome, and performed the safe click, but the native picker still did not open after `/` + Enter:

```text
chrome_target_ready:true
chrome_target_focused:true
slash_key_pressed:true
picker_opened:false
issues:
- native file picker did not open after slash + Enter
```

## New flow

```text
create self-report on C:\Users\vicky\Desktop
focus Chrome target
safe neutral click
click visible upload/paperclip control
if a menu opens, click the best upload-file/from-computer menu item
wait for native Windows picker
write only the Desktop filename into the picker
press Enter in the picker
verify a new visible attachment appears
stop before Send
```

## Important evidence

```text
upload_button_clicked:true
slash_key_pressed:false
upload_command_enter_pressed:false
filename_written:true
full_path_written_to_picker:false
open_button_clicked:false
picker_enter_pressed:true
enter_key_pressed_in_chat_composer:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

## Expected success label

```text
PASS_CHROME_SELF_REPORT_UPLOAD_BUTTON_DESKTOP_FILENAME_ATTACHED_NO_SEND
```

No slash command trigger, no Tab trigger, no Open button click, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.