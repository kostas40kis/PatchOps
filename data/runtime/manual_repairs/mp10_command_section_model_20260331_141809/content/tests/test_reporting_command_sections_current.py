from __future__ import annotations

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
