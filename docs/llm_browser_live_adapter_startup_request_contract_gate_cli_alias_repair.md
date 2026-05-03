# L1.8i startup request contract gate CLI alias check repair

This repair preserves the L1.8 passive startup-request contract gate and restores the public check-name alias `cli_alias_argument_model`.

The gate remains passive-only:

- no Selenium import;
- no browser startup;
- no click, download, paste, send, or package-run side effect;
- no git commit or push.

The expected PASS condition remains blocked startup with no browser/session creation and no side effects.
