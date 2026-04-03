from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    render_command_output_section,
    render_report_command_output_section,
)


def _result(name: str = "alpha", stdout: str = "hello\n", stderr: str = "warn\n") -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q", "tests/test_reporting.py"],
        working_directory=Path("."),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command="py -m pytest -q tests/test_reporting.py",
        phase="validation",
    )


def test_report_output_helper_alias_matches_base_helper() -> None:
    result = _result("alpha", "hello\n", "warn\n")
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"

    base = render_command_output_section("FULL OUTPUT", [result], rule)
    alias = render_report_command_output_section("FULL OUTPUT", [result], rule)

    assert alias == base


def test_report_output_helper_single_section_shape_is_available() -> None:
    result = _result("alpha", "hello\n", "warn\n")
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"
    section = ReportCommandOutputSection(title="FULL OUTPUT", results=[result], rule=rule)

    lines = render_report_command_output_section(section)

    assert isinstance(lines, tuple)
    assert section.command_name == "alpha"
    assert lines[0] == rule("FULL OUTPUT")
    assert lines[1] == "[alpha][stdout]"
    assert lines[2] == "hello\n"
    assert lines[3] == "[alpha][stderr]"
    assert lines[4] == "warn\n"
