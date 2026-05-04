# L26.8 ChatGPT Composer Dry-Run Text Gate

L26.7 proved that PatchOps can focus the real in-page ChatGPT composer without clicking or entering text. L26.8 performs the next smallest live proof: a harmless dry-run text cycle.

## Scope

Allowed:

- target ChatGPT through the accepted L26.5A/L26.6B/L26.7 chain;
- focus the in-page `prompt-textarea` composer;
- set a harmless dry-run marker on the clipboard;
- paste the marker with `Ctrl+V`;
- verify the marker through `Ctrl+A` / `Ctrl+C` copyback;
- clear the marker with `Backspace`;
- verify the marker is not left in the composer;
- restore the operator clipboard.

Forbidden:

- pressing Enter;
- submitting a ChatGPT prompt;
- clicking page controls;
- downloads;
- PatchOps `run-package`;
- CAPTCHA or Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- full conversation logging.

If the marker cannot be proven cleared, L26.8 fails and the operator must manually clear the composer before continuing.
