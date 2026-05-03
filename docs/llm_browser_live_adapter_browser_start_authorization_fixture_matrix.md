# L3.3 Live adapter browser-start authorization fixture matrix

Patch L3.3 adds a passive fixture matrix for the explicit browser-start authorization contract.

This is still not live browser automation. The matrix exercises only model/readback cases:

- Edge default request with missing acknowledgements.
- Opera request with all acknowledgements and modelled permission flags.
- Unsupported browser rejection.
- Shared/default profile rejection.
- Download, paste, send, and package-run side-effect requests staying blocked/modelled-only.

Safety requirements:

- no Selenium import,
- no optional browser dependency import or requirement,
- no browser start,
- no WebDriver/session creation,
- no profile directory creation,
- no adapter filesystem writes,
- no click/download/paste/send/package-run side effect,
- no commit or push.

Readback command:

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_authorization_fixtures --repo-root C:\dev\patchops --json --compact
```

Expected next patch: **L3.4 Live adapter browser-start authorization fixture matrix CLI/readback**.
