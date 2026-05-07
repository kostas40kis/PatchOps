# Repair 16: Win32 dialog filename submit

Patch `pseudo_self_report_upload_no_send_repair_16_win32_dialog_filename_submit` addresses the 15 result.

## What 15 proved

```text
foreground_picker_ready:true
foreground_picker_class:#32770
picker_edit_found:false
issues:
- no visible enabled filename Edit control was found in foreground Windows picker
```

So File Explorer was open, but UIA could not see its filename edit field.

## New flow

```text
use the already-loaded Chrome target
no new tab
no mouse click
press /
press Enter
confirm foreground is the native Windows file picker
use the foreground dialog HWND directly
write the full Desktop path to the common-file-dialog filename control ID 1148
also try visible native child Edit/ComboBox/ComboBoxEx32 controls
submit with Enter-message / IDOK fallback
verify visible attachment
stop before Send
```

## Full path used

```text
C:\Users\vicky\Desktop\pseudo_self_report_upload_no_send_repair_16_win32_dialog_filename_submit_self_report.txt
```

## Evidence contract

```text
foreground_picker_ready:true
dialog_filename_control_attempted:true
dialog_filename_candidate_count:>=1
full_path_written_to_picker:true
dialog_submit_attempted:true
picker_enter_pressed:true
clipboard_text_written:false
ctrl_v_pressed_in_picker:false
open_button_clicked:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
```

No new Chrome tab, no mouse clicks, no Tab trigger, no clipboard/Ctrl+V, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.