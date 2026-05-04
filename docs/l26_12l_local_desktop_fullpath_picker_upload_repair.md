# L26.12L Local Desktop Full-Path Picker Upload Repair

L26.12K reached the same real picker layer and attempted to change directory, but on the operator machine the picker received an invalid path that began with `lC:\...` / `iC:\...`. That means the Ctrl+L directory step leaked a literal key into the path instead of focusing the address bar.

Operator corrections for L26.12L:

- reports should be written to `C:\Users\ksarantak\Desktop`, not `C:\Users\ksarantak\OneDrive - OTE\Desktop`;
- the report already exists at the Desktop report path chosen by the script;
- do not use Ctrl+L to change directories because it caused the invalid `lC:\` path;
- use the OS picker filename field with the full quoted file path instead.

L26.12L implements:

1. use `C:\Users\ksarantak\Desktop` as the outer report directory;
2. write the Desktop operator report before upload proof;
3. create a closed runtime upload-safe copy;
4. verify the safe-copy path has a valid drive prefix such as `C:\`, and not `lC:\` or `iC:\`;
5. focus existing ChatGPT composer;
6. clear composer, type `/`, press Ctrl+U directly;
7. accept the foreground OS picker handoff;
8. do **not** press Ctrl+L;
9. press Alt+N where available and paste the full quoted safe-copy path;
10. press Enter only in the OS picker;
11. wait for staged attachment evidence;
12. keep final ChatGPT submit/send forbidden.
