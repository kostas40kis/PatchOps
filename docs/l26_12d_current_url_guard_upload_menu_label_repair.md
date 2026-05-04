# L26.12D Current-URL Guard Upload-Menu Label Repair

L26.12C successfully proved the operator-requested current-URL behavior:

- current URL was observed;
- current URL matched the requested project chat;
- navigation was skipped;
- navigation was not attempted.

The remaining failure was upload-menu discovery. L26.12C also lost partial state in the final failure payload, making successful intermediate steps harder to diagnose.

L26.12D repairs that layer:

- keep the current-URL guard and skip refresh/navigation when the target chat is already loaded;
- treat skipped navigation as target page ready;
- press Escape after reading the address bar so focus can return to the page;
- retry composer focus for a short bounded window;
- preserve partial evidence on failure;
- broaden upload-menu label scoring for current ChatGPT labels like Upload, files, photos, computer, local, browse, and attach;
- write a redacted upload-menu inventory whenever menu discovery fails.

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
