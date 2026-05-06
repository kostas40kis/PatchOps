# ChatGPT Uploader U2.4A Missing pywinauto Guard

U2.4A repairs the U2.4 live failure where the picker opener crashed when `pywinauto` was not installed in the `py` runtime.

## Rule

Missing `pywinauto` must be a controlled blocked state:

```text
BLOCKED_MISSING_PYWINAUTO
```

It must write JSON/TXT evidence and keep all upload/send safety flags false.

## What U2.4A does not do

- does not install dependencies;
- does not open the picker when the dependency is missing;
- does not select a file;
- does not write a file path;
- does not press Open/Enter;
- does not confirm attachment;
- does not send a ChatGPT message.

## Next step

After U2.4A is accepted, either:

1. install `pywinauto` in the runtime used by `py`, then rerun the U2.4 live opener; or
2. add a non-pywinauto Win32/UI Automation trigger path in a later patch.
