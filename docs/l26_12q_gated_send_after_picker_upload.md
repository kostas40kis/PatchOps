# L26.12Q Gated Send After Picker Upload

L26.12P accepted the browser upload milestone: local Desktop report, closed safe copy, slash + Ctrl+U, foreground OS picker, full quoted path, picker confirmation, no Ctrl+L, and no forbidden browser automation.

L26.12Q adds the next gated step: click ChatGPT Send after the picker-confirmed upload succeeds.

The send step is only allowed when `--allow-chatgpt-submit` is present. The generated operator script passes that flag through its `AllowChatGptSubmit` parameter.

Acceptance requires:

- L26.12P upload precondition passes;
- send/submit button is found through Edge UIA, not DOM/WebDriver;
- send button is clicked;
- ChatGPT submit is recorded as performed;
- no Ctrl+L, no downloads, no run-package, no Selenium/WebDriver, no DOM automation, and no conversation/prompt/file-content logging.
