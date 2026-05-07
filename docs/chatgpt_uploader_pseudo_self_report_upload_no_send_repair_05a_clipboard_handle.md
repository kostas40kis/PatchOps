# Repair 05a: 64-bit clipboard handle fix

Patch `pseudo_self_report_upload_no_send_repair_05a_clipboard_handle` repairs the keyboard-paste upload path after Chrome focus succeeded but CF_HDROP clipboard setup failed.

## Failure fixed

Previous live smoke evidence showed:

```text
chrome_target_ready: true
chrome_target_focused: true
result_label: BLOCKED_CHROME_KEYBOARD_CLIPBOARD_FAILED
issues:
- file clipboard setup failed: GlobalLock failed
```

The failure was caused by default `ctypes` signatures truncating/handling Windows clipboard memory handles unsafely on 64-bit Python.

## Repair behavior

The clipboard helper now uses explicit signatures for:

```text
OpenClipboard
EmptyClipboard
GlobalAlloc
GlobalLock
GlobalUnlock
GlobalFree
SetClipboardData
CloseClipboard
```

It also factors out `build_cf_hdrop_payload()` so the file-drop payload can be unit tested without touching the real clipboard.

## Expected live label

```text
PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND
```

## No-send contract

```text
keyboard_shortcuts_used: CTRL+V
enter_key_pressed:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
file_picker_used:false
```

No DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation logging, random clicks, upload-menu guessing, Enter fallback, or Send is added.