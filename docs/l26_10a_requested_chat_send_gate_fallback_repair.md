# L26.10A Requested-Chat Send Gate Fallback Repair

L26.10 correctly kept the send path disabled, but failed its live proof because the requested project chat URL returned `classification: unknown` before the paste cycle could begin.

L26.10A repairs the targeting layer without weakening the safety boundary:

- target the exact requested project chat URL;
- use controlled navigation to reach the chat URL;
- if the older classifier cannot classify the requested chat, use a direct in-page composer fallback based on the already accepted `prompt-textarea` / ProseMirror focus detector;
- paste, verify, and clear the bounded prompt;
- prove the send gate remains disabled by default.

Forbidden:

- pressing Enter;
- submitting a ChatGPT prompt;
- clicking page controls;
- downloads;
- PatchOps `run-package`;
- CAPTCHA or Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- git commit or push;
- logging full prompt text or conversation text.
