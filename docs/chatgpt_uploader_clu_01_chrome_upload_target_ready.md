# CLU-01 Chrome upload target ready

Patch clu_01_chrome_upload_target_ready sets the Chrome uploader target to the supplied PatchOps ChatGPT link and adds the first mini live-test doctor.

## Target

The raw target URL is stored in:

`	ext
data/config/uploader_status_target_config.json
`

Evidence stores only the URL hash/redacted value:

`	ext
sha256:ffc9dabd16f479a6cae0899920247b498cbd0138eb3a8c4a6567d5a9434a39fc
`

## Purpose

This patch proves Chrome target readiness before any file picker or attachment action.

It checks:

`	ext
status_chat.enabled == true
browser_lane == chrome
target URL is an HTTPS chatgpt.com conversation URL containing /c/<id>
single visible Chrome ChatGPT/PatchOps target window
attachment control candidate exists
no file picker opened
no upload
no send
`

## Focused test command

`powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_chatgpt_uploader_chrome_upload_target_ready_current.py
`

## Live command

Open the target link in Chrome first, then run:

`powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_upload_target_ready.py 
  --live-browser 
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_UPLOAD_TARGET_READY 
  --provider pywinauto
`

## Acceptance labels

`	ext
PASS_CHROME_UPLOAD_TARGET_READY
BLOCKED_CHROME_UPLOAD_TARGET_CONFIG_MISSING
BLOCKED_CHROME_UPLOAD_TARGET_BROWSER_MISMATCH
BLOCKED_CHROME_UPLOAD_TARGET_URL_INVALID
BLOCKED_CHROME_UPLOAD_TARGET_CONFIRMATION_REQUIRED
BLOCKED_CHROME_UPLOAD_TARGET_CONFIRMATION_MISMATCH
BLOCKED_CHROME_UPLOAD_TARGET_NOT_READY
BLOCKED_CHROME_UPLOAD_AMBIGUOUS_TARGET
BLOCKED_CHROME_UPLOAD_ATTACHMENT_CONTROL_NOT_FOUND
BLOCKED_SEND_RISK
`

## Evidence outputs

`	ext
data/runtime/copilot_handoff/latest_chrome_upload_target_ready.json
data/runtime/copilot_handoff/latest_chrome_upload_target_ready.txt
`

## Safety boundary

CLU-01 may focus the visible Chrome ChatGPT target during live mode. It must not type, paste, open the file picker, attach a file, upload a report, press Send, submit ChatGPT input, inspect DOM, use Selenium/WebDriver, bypass CAPTCHA/Cloudflare, log raw conversation text, random-click, or run an unbounded loop.