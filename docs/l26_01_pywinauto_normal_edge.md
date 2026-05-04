# L26.1 Pywinauto Normal Edge Dependency + Attach Doctor

This patch starts the L26 normal Microsoft Edge + pywinauto/UI Automation RPA stream.

## Scope

Allowed in this patch:

- import `pywinauto` lazily;
- prove UIA backend construction;
- detect a normal Microsoft Edge process/window;
- optionally start normal Edge if no Edge process exists;
- focus the Edge window;
- write a bounded, redacted top-level UIA control summary;
- emit JSON acceptance evidence.

Forbidden in this patch:

- Selenium/WebDriver;
- URL navigation;
- ChatGPT prompt paste/send;
- CAPTCHA or Cloudflare bypass;
- download clicking;
- archive extraction;
- PatchOps `run-package`;
- git commit or push.

## Live proof command

```powershell
py scripts/run_l26_01_pywinauto_edge_live_proof.py --output-dir data/runtime/edge_rpa/l26_01_live --start-if-missing
```

The command must run against a real normal Microsoft Edge window and must report:

```text
pywinauto_imported:true
uia_backend_available:true
normal_edge_attached:true OR normal_edge_started:true
edge_window_title_read:true
edge_focused:true
uia_control_tree_dumped:true
webdriver_used:false
cloudflare_bypass_attempted:false
browser_navigation_performed:false
download_click_performed:false
run_package_invoked:false
pasteback_or_send_performed:false
```
