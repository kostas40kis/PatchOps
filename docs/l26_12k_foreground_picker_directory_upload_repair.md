# L26.12K Foreground Picker Directory Upload Repair

L26.12J proved that PatchOps apply passed and the Desktop report existed, but the post-apply upload failed before file selection. The operator observed that Windows File Explorer / the OS picker opened, but the script's strict class detector did not accept it, so the script never changed directories or entered the report filename.

L26.12K repairs that exact layer:

- write the Desktop operator report first;
- copy that report to a closed runtime upload-safe `.txt` file;
- focus the existing ChatGPT composer;
- clear it, type `/`, and press Ctrl+U directly;
- do not press `+` after `/`;
- treat the foreground non-Edge window after Ctrl+U as the OS picker handoff;
- change directory with Ctrl+L to the safe-copy folder;
- enter the safe-copy filename with Alt+N where available;
- press Enter only in the OS picker;
- wait for staged attachment evidence;
- keep final ChatGPT submit/send forbidden.

This patch intentionally avoids strict window-class filtering because the real machine already showed a picker window that the strict filter missed.
