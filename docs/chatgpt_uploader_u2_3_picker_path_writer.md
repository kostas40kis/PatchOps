# ChatGPT Uploader U2.3 Picker Path Writer

U2.3 adds the exact-report path writer for an already-open Windows file picker.

## Scope

Added:

```text
patchops/chatgpt_uploader/picker_path_writer.py
scripts/run_uploader_write_report_path_to_picker.py
tests/test_chatgpt_uploader_u2_3_picker_path_writer_current.py
```

## Rules

- Resolve the exact report path first.
- Detect Windows file picker state.
- If no picker is open, return `PASS_NO_PICKER_NO_WRITE`.
- If multiple pickers are open, block as ambiguous.
- If exactly one picker is open, find a visible enabled filename control and write the exact report path.
- Do not press Open or Enter.
- Do not claim upload success.
- Do not send a ChatGPT message.

## Safety boundary

No picker opening, no global Desktop/File Explorer keystrokes, no Open button press, no file-selected claim, no upload success claim, no ChatGPT send/submit, no Selenium/WebDriver, no DOM automation, no random clicking, no conversation text logging.

Later patches:

- U2.4 opens the picker reliably from ChatGPT.
- U2.5 writes path + presses Open + confirms attachment while still not sending.
