from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from patchops.models import CommandResult


RuleFunc = Callable[[str], str]


@dataclass(frozen=True)
class ReportCommandOutputSection:
    title: str
    results: Sequence[CommandResult]
    rule: RuleFunc

    @property
    def command_name(self) -> str:
        if self.results:
            return str(self.results[0].name)
        return "(none)"


def _normalize_output_text(value: str) -> list[str]:
    if not value:
        return [""]
    trimmed = value.rstrip("\n")
    if not trimmed:
        return [""]
    return trimmed.splitlines()


def _body_lines(results: Sequence[CommandResult]) -> list[str]:
    if not results:
        return ["(none)"]

    lines: list[str] = []
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.extend(_normalize_output_text(result.stdout))
        lines.append(f"[{result.name}][stderr]")
        lines.extend(_normalize_output_text(result.stderr))
    return lines


def _header_lines(title: str, rule: RuleFunc) -> list[str]:
    rendered = str(rule(title))
    rendered = rendered.lstrip("\n")
    if not rendered:
        return [title, "-" * len(title)]
    return rendered.splitlines()


def render_command_output_section(title: str, results: Sequence[CommandResult], rule: RuleFunc) -> str:
    return "\n".join([*_header_lines(title, rule), *_body_lines(results)])


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = args[0]
        if not isinstance(section, ReportCommandOutputSection):
            raise TypeError("Single-argument report output rendering requires ReportCommandOutputSection.")
        return tuple(_body_lines(section.results))

    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(str(title), results, rule)

    raise TypeError("render_report_command_output_section() expects either (section) or (title, results, rule).")
