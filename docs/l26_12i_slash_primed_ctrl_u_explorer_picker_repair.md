# L26.12I Slash-Primed Ctrl+U Explorer Picker Repair

The operator observed that L26.12H did open the Windows file browser, but the program stopped because the previous detector only looked for a narrow file-dialog shape.

The operator also clarified the faster working sequence:

1. type `/` in the ChatGPT composer;
2. press the plus button;
3. press Ctrl+U;
4. use the OS file picker / Explorer-style picker;
5. enter the local `.txt` report path;
6. press Enter in the OS picker;
7. wait for the attachment to stage.

L26.12I implements that sequence:

- keep the current-URL/no-refresh guard;
- create a closed upload-safe report copy outside OneDrive;
- verify a safe composer candidate exists;
- type `/` in the composer;
- click `composer-plus-btn`;
- send Ctrl+U;
- detect either a classic Open dialog or Explorer-style picker window;
- paste the upload-safe `.txt` path;
- press Enter only in the OS picker;
- verify staged attachment evidence;
- keep ChatGPT final submit/send forbidden.

Forbidden:

- pressing Enter in the ChatGPT composer to submit;
- activating the send button;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full URLs, file paths, prompt text, file contents, or conversation text.
