from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_function(text: str, function_name: str, new_block: str) -> str:
    pattern = re.compile(rf"(?ms)^def {re.escape(function_name)}\(.*?(?=^def |\Z)")
    if not pattern.search(text):
        raise RuntimeError(f"Could not locate {function_name} in sections.py.")
    replacement = new_block.strip() + "\n\n"
    return pattern.sub(replacement, text, count=1)


def ensure_sections_import(text: str) -> str:
    import_line = "from patchops.reporting.command_sections import render_command_output_section\n"
    if "render_command_output_section" in text:
        return text

    marker = "from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord\n"
    if marker in text:
        return text.replace(marker, marker + import_line, 1)

    wrapper_marker = "from patchops.workflows.wrapper_retry import (\n"
    if wrapper_marker in text:
        return text.replace(wrapper_marker, import_line + wrapper_marker, 1)

    future_marker = "from __future__ import annotations\n\n"
    if future_marker in text:
        return text.replace(future_marker, future_marker + import_line, 1)

    raise RuntimeError("Could not find a safe import anchor in sections.py.")


def ensure_output_helper(text: str) -> tuple[str, bool]:
    if "def render_command_output_section(" in text:
        return text, False

    helper = '''

def render_command_output_section(title, results, rule):
    lines = [rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
    return "\\n".join(lines)
'''
    base = text.rstrip() + "\n"
    return base + helper, True


def build_test_text() -> str:
    return '''from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import render_command_output_section
from patchops.reporting.sections import full_output_section



def _result(name: str, stdout: str, stderr: str) -> CommandResult:
    return CommandResult(
        name=name,
        program="python",
        args=["-c", "pass"],
        working_directory=Path("."),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command="python -c pass",
        phase="validation",
    )



def test_render_command_output_section_renders_named_stdout_and_stderr_blocks() -> None:
    rendered = render_command_output_section(
        "FULL OUTPUT",
        [_result("alpha", "hello\\n", "warn\\n")],
        lambda title: f"\\n{title}\\n{'-' * len(title)}",
    )

    assert "FULL OUTPUT" in rendered
    assert "[alpha][stdout]" in rendered
    assert "hello" in rendered
    assert "[alpha][stderr]" in rendered
    assert "warn" in rendered



def test_render_command_output_section_renders_none_when_no_results() -> None:
    rendered = render_command_output_section(
        "AUDIT OUTPUT",
        [],
        lambda title: f"\\n{title}\\n{'-' * len(title)}",
    )

    assert "AUDIT OUTPUT" in rendered
    assert "(none)" in rendered



def test_full_output_section_uses_helper_shape_for_additional_workflow_path() -> None:
    rendered = full_output_section([_result("beta", "", "")], "SMOKE OUTPUT")

    assert "SMOKE OUTPUT" in rendered
    assert "[beta][stdout]" in rendered
    assert "[beta][stderr]" in rendered



def test_full_output_section_renders_none_for_empty_results() -> None:
    rendered = full_output_section([], "ARCHIVE OUTPUT")

    assert "ARCHIVE OUTPUT" in rendered
    assert "(none)" in rendered
'''


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15a.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    sections_rel = Path("patchops") / "reporting" / "sections.py"
    command_sections_rel = Path("patchops") / "reporting" / "command_sections.py"
    test_rel = Path("tests") / "test_reporting_output_helper_current.py"

    sections_path = wrapper_root / sections_rel
    command_sections_path = wrapper_root / command_sections_rel

    if not sections_path.exists():
        raise RuntimeError("sections.py was not found in the wrapper repo.")
    if not command_sections_path.exists():
        raise RuntimeError("command_sections.py was not found in the wrapper repo.")

    sections_text = read_text(sections_path)
    command_sections_text = read_text(command_sections_path)

    helper_already_present = "def render_command_output_section(" in command_sections_text
    updated_command_sections, helper_added = ensure_output_helper(command_sections_text)

    updated_sections = ensure_sections_import(sections_text)
    updated_sections = replace_function(
        updated_sections,
        "full_output_section",
        '''

def full_output_section(results: list[CommandResult], title: str) -> str:
    return render_command_output_section(title, results, _rule)
''',
    )

    content_sections = working_root / "content" / sections_rel
    content_command_sections = working_root / "content" / command_sections_rel
    content_test = working_root / "content" / test_rel

    write_text(content_sections, updated_sections)
    write_text(content_command_sections, updated_command_sections)
    write_text(content_test, build_test_text())

    validation_targets = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_reporting_output_helper_current.py",
        "tests/test_summary_integrity_current.py",
        "tests/test_summary_derivation_lock_current.py",
        "tests/test_required_vs_tolerated_report_current.py",
        "tests/test_summary_integrity_workflow_current.py",
    ]

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp15a_report_helper_additional_workflow_path_repair",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root).replace("\\\\", "/"),
        "backup_files": [
            str(sections_rel).replace("\\\\", "/"),
            str(command_sections_rel).replace("\\\\", "/"),
            str(test_rel).replace("\\\\", "/"),
        ],
        "files_to_write": [
            {
                "path": str(sections_rel).replace("\\\\", "/"),
                "content_path": str((Path("content") / sections_rel)).replace("\\\\", "/"),
                "encoding": "utf-8",
            },
            {
                "path": str(command_sections_rel).replace("\\\\", "/"),
                "content_path": str((Path("content") / command_sections_rel)).replace("\\\\", "/"),
                "encoding": "utf-8",
            },
            {
                "path": str(test_rel).replace("\\\\", "/"),
                "content_path": str((Path("content") / test_rel)).replace("\\\\", "/"),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "report_helper_pytest",
                "program": "python",
                "args": ["-m", "pytest", "-q", *validation_targets],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str((working_root / "inner_reports")).replace("\\\\", "/"),
            "report_name_prefix": "mp15a_report_helper_additional_workflow_path_repair",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper"],
        "notes": "Narrow MP15 repair. Route full_output_section through a dedicated reporting helper instead of inline assembly.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

    prep_lines = [
        "decision=mp15a_report_helper_repair",
        f"sections_path={sections_path}",
        f"command_sections_path={command_sections_path}",
        f"helper_already_present={str(helper_already_present).lower()}",
        f"helper_added={str(helper_added).lower()}",
        f"manifest_path={manifest_path}",
        "validation_targets=" + ";".join(validation_targets),
        "rationale=Use a robust function-boundary replacement for full_output_section instead of exact text surgery.",
    ]
    write_text(working_root / "prepare_result.txt", "\n".join(prep_lines) + "\n")

    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())