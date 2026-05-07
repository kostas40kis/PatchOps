# Repair 15: set the foreground picker filename edit directly

Patch `pseudo_self_report_upload_no_send_repair_15_foreground_picker_edit_set_text` addresses the 14 result and the visible observation that nothing was written into File Explorer.

## What 14 proved

```text
foreground_picker_ready:true
foreground_picker_class:#32770
clipboard_text_written:true
low_level_ctrl_v_sent:false
issues:
- low-level Ctrl+V failed: SendInput sent 0/4 events
```

So the picker was ready, but no path was typed/pasted.

## New flow

```text
use the already-loaded Chrome target
no new tab
no mouse click
press /
press Enter
confirm foreground window is Windows file picker
find the foreground picker's filename Edit control
write the full Desktop path directly with UIA set_edit_text
verify the edit reflects the filename/path
press Enter in the picker
verify visible attachment
stop before Send
```

## Full path used

```text
C:\Users\vicky\Desktop\pseudo_self_report_upload_no_send_repair_15_foreground_picker_edit_set_text_self_report.txt
```

## Evidence contract

```text
foreground_picker_ready:true
picker_edit_found:true
picker_edit_value_set:true
picker_edit_verified:true
full_path_written_to_picker:true
clipboard_text_written:false
ctrl_v_pressed_in_picker:false
low_level_ctrl_v_sent:false
picker_enter_pressed:true
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

No new Chrome tab, no mouse clicks, no Tab trigger, no Open button click, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.