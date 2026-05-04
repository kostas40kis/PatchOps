# L26.5 ChatGPT Accessibility / Session Classifier

This patch classifies the current ChatGPT session state in normal Microsoft Edge using pywinauto/UI Automation.

## Scope

Allowed:

- attach to the current normal Microsoft Edge window;
- focus it;
- read the window title as bounded/redacted evidence;
- scan a bounded UIA tree for challenge/login/accessibility indicators;
- classify the session as one of:
  - `accessible`
  - `login_required`
  - `human_challenge_required`
  - `unknown`
- stop classification when challenge/login indicators are found.

Forbidden:

- Selenium/WebDriver;
- DOM automation;
- URL navigation;
- ChatGPT prompt paste/send;
- page clicking;
- CAPTCHA or Cloudflare bypass;
- downloads;
- archive extraction;
- PatchOps `run-package`;
- git commit or push;
- full conversation text logging.

A challenge state is a successful classifier result, not a bypass:

```text
human_challenge_required:true
loop_stopped:true
cloudflare_bypass_attempted:false
```

L26.6 may only proceed to input detection if L26.5 reports `classification:accessible` or if the operator deliberately chooses another diagnostic path.
