# L26.12Y Canonical Browser Evidence Report

The operator asked whether the automatically uploaded PatchOps apply report is enough. The answer is: it proves PatchOps apply, but it does not contain the browser/live proof. The full operator report contains browser proof but is not the right long-term upload target.

L26.12Y creates the bridge:

1. run the accepted L26.12X browser proof;
2. upload exactly one short safe copy of the inner PatchOps apply report for this run;
3. after browser upload/submit/probe finishes, write one local canonical report;
4. the canonical report merges PatchOps apply evidence and browser/live proof summary;
5. the canonical report explicitly states it was not uploaded in the same run, avoiding self-upload/circular-proof claims;
6. no candidate/download clicks, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This patch prepares the next upload-target change: upload a canonical evidence report shape rather than either the raw inner apply report or the outer operator report.
