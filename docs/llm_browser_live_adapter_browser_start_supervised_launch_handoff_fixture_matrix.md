# L5.3 Live adapter browser-start supervised launch handoff fixture matrix

L5.3 adds a passive fixture matrix for the accepted L5 browser-start supervised-launch handoff contract.

The matrix exercises the supervised-launch handoff across Edge, Opera, mixed-case normalization, unsupported-browser rejection, and invalid operator-decision rejection. It remains **modelled-only** and does not move PatchOps into live browser automation.

It verifies that:

- the L5.1 supervised-launch handoff contract artifacts remain present;
- the L5.2 CLI/readback artifacts remain present;
- the L5.3 fixture matrix source, docs, and focused test are present;
- Edge and Opera are modelled only as supervised-launch handoff targets;
- unsupported browsers and invalid operator decisions are rejected without startup;
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
py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures --repo-root "C:\dev\patchops" --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root "C:\dev\patchops" --browser edge --operator-decision review_only --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root "C:\dev\patchops" --browser opera --operator-decision prepare_only --json --compact
git status --short --branch
```

These commands are listed for readback only. They do not authorize a live browser start.

## Boundary

This is not a live browser automation patch. It does not import Selenium, does not start Edge or Opera, does not create a browser session, does not create a driver, does not create profile directories, does not click downloads, does not paste into a composer, does not send/submit messages, does not run downloaded packages from adapter logic, and does not commit or push.

The fixture matrix exists to prove the supervised-launch handoff stays data-only until a later phase explicitly permits live startup.

## Next patch

If accepted, continue with:

`L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback`
