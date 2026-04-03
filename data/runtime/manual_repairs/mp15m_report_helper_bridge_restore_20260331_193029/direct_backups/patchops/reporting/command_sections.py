from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from patchops.models import CommandResult

SectionRule = Callable[[str], str]


@dataclass(slots=True)
class ReportCommandOutputSection:
    title: str
    command_name: str
    stdout: str
    stderr: str
    rule: SectionRule


def _coerce_first_result(result_or_results: CommandResult | Iterable[CommandResult]) -> CommandResult | None:
    if isinstance(result_or_results, CommandResult):
        return result_or_results
    for item in result_or_results:
        return item
    return None


def build_report_command_section(
    title: str,
    result_or_results: CommandResult | Iterable[CommandResult],
    rule: SectionRule,
) -> ReportCommandOutputSection:
    result = _coerce_first_result(result_or_results)
    if result is None:
        return ReportCommandOutputSection(title=title, command_name="", stdout="", stderr="", rule=rule)
    return ReportCommandOutputSection(
        title=title,
        command_name=result.name,
        stdout=result.stdout if result.stdout else "",
        stderr=result.stderr if result.stderr else "",
        rule=rule,
    )


def build_report_command_output_section(
    title: str,
    result_or_results: CommandResult | Iterable[CommandResult],
    rule: SectionRule,
) -> ReportCommandOutputSection:
    return build_report_command_section(title, result_or_results, rule)


def _render_single_section(section: ReportCommandOutputSection) -> tuple[str, str, str, str]:
    return (
        f"[{section.command_name}][stdout]",
        section.stdout if section.stdout else "",
        f"[{section.command_name}][stderr]",
        section.stderr if section.stderr else "",
    )


def render_command_output_section(
    title: str,
    results: list[CommandResult],
    rule: SectionRule,
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
        return _render_single_section(args[0])
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, list(results), rule)
    raise TypeError("render_report_command_output_section expects either (section) or (title, results, rule).")


__all__ = [
    "ReportCommandOutputSection",
    "build_report_command_output_section",
    "build_report_command_section",
    "render_command_output_section",
    "render_report_command_output_section",
]