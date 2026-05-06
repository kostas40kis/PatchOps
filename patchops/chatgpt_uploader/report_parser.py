from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


_RESULT_RE = re.compile(r"^\s*Result\s*:\s*([A-Za-z_][A-Za-z0-9_-]*)\s*$", re.IGNORECASE)
_EXIT_CODE_RE = re.compile(r"^\s*Exit(?:\s*Code|Code)\s*:\s*(-?\d+)\s*$", re.IGNORECASE)
_FAILURE_CATEGORY_RE = re.compile(r"^\s*Failure\s*Category\s*:\s*(.*)\s*$", re.IGNORECASE)
_FAILURE_CATEGORY_COMPACT_RE = re.compile(r"^\s*FailureCategory\s*:\s*(.*)\s*$", re.IGNORECASE)
_REPORT_PATH_RE = re.compile(r"^\s*(?:Outer\s*)?Report\s*Path\s*:\s*(.+?)\s*$", re.IGNORECASE)
_PATCH_NAME_RE = re.compile(r"^\s*(?:Patch\s*Name|Patch)\s*:\s*(.+?)\s*$", re.IGNORECASE)
_COMMAND_RE = re.compile(r"^\s*(?:COMMAND|Command|name)\s*:?\s*(.+?)\s*$", re.IGNORECASE)
_COMMAND_NAME_JSON_RE = re.compile(r'^\s*"name"\s*:\s*"([^"]+)"\s*,?\s*$')
_ERROR_TYPE_RE = re.compile(
    r"(?P<type>[A-Za-z_][A-Za-z0-9_]*(?:Error|Exception|Failure|Warning))\s*:\s*(?P<message>.+)"
)
_FILE_LINE_RE = re.compile(r'File\s+"(?P<file>[^"]+)",\s+line\s+(?P<line>\d+)(?:,\s+in\s+(?P<function>.+))?')


@dataclass(frozen=True)
class ParsedReport:
    """Compact, JSON-safe summary of a PatchOps canonical report."""

    result: str = "UNKNOWN"
    exit_code: int | None = None
    failure_category: str = ""
    failure_layer: str = "unknown"
    patch_name: str = ""
    report_path: str = ""
    first_failing_command: str = ""
    primary_error_type: str = ""
    primary_error_message: str = ""
    primary_error_file: str = ""
    primary_error_line: int | None = None
    primary_error_function: str = ""
    safety_flags: Mapping[str, str] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    source_path: str = ""

    @property
    def ok(self) -> bool:
        return self.result.upper() == "PASS" and self.exit_code == 0

    def to_payload(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "result": self.result,
            "exit_code": self.exit_code,
            "failure_category": self.failure_category,
            "failure_layer": self.failure_layer,
            "patch_name": self.patch_name,
            "report_path": self.report_path,
            "first_failing_command": self.first_failing_command,
            "primary_error": {
                "type": self.primary_error_type,
                "message": self.primary_error_message,
                "file": self.primary_error_file,
                "line": self.primary_error_line,
                "function": self.primary_error_function,
            },
            "safety_flags": dict(self.safety_flags),
            "warnings": list(self.warnings),
            "source_path": self.source_path,
        }


def _last_nonempty(values: Sequence[str]) -> str:
    for value in reversed(values):
        if value.strip():
            return value.strip()
    return ""


def _first_int(values: Sequence[int | None]) -> int | None:
    for value in values:
        if value is not None:
            return value
    return None


def _normalise_result(value: str) -> str:
    upper = value.strip().upper()
    if upper in {"PASS", "FAIL", "BLOCKED", "UNKNOWN"}:
        return upper
    return value.strip() or "UNKNOWN"


def _extract_key_values(lines: Sequence[str]) -> dict[str, Any]:
    results: list[str] = []
    exit_codes: list[int | None] = []
    failure_categories: list[str] = []
    report_paths: list[str] = []
    patch_names: list[str] = []

    for line in lines:
        if match := _RESULT_RE.match(line):
            results.append(match.group(1))
        if match := _EXIT_CODE_RE.match(line):
            try:
                exit_codes.append(int(match.group(1)))
            except ValueError:
                exit_codes.append(None)
        if match := _FAILURE_CATEGORY_RE.match(line):
            failure_categories.append(match.group(1).strip())
        if match := _FAILURE_CATEGORY_COMPACT_RE.match(line):
            failure_categories.append(match.group(1).strip())
        if match := _REPORT_PATH_RE.match(line):
            report_paths.append(match.group(1).strip())
        if match := _PATCH_NAME_RE.match(line):
            patch_names.append(match.group(1).strip())

    return {
        "result": _normalise_result(_last_nonempty(results) or "UNKNOWN"),
        "exit_code": _first_int(list(reversed(exit_codes))),
        "failure_category": _last_nonempty(failure_categories),
        "report_path": _last_nonempty(report_paths),
        "patch_name": _last_nonempty(patch_names),
    }


def _extract_primary_error(lines: Sequence[str]) -> dict[str, Any]:
    error_type = ""
    error_message = ""
    error_file = ""
    error_line: int | None = None
    error_function = ""

    for index, line in enumerate(lines):
        match = _FILE_LINE_RE.search(line)
        if match:
            error_file = match.group("file").strip()
            try:
                error_line = int(match.group("line"))
            except (TypeError, ValueError):
                error_line = None
            error_function = (match.group("function") or "").strip()

            for follow in lines[index + 1 : min(index + 8, len(lines))]:
                type_match = _ERROR_TYPE_RE.search(follow.strip())
                if type_match:
                    error_type = type_match.group("type").strip()
                    error_message = type_match.group("message").strip()
                    break

    if not error_type:
        for line in lines:
            type_match = _ERROR_TYPE_RE.search(line.strip())
            if type_match:
                error_type = type_match.group("type").strip()
                error_message = type_match.group("message").strip()
                break

    return {
        "primary_error_type": error_type,
        "primary_error_message": error_message,
        "primary_error_file": error_file,
        "primary_error_line": error_line,
        "primary_error_function": error_function,
    }


def _extract_safety_flags(lines: Sequence[str]) -> dict[str, str]:
    flags: dict[str, str] = {}
    wanted = {
        "webdriver_used",
        "selenium_used",
        "browser_dom_automation_used",
        "cloudflare_bypass_attempted",
        "captcha_bypass_attempted",
        "file_upload_attempted",
        "chatgpt_submit_performed",
        "conversation_text_logged",
        "random_page_click_performed",
        "canonical_report_found",
    }
    for line in lines:
        stripped = line.strip().strip("-*")
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if key in wanted:
            flags[key] = value.strip()
    return flags


def _extract_first_failing_command(lines: Sequence[str]) -> str:
    current_command = ""
    json_command = ""
    for line in lines:
        command_match = _COMMAND_RE.match(line)
        if command_match:
            candidate = command_match.group(1).strip().strip('"').rstrip(",")
            if candidate and candidate not in {"{", "}"}:
                current_command = candidate

        json_match = _COMMAND_NAME_JSON_RE.match(line)
        if json_match:
            json_command = json_match.group(1).strip()

        exit_match = _EXIT_CODE_RE.match(line)
        if exit_match:
            try:
                exit_code = int(exit_match.group(1))
            except ValueError:
                continue
            if exit_code != 0 and (current_command or json_command):
                return current_command or json_command

        lowered = line.lower()
        if "timedout" in lowered and "true" in lowered:
            return current_command or json_command
        if "allowed_exit_codes" in lowered:
            continue
        if any(marker in lowered for marker in ("failed command", "validation command failed", "command failed")):
            return current_command or json_command or line.strip()

    return ""


def _classify_failure_layer(*, result: str, exit_code: int | None, failure_category: str, text: str) -> str:
    lowered = text.lower()

    if result.upper() == "PASS" and exit_code == 0:
        return "none"
    if "manifesterror" in lowered or "manifest field" in lowered or "manifest_validation" in lowered:
        return "manifest_validation"
    if "bundle preflight" in lowered and "fail" in lowered:
        return "bundle_shape_preflight"
    if "fatal launcher stderr" in lowered or "traceback" in lowered:
        return "launcher_execution"
    if "pytest" in lowered or "assertionerror" in lowered or "target_validation" in lowered:
        return "target_validation"
    if "canonical report" in lowered and "missing" in lowered:
        return "inner_report_detection"
    if failure_category:
        lowered_category = failure_category.lower()
        if "wrapper" in lowered_category:
            return "wrapper_execution"
        if "environment" in lowered_category:
            return "environment"
        if "authoring" in lowered_category:
            return "package_authoring"
        if "target" in lowered_category:
            return "target_validation"
    return "unknown"


def parse_report_text(text: str, *, source_path: str = "") -> ParsedReport:
    """Parse a PatchOps txt report into a compact summary.

    The parser is intentionally conservative. It extracts what is clearly present and
    leaves unknown fields blank instead of guessing.
    """

    lines = text.splitlines()
    key_values = _extract_key_values(lines)
    primary_error = _extract_primary_error(lines)
    first_failing_command = _extract_first_failing_command(lines)
    safety_flags = _extract_safety_flags(lines)
    warnings: list[str] = []

    result = key_values["result"]
    exit_code = key_values["exit_code"]
    failure_category = key_values["failure_category"]

    if result == "UNKNOWN":
        warnings.append("result_not_found")
    if exit_code is None:
        warnings.append("exit_code_not_found")

    failure_layer = _classify_failure_layer(
        result=result,
        exit_code=exit_code,
        failure_category=failure_category,
        text=text,
    )

    return ParsedReport(
        result=result,
        exit_code=exit_code,
        failure_category=failure_category,
        failure_layer=failure_layer,
        patch_name=key_values["patch_name"],
        report_path=key_values["report_path"],
        first_failing_command=first_failing_command,
        primary_error_type=primary_error["primary_error_type"],
        primary_error_message=primary_error["primary_error_message"],
        primary_error_file=primary_error["primary_error_file"],
        primary_error_line=primary_error["primary_error_line"],
        primary_error_function=primary_error["primary_error_function"],
        safety_flags=safety_flags,
        warnings=tuple(warnings),
        source_path=source_path,
    )


def parse_report_file(path: str | Path, *, encoding: str = "utf-8") -> ParsedReport:
    report_path = Path(path)
    text = report_path.read_text(encoding=encoding, errors="replace")
    parsed = parse_report_text(text, source_path=str(report_path))
    if not parsed.report_path:
        return ParsedReport(
            result=parsed.result,
            exit_code=parsed.exit_code,
            failure_category=parsed.failure_category,
            failure_layer=parsed.failure_layer,
            patch_name=parsed.patch_name,
            report_path=str(report_path),
            first_failing_command=parsed.first_failing_command,
            primary_error_type=parsed.primary_error_type,
            primary_error_message=parsed.primary_error_message,
            primary_error_file=parsed.primary_error_file,
            primary_error_line=parsed.primary_error_line,
            primary_error_function=parsed.primary_error_function,
            safety_flags=parsed.safety_flags,
            warnings=parsed.warnings,
            source_path=parsed.source_path,
        )
    return parsed


def render_text_summary(parsed: ParsedReport) -> str:
    payload = parsed.to_payload()
    primary = payload["primary_error"]
    lines = [
        "PATCHOPS REPORT PARSE SUMMARY",
        "============================",
        f"Result              : {payload['result']}",
        f"ExitCode            : {payload['exit_code'] if payload['exit_code'] is not None else 'unknown'}",
        f"OK                  : {str(payload['ok']).lower()}",
        f"FailureCategory     : {payload['failure_category'] or 'n/a'}",
        f"FailureLayer        : {payload['failure_layer']}",
        f"PatchName           : {payload['patch_name'] or 'n/a'}",
        f"ReportPath          : {payload['report_path'] or 'n/a'}",
        f"FirstFailingCommand : {payload['first_failing_command'] or 'n/a'}",
        "PrimaryError        :",
        f"  Type              : {primary['type'] or 'n/a'}",
        f"  Message           : {primary['message'] or 'n/a'}",
        f"  File              : {primary['file'] or 'n/a'}",
        f"  Line              : {primary['line'] if primary['line'] is not None else 'n/a'}",
        f"Warnings            : {', '.join(payload['warnings']) if payload['warnings'] else 'none'}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse a PatchOps canonical txt report.")
    parser.add_argument("--report", required=True, help="Path to the PatchOps report txt file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of compact text.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero unless parsed result is PASS and ExitCode is 0.")
    args = parser.parse_args(argv)

    parsed = parse_report_file(args.report)
    if args.json:
        print(json.dumps(parsed.to_payload(), indent=2, sort_keys=True))
    else:
        print(render_text_summary(parsed), end="")

    if args.strict and not parsed.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
