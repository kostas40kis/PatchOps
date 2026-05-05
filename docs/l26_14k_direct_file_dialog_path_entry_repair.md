# L26.14K Direct File-Dialog Path Entry Repair

L26.14J isolated the failure to the upload primitive:

- the probe file was created;
- Edge was found;
- the picker was reported accepted;
- the file dialog still appeared to be open after confirm;
- the UIA attachment detector found no staged attachment;
- the patch did not submit, did not publish canonical evidence, and did not click candidates.

At the same time, the uploaded probe appeared in the conversation, which means the current detector/helper is not a reliable acceptance model.

L26.14K repairs the primitive by bypassing remembered-folder selection:

1. keep the latest canonical pointer at the known-good L26.14F PASS report;
2. create a tiny upload probe file;
3. open the ChatGPT upload picker from the existing Edge session;
4. wait for the Windows file dialog;
5. use the File name field directly (`Alt+N`) and enter the full probe path;
6. press Enter/Open;
7. require the dialog to close, Edge to return, and a visible/staged attachment signal to appear;
8. do not submit/send;
9. do not publish a canonical report;
10. do not click response candidates;
11. do not use DOM/WebDriver/Selenium or log prompt/conversation/file contents.

If this passes, the next patch can rerun strict upload + submit using direct file-dialog path entry. If it fails, repair upload trigger/menu focus before path entry.
