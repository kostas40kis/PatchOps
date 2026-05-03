# L7.3 Microsoft Edge executable probe authorization fixture matrix

L7.3 adds a passive fixture matrix for the accepted L7.2 Microsoft Edge executable-probe authorization CLI/readback surface.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7.2 executable probe authorization CLI/readback remains accepted.
- fixture matrix modeled.
- `no_probe_auth_dedicated_profile` fixture modeled.
- `live_auth_without_probe_auth` fixture modeled.
- `probe_auth_dedicated_profile` fixture modeled.
- `probe_auth_default_profile` fixture modeled.
- `probe_auth_missing_profile` fixture modeled.
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

`L7.4 Live adapter Microsoft Edge executable probe authorization fixture matrix CLI/readback`
