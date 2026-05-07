# Repair 06: strict visible attachment verification

Patch `pseudo_self_report_upload_no_send_repair_06_strict_visible_attachment` fixes a false PASS risk in the Chrome keyboard-paste no-send uploader.

## Why this repair exists

The previous run returned PASS, but the operator observed that nothing was visibly uploaded/attached. The evidence also showed the run was no-send by design:

```text
operator_report_uploaded:false
chatgpt_submit_performed:false
send_button_pressed:false
```

The PASS was based on seeing filename-like accessibility text somewhere after Ctrl+V. That is too weak.

## New verification rule

After focusing Chrome and before pressing Ctrl+V, the helper records visible lower-composer filename matches.

After Ctrl+V, it waits until a new visible lower-composer match appears.

The run only passes if the match is:

```text
visible
inside the lower portion of the Chrome target window
contains the generated report filename/stem
new after Ctrl+V, not already present before paste
```

## Expected true success label

```text
PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND
```

If no new visible attachment appears, the run blocks with an issue like:

```text
new visible lower-composer attachment was not verified after Ctrl+V file paste
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