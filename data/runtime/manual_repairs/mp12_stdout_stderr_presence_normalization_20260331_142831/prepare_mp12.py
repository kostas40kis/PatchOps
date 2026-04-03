from __future__ import annotations

import json
import sys
from pathlib import Path


PATCH_NAME = "mp12_stdout_stderr_presence_normalization"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def as_repo_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp12.py <repo_root> <work_root>")

    repo_root = Path(sys.argv[1]).resolve()
    work_root = Path(sys.argv[2]).resolve()
    content_root = work_root / "content"
    inner_reports = work_root / "inner_reports"
    inner_reports.mkdir(parents=True, exist_ok=True)

    command_sections_path = repo_root / "patchops" / "reporting" / "command_sections.py"
    tests_path = repo_root / "tests" / "test_reporting_command_sections_current.py"

    required_paths = (command_sections_path, tests_path)
    for path in required_paths:
        if not path.exists():
            raise RuntimeError(f"Required repo file missing: {path}")

    command_sections_text = command_sections_path.read_text(encoding="utf-8")
    tests_text = tests_path.read_text(encoding="utf-8")

    old_helper = """def render_report_command_output_section(
    section: ReportCommandSection,
) -> tuple[str, ...]:
    return (
        f"[{section.command_name}][stdout]",
        section.stdout if section.stdout else "",
        f"[{section.command_name}][stderr]",
        section.stderr if section.stderr else "",
    )
"""
    new_helper = """def _normalized_output_text(value: str | None) -> str:
    return value if value else ""


def render_report_command_output_section(
    section: ReportCommandSection,
) -> tuple[str, ...]:
    return (
        f"[{section.command_name}][stdout]",
        _normalized_output_text(section.stdout),
        f"[{section.command_name}][stderr]",
        _normalized_output_text(section.stderr),
    )
"""
    if "def _normalized_output_text(" in command_sections_text:
        # Keep reruns idempotent by normalizing the helper block if it already exists.
        start_marker = "def _normalized_output_text(value: str | None) -> str:\n"
        render_marker = "def render_report_command_output_section(\n"
        start_index = command_sections_text.index(start_marker)
        render_index = command_sections_text.index(render_marker, start_index)
        # capture existing render helper block end
        after_render = command_sections_text.index("\n\n", render_index)
        # if there are two consecutive blank lines after the helper block, keep the tail from there
        command_sections_text = command_sections_text[:start_index] + new_helper + command_sections_text[after_render + 2:]
    else:
        if old_helper not in command_sections_text:
            raise RuntimeError("Could not locate render_report_command_output_section block in command_sections.py.")
        command_sections_text = command_sections_text.replace(old_helper, new_helper, 1)

    helper_test_block = """

def test_render_report_command_output_section_keeps_labels_when_stdout_empty():
    result = _command_result(stdout="", stderr="captured stderr")

    section = build_report_command_section(result, section_label="FULL OUTPUT")
    lines = render_report_command_output_section(section)

    assert lines == (
        "[reporting_contracts][stdout]",
        "",
        "[reporting_contracts][stderr]",
        "captured stderr",
    )


def test_render_report_command_output_section_keeps_labels_when_stderr_empty():
    result = _command_result(stdout="captured stdout", stderr="")

    section = build_report_command_section(result, section_label="FULL OUTPUT")
    lines = render_report_command_output_section(section)

    assert lines == (
        "[reporting_contracts][stdout]",
        "captured stdout",
        "[reporting_contracts][stderr]",
        "",
    )


def test_render_report_command_output_section_keeps_labels_when_both_outputs_empty():
    result = _command_result(stdout="", stderr="")

    section = build_report_command_section(result, section_label="FULL OUTPUT")
    lines = render_report_command_output_section(section)

    assert lines == (
        "[reporting_contracts][stdout]",
        "",
        "[reporting_contracts][stderr]",
        "",
    )
"""
    helper_marker = "def test_render_report_command_output_section_keeps_labels_when_stdout_empty():"
    if helper_marker in tests_text:
        tests_text = tests_text.split(helper_marker, 1)[0].rstrip() + "\n\n" + helper_test_block.strip() + "\n"
    else:
        tests_text = tests_text.rstrip() + "\n\n" + helper_test_block.strip() + "\n"

    command_sections_content_path = content_root / "patchops" / "reporting" / "command_sections.py"
    tests_content_path = content_root / "tests" / "test_reporting_command_sections_current.py"

    write_utf8(command_sections_content_path, command_sections_text)
    write_utf8(tests_content_path, tests_text)

    selected_tests = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_summary_integrity_current.py",
    ]
    workflow_summary_test = repo_root / "tests" / "test_summary_integrity_workflow_current.py"
    if workflow_summary_test.exists():
        selected_tests.append("tests/test_summary_integrity_workflow_current.py")

    manifest = {
        "manifest_version": "1",
        "patch_name": PATCH_NAME,
        "active_profile": "generic_python",
        "target_project_root": str(repo_root).replace("\\", "/"),
        "backup_files": [
            "patchops/reporting/command_sections.py",
            "tests/test_reporting_command_sections_current.py",
        ],
        "files_to_write": [
            {
                "path": "patchops/reporting/command_sections.py",
                "content_path": as_repo_relative(command_sections_content_path, work_root),
                "encoding": "utf-8",
            },
            {
                "path": "tests/test_reporting_command_sections_current.py",
                "content_path": as_repo_relative(tests_content_path, work_root),
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "stdout_stderr_presence_contracts",
                "program": "py",
                "args": ["-m", "pytest", "-q", *selected_tests],
                "working_directory": ".",
            }
        ],
        "report_preferences": {
            "report_name_prefix": "mp12",
            "report_dir": str(inner_reports.resolve()).replace("\\", "/"),
        },
        "tags": [
            "self_hosted",
            "pythonization",
            "mp12",
            "stdout_stderr_presence_normalization",
            "reporting",
        ],
        "notes": "MP12: guarantee command output labels stay visible even when stdout or stderr is empty.",
    }

    manifest_path = work_root / "patch_manifest.json"
    write_utf8(manifest_path, json.dumps(manifest, indent=2) + "\n")

    print(f"INFO: staged_command_sections={command_sections_content_path}")
    print(f"INFO: staged_tests={tests_content_path}")
    print(f"INFO: selected_tests={selected_tests}")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())