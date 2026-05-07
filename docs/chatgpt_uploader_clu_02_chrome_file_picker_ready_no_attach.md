# CLU-02 Chrome file picker ready no-attach

Patch `clu_02_chrome_file_picker_ready_no_attach` adds the second Chrome live-upload mini test.

## Purpose

This patch proves Chrome can safely reach the native file picker and identify the filename/path edit box, then cancel without selecting a file.

It checks:

```text
status_chat.enabled == true
browser_lane == chrome
target URL/hash valid
single visible Chrome ChatGPT/PatchOps target window
single attachment control candidate
file picker opens
filename/path edit exists
picker is cancelled/closed
no file selected
no report uploaded
no ChatGPT submit
no Send
```

## Focused test command

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_chatgpt_uploader_chrome_file_picker_ready_no_attach_current.py
```

## Live command

Open the CLU-01 target link in Chrome first, then run:

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_file_picker_ready_no_attach.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_FILE_PICKER_READY_NO_ATTACH `
  --provider pywinauto
```

## Acceptance labels

```text
PASS_CHROME_FILE_PICKER_READY_NO_ATTACH
BLOCKED_CHROME_FILE_PICKER_CONFIG_MISSING
BLOCKED_CHROME_FILE_PICKER_BROWSER_MISMATCH
BLOCKED_CHROME_FILE_PICKER_URL_INVALID
BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_REQUIRED
BLOCKED_CHROME_FILE_PICKER_CONFIRMATION_MISMATCH
BLOCKED_CHROME_FILE_PICKER_TARGET_NOT_READY
BLOCKED_CHROME_FILE_PICKER_AMBIGUOUS_TARGET
BLOCKED_CHROME_FILE_PICKER_ATTACHMENT_CONTROL_NOT_FOUND
BLOCKED_CHROME_FILE_PICKER_NOT_FOUND
BLOCKED_CHROME_FILE_PICKER_PATH_EDIT_NOT_FOUND
BLOCKED_CHROME_FILE_PICKER_CANCEL_NOT_PROVEN
BLOCKED_SEND_RISK
```

## Evidence outputs

```text
data/runtime/copilot_handoff/latest_chrome_file_picker_ready_no_attach.json
data/runtime/copilot_handoff/latest_chrome_file_picker_ready_no_attach.txt
```

## Safety boundary

CLU-02 may focus Chrome, click the single verified attachment control, open the native file picker, inspect native file picker controls through UIA, and cancel the picker.

It must not write a file path, select a file, attach a file, upload an operator report, press Send, submit ChatGPT input, inspect DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.