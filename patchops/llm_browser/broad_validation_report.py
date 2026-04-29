"""Parser for PatchOps llm-browser broad-validation reports.

The broad-validation PowerShell script writes a plain text report. This module
turns that report into a compact structured summary so operators can quickly
check result, failing commands, timeouts, and report location.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_SECTION_LINE_RE = re.compile(r"^={20,}$")
_KEY_VALUE_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9 ]*?)\s*:\s*(?P<value>.*)$")


@dataclass(frozen=True)
class ParsedBroadValidationCommand:
    label: str
    cwd: str | None
    command: str | None
    timeout_seconds: int | None
    timed_out: bool | None
    exit_code: str | None
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.timed_out is False and self.exit_code == "0"

    def to_payload(self) -> dict[str, object]:
        return {
            "label": self.label,
            "ok": self.ok,
            "cwd": self.cwd,
            "command": self.command,
            "timeout_seconds": self.timeout_seconds,
            "timed_out": self.timed_out,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


@dataclass(frozen=True)
class ParsedBroadValidationReport:
    path: Path | None
    result: str | None
    exit_code: str | None
    mode: str | None
    report_path: str | None
    command_count_reported: int | None
    commands: tuple[ParsedBroadValidationCommand, ...]
    failures: tuple[str, ...]

    @property
    def ok(self) -> bool:
        if self.result is None:
            return False
        return self.result.upper() == "PASS" and (self.exit_code in {None, "0"})

    @property
    def failed_commands(self) -> tuple[ParsedBroadValidationCommand, ...]:
        return tuple(command for command in self.commands if not command.ok)

    @property
    def timed_out_commands(self) -> tuple[ParsedBroadValidationCommand, ...]:
        return tuple(command for command in self.commands if command.timed_out is True)

    def to_payload(self) -> dict[str, object]:
        return {
            "path": None if self.path is None else str(self.path),
            "ok": self.ok,
            "result": self.result,
            "exit_code": self.exit_code,
            "mode": self.mode,
            "report_path": self.report_path,
            "command_count_reported": self.command_count_reported,
            "command_count_parsed": len(self.commands),
            "failed_command_count": len(self.failed_commands),
            "timed_out_command_count": len(self.timed_out_commands),
            "failures": list(self.failures),
            "commands": [command.to_payload() for command in self.commands],
        }


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    text = value.strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def _parse_int_from_text(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.search(r"-?\d+", value)
    if not match:
        return None
    return int(match.group(0))


def _extract_key_values(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in lines:
        match = _KEY_VALUE_RE.match(line)
        if match:
            values[match.group("key").strip().lower()] = match.group("value").strip()
    return values


def _extract_block(lines: list[str], start_marker: str, stop_markers: tuple[str, ...]) -> str:
    try:
        start = lines.index(start_marker) + 1
    except ValueError:
        return ""

    end = len(lines)
    for marker in stop_markers:
        try:
            candidate = lines.index(marker, start)
        except ValueError:
            continue
        end = min(end, candidate)

    return "\n".join(lines[start:end]).strip()


def _iter_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    sections: list[tuple[str, list[str]]] = []
    index = 0
    while index < len(lines):
        if not _SECTION_LINE_RE.match(lines[index].strip()):
            index += 1
            continue

        if index + 2 >= len(lines):
            index += 1
            continue

        title = lines[index + 1].strip()
        if not _SECTION_LINE_RE.match(lines[index + 2].strip()):
            index += 1
            continue

        content_start = index + 3
        content_end = len(lines)
        search = content_start
        while search < len(lines):
            if _SECTION_LINE_RE.match(lines[search].strip()):
                content_end = search
                break
            search += 1

        sections.append((title, lines[content_start:content_end]))
        index = content_end

    return sections


def _parse_command_section(title: str, lines: list[str]) -> ParsedBroadValidationCommand:
    label = title.replace("COMMAND:", "", 1).strip()
    values = _extract_key_values(lines)

    stdout = _extract_block(lines, "--- STDOUT ---", ("--- STDERR ---", "--- EXCEPTION ---"))
    stderr = _extract_block(lines, "--- STDERR ---", ("--- EXCEPTION ---",))

    return ParsedBroadValidationCommand(
        label=label,
        cwd=values.get("cwd"),
        command=values.get("command"),
        timeout_seconds=_parse_int_from_text(values.get("timeout")),
        timed_out=_parse_bool(values.get("timedout")),
        exit_code=values.get("exitcode"),
        stdout=stdout,
        stderr=stderr,
    )


def parse_broad_validation_report_text(text: str, *, path: str | Path | None = None) -> ParsedBroadValidationReport:
    lines = text.splitlines()
    sections = _iter_sections(lines)

    commands: list[ParsedBroadValidationCommand] = []
    summary_values: dict[str, str] = {}
    failures: list[str] = []
    in_failures = False

    for title, content in sections:
        if title.startswith("COMMAND:"):
            commands.append(_parse_command_section(title, content))
            continue

        if title == "SUMMARY":
            summary_values = _extract_key_values(content)
            for line in content:
                stripped = line.strip()
                if stripped == "Failures:":
                    in_failures = True
                    continue
                if in_failures:
                    if stripped.startswith("- "):
                        failures.append(stripped[2:].strip())
                    elif stripped:
                        in_failures = False

    command_count_reported = _parse_int_from_text(summary_values.get("commands captured"))

    return ParsedBroadValidationReport(
        path=None if path is None else Path(path),
        result=summary_values.get("result"),
        exit_code=summary_values.get("exitcode"),
        mode=summary_values.get("mode"),
        report_path=summary_values.get("reportpath"),
        command_count_reported=command_count_reported,
        commands=tuple(commands),
        failures=tuple(failures),
    )


def parse_broad_validation_report_file(path: str | Path) -> ParsedBroadValidationReport:
    report_path = Path(path)
    text = report_path.read_text(encoding="utf-8", errors="replace")
    return parse_broad_validation_report_text(text, path=report_path)


def render_broad_validation_report_summary(report: ParsedBroadValidationReport) -> str:
    lines: list[str] = []
    lines.append("Broad validation report summary")
    lines.append(f"Path       : {report.path}")
    lines.append(f"Result     : {report.result or 'UNKNOWN'}")
    lines.append(f"ExitCode   : {report.exit_code or 'UNKNOWN'}")
    lines.append(f"Mode       : {report.mode or 'UNKNOWN'}")
    lines.append(f"OK         : {str(report.ok).lower()}")
    lines.append(f"Commands   : {len(report.commands)} parsed")
    lines.append(f"Failed     : {len(report.failed_commands)}")
    lines.append(f"TimedOut   : {len(report.timed_out_commands)}")
    lines.append("")

    if report.failures:
        lines.append("Failures:")
        for failure in report.failures:
            lines.append(f"- {failure}")
        lines.append("")

    if report.failed_commands:
        lines.append("Failed commands:")
        for command in report.failed_commands:
            lines.append(f"- {command.label}: exit={command.exit_code} timed_out={str(command.timed_out).lower()}")
        lines.append("")

    return "\n".join(lines)
