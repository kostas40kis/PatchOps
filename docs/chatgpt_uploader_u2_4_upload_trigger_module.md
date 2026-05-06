# ChatGPT Uploader U2.4 Upload Trigger Module

U2.4 adds the first explicit-gated picker-opening module.

## Scope

Added:

```text
patchops/chatgpt_uploader/upload_trigger.py
scripts/run_uploader_open_picker_live.py
tests/test_chatgpt_uploader_u2_4_upload_trigger_current.py
```

## Trigger policy

The trigger must prefer verified UIA controls and reject dangerous controls.

Order:

```text
1. Focus configured normal Microsoft Edge ChatGPT target.
2. Find verified composer plus/attach UIA control.
3. Activate it using UIA invoke, or verified UIA click only after a scored candidate is recorded.
4. If a menu opens, find verified Add photos/files menu item.
5. Detect the Windows picker.
6. Close the picker.
7. Repeat for the requested attempt count.
```

## Safety boundary

U2.4 may open and close the picker only when `--allow-open-picker` is explicitly passed.

It must not:

```text
write a path
select a file
press Open or Enter
confirm attachment
claim upload success
send/submit
use Selenium/WebDriver
use browser DOM automation
click random coordinates
log conversation text
```

## Acceptance

Preferred live acceptance:

```text
5/5 picker-open attempts pass
picker closed after each attempt
no report selected
no send
no random clicks
```

If the live UI has changed, the run must block with JSON/TXT evidence rather than guessing.
