# L26.12G Upload-Menu Candidate Retry/Fingerprint Repair

L26.12F proved most of the upload stack:

- current URL matched the requested chat;
- navigation was skipped;
- composer candidate and focus were valid;
- source report was found;
- upload-safe copy was created, closed, outside OneDrive, and hash-matched;
- composer plus button was clicked;
- an Edge-scoped upload candidate was found and clicked;
- no ChatGPT send happened.

The remaining failure was that the clicked candidate did not open the Windows file picker. L26.12G stops relying on a single guessed candidate.

L26.12G:

- keeps the current-URL/no-refresh guard;
- keeps the upload-safe copy path;
- opens the composer-plus menu;
- collects multiple Edge-scoped upload candidates as redacted fingerprints only;
- tries candidates in score order until a real Windows file picker opens;
- records failed and successful candidate fingerprints without logging labels or conversation text;
- selects the safe report copy;
- verifies staged attachment;
- keeps ChatGPT send forbidden.

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
