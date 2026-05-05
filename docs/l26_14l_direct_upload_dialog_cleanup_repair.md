# L26.14L Direct Upload Dialog Cleanup Repair

L26.14K improved the upload primitive: it opened the file dialog, entered the full path, invoked Open, Edge was still present, and the attachment detector saw a staged attachment with positive signals.

L26.14K failed only because `file_dialog_closed_after_open` stayed false. That means the next repair should not go back to folder seeding or submit/canonical layers. It should clean up stale file-dialog/menu state after attachment staging.

L26.14L:

1. keeps the latest canonical pointer at the known-good L26.14F PASS report;
2. creates a tiny upload probe file;
3. opens the ChatGPT upload picker from the existing Edge session;
4. enters the full probe path into the Windows file dialog;
5. confirms attachment staging using UIA signals;
6. attempts to close any stale file dialog/menu with Esc/Alt+F4/Esc without submitting a chat message;
7. requires Edge to remain present;
8. requires no file dialog to remain after cleanup;
9. requires the attachment to remain visible after cleanup;
10. does not submit/send;
11. does not publish canonical evidence;
12. does not click response candidates;
13. does not use DOM/WebDriver/Selenium or log prompt/conversation/file contents.

If this passes, the next patch can safely attempt strict upload + submit using the direct-path-entry cleanup primitive.
