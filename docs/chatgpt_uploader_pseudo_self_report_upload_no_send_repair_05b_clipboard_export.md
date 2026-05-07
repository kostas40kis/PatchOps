# Repair 05b: export clipboard payload helper

Patch `pseudo_self_report_upload_no_send_repair_05b_clipboard_export` fixes repair 05a.

## Failure fixed

Repair 05a added a unit test for `build_cf_hdrop_payload`, but the helper was accidentally inserted before `build_adapter` and then deleted by the later replacement of the whole `set_clipboard_file_drop -> build_adapter` region.

Observed failure:

```text
ImportError: cannot import name 'build_cf_hdrop_payload'
```

## Repair behavior

This patch replaces the whole clipboard section in one pass, including:

```text
build_cf_hdrop_payload
_last_winerror_message
set_clipboard_file_drop
```

Then it runs compile, focused tests, and the live Chrome keyboard smoke.

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