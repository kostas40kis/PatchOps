# L26.7 ChatGPT Composer Focus-Only Probe

L26.6B proved the top accepted composer candidate is in-page and not the Microsoft Edge omnibox. L26.7 performs the next smallest safe step: focus-only probing.

## Scope

Allowed:

- target ChatGPT through the accepted L26.5A/L26.6B chain;
- locate the in-page composer candidate;
- call UIA `set_focus()` on the candidate;
- observe whether UIA reports keyboard focus.

Forbidden:

- entering text;
- setting a prompt on the clipboard;
- sending keyboard text;
- submitting a prompt;
- clicking page controls;
- downloads;
- CAPTCHA or Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- PatchOps `run-package`;
- git commit or push;
- full conversation text logging.

If focus verification fails, the next repair should improve focus observation or use a safer explicit focus handoff before any text-entry patch is attempted.
