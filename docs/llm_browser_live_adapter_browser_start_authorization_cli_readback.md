# L3.2 Live adapter explicit browser-start authorization CLI/readback

L3.2 adds a passive `llm-browser` CLI/readback surface for the L3.1 browser-start authorization contract.

Command:

```powershell
py -m patchops.cli llm-browser browser-start-authorization --repo-root C:\dev\patchops --json --compact
```

This patch is still model/readback only. It must not:

- import Selenium or optional browser automation dependencies,
- start Edge or Opera,
- create a WebDriver session,
- create browser profile directories,
- read a live browser page,
- click downloads,
- run downloaded PatchOps packages from adapter logic,
- paste to the composer,
- send or submit messages,
- commit or push.

The command can model operator flags such as `--allow-browser-start`, but L3.2 still routes them to the passive authorization evaluator. The result should keep `startup_authorized` false and report no performed side effects.

Expected next patch: **L3.3 Live adapter browser-start authorization fixture matrix**.
