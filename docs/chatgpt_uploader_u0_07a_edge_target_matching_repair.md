# U0.7A ChatGPT uploader Edge target matching repair

U0.7A repairs the first real Edge diagnostic result. The live diagnostic proved that pywinauto could enumerate browser windows and found a real normal Edge window titled `ChatGPT - Personal - Microsoft Edge`, but the U0.7 matcher still returned `BLOCKED_TARGET_NOT_FOUND` because UIA did not expose the URL and the title-only score was too weak.

## What changed

- Adds bounded candidate diagnostics to normal U0.7 JSON/TXT evidence.
- Adds safe title-based matching for normal Microsoft Edge ChatGPT windows when URL evidence is unavailable.
- Distinguishes normal Edge from other Chromium windows such as Opera and Brave using process name and/or title evidence.
- Handles zero-width title characters such as `Microsoft\u200b Edge`.
- Blocks ambiguous states when multiple normal Edge ChatGPT windows match.

## Safety boundary

This patch still does not:

```text
paste into ChatGPT
upload files
send or submit messages
use Selenium/WebDriver
use DOM automation
bypass CAPTCHA or Cloudflare
log conversation body text
click random UI controls
```

U0.7A only repairs target identification and evidence. U0.8 paste-to-composer dry run should wait until this repair is accepted.
