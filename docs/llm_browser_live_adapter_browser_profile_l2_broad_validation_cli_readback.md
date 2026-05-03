# L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback

L2.11 exposes the passive L2.10 browser-profile preflight broad-validation checkpoint through the main PatchOps `llm-browser` CLI.

## Command

```powershell
py -m patchops.cli llm-browser profile-preflight-l2-broad-validation --repo-root C:\dev\patchops --json --compact
```

Text readback is also available:

```powershell
py -m patchops.cli llm-browser profile-preflight-l2-broad-validation --repo-root C:\dev\patchops
```

## Contract

The command is a readback-only CLI wrapper around `patchops.llm_browser.l2_10_broad_validation`.

It must preserve the L2 passive boundary:

- no Selenium import;
- no optional browser dependency import;
- no browser start;
- no browser session creation;
- no profile directory creation;
- no adapter filesystem writes;
- no click/download/paste/send/package-run side effect;
- no automatic git commit;
- no automatic git push.

The command only reports the broad validation plan and checkpoint payload. It does not execute unsafe live browser actions and does not run downloaded packages from adapter logic.

## Expected readback

A successful readback keeps these fields stable:

```text
phase                       : L2
patch                       : L2.10
status                      : PASS
startup_allowed             : false
browser_started             : false
browser_session_created     : false
profile_directory_created   : false
side_effects_performed      : []
filesystem_writes_performed : []
executed_validation_commands: []
```

## Next patch

L2.12 Live adapter browser profile preflight L2 final acceptance marker.
