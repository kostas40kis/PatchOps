from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

from patchops.models import CommandResult


@dataclass(frozen=True)
class ReportCommandSection:
    section_label: str
    command_name: str
    command_text: str
    working_directory: Path | None
    exit_code: int
    stdout_text: str
    stderr_text: str
    classification: str | None = None

    @property
    def cwd_text(self) -> str:
        if self.working_directory is None:
            return "(none)"
        return str(self.working_directory)

    @property
    def exit_text(self) -> str:
        return str(self.exit_code)


@dataclass(frozen=True)
class ReportCommandOutputSection:
    title: str
    results: Sequence[CommandResult]
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
        return self.results[0].stdout if self.results[0].stdout else ""

    @property
    def stderr_text(self) -> str:
        if not self.results:
            return ""
        return self.results[0].stderr if self.results[0].stderr else ""


def build_report_command_section(
    result: CommandResult,
    section_label: str = "COMMANDS",
    classification: str | None = None,
) -> ReportCommandSection:
    return ReportCommandSection(
        section_label=section_label,
        command_name=result.name,
        command_text=result.display_command,
        working_directory=result.working_directory,
        exit_code=int(result.exit_code),
        stdout_text=result.stdout if result.stdout else "",
        stderr_text=result.stderr if result.stderr else "",
        classification=classification,
    )


def build_report_command_sections(
    results: Sequence[CommandResult],
    section_label: str = "COMMANDS",
    classifications: Mapping[str, str] | None = None,
) -> list[ReportCommandSection]:
    classifications = classifications or {}
    return [
        build_report_command_section(
            result,
            section_label=section_label,
            classification=classifications.get(result.name),
        )
        for result in results
    ]


def _render_output_lines_from_command_section(section: ReportCommandSection) -> list[str]:
    return [
        f"[{section.command_name}][stdout]",
        section.stdout_text if section.stdout_text else "",
        f"[{section.command_name}][stderr]",
        section.stderr_text if section.stderr_text else "",
    ]


def _render_output_lines_from_result(result: CommandResult) -> list[str]:
    return [
        f"[{result.name}][stdout]",
        result.stdout if result.stdout else "",
        f"[{result.name}][stderr]",
        result.stderr if result.stderr else "",
    ]


def render_report_command_output_section(*args) -> str:
    if len(args) == 1:
        section = args[0]
        if isinstance(section, ReportCommandOutputSection):
            lines: list[str] = []
            for result in section.results:
                lines.extend(_render_output_lines_from_result(result))
            return "\n".join(lines)
        if isinstance(section, ReportCommandSection):
            return "\n".join(_render_output_lines_from_command_section(section))
        raise TypeError("Unsupported single-section argument.")

    if len(args) == 3:
        _title, results, _rule = args
        lines: list[str] = []
        for result in results:
            lines.extend(_render_output_lines_from_result(result))
        return "\n".join(lines)

    raise TypeError("render_report_command_output_section expects either one section object or title/results/rule.")


def render_command_output_section(title: str, results: Sequence[CommandResult], rule: Callable[[str], str]) -> str:
    return render_report_command_output_section(title, results, rule)