# L26.13B Canonical Rollover Publish

L26.13A proved that an existing canonical browser-evidence report can be the single browser upload target. L26.13B turns that into a rollover pattern.

L26.13B:

1. uploads the previous accepted canonical browser-evidence report as the single browser target;
2. submits and observes idle/readiness;
3. after the live proof completes, creates a new current canonical report for this patch;
4. updates a stable Desktop latest-canonical pointer: `patchops_latest_canonical_browser_evidence_report_canonical.txt`;
5. verifies that the latest pointer matches the current canonical report by hash;
6. keeps current-canonical same-run upload disabled to avoid circular proof;
7. performs no candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This gives future runs a stable canonical upload source instead of relying on ad-hoc wildcard selection.
