# L6.3 Microsoft Edge executable discovery fixture matrix

L6.3 adds a passive fixture matrix for the Microsoft Edge executable-discovery line.

Command:

`browser-start-supervised-launch-edge-executable-discovery-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-readback`

This patch keeps brief validation output: validation captures large JSON internally and prints only short PASS summaries.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- L6.2 executable discovery CLI/readback remains accepted.
- fixture matrix modeled.
- `win_program_files_edge` fixture modeled.
- `win_program_files_x86_edge` fixture modeled.
- `win_localappdata_edge` fixture modeled.
- `future_operator_override` fixture modeled.
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

`L6.4 Live adapter Microsoft Edge executable discovery fixture matrix CLI/readback`
