# L7.5 Microsoft Edge executable probe authorization aggregate gate

L7.5 adds a passive aggregate gate for the Microsoft Edge executable-probe authorization slice.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7.1 executable probe authorization passive contract remains accepted.
- L7.2 executable probe authorization CLI/readback remains accepted.
- L7.3 executable probe authorization fixture matrix remains accepted.
- L7.4 executable probe authorization fixture matrix CLI/readback remains accepted.
- executable probe authorization aggregate gate enforced.
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

`L7.6 Live adapter Microsoft Edge executable probe authorization aggregate gate CLI/readback`
