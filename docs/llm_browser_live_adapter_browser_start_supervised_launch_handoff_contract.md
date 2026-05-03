# L5.1 Live adapter browser-start supervised launch handoff contract

L5.1 defines the first L5 browser-start supervised-launch handoff contract as **modelled-only** data. It intentionally does not cross into live browser automation.

This patch connects the accepted L4 browser-start dry-run handoff stack to a future supervised browser-start surface while preserving the same operator-safety boundary.

It verifies that:

- the L4 final acceptance marker artifacts remain present;
- the L5.1 supervised-launch handoff contract source, docs, and focused test are present;
- Edge and Opera are modelled as allowed browser targets only;
- the supervised-launch handoff is modelled-only;
- a manual operator decision is represented as data only;
- startup authorization is still required;
- startup is not allowed by this patch;
- live driver/session creation is not allowed by this patch;
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
py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root "C:\dev\patchops" --browser edge --operator-decision review_only --json --compact
py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root "C:\dev\patchops" --browser opera --operator-decision review_only --json --compact
git status --short --branch
```

These commands are listed for operator readback only. The adapter does not execute them as live browser actions.

## Boundary

This is not a live browser automation patch. It does not import Selenium, does not start Edge or Opera, does not create a browser session, does not create profile directories, does not click downloads, does not paste into a composer, does not send/submit messages, does not run downloaded packages from adapter logic, and does not commit or push.

The phrase **supervised-launch handoff** means that later patches may define an operator-reviewed handoff toward browser startup, but this patch still performs no startup and creates no browser/profile side effects.

## Next patch

If accepted, continue with:

`L5.2 Live adapter browser-start supervised launch handoff CLI/readback`
