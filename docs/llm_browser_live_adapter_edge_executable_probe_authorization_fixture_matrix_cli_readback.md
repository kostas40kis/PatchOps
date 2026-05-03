# L7.4 Microsoft Edge executable probe authorization fixture matrix CLI/readback

L7.4 adds a passive CLI/readback layer for the accepted L7.3 Microsoft Edge executable-probe authorization fixture matrix.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix-readback`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7.3 executable probe authorization fixture matrix remains accepted.
- fixture matrix CLI/readback enforced.
- `no_probe_auth_dedicated_profile` fixture remains modeled.
- `live_auth_without_probe_auth` fixture remains modeled.
- `probe_auth_dedicated_profile` fixture remains modeled.
- `probe_auth_default_profile` fixture remains modeled.
- `probe_auth_missing_profile` fixture remains modeled.
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

`L7.5 Live adapter Microsoft Edge executable probe authorization aggregate gate`
