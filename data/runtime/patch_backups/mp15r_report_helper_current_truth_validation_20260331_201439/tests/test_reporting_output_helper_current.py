from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    build_report_command_section,
    render_command_output_section,
    render_report_command_output_section,
)


def _result(name: str = "alpha", stdout: str = "hello\n", stderr: str = "warn\n") -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q", "tests/test_reporting.py"],
        working_directory=Path.cwd(),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command="py -m pytest -q tests/test_reporting.py",
        phase="validation",
    )


def test_build_report_command_section_exposes_current_fields() -> None:
    section = build_report_command_section(_result())

    assert section.command_name == "alpha"
    assert "pytest" in section.command_text
    assert section.exit_code == 0
    assert str(Path.cwd()) == section.working_directory


def test_report_output_helper_alias_matches_base_helper() -> None:
    result = _result("alpha", "hello\n", "warn\n")
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"

    base = render_command_output_section("FULL OUTPUT", [result], rule)
    alias = render_report_command_output_section("FULL OUTPUT", [result], rule)

    assert alias == base


def test_report_output_helper_accepts_single_section_object() -> None:
    result = _result("alpha", "hello\n", "warn\n")
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"
    section = ReportCommandOutputSection(title="FULL OUTPUT", results=[result], rule=rule)

    text = render_report_command_output_section(section)

    assert section.command_name == "alpha"
    assert "[alpha][stdout]" in text
    assert "hello" in text
    assert "[alpha][stderr]" in text
    assert "warn" in text