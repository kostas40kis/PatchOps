from __future__ import annotations

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


def _normalized_output_text(value: str | None) -> str:
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

