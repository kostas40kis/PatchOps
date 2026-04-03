from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from patchops.models import CommandResult


@dataclass(frozen=True)
class ReportCommandOutputSection:
    title: str
    results: Sequence[CommandResult]
    rule: Callable[[str], str]

    @property
    def command_name(self) -> str:
        if len(self.results) == 1:
            return self.results[0].name
        if not self.results:
            return self.title
        return self.results[0].name


def _coerce_section(section: object) -> ReportCommandOutputSection:
    if isinstance(section, ReportCommandOutputSection):
        return section
    title = getattr(section, "title", None)
    results = getattr(section, "results", None)
    rule = getattr(section, "rule", None)
    if title is None or results is None or rule is None:
        raise TypeError("Single-argument report helper calls require an object with title, results, and rule.")
    return ReportCommandOutputSection(title=title, results=list(results), rule=rule)


def _render_section_lines(section: ReportCommandOutputSection) -> tuple[str, ...]:
    lines = [section.rule(section.title)]
    if not section.results:
        lines.append("(none)")
        return tuple(lines)
    for result in section.results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
    return tuple(lines)


def render_command_output_section(
    title: str,
    results: Sequence[CommandResult],
    rule: Callable[[str], str],
) -> str:
    section = ReportCommandOutputSection(title=title, results=list(results), rule=rule)
    return "\n".join(_render_section_lines(section))


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = _coerce_section(args[0])
        return _render_section_lines(section)
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, results, rule)
    raise TypeError("render_report_command_output_section expects either one section-like object or title/results/rule.")
