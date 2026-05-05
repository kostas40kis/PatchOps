# L26.14G Seeded Picker Bridge Canonical Cycle

L26.14F passed and restored canonical publication, but the operator still observed a crash-like Windows picker moment when the dialog opened in a remembered upload directory.

L26.14G keeps the successful L26.14F path and makes it less brittle by seeding multiple safe upload locations before opening the picker:

1. copy the latest canonical source into the current upload directory;
2. copy it into the observed remembered picker directory if present;
3. copy it into several recent upload directories and the Desktop fallback;
4. run the visible attachment gate using the primary bridge directory;
5. require visible attachment evidence before submit;
6. submit and observe idle/readiness;
7. publish a current canonical report and update the latest-canonical pointer;
8. keep response-candidate selection as dry-run only;
9. perform no response-candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This does not advance to candidate clicking. It stabilizes the picker/upload foundation first.
