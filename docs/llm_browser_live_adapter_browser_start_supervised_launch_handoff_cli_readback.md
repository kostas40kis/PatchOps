# L5.2 Live adapter browser-start supervised launch handoff CLI/readback

This patch exposes a passive `llm-browser browser-start-supervised-launch-handoff` CLI/readback surface for the L5.1 supervised-launch handoff contract.

The command forwards operator-readable arguments to `patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract` and returns that module's payload. It remains modelled-only and does not perform live browser automation.

## Boundary

This patch does **not** import Selenium, does **not** start Edge or Opera, does **not** create a WebDriver or browser session, does **not** create profile directories, does **not** click downloads, does **not** paste into a composer, does **not** send or submit messages, does **not** run downloaded packages from adapter logic, and does **not** commit or push.

The CLI/readback surface is for supervised-launch handoff review only. `--operator-decision` is represented as data and can be `block`, `review_only`, or `prepare_only`; none of those values authorizes startup in this patch.

## Readback commands

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-handoff --repo-root C:\dev\patchops --browser edge --operator-decision review_only --json --compact
py -m patchops.cli llm-browser browser-start-supervised-launch-handoff --repo-root C:\dev\patchops --browser opera --operator-decision review_only --json --compact
```

## Required passive checks

- no Selenium import
- no optional browser dependency import requirement
- no browser start
- no browser session creation
- no driver creation
- no profile directory creation
- no adapter filesystem writes
- no click/download/paste/send/package-run side effect
- no commit/push

## Next patch

L5.3 Live adapter browser-start supervised launch handoff fixture matrix.
