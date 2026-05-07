# Repair 09d: same-line detector fix and test alignment

Patch `pseudo_self_report_upload_no_send_repair_09d_detector_fix_test_alignment` fixes repair 09c's detector bug.

## Failure fixed

Repair 09c used a detector with `\s+`, which can match a correctly split newline. This caused a false refusal:

```text
Collapsed picker wait/if line still present after force-fix.
```

This patch uses a same-line-only detector and only treats this as broken:

```text
pickers = self._wait_for_picker()        if len(pickers) == 0:
```

## Trigger behavior

```text
type /
press Enter
wait for native picker
if no picker appears, press Enter once more
wait for native picker
```

After picker open, the helper writes the exact generated self-report path, clicks native Open, verifies a new visible lower-composer attachment, and stops before Send.

## Expected success label

```text
PASS_CHROME_SELF_REPORT_SLASH_ENTER_ENTER_ATTACHED_NO_SEND
```

No Tab trigger, no Selenium/WebDriver, no DOM automation, no Cloudflare/CAPTCHA bypass, no raw conversation logging, no random page click, no unbounded retries, and no Send.