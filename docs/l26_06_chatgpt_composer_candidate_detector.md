# L26.6 ChatGPT Composer Candidate Detector

This patch starts the input-surface discovery stage after L26.5A proved the targeted ChatGPT page is accessible.

## Scope

Allowed:

- target ChatGPT through the already accepted controlled navigation/classifier bridge;
- require `classification: accessible`;
- scan a bounded UIA tree for composer/input/send/attach candidates;
- write redacted metadata about candidates.

Forbidden:

- entering prompt text;
- pasting a prompt;
- sending/submitting a prompt;
- page clicking;
- downloads;
- CAPTCHA or Cloudflare bypass;
- Selenium/WebDriver or DOM automation;
- PatchOps `run-package`;
- git commit or push;
- full conversation text logging.

The first L26.6 acceptance only requires a completed diagnostic scan while the targeted ChatGPT page is accessible. `prompt_input_candidate_found` and `send_button_candidate_found` are reported as truth markers and will decide whether L26.7 can safely move to focus-only testing or must repair discovery first.
