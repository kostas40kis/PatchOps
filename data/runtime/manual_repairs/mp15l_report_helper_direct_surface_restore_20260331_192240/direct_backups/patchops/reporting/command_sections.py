from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from patchops.models import CommandResult

SectionRule = Callable[[str], str]


@dataclass(slots=True)
class ReportCommandOutputSection:
    title: str
    results: list[CommandResult]
    rule: SectionRule

    @property
    def command_name(self) -> str:
        return self.results[0].name if self.results else ""


def build_report_command_section(
    title: str,
    results: list[CommandResult],
    rule: SectionRule,
) -> ReportCommandOutputSection:
    return ReportCommandOutputSection(title=title, results=list(results), rule=rule)


def build_report_command_output_section(
    title: str,
    results: list[CommandResult],
    rule: SectionRule,
) -> ReportCommandOutputSection:
    return build_report_command_section(title, results, rule)


def render_report_command_output_section(*args) -> str:
    if len(args) == 1:
        section = args[0]
        title = section.title
        results = list(section.results)
        rule = section.rule
    elif len(args) == 3:
        title, results, rule = args
        results = list(results)
    else:
        raise TypeError("render_report_command_output_section expects either (section) or (title, results, rule).")

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


def render_command_output_section(
    title: str,
    results: list[CommandResult],
    rule: SectionRule,
) -> str:
    return render_report_command_output_section(title, results, rule)


__all__ = [
    "ReportCommandOutputSection",
    "build_report_command_output_section",
    "build_report_command_section",
    "render_command_output_section",
    "render_report_command_output_section",
]