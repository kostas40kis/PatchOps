# Repair 10c: remove bad self-referential guard tests

Patch `pseudo_self_report_upload_no_send_repair_10c_remove_bad_guard_test` removes the self-referential source-string guard tests introduced in repairs 10a/10b.

## Failure fixed

Repair 10b still contained this shape inside a guard test:

```text
assert 'assert "BLOCKED_CHROME_DESKTOP_FILENAME_ENTER_FAILED" not in test_source' not in test_source
```

That assertion necessarily fails because the string exists inside the assertion itself.

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