# L26.12A Menu-Aware Report Upload Staging Repair

L26.12 failed because the first attach attempt treated `composer-plus-btn` as if it opened the Windows file picker directly. In the current ChatGPT UI, that button opens an attachment menu first.

L26.12A repairs the flow:

- run the accepted L26.11 dry-run precondition;
- find the safe in-page `composer-plus-btn` button;
- click the plus/menu button;
- find and click the Upload files menu item;
- use the Windows file picker to select the latest local PatchOps `.txt` report;
- verify the selected file appears staged in ChatGPT UIA evidence;
- record only hashes, sizes, booleans, and redacted filenames/paths.

Forbidden:

- pressing Enter in the ChatGPT composer;
- submitting a ChatGPT prompt;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full prompt text, file contents, or conversation text.

File-picker confirmation is allowed as part of report attachment staging. ChatGPT send remains forbidden.
