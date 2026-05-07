# Repair 10b: self-referential test assertion fix

Patch `pseudo_self_report_upload_no_send_repair_10b_self_referential_test_fix` fixes a test bug from repair 10a.

## Failure fixed

Repair 10a changed the import to the correct constant:

```text
BLOCKED_CHROME_DESKTOP_FILENAME_PICKER_ENTER_FAILED
```

but the new guard test checked that the old constant string was absent from the entire test file while containing that old string in the assertion itself.

This patch removes that self-referential assertion.

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