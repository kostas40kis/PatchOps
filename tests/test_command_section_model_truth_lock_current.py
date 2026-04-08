from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    build_report_command_section,
    build_report_command_sections,
    render_report_command_output_section,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


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


def _test_build_report_command_section_preserves_current_values() -> None:
    result = _command_result()
    section = build_report_command_section(result, section_label="VALIDATION COMMANDS")

    _assert(section.section_label == "VALIDATION COMMANDS", "section_label drifted")
    _assert(section.command_name == result.name, "command_name drifted")
    _assert(section.command_text == result.display_command, "command_text drifted")
    _assert(section.working_directory == result.working_directory, "working_directory drifted")
    _assert(section.stdout == result.stdout, "stdout drifted")
    _assert(section.stderr == result.stderr, "stderr drifted")
    _assert(section.exit_code == result.exit_code, "exit_code drifted")
    _assert(section.classification is None, "classification should default to None")
    _assert(section.phase == result.phase, "phase drifted")


def _test_build_report_command_sections_support_optional_classification_map() -> None:
    required_result = _command_result(name="required_check", exit_code=1)
    tolerated_result = _command_result(name="tolerated_check", exit_code=5)

    sections = build_report_command_sections(
        [required_result, tolerated_result],
        section_label="VALIDATION COMMANDS",
        classifications={"required_check": "required", "tolerated_check": "tolerated"},
    )

    _assert([section.command_name for section in sections] == ["required_check", "tolerated_check"], "command name ordering drifted")
    _assert([section.classification for section in sections] == ["required", "tolerated"], "classification mapping drifted")


def _test_report_command_output_section_preserves_labels_and_output_text() -> None:
    result = _command_result(stdout="captured stdout", stderr="captured stderr")
    section = build_report_command_section(result, section_label="FULL OUTPUT")
    output_section = ReportCommandOutputSection(title="FULL OUTPUT", results=[section])

    _assert(output_section.command_name == result.name, "output section command_name drifted")
    _assert(output_section.command_text == result.display_command, "output section command_text drifted")
    _assert(output_section.stdout_label == f"[{result.name}][stdout]", "stdout label drifted")
    _assert(output_section.stderr_label == f"[{result.name}][stderr]", "stderr label drifted")
    _assert(output_section.stdout == "captured stdout", "output section stdout drifted")
    _assert(output_section.stderr == "captured stderr", "output section stderr drifted")

    rendered = render_report_command_output_section(section)
    _assert(
        rendered == (
            f"[{result.name}][stdout]",
            "captured stdout",
            f"[{result.name}][stderr]",
            "captured stderr",
        ),
        "render_report_command_output_section tuple shape drifted",
    )


def _test_render_report_command_output_section_keeps_empty_output_labels() -> None:
    result = _command_result(stdout="", stderr="")
    section = build_report_command_section(result, section_label="FULL OUTPUT")
    rendered = render_report_command_output_section(section)

    _assert(
        rendered == (
            f"[{result.name}][stdout]",
            "",
            f"[{result.name}][stderr]",
            "",
        ),
        "empty stdout/stderr label preservation drifted",
    )


def main() -> int:
    _test_build_report_command_section_preserves_current_values()
    _test_build_report_command_sections_support_optional_classification_map()
    _test_report_command_output_section_preserves_labels_and_output_text()
    _test_render_report_command_output_section_keeps_empty_output_labels()
    print("command-section-model truth-lock validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
