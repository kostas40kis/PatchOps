# Pseudo self-report upload no-send

Patch `pseudo_self_report_upload_no_send` creates a pseudo/no-op PatchOps patch and then runs a live Chrome self-report attach step.

## Behavior

The outer PowerShell script:

1. Writes this helper module, CLI, tests, docs, and the Chrome status target config.
2. Applies the pseudo patch through PatchOps.
3. Builds a self report file from the patch run output.
4. Runs the live Chrome attach step against the configured target URL.
5. Stops before Send.

## Live command emitted by the patch script

```powershell
.\.venv\Scripts\python.exe scripts\run_uploader_chrome_self_report_upload_no_send.py `
  --live-browser `
  --confirm-live-browser-text PATCHOPS_CONFIRM_CHROME_SELF_REPORT_UPLOAD_NO_SEND `
  --provider pywinauto `
  --self-report-path <generated-self-report> `
  --self-report-sha256 <sha256>
```

## No-Enter rule

This helper does not use Enter as a fallback.

The native file picker path is written into the path edit control and the visible `Open` button is clicked. If the `Open` button cannot be found, the run blocks with:

```text
BLOCKED_CHROME_SELF_REPORT_OPEN_BUTTON_NOT_FOUND
```

## No-send rule

This helper never presses Send and never submits ChatGPT.

Expected success evidence:

```text
PASS_CHROME_SELF_REPORT_ATTACHED_NO_SEND
operator_report_attached_to_composer: true
file_upload_attempted: true
open_button_clicked: true
enter_key_pressed: false
send_button_pressed: false
chatgpt_submit_performed: false
operator_report_uploaded: false
```

`operator_report_uploaded` stays false because the report is attached to the composer but the chat is not submitted.

## Safety boundary

This helper uses visible Chrome UI only through UI Automation. It does not use DOM automation, Selenium/WebDriver, Cloudflare/CAPTCHA bypass, raw conversation text logging, random clicks, unbounded loops, or generic all-browser abstractions.