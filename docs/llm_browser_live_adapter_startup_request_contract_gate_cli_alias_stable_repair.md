# L1.8j startup request contract gate CLI alias stable repair

L1.8j is a narrow repair for the passive startup-request contract gate.

It restores the missing `cli_alias_argument_model` check while preserving the
existing passive success contract:

- `startup_allowed` remains `false`
- `browser_started` remains `false`
- `browser_session_created` remains `false`
- `side_effects_performed` remains an empty JSON array
- no Selenium, browser, click, download, paste, send, package-run, commit, or
  push operation is performed

The gate remains a readback/proof surface only.
