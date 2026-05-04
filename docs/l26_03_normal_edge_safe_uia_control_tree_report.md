# L26.3 Normal Edge Safe UIA Control Tree Report

This patch advances the L26 normal Microsoft Edge + pywinauto stream from selected-window attach/focus into a bounded safe UIA diagnostic report.

## Scope

Allowed:

- attach to the selected normal Microsoft Edge window;
- focus it;
- walk a bounded UIA tree;
- redact unsafe control names;
- record control type/class/automation id/rectangle metadata;
- summarize visible control types;
- report address-bar and input-like candidate hints.

Forbidden:

- reading or storing full conversation text;
- Selenium/WebDriver;
- URL navigation;
- ChatGPT-specific prompt paste/send;
- clicking page controls;
- CAPTCHA or Cloudflare bypass;
- download clicking;
- archive extraction;
- PatchOps `run-package`;
- git commit or push.

## Acceptance markers

```text
uia_control_tree_dumped:true
control_count_reported:true
control_type_summary_written:true
conversation_text_logged:false
full_conversation_text_logged:false
browser_navigation_performed:false
download_click_performed:false
run_package_invoked:false
pasteback_or_send_performed:false
```

`address_bar_candidate_found` is reported but not required to be true yet, because Chromium/Edge UIA exposure can vary by focus state and version. L26.4 will handle navigation only after this diagnostic layer is accepted.
