# L4.3 Live adapter browser-start dry-run handoff fixture matrix

L4.3 adds a passive fixture matrix for the accepted L4 browser-start dry-run handoff contract.

The matrix checks the dry-run handoff payload across Edge, Opera, mixed-case browser normalization, and an unsupported-browser rejection case. It remains **dry-run-only** and does not move PatchOps into live browser automation.

It verifies that:

- the L4.1 handoff contract artifacts remain present;
- the L4.2 CLI/readback artifacts remain present;
- the L4.3 fixture matrix source, docs, and focused test are present;
- Edge and Opera are modelled only as dry-run handoff targets;
- unsupported browsers are rejected without startup;
- startup authorization remains false;
- startup remains not allowed;
- no Selenium import is required;
- no browser start occurs;
- no browser session is created;
- no driver is created;
- no profile directory creation occurs;
- no adapter filesystem writes occur;
- no click/download/paste/send/package-run side effect occurs;
- `git_commit_executed: false`;
- `git_push_executed: false`.

## Operator readback commands

```powershell
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures --repo-root "C:\dev\patchops" --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root "C:\dev\patchops" --browser edge --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root "C:\dev\patchops" --browser opera --json --compact
git status --short --branch
```

These commands are listed for readback only. They do not authorize a live browser start.

## Boundary

This is not a live browser automation patch. It does not import Selenium, does not start Edge or Opera, does not create a browser session, does not create a driver, does not create profile directories, does not click downloads, does not paste into a composer, does not send/submit messages, does not run downloaded packages from adapter logic, and does not commit or push.

## Next patch

If accepted, continue with:

`L4.4 Live adapter browser-start dry-run handoff fixture matrix CLI/readback`
