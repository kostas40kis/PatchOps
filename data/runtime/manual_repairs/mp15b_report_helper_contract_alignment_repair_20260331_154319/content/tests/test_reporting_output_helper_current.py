from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting import sections as reporting_sections
from patchops.reporting.command_sections import (
    render_command_output_section,
    render_report_command_output_section,
)


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


def test_report_output_helper_alias_matches_base_helper() -> None:
    result = _result("alpha", "hello\n", "warn\n")
    rule = lambda title: f"\n{title}\n{'-' * len(title)}"

    base = render_command_output_section("FULL OUTPUT", [result], rule)
    alias = render_report_command_output_section("FULL OUTPUT", [result], rule)

    assert alias == base
    assert "[alpha][stdout]" in alias
    assert "[alpha][stderr]" in alias


def test_sections_module_exposes_monkeypatchable_report_output_helper_name() -> None:
    assert hasattr(reporting_sections, "render_report_command_output_section")


def test_full_output_section_uses_report_helper_name_in_sections_module(monkeypatch) -> None:
    seen: list[str] = []

    def fake_renderer(title, results, rule):
        seen.append(title)
        return "\nFAKE OUTPUT\n"

    monkeypatch.setattr(reporting_sections, "render_report_command_output_section", fake_renderer)

    rendered = reporting_sections.full_output_section([_result("beta", "", "")], "SMOKE OUTPUT")

    assert seen == ["SMOKE OUTPUT"]
    assert "FAKE OUTPUT" in rendered
