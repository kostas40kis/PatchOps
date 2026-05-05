# L26.14H Attachment Detector False-Negative Tolerant Cycle

L26.14G failed even though the picker accepted the upload and seed copies were correct. The failure was:

- `picker_confirmed_upload_accepted: True`
- `seed_copy_hashes_match: True`
- `attachment_visible_before_submit: False`

The current chat also received attachment files from that run, which shows the picker/upload path can succeed while the UIA visible-attachment detector misses the attachment chip.

L26.14H changes the gate:

1. still requires a canonical source file;
2. still requires a safe copied upload file with matching hash;
3. still requires picker-confirmed upload acceptance;
4. treats the visible-attachment detector as diagnostic;
5. allows an explicit detector false-negative fallback only when picker upload is accepted;
6. requires submit and post-submit idle/readiness;
7. publishes a current canonical report and updates the latest pointer;
8. keeps response-candidate selection as dry-run only;
9. performs no response-candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This avoids blocking on a brittle UIA attachment-chip detector while keeping the other proof gates strict.
