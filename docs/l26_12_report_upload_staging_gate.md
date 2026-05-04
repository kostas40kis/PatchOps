# L26.12 Report Upload Staging Gate

L26.11 proved the report-upload prerequisites in dry-run mode: requested-chat composer accessibility, a local text report candidate, and a safe in-page attach/upload control.

L26.12 is the first explicit upload gate. It requires `--allow-report-upload` in the live validation command.

Allowed:

- target the requested project chat URL;
- run the accepted L26.11 dry-run precondition;
- locate the in-page attach/upload control;
- click the attach control;
- select the latest local PatchOps `.txt` report in the Windows file picker;
- verify that the file appears staged in ChatGPT UIA evidence;
- record only hashes, sizes, booleans, and redacted filenames/paths.

Forbidden:

- pressing Enter;
- submitting a ChatGPT prompt;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full prompt text, file contents, or conversation text.

If L26.12 passes, a later patch can add a separate explicit send/upload-finalization gate. L26.12 must not submit the message.
