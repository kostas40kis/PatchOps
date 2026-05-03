# L6.4 Microsoft Edge executable discovery fixture matrix CLI/readback

L6.4 adds a passive CLI/readback layer for the accepted L6.3 Microsoft Edge executable discovery fixture matrix.

Command:

`browser-start-supervised-launch-edge-executable-discovery-fixture-matrix-readback`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-fixture-matrix`

This patch keeps brief validation output: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- L6.3 executable discovery fixture matrix remains accepted.
- fixture matrix CLI/readback enforced.
- `win_program_files_edge` fixture remains modeled.
- `win_program_files_x86_edge` fixture remains modeled.
- `win_localappdata_edge` fixture remains modeled.
- `future_operator_override` fixture remains modeled.
- `msedge.exe` candidates remain listed for future discovery logic.
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

`L6.5 Live adapter Microsoft Edge executable discovery aggregate gate`
