# L26.12Z Short Live Root Canonical Report

L26.12Y applied successfully, but its live browser proof failed before upload/submit because the nested live-proof path became too long/deep:

`post_apply_canonical_browser_evidence_report/generated_candidate_diff/single_upload_submit_idle/l26_12u_short_safe_inner_patchops_report_upload_live_report.txt`

L26.12Z keeps the canonical-report design and repairs only the live-output root:

1. run PatchOps check / inspect / plan / apply;
2. discover the inner PatchOps apply report;
3. run the accepted generated-candidate diff flow from a short live root under `data/runtime/edge_live_short/z_<timestamp>`;
4. upload exactly one short safe copy of the inner PatchOps apply report;
5. submit, observe idle, and run the diff filter;
6. create one local canonical report merging PatchOps apply evidence and browser/live proof;
7. keep same-run canonical upload disabled to avoid circular self-proof;
8. no candidate clicks, no downloads, no DOM/WebDriver/Selenium, and no prompt/conversation/file-content logging.
