from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from patchops.models import CommandResult


RuleFn = Callable[[str], str]


@dataclass(slots=True)
class ReportCommandSection:
    section_label: str
    command_name: str
    command_text: str
    working_directory: Path
    exit_code: int
    stdout_text: str
    stderr_text: str
    classification: str | None = None

    @property
    def cwd_text(self) -> str:
        return str(self.working_directory)

    @property
    def exit_text(self) -> str:
        return str(self.exit_code)


@dataclass(slots=True)
class ReportCommandOutputSection:
    title: str
    results: list[CommandResult]
    rule: RuleFn

    @property
    def command_name(self) -> str:
        return self.results[0].name if self.results else "(none)"

    @property
    def stdout_text(self) -> str:
        return self.results[0].stdout if self.results else ""

    @property
    def stderr_text(self) -> str:
        return self.results[0].stderr if self.results else ""


def build_report_command_section(
    result: CommandResult,
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
    results: list[CommandResult],
    section_label: str = "VALIDATION COMMANDS",
    classifications: Mapping[str, str] | None = None,
) -> tuple[ReportCommandSection, ...]:
    classifications = classifications or {}
    return tuple(
        build_report_command_section(
            result,
            section_label=section_label,
            classification=classifications.get(result.name),
        )
        for result in results
    )


def render_command_output_section(title: str, results: list[CommandResult], rule: RuleFn) -> str:
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


def render_report_command_output_section(*args) -> str:
    if len(args) == 1:
        section = args[0]
        if hasattr(section, "title") and hasattr(section, "results") and hasattr(section, "rule"):
            return render_command_output_section(
                str(section.title),
                list(section.results),
                section.rule,
            )
        return "\n".join(
            [
                f"[{section.command_name}][stdout]",
                section.stdout_text if section.stdout_text else "",
                f"[{section.command_name}][stderr]",
                section.stderr_text if section.stderr_text else "",
            ]
        )

    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(str(title), list(results), rule)

    raise TypeError(
        "render_report_command_output_section expects either (section) or (title, results, rule)."
    )
