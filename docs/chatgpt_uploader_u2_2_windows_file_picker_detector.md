# ChatGPT Uploader U2.2 Windows File-Picker Detector

U2.2 adds the reusable Windows file-picker detector and stale error-modal classifier.

## Scope

Added:

```text
patchops/chatgpt_uploader/windows_file_picker.py
scripts/run_uploader_detect_picker_live.py
tests/test_chatgpt_uploader_u2_2_windows_file_picker_current.py
```

## Detection signals

The detector looks for sanitized Windows dialog descriptors:

```text
#32770 class
Open / Choose / Select title signal
File-name-capable child controls
Open-button/shell child controls
known error modal titles/text
foreground/top-level ownership metadata
```

Raw dialog text is not written into evidence. Evidence records hashes, lengths, booleans, class counts, and classifier results.

## Safety boundary

U2.2 does not open the picker, write a file path, select a file, press Open, upload anything, or send a ChatGPT message.

The live detector can return:

```text
PASS_PICKER_DETECTED
PASS_ERROR_MODAL_DETECTED
PASS_NO_PICKER
BLOCKED_AMBIGUOUS_PICKERS
```

`BLOCKED_AMBIGUOUS_PICKERS` exits non-zero because selecting among multiple picker windows would be unsafe.

## Later patches

U2.3 will write the exact report path into an already-detected picker.
U2.4 will add the reliable picker-opening trigger.
U2.5 will attach the selected report and stop before send.
