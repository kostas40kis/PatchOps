from pathlib import Path

project_root = Path(r"C:\dev\patchops")
target_path = project_root / "docs" / "overview.md"

section = """## Internal execution path note

For internal command execution, PatchOps should prefer the Python-owned execution path instead of reintroducing ad hoc subprocess loops inside individual workflow files or PowerShell patch bodies.

The maintained internal path is:

- `patchops.execution.process_runner.run_command(...)` for process execution and captured result creation,
- the normalized execution result model under `patchops.execution.result_model`,
- and the shared workflow adapter in `patchops.workflows.common` for command-group execution inside apply/verify-style flows.

When future maintenance work needs to run commands, the first question should be whether the existing execution helper path can be reused. New direct execution code should be treated as an exception that needs a clear reason, not as the default authoring pattern.
"""

text = target_path.read_text(encoding="utf-8")
normalized = text.rstrip() + "\n\n"

if "## Internal execution path note" not in text:
    normalized += section + "\n"

# keep file ending predictable
Path(target_path).write_text(normalized, encoding="utf-8")
print(str(target_path))