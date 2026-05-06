# ChatGPT Uploader U2.4B Runtime Dependency Preflight

U2.4B prepares the exact Python runtime used by the uploader scripts for the verified UIA upload trigger.

The previous accepted state is U2.4A, where missing `pywinauto` became a controlled evidence-backed block instead of a traceback.

## What U2.4B adds

```text
patchops/chatgpt_uploader/runtime_dependency.py
scripts/ensure_chatgpt_uploader_runtime_deps.py
```

The helper records:

```text
python executable
python version
package/import name
available before install
whether install was attempted
pip exit code
available after install
JSON/TXT evidence paths
```

## Safety boundary

This patch may run `python -m pip install pywinauto` only when explicitly called with `--allow-install`.

It must not:

```text
select a file
write a report path
press Open/Enter
confirm attachment
claim upload success
send/submit
use Selenium/WebDriver
use browser DOM automation
```

## After dependency passes

The live script reruns U2.4 picker open/close proof:

```text
scripts/run_uploader_open_picker_live.py --allow-open-picker --attempts 5
```

If dependency installation fails because of network, permissions, or pip issues, the patch must write controlled evidence and stop safely.
