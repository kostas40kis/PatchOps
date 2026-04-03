# Self-hosted PatchOps helper note

## Problem that occurred

A self-hosted PowerShell helper attempted to locate the generated PatchOps report by guessing a filename pattern based only on the patch name.

That guess was too narrow.

Example:
- patch name: `patch_49_documentation_stop_h`
- actual report path emitted by PatchOps:
  `generic_python_patch_patch_49_documentation_stop_h_<timestamp>.txt`

Because the helper guessed the wrong prefix, it printed a false message saying no report was found even though PatchOps had already reported the correct path.

## Correct rule

When PatchOps prints a `Report Path` line in stdout, treat that as the source of truth.

Do not guess the report filename pattern if the exact path was already emitted.

## Recommended operator behavior

For self-hosted runs:

1. run PatchOps
2. read stdout
3. extract the `Report Path`
4. open that exact file
5. only fall back to directory scanning if the stdout line is absent

This is the safest behavior because report naming can vary by profile or workflow class.