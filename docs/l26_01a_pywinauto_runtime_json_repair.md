# L26.1A Pywinauto Runtime + JSON Evidence Repair

This patch repairs the first L26.1 attempt.

The failed run proved that `pywinauto` could be installed for the default `py` launcher, but PatchOps apply still failed before a live proof JSON file was found. L26.1A makes the proof stricter and more diagnosable:

- install/check `pywinauto` in the PatchOps profile runtime before apply;
- run manifest validation through the profile runtime;
- always write `normal_edge_l26_01_probe_result.json`, even on import/UIA/window discovery failure;
- keep the L26.1 live browser boundary unchanged.

## Still forbidden

- Selenium/WebDriver;
- URL navigation;
- ChatGPT prompt paste/send;
- CAPTCHA or Cloudflare bypass;
- download clicking;
- archive extraction;
- PatchOps `run-package`;
- git commit or push.
