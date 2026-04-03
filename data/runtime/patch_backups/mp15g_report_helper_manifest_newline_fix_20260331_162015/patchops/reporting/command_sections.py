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


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        try:
            title = section.title
            results = section.results
            rule = section.rule
        except AttributeError as exc:
            raise TypeError(
                "render_report_command_output_section() single-argument form expects an object with title, results, and rule attributes."
            ) from exc
    elif len(args) == 3:
        title, results, rule = args
    else:
        raise TypeError(
            "render_report_command_output_section() expected 1 or 3 positional arguments."
        )
    return render_command_output_section(title, results, rule)

class ReportCommandOutputSection:
    title: str
    results: list[CommandResult]
    rule: object

    @property
    def command_name(self) -> str:
        if self.results:
            return self.results[0].name
        return self.title


def render_command_output_section(title, results, rule):
    lines = [rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
    return "\n".join(lines)
