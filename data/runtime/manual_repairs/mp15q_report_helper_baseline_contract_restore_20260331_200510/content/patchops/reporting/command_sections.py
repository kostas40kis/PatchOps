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
        return "(none)" if self.working_directory is None else str(self.working_directory)

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
        return self.results[0].name if self.results else ""

    @property
    def stdout_text(self) -> str:
        return self.results[0].stdout if self.results else ""

    @property
    def stderr_text(self) -> str:
        return self.results[0].stderr if self.results else ""


def build_report_command_section(
    result: CommandResult,
    *,
    section_label: str = "VALIDATION COMMANDS",
    classification: str | None = None,
) -> ReportCommandSection:
    return ReportCommandSection(
        section_label=section_label,
        command_name=result.name,
        command_text=result.display_command,
        working_directory=result.working_directory,
        exit_code=result.exit_code,
        stdout_text=result.stdout,
        stderr_text=result.stderr,
        classification=classification,
    )


def build_report_command_sections(
    results: Iterable[CommandResult],
    *,
    section_label: str = "VALIDATION COMMANDS",
    classifications: Mapping[str, str] | None = None,
) -> list[ReportCommandSection]:
    classification_map = classifications or {}
    return [
        build_report_command_section(
            result,
            section_label=section_label,
            classification=classification_map.get(result.name),
        )
        for result in results
    ]


def _render_output_from_command_section(section: ReportCommandSection) -> str:
    return "\n".join(
        [
            f"[{section.command_name}][stdout]",
            section.stdout_text if section.stdout_text else "",
            f"[{section.command_name}][stderr]",
            section.stderr_text if section.stderr_text else "",
        ]
    )


def _render_output_from_output_section(section: ReportCommandOutputSection) -> str:
    lines = [section.rule(section.title)]
    if not section.results:
        lines.append("(none)")
        return "\n".join(lines)
    for result in section.results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
    return "\n".join(lines)


def render_report_command_output_section(*args) -> str:
    if len(args) == 1:
        section = args[0]
        if isinstance(section, ReportCommandOutputSection):
            return _render_output_from_output_section(section)
        if isinstance(section, ReportCommandSection):
            return _render_output_from_command_section(section)
        if hasattr(section, "results") and hasattr(section, "title") and hasattr(section, "rule"):
            return _render_output_from_output_section(
                ReportCommandOutputSection(
                    title=section.title,
                    results=section.results,
                    rule=section.rule,
                )
            )
        if hasattr(section, "command_name") and hasattr(section, "stdout_text") and hasattr(section, "stderr_text"):
            return _render_output_from_command_section(
                ReportCommandSection(
                    section_label=getattr(section, "section_label", "FULL OUTPUT"),
                    command_name=section.command_name,
                    command_text=getattr(section, "command_text", ""),
                    working_directory=getattr(section, "working_directory", None),
                    exit_code=getattr(section, "exit_code", 0),
                    stdout_text=section.stdout_text,
                    stderr_text=section.stderr_text,
                    classification=getattr(section, "classification", None),
                )
            )
        raise TypeError("Unsupported section object for render_report_command_output_section().")

    if len(args) == 3:
        title, results, rule = args
        return _render_output_from_output_section(
            ReportCommandOutputSection(title=title, results=list(results), rule=rule)
        )

    raise TypeError("render_report_command_output_section() accepts either one section object or title/results/rule.")