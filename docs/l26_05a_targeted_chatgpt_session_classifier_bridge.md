# L26.5A Targeted ChatGPT Session Classifier Bridge

L26.5 passed as a classifier, but the live selected Edge title was not ChatGPT. It returned `classification:unknown`, which is a valid classifier result but not enough to advance to input detection.

This repair/bridge patch first uses the already-accepted L26.4 controlled navigation primitive to target `https://chatgpt.com/`, then immediately runs the L26.5 classifier against the current normal Edge window.

## Scope

Allowed:

- use controlled navigation from L26.4: focus Edge, Ctrl+L, controlled clipboard URL paste, Enter;
- run the L26.5 classifier after navigation;
- accept only a known state:
  - `accessible`
  - `login_required`
  - `human_challenge_required`
- stop on login/challenge states.

Forbidden:

- Selenium/WebDriver;
- DOM automation;
- ChatGPT prompt paste/send;
- page clicking;
- CAPTCHA or Cloudflare bypass;
- downloads;
- archive extraction;
- PatchOps `run-package`;
- git commit or push;
- full conversation text logging.

Unknown is rejected after targeting because L26.6 input detection should not start until the target page has a known session state.
