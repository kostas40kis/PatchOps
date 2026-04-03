from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    build_report_command_section,
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


def test_build_report_command_section_exposes_command_name() -> None:
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"
    section = build_report_command_section("FULL OUTPUT", [_result("alpha")], rule)
    assert section.title == "FULL OUTPUT"
    assert section.command_name == "alpha"


def test_report_output_helper_alias_matches_base_helper() -> None:
    result = _result("alpha", "hello\n", "warn\n")
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"

    base = render_command_output_section("FULL OUTPUT", [result], rule)
    alias = render_report_command_output_section("FULL OUTPUT", [result], rule)

    assert alias == base
    assert "[alpha][stdout]" in alias
    assert "[alpha][stderr]" in alias


def test_report_output_helper_accepts_single_section_object() -> None:
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"
    section = build_report_command_section("FULL OUTPUT", [_result("beta")], rule)
    rendered = render_report_command_output_section(section)
    assert rendered == (
        "[beta][stdout]",
        "hello\n",
        "[beta][stderr]",
        "warn\n",
    )