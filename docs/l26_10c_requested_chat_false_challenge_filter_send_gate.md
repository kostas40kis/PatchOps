# L26.10C Requested-Chat False-Positive Challenge Filter Send Gate

L26.10B passed diagnostics and found the real requested-chat composer (`prompt-textarea`, `ProseMirror`, `Chat with ChatGPT`) plus attach controls, but it also classified the run as `human_challenge_required` because transcript/code text included challenge-related safety field names such as `cloudflare_bypass_attempted`.

L26.10C repairs that false positive:

- if a safe in-page composer is present and focusable, transcript/code-like challenge terms do not block the requested-chat path;
- real challenge is only blocking when no safe composer can be reached;
- the patch then performs the accepted paste/copyback/clear proof;
- send remains disabled by default.

Forbidden:

- report upload;
- file attach;
- pressing Enter;
- submitting a ChatGPT prompt;
- page clicking;
- downloads;
- PatchOps `run-package`;
- CAPTCHA/Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full prompt text or conversation text.

If L26.10C passes, the next patch can start a report-upload dry-run gate, still disabled by default.
