# L26.2 Normal Edge Window Inventory + Selected Attach Proof

This patch advances the L26 normal Microsoft Edge + pywinauto stream from dependency/first attach proof into a reusable window-discovery layer.

## Scope

Allowed:

- discover running normal Microsoft Edge processes;
- inspect top-level UIA windows;
- build a redacted Edge window inventory;
- select the best candidate deterministically;
- attach/focus the selected normal Edge window;
- write a bounded selected-window top-level UIA summary.

Forbidden:

- Selenium/WebDriver;
- URL navigation;
- ChatGPT-specific probing;
- prompt paste/send;
- CAPTCHA or Cloudflare bypass;
- download clicking;
- archive extraction;
- PatchOps `run-package`;
- git commit or push.

## Live proof command

```powershell
py scripts/run_l26_02_edge_window_inventory_live_proof.py --output-dir data/runtime/edge_rpa/l26_02_live --start-if-missing
```

Expected markers:

```text
edge_window_inventory_written:true
selected_window_found:true
normal_edge_attached:true
edge_window_title_read:true
edge_focused:true
uia_top_level_tree_dumped:true
webdriver_used:false
browser_navigation_performed:false
download_click_performed:false
run_package_invoked:false
```
