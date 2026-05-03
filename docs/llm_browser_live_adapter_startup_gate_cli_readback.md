
# LLM Browser L1.5 Startup Gate CLI Readback

L1.5 exposes the L1.4 startup-gate scaffold through the main PatchOps CLI:

```powershell
py -m patchops.cli llm-browser startup-gate --json --compact
py -m patchops.cli llm-browser startup-gate
```

This command is passive readback only. It delegates to `patchops.llm_browser.live_adapter_startup_gate` and must not import Selenium, start a browser, create a browser session, click, download, paste, send, run PatchOps packages from the adapter, commit, or push.

The JSON payload must continue to report:

```text
status = PASSIVE_STARTUP_GATE_SCAFFOLD
startup_allowed = false
browser_started = false
browser_session_created = false
side_effects_performed = []
optional_browser_dependencies_required = false
```

## L1.5b packaging repair

L1.5b repairs a package-authoring failure from L1.5a where a stale `content\__pycache__\*.pyc` reference was included in the bundle contract. The repaired bundle includes only `content/apply_l1_05b.py` as executable package content and excludes all `__pycache__` and `.pyc` references.

## Next patch

```text
L1.6 Live adapter startup decision request model
```
