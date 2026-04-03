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
    working_directory: Path | None
    exit_code: int


@dataclass(frozen=True)
class ReportCommandOutputSection:
    command_name: str
    stdout: str
    stderr: str


def build_report_command_section(result: CommandResult) -> ReportCommandSection:
    return ReportCommandSection(
        command_name=result.name,
        command_text=result.display_command,
        working_directory=result.working_directory,
        exit_code=int(result.exit_code),
    )


def render_command_section(section: ReportCommandSection) -> tuple[str, ...]:
    return (
        f"NAME    : {section.command_name}",
        f"COMMAND : {section.command_text}",
        f"CWD     : {_display_path(section.working_directory)}",
        f"EXIT    : {section.exit_code}",
    )


def build_report_command_output_section(result: CommandResult) -> ReportCommandOutputSection:
    return ReportCommandOutputSection(
        command_name=result.name,
        stdout=result.stdout if result.stdout else "",
        stderr=result.stderr if result.stderr else "",
    )


def _render_output_tuple(section: ReportCommandOutputSection) -> tuple[str, str, str, str]:
    return (
        f"[{section.command_name}][stdout]",
        section.stdout if section.stdout else "",
        f"[{section.command_name}][stderr]",
        section.stderr if section.stderr else "",
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
        lines.extend(_render_output_tuple(build_report_command_output_section(result)))
    return "\n".join(lines)


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        command_name = getattr(section, "command_name")
        stdout = getattr(section, "stdout", "") or ""
        stderr = getattr(section, "stderr", "") or ""
        return (
            f"[{command_name}][stdout]",
            stdout,
            f"[{command_name}][stderr]",
            stderr,
        )

    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, results, rule)

    raise TypeError("render_report_command_output_section expects either (section) or (title, results, rule).")
