# Repair 04: upload menu before native file picker

Patch `pseudo_self_report_upload_no_send_repair_04_upload_menu` repairs the live no-send smoke after the attachment candidate was found and clicked but no native file picker appeared.

## Failure fixed

Previous evidence:

```text
chrome_target_ready: true
chrome_target_focused: true
attachment_control_found: true
attachment_candidate_count: 1
file_picker_used: true
file_picker_opened: false
issues:
- expected exactly one native file picker; found 0
```

That likely means the clicked ChatGPT control opened an intermediate plus/upload menu instead of directly opening the native file picker.

## Repair behavior

After clicking the attachment/plus control, the helper now:

1. checks for the native file picker
2. if no picker is present, searches visible UIA elements for an explicit upload/add-files menu item
3. clicks exactly one such menu item if found
4. checks for the native file picker again
5. continues with path write and native Open button click

## Safety boundary

No DOM automation, no Selenium/WebDriver, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random clicks, no Enter fallback, and no Send.

Expected final label:

```text
PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND
```