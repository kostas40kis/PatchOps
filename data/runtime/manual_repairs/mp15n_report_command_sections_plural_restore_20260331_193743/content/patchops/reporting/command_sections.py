from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from patchops.models import CommandResult


@dataclass(frozen=True)
class ReportCommandOutputSection:
    command_name: str
    display_command: str
    working_directory: str
    exit_code: int
    stdout: str
    stderr: str


def build_report_command_section(result: CommandResult) -> ReportCommandOutputSection:
    return ReportCommandOutputSection(
        command_name=result.name,
        display_command=result.display_command,
        working_directory=str(result.working_directory) if isinstance(result.working_directory, Path) else str(result.working_directory),
        exit_code=int(result.exit_code),
        stdout=result.stdout if result.stdout else "",
        stderr=result.stderr if result.stderr else "",
    )


def build_report_command_sections(results: list[CommandResult]) -> list[ReportCommandOutputSection]:
    return [build_report_command_section(result) for result in results]


def _render_section_tuple(section: object) -> tuple[str, str, str, str]:
    command_name = str(getattr(section, "command_name"))
    stdout = getattr(section, "stdout", "") or ""
    stderr = getattr(section, "stderr", "") or ""
    return (
        f"[{command_name}][stdout]",
        str(stdout),
        f"[{command_name}][stderr]",
        str(stderr),
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
    for section in build_report_command_sections(results):
        lines.extend(_render_section_tuple(section))
    return "\n".join(lines)


def render_report_command_output_section(*args):
    if len(args) == 1:
        return _render_section_tuple(args[0])
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(str(title), list(results), rule)
    raise TypeError(
        "render_report_command_output_section expected either (section) or (title, results, rule)."
    )


__all__ = [
    "ReportCommandOutputSection",
    "build_report_command_section",
    "build_report_command_sections",
    "render_command_output_section",
    "render_report_command_output_section",
]
