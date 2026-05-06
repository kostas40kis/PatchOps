# ChatGPT Uploader U2.4H Validation Chain Repair

U2.4G failed before live testing because the validation command referenced a missing file:

```text
tests/test_chatgpt_uploader_u2_4f_quiet_trigger_contract_current.py
```

U2.4H is intentionally narrow:

- keep the U2.4G slash/Enter trigger implementation unchanged;
- remove the missing U2.4F test reference from this patch's validation chain;
- keep existing reachable regression tests;
- rerun one live slash/Enter picker-open proof after apply passes.

## Behavior boundary

The slash/Enter trigger remains:

```text
focus Edge
one calculated safe click
send `/`
send Enter once
detect picker
close picker if detected
```

U2.4H does not add Tab, second Enter, plus/menu search, Ctrl+U, file selection, path writing, upload, or send.
