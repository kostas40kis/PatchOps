# L26.13A Canonical Report Upload Target Smoke

L26.12Z created the first accepted canonical report that contains both PatchOps apply evidence and browser live proof. The next step is to prove that this canonical report shape can be the single browser upload target.

L26.13A:

1. runs PatchOps check / inspect / plan / apply for this patch;
2. finds or accepts an existing `*_canonical.txt` report, normally the previous accepted canonical report;
3. verifies that report contains both `PATCHOPS APPLY EVIDENCE` and `BROWSER LIVE PROOF SUMMARY`;
4. copies it once to a short upload-safe path named `canonical_browser_evidence_report.txt`;
5. uploads exactly that one canonical report;
6. submits and observes idle/readiness;
7. rejects uploading the current raw PatchOps apply report or the outer operator report as the browser target;
8. performs no candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This proves the upload target can move from raw PatchOps apply reports to canonical browser-evidence reports.
