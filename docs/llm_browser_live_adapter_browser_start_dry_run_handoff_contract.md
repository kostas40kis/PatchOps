# L4.1 Live adapter browser-start dry-run handoff contract

L4.1 defines the first L4 browser-start handoff contract as **dry-run-only** data. It intentionally does not cross into live browser automation.

This patch exists to connect the accepted L2 browser-profile preflight stack and the accepted L3 browser-start authorization stack to a future dry-run handoff surface.

It verifies that:

- the L3 final acceptance marker artifacts remain present;
- the L4.1 handoff contract source, docs, and focused test are present;
- Edge and Opera are modelled as allowed browser targets only;
- the handoff request is dry-run-only;
- startup authorization is still required;
- startup is not allowed by this patch;
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
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root "C:\dev\patchops" --browser edge --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract --repo-root "C:\dev\patchops" --browser opera --json --compact
git status --short --branch
```

These commands are listed for operator readback only. The adapter does not execute them as live browser actions.

## Boundary

This is not a live browser automation patch. It does not import Selenium, does not start Edge or Opera, does not create a browser session, does not create profile directories, does not click downloads, does not paste into a composer, does not send/submit messages, does not run downloaded packages from adapter logic, and does not commit or push.

## Next patch

If accepted, continue with:

`L4.2 Live adapter browser-start dry-run handoff CLI/readback`
