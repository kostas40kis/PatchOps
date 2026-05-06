# U0.6 — ChatGPT uploader clipboard set/verify

Patch `u0_06_chatgpt_uploader_clipboard_set_verify` adds the bounded clipboard layer for PatchOps Co-Pilot.

## Scope

Allowed:

```text
build or receive a PATCHOPS_LLM_PASTEBACK text payload
set clipboard text
read clipboard text back
verify sha256 and exact text equality
optionally restore the prior clipboard contents
write local JSON/TXT evidence
```

Forbidden in this patch:

```text
browser focus
Edge control
ChatGPT composer interaction
paste into ChatGPT
file upload
send/submit
Selenium/WebDriver
DOM automation
CAPTCHA/Cloudflare bypass
```

## Safety behavior

The implementation avoids requiring `pyperclip`. On Windows it can use
PowerShell `Set-Clipboard` / `Get-Clipboard`; tests use a deterministic memory
backend. Previous clipboard contents are never written to evidence.

The runner defaults to preserving existing clipboard contents after verifying
the U0.6 smoke payload. Future uploader patches can use `--leave-on-clipboard`
when the paste phase is explicitly allowed.
