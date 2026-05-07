# Repair 05: Edge-style keyboard paste upload path for Chrome

Patch `pseudo_self_report_upload_no_send_repair_05_keyboard_paste` stops tuning the Chrome upload-menu click selector and switches to the keyboard-style path used by the Edge/pasteback lane: clipboard + `Ctrl+V`.

## Why this repair exists

The last live run proved the UI click path had reached a bad state:

```text
chrome_target_ready: true
chrome_target_focused: true
attachment_control_found: true
attachment_candidate_count: 1
file_picker_used: true
file_picker_opened: false
issues:
- expected zero or one upload menu item; found 2
```

Continuing to choose between two menu items risks the wrong click. This repair avoids the menu entirely.

## New live behavior

```text
focus visible Chrome target
write generated self-report file to the Windows clipboard as CF_HDROP
press Ctrl+V in the focused ChatGPT composer
verify attachment chip/text appears
stop before Enter
stop before Send
```

## Keyboard shortcuts

Allowed shortcut used:

```text
CTRL+V
```

Forbidden shortcuts not used:

```text
ENTER
CTRL+ENTER
ALT+ENTER
CTRL+U
/
```

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_pseudo_self_report_keyboard_upload_no_send.json
data/runtime/copilot_handoff/latest_pseudo_self_report_keyboard_upload_no_send.txt
data/runtime/copilot_handoff/pseudo_self_report_keyboard_upload_no_send_self_report.txt
```

## Expected success label

```text
PASS_CHROME_SELF_REPORT_KEYBOARD_ATTACHED_NO_SEND
```

## No-send contract

```text
enter_key_pressed:false
send_button_pressed:false
chatgpt_submit_performed:false
operator_report_uploaded:false
file_picker_used:false
```

`operator_report_uploaded` remains false because the report is attached to the composer only. No ChatGPT message is submitted.

## Safety boundary

No DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation logging, random clicks, picker menu guessing, Enter fallback, or Send is added.