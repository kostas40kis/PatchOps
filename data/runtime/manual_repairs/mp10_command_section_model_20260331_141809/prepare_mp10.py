from __future__ import annotations

import json
import sys
from pathlib import Path

PATCH_NAME = "mp10_command_section_model"


def write_utf8(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def as_repo_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare_mp10.py <repo_root> <work_root>")

    repo_root = Path(sys.argv[1]).resolve()
    work_root = Path(sys.argv[2]).resolve()
    content_root = work_root / "content"
    inner_reports = work_root / "inner_reports"
    inner_reports.mkdir(parents=True, exist_ok=True)

    sections_path = repo_root / "patchops" / "reporting" / "sections.py"
    tests_reporting_path = repo_root / "tests" / "test_reporting.py"
    if not sections_path.exists():
        raise RuntimeError(f"Required repo file missing: {sections_path}")
    if not tests_reporting_path.exists():
        raise RuntimeError(f"Required repo file missing: {tests_reporting_path}")

    sections_text = sections_path.read_text(encoding="utf-8")

    command_sections_code = """from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

from patchops.models import CommandResult


@dataclass(frozen=True)
class ReportCommandSection:
    section_label: str
    command_name: str
    command_text: str
    working_directory: Path | None
    stdout: str
    stderr: str
    exit_code: int
    classification: str | None = None
    phase: str | None = None


def build_report_command_section(
    result: CommandResult,
    *,
    section_label: str,
    classification: str | None = None,
) -> ReportCommandSection:
    return ReportCommandSection(
        section_label=section_label,
        command_name=result.name,
        command_text=result.display_command,
        working_directory=result.working_directory,
        stdout=result.stdout,
        stderr=result.stderr,
        exit_code=result.exit_code,
        classification=classification,
        phase=result.phase,
    )


def build_report_command_sections(
    results: Iterable[CommandResult],
    *,
    section_label: str,
    classifications: Mapping[str, str] | None = None,
) -> tuple[ReportCommandSection, ...]:
    items: list[ReportCommandSection] = []
    for result in results:
        classification = classifications.get(result.name) if classifications is not None else None
        items.append(
            build_report_command_section(
                result,
                section_label=section_label,
                classification=classification,
            )
        )
    return tuple(items)
"""

    replacement_import = 'from patchops.reporting.command_sections import build_report_command_sections\nfrom patchops.reporting.metadata import build_report_header_metadata, render_report_header\n'
    old_import = 'from patchops.reporting.metadata import build_report_header_metadata, render_report_header\n'
    if 'from patchops.reporting.command_sections import build_report_command_sections' not in sections_text:
        if old_import not in sections_text:
            raise RuntimeError('Could not locate reporting metadata import in sections.py.')
        sections_text = sections_text.replace(old_import, replacement_import, 1)

    old_group = """def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.append(f"NAME    : {result.name}")
        lines.append(f"COMMAND : {result.display_command}")
        lines.append(f"CWD     : {display_path(result.working_directory)}")
        lines.append(f"EXIT    : {result.exit_code}")
    return "\\n".join(lines)
"""
    new_group = """def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    sections = build_report_command_sections(results, section_label=title)
    for section in sections:
        lines.append(f"NAME    : {section.command_name}")
        lines.append(f"COMMAND : {section.command_text}")
        lines.append(f"CWD     : {display_path(section.working_directory)}")
        lines.append(f"EXIT    : {section.exit_code}")
    return "\\n".join(lines)
"""
    if old_group not in sections_text:
        raise RuntimeError('Could not locate command_group_section block in sections.py.')
    sections_text = sections_text.replace(old_group, new_group, 1)

    old_output = """def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
    return "\\n".join(lines)
"""
    new_output = """def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    sections = build_report_command_sections(results, section_label=title)
    for section in sections:
        lines.append(f"[{section.command_name}][stdout]")
        lines.append(section.stdout if section.stdout else "")
        lines.append(f"[{section.command_name}][stderr]")
        lines.append(section.stderr if section.stderr else "")
    return "\\n".join(lines)
"""
    if old_output not in sections_text:
        raise RuntimeError('Could not locate full_output_section block in sections.py.')
    sections_text = sections_text.replace(old_output, new_output, 1)

    command_sections_test_code = """from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    build_report_command_section,
    build_report_command_sections,
)
from patchops.reporting.sections import command_group_section, full_output_section


def _command_result(
    *,
    name: str = "reporting_contracts",
    display_command: str = "py -m pytest -q tests/test_reporting.py",
    stdout: str = "ok stdout",
    stderr: str = "ok stderr",
    exit_code: int = 0,
) -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q", "tests/test_reporting.py"],
        working_directory=Path("C:/dev/patchops"),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        display_command=display_command,
        phase="validation",
    )


def test_build_report_command_section_preserves_current_command_values():
    result = _command_result()

    section = build_report_command_section(result, section_label="VALIDATION COMMANDS")

    assert section.section_label == "VALIDATION COMMANDS"
    assert section.command_name == result.name
    assert section.command_text == result.display_command
    assert section.working_directory == result.working_directory
    assert section.stdout == result.stdout
    assert section.stderr == result.stderr
    assert section.exit_code == result.exit_code
    assert section.classification is None
    assert section.phase == result.phase


def test_build_report_command_sections_supports_optional_classification_map():
    required_result = _command_result(name="required_check", exit_code=1)
    tolerated_result = _command_result(name="tolerated_check", exit_code=5)

    sections = build_report_command_sections(
        [required_result, tolerated_result],
        section_label="VALIDATION COMMANDS",
        classifications={"required_check": "required", "tolerated_check": "tolerated"},
    )

    assert [section.command_name for section in sections] == ["required_check", "tolerated_check"]
    assert [section.classification for section in sections] == ["required", "tolerated"]


def test_command_group_section_preserves_visible_shape_after_model_introduction():
    result = _command_result()

    text = command_group_section("VALIDATION COMMANDS", [result])

    assert "VALIDATION COMMANDS" in text
    assert f"NAME    : {result.name}" in text
    assert f"COMMAND : {result.display_command}" in text
    assert f"CWD     : {result.working_directory}" in text
    assert f"EXIT    : {result.exit_code}" in text


def test_full_output_section_preserves_stdout_and_stderr_labels_after_model_introduction():
    result = _command_result(stdout="captured stdout", stderr="captured stderr")

    text = full_output_section([result], "FULL OUTPUT")

    assert "[reporting_contracts][stdout]" in text
    assert "captured stdout" in text
    assert "[reporting_contracts][stderr]" in text
    assert "captured stderr" in text
"""

    command_sections_content_path = content_root / "patchops" / "reporting" / "command_sections.py"
    sections_content_path = content_root / "patchops" / "reporting" / "sections.py"
    tests_content_path = content_root / "tests" / "test_reporting_command_sections_current.py"

    write_utf8(command_sections_content_path, command_sections_code)
    write_utf8(sections_content_path, sections_text)
    write_utf8(tests_content_path, command_sections_test_code)

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
            "patchops/reporting/sections.py",
            "tests/test_reporting_command_sections_current.py",
        ],
        "files_to_write": [
            {
                "path": "patchops/reporting/command_sections.py",
                "content_path": as_repo_relative(command_sections_content_path, work_root),
                "encoding": "utf-8",
            },
            {
                "path": "patchops/reporting/sections.py",
                "content_path": as_repo_relative(sections_content_path, work_root),
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
                "name": "command_section_model_contracts",
                "program": "py",
                "args": ["-m", "pytest", "-q", *selected_tests],
                "working_directory": ".",
            }
        ],
        "report_preferences": {
            "report_name_prefix": "mp10",
            "report_dir": str(inner_reports.resolve()).replace("\\", "/"),
        },
        "tags": [
            "self_hosted",
            "pythonization",
            "mp10",
            "command_section_model",
            "reporting",
        ],
        "notes": "MP10: introduce a small reportable command section model and route current command section assembly through it without changing rendered shape.",
    }

    manifest_path = work_root / "patch_manifest.json"
    write_utf8(manifest_path, json.dumps(manifest, indent=2) + "\n")

    print(f"INFO: staged_command_sections={command_sections_content_path}")
    print(f"INFO: staged_sections={sections_content_path}")
    print(f"INFO: staged_tests={tests_content_path}")
    print(f"INFO: selected_tests={selected_tests}")
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())