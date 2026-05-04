# L26.12H Plus-Menu Ctrl+U Upload Shortcut Repair

The operator discovered the missing upload primitive: after pressing ChatGPT's plus button, Ctrl+U opens the operating-system file picker for photos/files.

L26.12G proved the surrounding stack but still failed to open the file picker by clicking guessed Edge-scoped menu candidates:

- current URL matched the requested chat;
- navigation was skipped;
- composer focus was verified;
- upload-safe report copy was created and closed;
- plus button was clicked;
- one Edge-scoped candidate was tried;
- no file picker opened.

L26.12H replaces candidate guessing with the shortcut:

- keep the current-URL/no-refresh guard;
- create a closed upload-safe report copy outside OneDrive;
- verify a safe composer candidate exists;
- click `composer-plus-btn`;
- send Ctrl+U to open the OS file picker;
- select the safe `.txt` report copy;
- verify staged attachment evidence;
- keep ChatGPT send forbidden.

Allowed Enter use is limited to the Windows file picker confirmation after a file path is entered. ChatGPT submit Enter remains forbidden in this patch.

Forbidden:

- pressing Enter in the ChatGPT composer to submit;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full URLs, file paths, prompt text, file contents, or conversation text.
