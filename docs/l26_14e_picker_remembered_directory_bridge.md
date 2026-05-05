# L26.14E Picker Remembered-Directory Bridge

L26.14D made acceptance stricter by requiring visible attachment evidence, but it regressed the file-picker path behavior. The picker opened a remembered directory such as:

`C:\dev\patchops\data\runtime\edge_upload_short\s_20260504_172603`

L26.14E repairs that without weakening the visible attachment gate:

1. resolve a remembered picker directory, preferring the observed directory if it exists;
2. place the upload-safe canonical copy directly in that directory;
3. run the visible attachment upload gate;
4. require the uploaded safe copy parent to match the bridge directory;
5. require visible attachment evidence before submit;
6. submit and observe idle/readiness;
7. run the selector dry-run;
8. perform no response-candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This should avoid the picker-current-directory crash while still failing closed if the attachment is not visibly present in ChatGPT.
