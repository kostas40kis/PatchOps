# L26.12P Picker-Confirmed Upload Acceptance

L26.12N and L26.12O uploaded report copies to the real ChatGPT chat, but the local script failed afterward because it tried to require a self-referential live proof in the same uploaded report snapshot.

A report cannot contain proof that it was uploaded before it is uploaded. Therefore L26.12P separates the two artifacts:

- uploaded artifact: a pre-upload snapshot of the operator report;
- local Desktop artifact: the final report rewritten after browser upload with PASS/FAIL.

L26.12P acceptance is based on:

1. local Desktop report path exists;
2. closed safe copy is created and hash-matched;
3. slash + Ctrl+U opens the foreground OS picker;
4. full quoted safe-copy path is pasted into the filename field;
5. Enter is sent only in the OS picker;
6. picker-confirmed upload is accepted;
7. leftover slash is tolerated;
8. no ChatGPT send/submit occurs.

This removes the circular staged-upload requirement that was causing false failures after visible uploads.
