# L26.12F Soft-Composer Edge-Scoped Upload Menu Repair

L26.12E preserved the current-URL guard, but failed because composer focus was treated as a hard stop. It found a composer candidate while `has_keyboard_focus()` returned false, then stopped before creating the upload-safe copy.

L26.12F repairs the next layer:

- keep the current-URL guard and avoid refresh/navigation when the target chat is already loaded;
- create a closed upload-safe report copy before UI actions;
- treat composer focus as a soft diagnostic when a safe composer candidate exists;
- use the composer-plus button as the real upload precondition;
- search for upload-menu items only within Edge/ChatGPT UIA scope, not all desktop windows;
- reject OneDrive/status-like controls;
- upload the safe copy only;
- keep ChatGPT send forbidden.

Forbidden:

- pressing Enter in the ChatGPT composer;
- submitting a ChatGPT prompt;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full URLs, file paths, prompt text, file contents, or conversation text.
