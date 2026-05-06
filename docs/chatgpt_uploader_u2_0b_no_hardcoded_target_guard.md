# ChatGPT Uploader U2.0B No-Hardcoded-Target Guard

U2.0B repairs a process safety issue discovered during U2.0A: a patch script must not silently set the uploader target to a hardcoded ChatGPT URL, and operator-set preflight must not open the configured URL automatically.

## Rules added

- Patch scripts must not seed or overwrite `data/config/chatgpt_copilot_target.json` unless the operator explicitly provides a target URL.
- `operator_set` mode is focus-only. It may focus an already-open normal Edge ChatGPT window, but it must not launch/open the configured URL.
- `launch_target` mode requires two explicit flags before opening the configured URL:
  - `--allow-launch-target`
  - `--allow-open-configured-url`
- `show_chatgpt_copilot_target.py` reports the redacted target and hash without printing the raw URL.

## Manual target setting

Use this only when the operator intentionally wants to set or replace the target:

```powershell
Set-Location C:\dev\patchops
py scripts/set_chatgpt_copilot_target.py --repo-root C:\dev\patchops --target-url "PASTE_THE_CHATGPT_TARGET_URL_HERE" --mode operator_set
```

Check the configured target without exposing the raw URL:

```powershell
py scripts/show_chatgpt_copilot_target.py --repo-root C:\dev\patchops
```

## Safety boundary

No upload, no file picker, no attachment selection, no send/submit, no Selenium/WebDriver, no browser DOM automation, no random clicking, no conversation text logging.
