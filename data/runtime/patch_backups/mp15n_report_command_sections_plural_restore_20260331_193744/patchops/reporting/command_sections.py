from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

from patchops.models import CommandResult


def _display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


@dataclass(frozen=True)
class ReportCommandSection:
    command_name: str
    command_text: str
    working_directory: str
    exit_code: int


@dataclass(frozen=True)
class ReportCommandOutputSection:
    title: str
    results: list[CommandResult]
    rule: Callable[[str], str]

    @property
    def command_name(self) -> str:
        if not self.results:
            return ""
        return self.results[0].name


def build_report_command_section(result: CommandResult) -> ReportCommandSection:
    return ReportCommandSection(
        command_name=result.name,
        command_text=result.display_command,
        working_directory=_display_path(result.working_directory),
        exit_code=int(result.exit_code),
    )


def render_command_output_section(
    title: str,
    results: list[CommandResult],
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
        return render_command_output_section(section.title, list(section.results), section.rule)
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, list(results), rule)
    raise TypeError(
        "render_report_command_output_section expects either "
        "(section) or (title, results, rule)."
    )