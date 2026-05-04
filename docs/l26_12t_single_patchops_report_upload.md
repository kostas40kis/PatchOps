# L26.12T Single PatchOps Report Upload

L26.12S accepted the browser upload + submit + idle-observer milestone, but it still uploaded an outer operator-report snapshot. The operator correction is that the uploaded file should be the report PatchOps itself authored.

L26.12T implements that contract:

1. run PatchOps check / inspect / plan / apply;
2. parse the inner PatchOps apply report path from `patchops_apply` output;
3. keep the Desktop operator report local only;
4. upload exactly one report: the inner PatchOps apply report;
5. submit it with the accepted gated submit flow;
6. observe idle/readiness with the accepted post-submit observer;
7. reject operator-report uploads and multiple-report uploads.

The uploaded report is now the PatchOps-authored apply report, not the outer script report. The local Desktop operator report remains useful for diagnosing the browser proof and final result, but it is not attached to ChatGPT.
