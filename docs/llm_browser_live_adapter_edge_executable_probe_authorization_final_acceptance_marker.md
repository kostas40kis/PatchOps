# L7.8 Microsoft Edge executable probe authorization final acceptance marker

L7.8 is the passive final acceptance marker for the Microsoft Edge executable-probe authorization slice.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-final-acceptance-marker`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7 executable probe authorization slice accepted.
- L7.1 executable probe authorization passive contract remains accepted.
- L7.2 executable probe authorization CLI/readback remains accepted.
- L7.3 executable probe authorization fixture matrix remains accepted.
- L7.4 executable probe authorization fixture matrix CLI/readback remains accepted.
- L7.5 executable probe authorization aggregate gate remains accepted.
- L7.6 executable probe authorization aggregate CLI/readback remains accepted.
- L7.7 executable probe authorization broad validation checkpoint remains accepted.
- final acceptance marker enforced.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization alone does not perform a probe.
- executable probe remains blocked by phase.
- executable filesystem probe not performed.
- executable path not selected.
- executable launch not attempted.
- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L8.1 Live adapter Microsoft Edge executable probe safety preflight passive contract`
