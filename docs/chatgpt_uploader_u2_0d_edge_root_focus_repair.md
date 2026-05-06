# ChatGPT Uploader U2.0D Edge Root Focus Repair

U2.0D repairs the focus-only live preflight for a root ChatGPT target:

```text
https://chatgpt.com/
```

The previous preflight required a window title containing `ChatGPT`. In practice, a root ChatGPT tab in normal Microsoft Edge may not expose a stable ChatGPT title through the top-level UIA window. U2.0D keeps the strong title-based match first, but adds a safe fallback for root targets only.

## Selection policy

1. Prefer a normal Edge window whose title indicates ChatGPT.
2. If the target is exactly the ChatGPT root and exactly one visible/enabled normal Edge window is available, use that single Edge window as a focus candidate.
3. If multiple Edge windows are available and none exposes a ChatGPT title, block as ambiguous.

## Safety boundary

No upload, no file picker, no attachment selection, no send/submit, no Selenium/WebDriver, no browser DOM automation, no random clicking, no conversation text logging, no automatic URL launch.
