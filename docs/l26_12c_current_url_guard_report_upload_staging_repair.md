# L26.12C Current-URL Guard Report Upload Staging Repair

L26.12B still failed before report staging. The operator observed that the requested project chat was already loaded in the same Microsoft Edge tab and that refreshing/re-navigating the page can disturb the UI state.

L26.12C adds a current-URL guard:

- read the active Edge URL by focusing the address bar and copying it;
- canonicalize the current URL and target URL;
- if they match, skip navigation/refresh entirely;
- verify the in-page composer directly;
- discover the latest local PatchOps `.txt` report;
- click `composer-plus-btn`;
- find the Upload files menu item;
- select the report in the Windows file picker;
- verify staged attachment evidence;
- record only hashes, booleans, sizes, and redacted paths.

Forbidden:

- refreshing/navigating when the target chat is already loaded;
- pressing Enter in the ChatGPT composer;
- submitting a ChatGPT prompt;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full URLs, file paths, prompt text, file contents, or conversation text.

If upload menu discovery still fails, L26.12C writes a bounded redacted upload-menu inventory so the next repair can target the actual current UI labels.
