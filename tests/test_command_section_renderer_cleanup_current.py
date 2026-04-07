from __future__ import annotations

from pathlib import Path

from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    build_report_command_section,
    render_report_command_output_section,
)
from patchops.reporting.sections import full_output_section


def _demo_section(section_label: str = "FULL OUTPUT"):
    return build_report_command_section(
        section_label=section_label,
        command_name="demo",
        command_text="py -c \"print('demo')\"",
        working_directory=Path.cwd(),
        exit_code=3,
        stdout="alpha stdout",
        stderr="beta stderr",
        phase="validation",
        classification="required",
    )


def test_full_output_section_matches_shared_command_output_renderer_with_heading_rule() -> None:
    section = _demo_section(section_label="FULL OUTPUT")
    expected = render_report_command_output_section(
        ReportCommandOutputSection(
            title="FULL OUTPUT",
            results=[section],
            rule=lambda title: title,
        )
    )

    actual = full_output_section([section], "FULL OUTPUT")

    assert actual == expected


def test_full_output_section_preserves_labels_and_output_text() -> None:
    section = _demo_section(section_label="FULL OUTPUT")

    actual = full_output_section([section], "FULL OUTPUT")

    assert actual.startswith("FULL OUTPUT")
    assert "[demo][stdout]" in actual
    assert "alpha stdout" in actual
    assert "[demo][stderr]" in actual
    assert "beta stderr" in actual