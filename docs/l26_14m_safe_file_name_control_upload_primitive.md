# L26.14M Safe File-name-control Upload Primitive

L26.14L opened the Windows file picker on the Desktop and selected many Desktop files, causing errors. The likely cause is global picker keyboard actions (`Ctrl+A` / free typing) landing on the file list instead of the File name field.

L26.14M repairs the primitive by making file selection control-specific:

1. close stale file dialogs before starting;
2. create the probe file under `data/runtime/edge_upload_short`, not on the Desktop;
3. open the ChatGPT upload picker from the existing Edge session;
4. find the real File name Edit/ComboBox control in the Windows picker;
5. set the full probe path using control-specific setters, not global `Ctrl+A`;
6. verify the File name control contains the expected path;
7. invoke Open or press Enter only after the value is verified;
8. require the picker to close, Edge to return, and the attachment to be visibly staged;
9. do not submit/send;
10. do not publish a canonical report;
11. do not click response candidates;
12. do not use DOM/WebDriver/Selenium or log prompt/conversation/file contents.

This patch explicitly records `global_ctrl_a_sent: false` and rejects any Desktop-parent probe or global-selection behavior.
