# Repair 10a: Desktop filename constant alignment

Patch `pseudo_self_report_upload_no_send_repair_10a_constant_alignment` fixes a test import mismatch from repair 10.

## Failure fixed

Repair 10 compiled, but tests imported:

```text
BLOCKED_CHROME_DESKTOP_FILENAME_ENTER_FAILED
```

The module intentionally defines:

```text
BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_ENTER_FAILED
```

This patch aligns the tests with the module constant and reruns the same live smoke.

## Behavior unchanged

The live browser flow remains:

```text
create self-report on C:\Users\vicky\Desktop
focus Chrome target
type /
press Enter once
wait for native Windows picker
write only the filename into the picker
press Enter in the picker
verify visible attachment
stop before Send
```

## Expected success label

```text
PASS_CHROME_SELF_REPORT_DESKTOP_FILENAME_ATTACHED_NO_SEND
```

No Tab trigger, no Open button click, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.