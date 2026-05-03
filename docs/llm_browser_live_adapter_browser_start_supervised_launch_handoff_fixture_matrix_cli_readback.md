# L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback

This patch adds a passive CLI/readback surface for the accepted L5.3 supervised-launch handoff fixture matrix.

## Command

```powershell
py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-fixtures --repo-root C:\dev\patchops --json --compact
```

## Boundary

The command is a readback wrapper over `patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures`.
It is modelled-only and must preserve the L5 supervised-launch handoff boundaries:

- no Selenium import;
- no browser start;
- no browser session creation;
- no driver creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no commit/push.

## Expected readback

The CLI returns the same passive L5.3 payload as the module-level fixture matrix. It should report `PASS`, list Edge and Opera fixture cases, keep startup blocked, and name:

`L5.4 Live adapter browser-start supervised launch handoff fixture matrix CLI/readback`

as the L5.3 payload's next patch.

## Next patch

After this patch is accepted, continue with:

`L5.5 Live adapter browser-start supervised launch handoff fixture matrix contract gate`


## L5.4a packaging/path repair

This repaired bundle uses short `content_path` entries (`content/c.py`, `content/d.md`, `content/t.py`) to avoid Windows extraction path-length failures while preserving the same target files and passive CLI/readback behavior.
