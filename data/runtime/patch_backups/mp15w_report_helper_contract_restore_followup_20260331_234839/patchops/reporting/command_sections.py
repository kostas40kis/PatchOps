from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from patchops.models import CommandResult


def _display_path(value: str | Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def _command_text_from_result(result: CommandResult) -> str:
    display = getattr(result, "display_command", None)
    if display:
        return str(display)
    program = str(getattr(result, "program", "") or "")
    args = [str(item) for item in getattr(result, "args", [])]
    parts = [program] + args if program else args
    return " ".join(part for part in parts if part)


@dataclass(frozen=True, slots=True)
class ReportCommandSection:
    section_label: str
    command_name: str
    command_text: str
    working_directory: str
    exit_code: int
    stdout: str
    stderr: str
    phase: str = "validation"

    @property
    def name(self) -> str:
        return self.command_name

    @property
    def display_command(self) -> str:
        return self.command_text

    @property
    def stdout_label(self) -> str:
        return f"[{self.command_name}][stdout]"

    @property
    def stderr_label(self) -> str:
        return f"[{self.command_name}][stderr]"


@dataclass(frozen=True, slots=True)
class ReportCommandOutputSection:
    section_label: str
    stdout_label: str
    stdout_text: str
    stderr_label: str
    stderr_text: str


def build_report_command_section(
    result: CommandResult | ReportCommandSection | None = None,
    section_label: str = "FULL OUTPUT",

    command_name: str | None = None,
    command_text: str | None = None,
    working_directory: str | Path | None = None,
    exit_code: int | None = None,
    stdout: str | None = None,
    stderr: str | None = None,
    phase: str | None = None,
) -> ReportCommandSection:
    if isinstance(result, ReportCommandSection):
        return ReportCommandSection(
            section_label=section_label,
            command_name=command_name if command_name is not None else result.command_name,
            command_text=command_text if command_text is not None else result.command_text,
            working_directory=_display_path(working_directory) if working_directory is not None else result.working_directory,
            exit_code=int(exit_code if exit_code is not None else result.exit_code),
            stdout=result.stdout if stdout is None else (stdout or ""),
            stderr=result.stderr if stderr is None else (stderr or ""),
            phase=result.phase if phase is None else phase,
        )

    if result is not None:
        command_name = command_name if command_name is not None else str(result.name)
        command_text = command_text if command_text is not None else _command_text_from_result(result)
        working_directory = working_directory if working_directory is not None else result.working_directory
        exit_code = int(exit_code if exit_code is not None else result.exit_code)
        stdout = result.stdout if stdout is None else stdout
        stderr = result.stderr if stderr is None else stderr
        phase = result.phase if phase is None else phase

    if command_name is None:
        raise ValueError("command_name is required")
    if command_text is None:
        raise ValueError("command_text is required")
    if exit_code is None:
        raise ValueError("exit_code is required")

    return ReportCommandSection(
        section_label=section_label,
        command_name=str(command_name),
        command_text=str(command_text),
        working_directory=_display_path(working_directory),
        exit_code=int(exit_code),
        stdout="" if stdout is None else str(stdout),
        stderr="" if stderr is None else str(stderr),
        phase="validation" if phase is None else str(phase),
    )


def build_report_command_sections(
    results: Iterable[CommandResult | ReportCommandSection],
    section_label: str = "FULL OUTPUT",

) -> list[ReportCommandSection]:
    return [
        build_report_command_section(result=item, section_label=section_label)
        for item in results
    ]


def build_report_command_output_section(
    section: CommandResult | ReportCommandSection | ReportCommandOutputSection,
    *,
    section_label: str | None = None,
) -> ReportCommandOutputSection:
    if isinstance(section, ReportCommandOutputSection):
        if section_label is None or section_label == section.section_label:
            return section
        return ReportCommandOutputSection(
            section_label=section_label,
            stdout_label=section.stdout_label,
            stdout_text=section.stdout_text,
            stderr_label=section.stderr_label,
            stderr_text=section.stderr_text,
        )

    if not isinstance(section, ReportCommandSection):
        if section_label is None:
            raise ValueError("section_label is required when building output from a command result")
        section = build_report_command_section(result=section, section_label=section_label)
    elif section_label is not None and section.section_label != section_label:
        section = build_report_command_section(result=section, section_label=section_label)

    return ReportCommandOutputSection(
        section_label=section.section_label,
        stdout_label=section.stdout_label,
        stdout_text=section.stdout,
        stderr_label=section.stderr_label,
        stderr_text=section.stderr,
    )


def render_report_command_output_section(
    section: CommandResult | ReportCommandSection | ReportCommandOutputSection,
    *,
    section_label: str | None = None,
) -> tuple[str, str, str, str]:
    output = build_report_command_output_section(section, section_label=section_label)
    return (
        output.stdout_label,
        output.stdout_text,
        output.stderr_label,
        output.stderr_text,
    )


def render_command_output_section(
    section: CommandResult | ReportCommandSection | ReportCommandOutputSection,
    *,
    section_label: str | None = None,
) -> tuple[str, str, str, str]:
    return render_report_command_output_section(section, section_label=section_label)


__all__ = [
    "ReportCommandOutputSection",
    "ReportCommandSection",
    "build_report_command_output_section",
    "build_report_command_section",
    "build_report_command_sections",
    "render_command_output_section",
    "render_report_command_output_section",
]