from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    render_report_command_output_section,
)
from patchops.reporting.sections import full_output_section


def _result(name: str, stdout: str, stderr: str) -> CommandResult:
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


def test_report_output_helper_renders_multiple_results_when_given_output_section_object() -> None:
    section = ReportCommandOutputSection(
        title="FULL OUTPUT",
        results=[
            _result("alpha", "hello from alpha\n", "warn from alpha\n"),
            _result("beta", "hello from beta\n", "warn from beta\n"),
        ],
        rule=lambda title: f"\n{title}\n{'-' * len(title)}",
    )

    text = render_report_command_output_section(section)

    assert text.lstrip().startswith("FULL OUTPUT")
    assert "\nFULL OUTPUT\n-----------\n" in text
    assert text.count("[alpha][stdout]") == 1
    assert text.count("[alpha][stderr]") == 1
    assert text.count("[beta][stdout]") == 1
    assert text.count("[beta][stderr]") == 1
    assert "hello from alpha" in text
    assert "warn from alpha" in text
    assert "hello from beta" in text
    assert "warn from beta" in text


def test_full_output_section_renders_all_results_without_single_result_assumption() -> None:
    results = [
        _result("alpha", "alpha stdout\n", "alpha stderr\n"),
        _result("beta", "beta stdout\n", "beta stderr\n"),
    ]

    text = full_output_section(results, "FULL OUTPUT")

    assert text.startswith("FULL OUTPUT\n")
    assert text.count("[alpha][stdout]") == 1
    assert text.count("[alpha][stderr]") == 1
    assert text.count("[beta][stdout]") == 1
    assert text.count("[beta][stderr]") == 1
    assert "alpha stdout" in text
    assert "beta stdout" in text
    assert "alpha stderr" in text
    assert "beta stderr" in text
