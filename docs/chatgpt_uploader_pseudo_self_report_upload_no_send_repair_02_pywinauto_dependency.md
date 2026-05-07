# Pseudo self-report upload no-send repair 02: pywinauto dependency

Patch `pseudo_self_report_upload_no_send_repair_02_pywinauto_dependency` records the live-smoke dependency repair for the pseudo self-report upload flow.

## Failure fixed

The previous live smoke did execute, but it stopped before touching Chrome because the PatchOps virtual environment did not have `pywinauto` installed.

Observed label:

```text
BLOCKED_CHROME_SELF_REPORT_TARGET_NOT_READY
```

Observed issue:

```text
pywinauto is required for live Chrome self-report upload: No module named 'pywinauto'
```

## Repair behavior

The repair script:

1. verifies the PatchOps venv Python exists
2. checks whether `pywinauto` can be imported
3. installs `pywinauto` into the venv if missing
4. verifies import again
5. applies this documentation marker patch
6. reruns the live no-send self-report smoke command

## Expected success label

```text
PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND
```

## No-send/no-enter contract

```text
enter_key_pressed: false
send_button_pressed: false
chatgpt_submit_performed: false
operator_report_uploaded: false
```

`operator_report_uploaded` remains false because the report is attached to the composer only. The chat is not submitted.

## Safety boundary

This repair does not add DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation logging, random clicks, generic browser abstractions, Enter fallback, or Send.