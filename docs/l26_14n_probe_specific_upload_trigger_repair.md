# L26.14N Probe-specific Upload Trigger Repair

L26.14M produced an impossible live state:

- `upload_trigger_attempted: false`
- `file_dialog_found: false`
- `file_name_control_found: false`
- but `attachment_visible_after_open: true`

That means the attachment detector was reading stale/generic attachment evidence, not proof that the current probe file was uploaded.

L26.14N repairs the acceptance model and upload trigger:

1. create a unique probe file under `data/runtime/edge_upload_short`;
2. baseline the exact probe filename before triggering upload and require zero pre-existing signals;
3. open the picker through UIA attach/add/upload controls when available, with slash+Ctrl+U only as a fallback trigger;
4. require a real Windows file dialog to appear;
5. target only the File name Edit/ComboBox control;
6. verify the full probe path is in the File name control;
7. invoke Open or press Enter only after verification;
8. require the dialog to close and Edge to return;
9. require a new probe-specific attachment signal after Open, not a generic `.txt` or stale attachment signal;
10. do not submit/send;
11. do not publish a canonical report;
12. do not click response candidates;
13. do not use DOM/WebDriver/Selenium or log prompt/conversation/file contents.

If this passes, the next patch can attempt strict upload + submit using the probe-specific primitive.
