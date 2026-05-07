# ChatGPT Uploader Chrome-Only Architecture

## Purpose

This document defines the architecture contract for the Chrome-only PatchOps uploader stream.

The current uploader stream is intentionally narrow: build Chrome upload support now, prove it under explicit local evidence, and do not introduce a generic all-browser layer.

## Active lane contract

Chrome is the only active browser lane.

No all-browser abstraction.

No browser registry.

No auto-detect-everything behavior.

A second browser may be added later only by explicit decision.

The second browser, if chosen later, must be implemented as a separate explicit lane with its own browser-specific modules, tests, scripts, and documentation. It must not be introduced by creating a generic browser adapter framework.

## Truth boundary

PatchOps remains truth. Chrome is only the delivery bridge.

```text
Downloader creates truth.
PatchOps validates/runs truth.
Canonical report records truth.
Uploader transports truth.
Chrome does not become truth.
```

The uploader must not claim success because a browser surface appears to show something unless local evidence and explicit uploader verification support that claim.

## In scope for the Chrome stream

The Chrome stream may eventually support this bounded live path:

```text
resolve canonical report
-> verify Chrome target readiness
-> focus normal visible Chrome ChatGPT window
-> open the Windows file picker from ChatGPT
-> write exact canonical report path into picker
-> press Enter/Open inside the picker
-> verify attachment is visible in ChatGPT
-> stop before send unless an explicit send gate is later invoked
```

## Out of scope

The Chrome stream must not add or depend on:

```text
all-browser abstraction
generic browser adapter framework
auto-detect all installed browsers
browser registry
browser plugin system
ChromeDriver
Selenium
WebDriver
browser DOM automation
CAPTCHA bypass
Cloudflare bypass
hidden browser automation
random clicking
unbounded upload loops
unbounded send loops
```

The following files must not be introduced under `patchops/chatgpt_uploader/` for this Chrome lane:

```text
browser_factory.py
browser_adapter.py
browser_registry.py
all_browsers.py
generic_browser.py
```

## Browser-specific module shape

Chrome-specific work belongs in explicit Chrome modules, for example:

```text
patchops/chatgpt_uploader/chrome_paths.py
patchops/chatgpt_uploader/chrome_target.py
patchops/chatgpt_uploader/chrome_focus_guard.py
patchops/chatgpt_uploader/chrome_picker_trigger.py
patchops/chatgpt_uploader/chrome_attachment_verifier.py
patchops/chatgpt_uploader/chrome_recovery.py
patchops/chatgpt_uploader/chrome_failure_labels.py
```

When a second browser is explicitly chosen later, it should use a parallel browser-specific lane rather than a shared browser registry.

## Safety flags

Every patch in this stream must preserve the phase-appropriate safety flags.

For this architecture-contract patch:

```text
selenium_used:false
webdriver_used:false
browser_dom_automation_used:false
cloudflare_bypass_attempted:false
captcha_bypass_attempted:false
conversation_text_logged:false
random_page_click_performed:false
chatgpt_submit_performed:false
file_upload_attempted:false
live_browser_used:false
canonical_report_found:false
```

`canonical_report_found` may become true only in later report-resolution or proof phases that actually resolve and verify a canonical local PatchOps report.

## Patch 1 boundary

Patch 1 is local only.

Allowed:

```text
docs
tests
local evidence
```

Forbidden:

```text
live browser
file upload
ChatGPT send/submit
Selenium/WebDriver
browser DOM automation
Cloudflare/CAPTCHA bypass
random page clicking
generic all-browser abstractions
```

## Acceptance for this contract patch

This patch is accepted only when:

```text
PatchOps check PASS
PatchOps inspect PASS
PatchOps plan PASS
PatchOps apply PASS
focused tests PASS
Desktop operator report PASS
```

No outer PASS may be reported if any inner PatchOps command failed.