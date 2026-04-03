from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

from patchops.models import CommandResult


def _display_path(value: Path | str | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


@dataclass(frozen=True)
class ReportCommandSection:
    section_label: str
    command_name: str
    command_text: str
    cwd_text: str
    exit_text: str
    classification: str | None = None


@dataclass(frozen=True)
class ReportCommandOutputSection:
    title: str
    results: tuple[CommandResult, ...]
    rule: Callable[[str], str]

    @property
    def command_name(self) -> str:
        if not self.results:
            return "(none)"
        return self.results[0].name

    @property
    def stdout_text(self) -> str:
        if not self.results:
            return ""
        return self.results[0].stdout or ""

    @property
    def stderr_text(self) -> str:
        if not self.results:
            return ""
        return self.results[0].stderr or ""


def build_report_command_section(
    result: CommandResult,
    section_label: str = "VALIDATION COMMANDS",
    classification: str | None = None,
) -> ReportCommandSection:
    return ReportCommandSection(
        section_label=section_label,
        command_name=result.name,
        command_text=result.display_command,
        cwd_text=_display_path(result.working_directory),
        exit_text=str(result.exit_code),
        classification=classification,
    )


def build_report_command_sections(
    results: Sequence[CommandResult],
    section_label: str = "VALIDATION COMMANDS",
    classifications: Mapping[str, str] | None = None,
) -> tuple[ReportCommandSection, ...]:
    items: list[ReportCommandSection] = []
    for result in results:
        classification = None
        if classifications is not None:
            classification = classifications.get(result.name)
        items.append(
            build_report_command_section(
                result,
                section_label=section_label,
                classification=classification,
            )
        )
    return tuple(items)


def render_command_output_section(
    title: str,
    results: Sequence[CommandResult],
    rule: Callable[[str], str],
) -> str:
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


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        return (
            f"[{section.command_name}][stdout]",
            section.stdout_text if section.stdout_text else "",
            f"[{section.command_name}][stderr]",
            section.stderr_text if section.stderr_text else "",
        )
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, results, rule)
    raise TypeError("render_report_command_output_section expects either a section object or (title, results, rule).")