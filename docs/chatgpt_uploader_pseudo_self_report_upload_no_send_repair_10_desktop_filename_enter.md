# Repair 10: Desktop filename + picker Enter

Patch `pseudo_self_report_upload_no_send_repair_10_desktop_filename_enter` follows the requested manual flow.

## Previous failure

Repair 09d compiled and passed tests, but live smoke still did not open a picker:

```text
picker_opened:false
issues:
- native file picker did not open after slash + Enter + Enter-if-needed
```

## New flow

The smoke creates its own self-report on:

```text
C:\Users\vicky\Desktop
```

Then the live browser flow is:

```text
focus Chrome target
safe neutral click
type /
press Enter once
wait for native Windows picker
write only the filename into the picker
press Enter in the picker
verify a new visible attachment appears
stop before Send
```

## Important distinction

The patch writes only:

```text
pseudo_self_report_upload_no_send_repair_10_desktop_filename_enter_self_report.txt
```

not the full path. Evidence includes:

```text
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
PASS_CHROME_SELF_REPORT_DESKTOP_FILENAME_ATTACHED_NO_SEND
```

No Tab trigger, no Open button click, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.