# ChatGPT Uploader U2.4C Keyboard Shortcut Trigger Probe

U2.4B installed `pywinauto` into the `py` runtime, but the live upload trigger still returned `FAIL_OR_BLOCKED` for 5 attempts. U2.4C keeps the same safety boundary while adding two things:

1. full observed candidate diagnostics for plus/menu controls;
2. an explicit keyboard-shortcut trigger probe.

## Trigger order

When `--allow-open-picker` is set:

```text
1. focus configured normal Edge ChatGPT target
2. if explicitly allowed, try the upload keyboard shortcut probe
3. detect the Windows picker
4. close picker if detected
5. if keyboard shortcut does not detect a picker, try scored UIA plus/menu controls
6. record observed candidates and failure reasons
```

## Safety boundary

U2.4C may attempt to open and close the picker, but must not:

```text
write a report path
select a file
press Open/Enter inside the picker
confirm attachment
claim upload success
send/submit
use Selenium/WebDriver
use browser DOM automation
click random coordinates
log conversation text
```

## Evidence additions

JSON evidence now includes:

```text
trigger_backend
keyboard_shortcut_attempted
observed_plus_candidates
observed_menu_candidates
plus_candidate
menu_candidate
backend/status counts in TXT evidence
```

If the keyboard shortcut works, the pass condition is still only picker opened and closed. It is not an upload.
