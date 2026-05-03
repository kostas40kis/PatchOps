# L1.9 Live adapter startup request fixture matrix

L1.9 adds a passive fixture matrix for the live-adapter startup request model.

The fixture matrix is readback-only. It models multiple request shapes for future live-browser work, but it does not start a browser and it does not perform any live operation.

## Contract

The fixture matrix proves that:

- default startup requests remain blocked;
- fully acknowledged startup requests remain blocked in L1;
- Opera and Edge request shapes are represented;
- invalid browser requests are reported without side effects;
- requested side-effect operations are modeled but not executed;
- no Selenium, webdriver-manager, clipboard, browser, download, paste, send, package-run, commit, or push side effect occurs.

## Operator command

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_fixtures --json --compact
```

Text readback is also passive:

```powershell
py -m patchops.llm_browser.live_adapter_startup_request_fixtures
```

## Boundary

L1.9 is still L1 passive model work. It does not silently expand into live browser automation.
