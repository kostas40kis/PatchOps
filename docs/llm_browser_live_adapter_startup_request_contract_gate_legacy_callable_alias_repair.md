# L1.8h startup request contract gate legacy-callable alias repair

This repair preserves the L1.8 passive startup-request contract gate and restores the public check-name alias `legacy_callable_compatibility_methods`.

The gate remains passive-only:

- no Selenium import;
- no browser startup;
- no click, download, paste, send, or package-run side effect;
- no git commit or push.

The expected PASS condition is blocked startup with no browser/session creation and no side effects.
