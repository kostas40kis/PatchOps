# ChatGPT Uploader U2.0 Target Config and Live Harness Base

U2.0 creates the durable target configuration and reusable evidence surface for the PatchOps Co-Pilot uploader.

## Scope

Added:

- `patchops/chatgpt_uploader/config.py`
- `patchops/chatgpt_uploader/evidence.py`
- `patchops/chatgpt_uploader/edge_target.py`
- `scripts/set_chatgpt_copilot_target.py`
- `scripts/run_uploader_edge_preflight.py`

## Boundary

Allowed:

- store and validate a configured ChatGPT target URL;
- store the URL hash and a redacted target display;
- write JSON and TXT uploader evidence;
- optionally focus or launch normal Microsoft Edge at the configured URL;
- record selected target window details without raw conversation text.

Forbidden:

- Selenium;
- WebDriver;
- browser DOM automation;
- upload picker opening;
- file selection;
- attachment confirmation;
- ChatGPT send/submit;
- random page clicking;
- full conversation text logging.

## Live proof command

```powershell
py scripts/set_chatgpt_copilot_target.py --repo-root C:\dev\patchops --target-url "<chatgpt target url>"
py scripts/run_uploader_edge_preflight.py --repo-root C:\dev\patchops --allow-real-edge --allow-launch-target
```

Expected safe result:

```text
PATCHOPS_UPLOADER_EDGE_PREFLIGHT_STATUS: PASS
FILE_UPLOAD_ATTEMPTED: false
CHATGPT_SUBMIT_PERFORMED: false
```

If Edge cannot be focused, the command must still write JSON and TXT evidence and return `FAIL_OR_BLOCKED`.
