# L26.12U Short Safe Inner PatchOps Report Upload

L26.12T selected the right upload target, the inner PatchOps apply report, but failed before browser automation started because it reused nested upload wrappers. The nested safe-copy path was too deep and the live proof failed with `FileNotFoundError` before the OS picker opened.

L26.12U keeps the single-upload contract and fixes the implementation:

1. run PatchOps check / inspect / plan / apply;
2. parse the inner PatchOps apply report path;
3. copy that report once to a short path: `data/runtime/edge_upload_short/u_<timestamp>/patchops_apply_report.txt`;
4. verify the short safe copy hashes exactly match the inner PatchOps report;
5. upload that one short safe copy through the proven slash + Ctrl+U full-path picker flow;
6. submit with the accepted gated submit primitive;
7. observe idle/readiness;
8. reject outer operator-report uploads, multiple uploads, and long nested safe-copy paths.

The uploaded file name is short, but its bytes match the PatchOps-authored apply report.
