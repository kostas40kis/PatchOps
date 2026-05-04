# L26.9 ChatGPT Prompt Builder Paste Gate

L26.8 proved a harmless dry-run paste/observe/clear cycle in the real in-page ChatGPT composer. L26.9 upgrades the payload from a marker to a bounded next-patch prompt while keeping the same no-send safety boundary.

## Scope

Allowed:

- build a deterministic bounded next-patch prompt from accepted local frontier evidence;
- record prompt hash and length only;
- require an explicit `--allow-paste` gate;
- focus the accepted in-page composer;
- paste the prompt;
- verify the paste by copyback hash;
- clear the prompt;
- restore the clipboard.

Forbidden:

- pressing Enter;
- submitting the prompt;
- clicking page controls;
- downloads;
- PatchOps `run-package`;
- CAPTCHA or Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging the full prompt text or full conversation text.

If the prompt cannot be proven cleared, L26.9 fails and the operator must manually clear the composer before continuing.
