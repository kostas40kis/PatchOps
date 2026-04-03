from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

from patchops.models import CommandResult


SectionRule = Callable[[str], str]


def _command_text_from_result(result: CommandResult) -> str:
    display = getattr(result, "display_command", None)
    if display:
        return str(display)
    program = str(getattr(result, "program", "") or "")
    args = [str(item) for item in getattr(result, "args", [])]
    parts = [program] + args if program else args
    return " ".join(part for part in parts if part)


@dataclass(slots=True)
class ReportCommandSection:
    section_label: str
    command_name: str
    command_text: str
    working_directory: str | Path | None
    exit_code: int
    stdout: str
    stderr: str
    phase: str = "validation"
    classification: str | None = None

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


@dataclass(slots=True)
class ReportCommandOutputSection:
    title: str
    results: Sequence[CommandResult | ReportCommandSection]
    rule: SectionRule | None = None


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
    classification: str | None = None,
) -> ReportCommandSection:
    if isinstance(result, ReportCommandSection):
        return ReportCommandSection(
            section_label=section_label,
            command_name=command_name if command_name is not None else result.command_name,
            command_text=command_text if command_text is not None else result.command_text,
            working_directory=working_directory if working_directory is not None else result.working_directory,
            exit_code=int(exit_code if exit_code is not None else result.exit_code),
            stdout=result.stdout if stdout is None else (stdout or ""),
            stderr=result.stderr if stderr is None else (stderr or ""),
            phase=result.phase if phase is None else phase,
            classification=result.classification if classification is None else classification,
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
        working_directory=working_directory,
        exit_code=int(exit_code),
        stdout="" if stdout is None else str(stdout),
        stderr="" if stderr is None else str(stderr),
        phase="validation" if phase is None else str(phase),
        classification=classification,
    )


def build_report_command_sections(
    results: Iterable[CommandResult | ReportCommandSection],
    section_label: str = "FULL OUTPUT",
    classifications: dict[str, str] | None = None,
) -> list[ReportCommandSection]:
    built: list[ReportCommandSection] = []
    for item in results:
        if isinstance(item, ReportCommandSection):
            name = item.command_name
        else:
            name = str(item.name)
        classification = classifications.get(name) if classifications else None
        built.append(
            build_report_command_section(
                result=item,
                section_label=section_label,
                classification=classification,
            )
        )
    return built


def build_report_command_output_section(
    section: CommandResult | ReportCommandSection | ReportCommandOutputSection,
    *,
    section_label: str | None = None,
) -> ReportCommandOutputSection:
    if isinstance(section, ReportCommandOutputSection):
        if section_label is None or section_label == section.title:
            return section
        return ReportCommandOutputSection(
            title=section_label,
            results=section.results,
            rule=section.rule,
        )

    title = section_label
    if isinstance(section, ReportCommandSection):
        title = title or section.section_label
        result_item: CommandResult | ReportCommandSection = build_report_command_section(
            result=section,
            section_label=title,
        )
    else:
        title = title or "FULL OUTPUT"
        result_item = build_report_command_section(
            result=section,
            section_label=title,
        )

    return ReportCommandOutputSection(
        title=title,
        results=[result_item],
        rule=None,
    )


def _extract_single_command_section(
    section: CommandResult | ReportCommandSection | ReportCommandOutputSection,
    *,
    section_label: str | None = None,
) -> ReportCommandSection:
    output_section = build_report_command_output_section(section, section_label=section_label)
    if not output_section.results:
        raise ValueError("ReportCommandOutputSection must contain at least one result")
    if len(output_section.results) != 1:
        raise ValueError("Current report output helper expects exactly one result")
    return build_report_command_section(
        result=output_section.results[0],
        section_label=output_section.title,
    )


def render_report_command_output_section(
    section: CommandResult | ReportCommandSection | ReportCommandOutputSection,
    *,
    section_label: str | None = None,
) -> tuple[str, str, str, str]:
    command_section = _extract_single_command_section(section, section_label=section_label)
    return (
        command_section.stdout_label,
        command_section.stdout,
        command_section.stderr_label,
        command_section.stderr,
    )


def render_command_output_section(
    section_or_title: str | CommandResult | ReportCommandSection | ReportCommandOutputSection,
    results: Sequence[CommandResult | ReportCommandSection] | None = None,
    rule: SectionRule | None = None,
) -> tuple[str, str, str, str]:
    if results is None:
        return render_report_command_output_section(section_or_title)

    if not isinstance(section_or_title, str):
        raise TypeError("section_or_title must be a title string when results are provided")

    section = ReportCommandOutputSection(
        title=section_or_title,
        results=list(results),
        rule=rule,
    )
    return render_report_command_output_section(section)


__all__ = [
    "ReportCommandOutputSection",
    "ReportCommandSection",
    "build_report_command_output_section",
    "build_report_command_section",
    "build_report_command_sections",
    "render_command_output_section",
    "render_report_command_output_section",
]