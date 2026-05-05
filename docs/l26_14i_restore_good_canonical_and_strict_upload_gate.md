# L26.14I Restore Good Canonical and Strict Upload Gate

L26.14H did not automatically upload into the chat, and it also overwrote the latest canonical pointer with a failed canonical report.

The failed latest canonical contains:

- picker upload accepted;
- submit happened;
- idle/readiness completed;
- selector dry-run completed;
- but `visible_attachment_gate_passed: False` and `browser_live_passed: False`.

L26.14I repairs the state before continuing:

1. inspect the latest canonical pointer;
2. if it is failed or not browser-good, restore it from the last known-good PASS canonical report on the Desktop;
3. rerun the strict visible upload gate using the remembered picker bridge;
4. do not tolerate attachment-detector fallback in this patch;
5. publish a new current canonical report only if the strict visible gate passes;
6. update the latest pointer only after successful strict browser proof;
7. keep response-candidate selection as dry-run only;
8. perform no response-candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This patch intentionally refuses to advance if no automatic upload is visible.
