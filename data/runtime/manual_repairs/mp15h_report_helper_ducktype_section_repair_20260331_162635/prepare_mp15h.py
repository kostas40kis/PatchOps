from __future__ import annotations

import json
import sys
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15h.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    sections_rel = Path("patchops") / "reporting" / "sections.py"
    command_sections_rel = Path("patchops") / "reporting" / "command_sections.py"
    helper_test_rel = Path("tests") / "test_reporting_output_helper_current.py"

    sections_text = """from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord
from patchops.reporting.command_sections import render_report_command_output_section
from patchops.workflows.wrapper_retry import (
    WRAPPER_ONLY_RETRY_KIND,
    build_wrapper_only_retry_state,
    get_active_wrapper_only_retry_reason,
    render_wrapper_only_retry_report_lines,
)


def _rule(title: str) -> str:
    return f"\\n{title}\\n{'-' * len(title)}"


def display_path(value: str | Path) -> str:
    if isinstance(value, Path):
        return str(value)
    return value


def header_section(result: WorkflowResult) -> str:
    lines = [f"PATCHOPS {result.mode.upper()}"]
    lines.append(f"Patch Name           : {result.manifest.patch_name}")
    lines.append(f"Manifest Path        : {display_path(result.manifest_path)}")
    lines.append(f"Workspace Root       : {display_path(result.workspace_root)}")
    lines.append(f"Wrapper Project Root : {display_path(result.wrapper_project_root)}")
    lines.append(f"Target Project Root  : {display_path(result.target_project_root)}")
    lines.append(f"Active Profile       : {result.manifest.active_profile}")
    lines.append(f"Runtime Path         : {display_path(result.runtime_path) if result.runtime_path else '(none)'}")
    lines.append(f"Backup Root          : {display_path(result.backup_root)}")
    lines.append(f"Report Path          : {display_path(result.report_path)}")
    lines.append(f"Manifest Version     : {result.manifest.manifest_version}")
    return "\\n".join(lines)


def target_files_section(result: WorkflowResult) -> str:
    lines = [_rule("TARGET FILES")]
    files = [result.target_project_root / spec.path for spec in result.manifest.files_to_write]
    if not files:
        lines.append("(none)")
        return "\\n".join(lines)
    for file_path in files:
        lines.append(display_path(file_path))
    return "\\n".join(lines)


def backup_section(result: WorkflowResult) -> str:
    lines = [_rule("BACKUP")]
    if not result.backups:
        lines.append("(none)")
        return "\\n".join(lines)
    for record in result.backups:
        if record.missing:
            lines.append(f"MISSING: {display_path(record.source)}")
        else:
            lines.append(f"BACKUP : {display_path(record.source)} -> {display_path(record.destination)}")
    return "\\n".join(lines)


def writing_files_section(result: WorkflowResult) -> str:
    lines = [_rule("WRITING FILES")]
    if not result.writes:
        lines.append("(none)")
        return "\\n".join(lines)
    for record in result.writes:
        lines.append(f"WROTE : {display_path(record.path)}")
    return "\\n".join(lines)


def command_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        lines.append(f"NAME    : {result.name}")
        lines.append(f"COMMAND : {result.display_command}")
        lines.append(f"CWD     : {display_path(result.working_directory)}")
        lines.append(f"EXIT    : {result.exit_code}")
    return "\\n".join(lines)


@dataclass(frozen=True)
class _ReportCommandOutputSection:
    title: str
    results: list[CommandResult]
    rule: object

    @property
    def command_name(self) -> str:
        if len(self.results) == 1:
            return self.results[0].name
        if not self.results:
            return self.title
        return self.results[0].name


def full_output_section(results: list[CommandResult], title: str) -> str:
    if not results:
        return "\\n".join([_rule(title), "(none)"])
    section = _ReportCommandOutputSection(title=title, results=list(results), rule=_rule)
    rendered = render_report_command_output_section(section)
    if isinstance(rendered, str):
        return rendered
    return "\\n".join(rendered)


def failure_section(result: WorkflowResult) -> str:
    lines = [_rule("FAILURE DETAILS")]
    if result.failure is None:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.append(f"Category : {result.failure.category}")
    lines.append(f"Message  : {result.failure.message}")
    return "\\n".join(lines)


def summary_section(result: WorkflowResult) -> str:
    lines = [_rule("SUMMARY")]
    lines.append(f"ExitCode : {result.exit_code}")
    lines.append(f"Result   : {result.result_label}")
    return "\\n".join(lines)


def render_workflow_report(result: WorkflowResult) -> str:
    sections = [
        header_section(result),
        "",
        target_files_section(result),
        "",
        backup_section(result),
        "",
        writing_files_section(result),
        "",
        command_section("VALIDATION COMMANDS", result.validation_results),
        "",
        full_output_section(result.validation_results, "FULL OUTPUT"),
        "",
        command_section("SMOKE COMMANDS", result.smoke_results),
        "",
        full_output_section(result.smoke_results, "SMOKE OUTPUT"),
        "",
        command_section("AUDIT COMMANDS", result.audit_results),
        "",
        full_output_section(result.audit_results, "AUDIT OUTPUT"),
        "",
        command_section("CLEANUP COMMANDS", result.cleanup_results),
        "",
        full_output_section(result.cleanup_results, "CLEANUP OUTPUT"),
        "",
        command_section("ARCHIVE COMMANDS", result.archive_results),
        "",
        full_output_section(result.archive_results, "ARCHIVE OUTPUT"),
        "",
        failure_section(result),
        "",
        summary_section(result),
    ]

    if result.mode == WRAPPER_ONLY_RETRY_KIND:
        retry_state = build_wrapper_only_retry_state(result)
        sections.extend(["", _rule("WRAPPER-ONLY RETRY"), *render_wrapper_only_retry_report_lines(retry_state)])

    return "\\n".join(sections) + "\\n"
"""

    command_sections_text = """from __future__ import annotations

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
    return "\\n".join(_render_section_lines(section))


def render_report_command_output_section(*args):
    if len(args) == 1:
        section = _coerce_section(args[0])
        return _render_section_lines(section)
    if len(args) == 3:
        title, results, rule = args
        return render_command_output_section(title, results, rule)
    raise TypeError("render_report_command_output_section expects either one section-like object or title/results/rule.")
"""

    helper_test_text = """from __future__ import annotations

from pathlib import Path

from patchops.models import CommandResult
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    render_command_output_section,
    render_report_command_output_section,
)


def _result(name: str = "alpha", stdout: str = "hello\\n", stderr: str = "warn\\n") -> CommandResult:
    return CommandResult(
        name=name,
        program="py",
        args=["-m", "pytest", "-q", "tests/test_reporting.py"],
        working_directory=Path("."),
        exit_code=0,
        stdout=stdout,
        stderr=stderr,
        display_command="py -m pytest -q tests/test_reporting.py",
        phase="validation",
    )


def test_report_output_helper_alias_matches_base_helper() -> None:
    result = _result("alpha", "hello\\n", "warn\\n")
    rule = lambda title: f"\\n{title}\\n{'-' * len(title)}"

    base = render_command_output_section("FULL OUTPUT", [result], rule)
    alias = render_report_command_output_section("FULL OUTPUT", [result], rule)

    assert alias == base


def test_report_output_helper_single_section_shape_is_available() -> None:
    result = _result("alpha", "hello\\n", "warn\\n")
    rule = lambda title: f"\\n{title}\\n{'-' * len(title)}"
    section = ReportCommandOutputSection(title="FULL OUTPUT", results=[result], rule=rule)

    lines = render_report_command_output_section(section)

    assert isinstance(lines, tuple)
    assert section.command_name == "alpha"
    assert lines[0] == rule("FULL OUTPUT")
    assert lines[1] == "[alpha][stdout]"
    assert lines[2] == "hello\\n"
    assert lines[3] == "[alpha][stderr]"
    assert lines[4] == "warn\\n"
"""

    write_text(working_root / "content" / sections_rel, sections_text)
    write_text(working_root / "content" / command_sections_rel, command_sections_text)
    write_text(working_root / "content" / helper_test_rel, helper_test_text)

    validation_targets = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_reporting_output_helper_current.py",
        "tests/test_summary_integrity_current.py",
        "tests/test_summary_derivation_lock_current.py",
        "tests/test_required_vs_tolerated_report_current.py",
        "tests/test_summary_integrity_workflow_current.py",
    ]

    manifest_data = {
        "manifest_version": "1",
        "patch_name": "mp15h_report_helper_ducktype_section_repair",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root),
        "backup_files": [
            str(sections_rel),
            str(command_sections_rel),
            str(helper_test_rel),
        ],
        "files_to_write": [
            {
                "path": str(sections_rel),
                "content_path": "content/patchops/reporting/sections.py",
                "encoding": "utf-8",
            },
            {
                "path": str(command_sections_rel),
                "content_path": "content/patchops/reporting/command_sections.py",
                "encoding": "utf-8",
            },
            {
                "path": str(helper_test_rel),
                "content_path": "content/tests/test_reporting_output_helper_current.py",
                "encoding": "utf-8",
            },
        ],
        "validation_commands": [
            {
                "name": "report_helper_ducktype_pytest",
                "program": "python",
                "args": ["-m", "pytest", "-q", *validation_targets],
                "working_directory": ".",
                "use_profile_runtime": False,
                "allowed_exit_codes": [0],
            }
        ],
        "smoke_commands": [],
        "audit_commands": [],
        "cleanup_commands": [],
        "archive_commands": [],
        "failure_policy": {},
        "report_preferences": {
            "report_dir": str((working_root / "inner_reports")),
            "report_name_prefix": "mp15h_report_helper_ducktype_section_repair",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "ducktype"],
        "notes": "Narrow MP15 repair. Keep command_sections as the reusable helper surface and let reporting.sections pass a monkeypatchable duck-typed section object.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest_data, indent=2) + "\n")

    prepare_result_text = "\n".join([
        "decision=mp15h_report_helper_ducktype_section_repair",
        f"sections_path={wrapper_root / sections_rel}",
        f"command_sections_path={wrapper_root / command_sections_rel}",
        f"manifest_path={manifest_path}",
        "rationale=Repair MP15 by separating the public helper dataclass from the private reporting.sections wrapper object and using duck-typed single-section handling.",
        "validation_targets=" + ";".join(validation_targets),
    ]) + "\n"
    write_text(working_root / "prepare_result.txt", prepare_result_text)
    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())