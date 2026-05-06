# U0.7 ChatGPT uploader Edge focus/target guard

U0.7 adds the conservative normal Microsoft Edge focus/target guard used by
the ChatGPT uploader stream.

## Purpose

This patch proves that uploader code can decide whether a configured
ChatGPT target is present in a normal Edge window before later paste phases.

## Default proof mode

The default validation path uses a fake adapter. It does not require Edge to
be open and does not touch the browser.

```text
provider: fake
browser_started:false
browser_focused:false unless explicitly allowed against the selected adapter
file_upload_attempted:false
chatgpt_submit_performed:false
selenium_used:false
webdriver_used:false
```

## Real Edge gate

A real pywinauto adapter is present only behind `--allow-real-edge`. Without
that flag the pywinauto provider returns `BLOCKED_REAL_EDGE_NOT_ALLOWED`.

The real adapter is intentionally limited to top-level normal Edge window
enumeration and optional focus. It does not browse the DOM, read conversation
text, paste text, upload files, click random controls, or submit messages.

## Boundary

U0.7 may:

```text
validate https://chatgpt.com target URLs
classify fake or real Edge target readiness
optionally focus a selected window only when explicitly allowed
write local JSON/TXT evidence
```

U0.7 must not:

```text
paste into ChatGPT
upload files
send or submit messages
use Selenium or WebDriver
bypass CAPTCHA or Cloudflare
read/log conversation text
```
