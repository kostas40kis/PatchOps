# L26.4 Normal Edge Controlled Navigation Proof

This patch advances the L26 normal Microsoft Edge + pywinauto stream into the first gated navigation proof.

## Scope

Allowed:

- focus a selected normal Microsoft Edge window;
- send `Ctrl+L`;
- place a controlled HTTP/HTTPS URL on the clipboard;
- verify the clipboard before paste when possible;
- paste the URL;
- press Enter;
- observe bounded title/UIA state after navigation;
- classify challenge/login indicators as stop states.

Forbidden:

- Selenium/WebDriver;
- DOM automation;
- ChatGPT prompt paste/send;
- page clicking;
- CAPTCHA or Cloudflare bypass;
- downloads;
- archive extraction;
- PatchOps `run-package`;
- git commit or push.

If a human challenge is observed, PatchOps must stop with:

```text
human_challenge_required:true
loop_stopped:true
cloudflare_bypass_attempted:false
```

## Live proof command

```powershell
py scripts/run_l26_04_edge_navigation_live_proof.py --output-dir data/runtime/edge_rpa/l26_04_live --target-url https://chatgpt.com/ --start-if-missing
```
