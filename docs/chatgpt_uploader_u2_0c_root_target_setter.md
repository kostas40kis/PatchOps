# ChatGPT Uploader U2.0C Root Target Setter

U2.0C allows the operator to explicitly configure the uploader target as the ChatGPT root page:

```text
https://chatgpt.com/
```

This is needed when the operator already has a normal Microsoft Edge tab open at ChatGPT and wants the uploader to use that page rather than a specific conversation URL.

## Rules

- `https://chatgpt.com/` and `https://chatgpt.com` are valid target URLs.
- The normalized stored value is `https://chatgpt.com/`.
- Upload and send remain disabled by default.
- Operator-set mode remains focus-only and must not open or navigate to a URL.
- The live proof may focus an already-open normal Edge ChatGPT tab, but must not launch or refresh it.

## Manual command

```powershell
Set-Location C:\dev\patchops
py scripts/set_chatgpt_copilot_target.py --repo-root C:\dev\patchops --target-url "https://chatgpt.com/" --mode operator_set
py scripts/show_chatgpt_copilot_target.py --repo-root C:\dev\patchops
```

## Safety boundary

No upload, no file picker, no attachment selection, no send/submit, no Selenium/WebDriver, no browser DOM automation, no random clicking, no conversation text logging.
