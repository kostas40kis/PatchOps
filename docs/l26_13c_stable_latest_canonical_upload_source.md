# L26.13C Stable Latest Canonical Upload Source

L26.13B created and updated a stable Desktop latest-canonical pointer:

`patchops_latest_canonical_browser_evidence_report_canonical.txt`

L26.13C proves that future browser-report uploads can use that stable pointer directly instead of wildcard-discovering the newest `*_canonical.txt` file.

L26.13C:

1. reads the stable latest-canonical pointer path directly;
2. verifies the source is a canonical browser-evidence report;
3. uploads that canonical report as the single browser target;
4. submits and observes idle/readiness;
5. publishes a new current canonical report after the proof completes;
6. updates the same latest-canonical pointer for the next run;
7. asserts wildcard source selection was not used;
8. performs no candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.

This makes the canonical-report upload loop deterministic and stable.
