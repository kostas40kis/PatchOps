from __future__ import annotations

import json
import sys
from pathlib import Path


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: prepare_mp15i.py <wrapper_root> <working_root>", file=sys.stderr)
        return 2

    wrapper_root = Path(sys.argv[1]).resolve()
    working_root = Path(sys.argv[2]).resolve()

    sections_rel = Path("patchops") / "reporting" / "sections.py"
    command_sections_rel = Path("patchops") / "reporting" / "command_sections.py"

    sections_text = """from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord
from patchops.reporting.command_sections import (
    build_report_command_output_section,
    build_report_command_section,
    render_command_section,
    render_report_command_output_section,
)
from patchops.workflows.wrapper_retry import (
    WRAPPER_ONLY_RETRY_KIND,
    build_wrapper_only_retry_state,
    get_active_wrapper_only_retry_reason,
    render_wrapper_only_retry_report_lines,
)


def _rule(title: str) -> str:
    return f"\\n{title}\\n{'-' * len(title)}"


def display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def header_section(result: WorkflowResult) -> str:
    return "\\n".join(
        [
            f"PATCHOPS {result.mode.upper()}",
            f"Patch Name           : {result.manifest.patch_name}",
            f"Manifest Path        : {display_path(result.manifest_path)}",
            f"Workspace Root       : {display_path(result.workspace_root)}",
            f"Wrapper Project Root : {display_path(result.wrapper_project_root)}",
            f"Target Project Root  : {display_path(result.target_project_root)}",
            f"Active Profile       : {result.manifest.active_profile}",
            f"Runtime Path         : {display_path(result.runtime_path)}",
            f"Backup Root          : {display_path(result.backup_root)}",
            f"Report Path          : {display_path(result.report_path)}",
            f"Manifest Version     : {result.manifest.manifest_version}",
        ]
    )


def wrapper_only_retry_section(result: WorkflowResult) -> str:
    if result.mode != WRAPPER_ONLY_RETRY_KIND:
        return ""

    lines = [_rule("WRAPPER-ONLY RETRY")]
    reason = (get_active_wrapper_only_retry_reason() or "").strip()
    if reason:
        lines.append(f"Reason : {reason}")

    try:
        state = build_wrapper_only_retry_state(result)
    except Exception:
        state = None

    if state is not None:
        payload = asdict(state) if hasattr(state, "__dataclass_fields__") else {}
        if payload:
            if "expected_target_count" in payload:
                lines.append(f"Expected Target Count : {payload['expected_target_count']}")
            if "existing_target_count" in payload:
                lines.append(f"Existing Target Count : {payload['existing_target_count']}")
            if "missing_target_count" in payload:
                lines.append(f"Missing Target Count  : {payload['missing_target_count']}")
            if "stay_narrow" in payload:
                lines.append(f"Stay Narrow           : {'yes' if payload['stay_narrow'] else 'no'}")
            blockers = payload.get("known_blockers") or ()
            if blockers:
                lines.append("Known Blockers")
                for item in blockers:
                    lines.append(f"- {item}")
    return "\\n".join(lines)


def target_files_section(paths: list[Path]) -> str:
    lines = [_rule("TARGET FILES")]
    if not paths:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.extend(display_path(path) for path in paths)
    return "\\n".join(lines)


def backup_section(records: list[BackupRecord]) -> str:
    lines = [_rule("BACKUP")]
    if not records:
        lines.append("(none)")
        return "\\n".join(lines)
    for record in records:
        if record.existed:
            lines.append(f"BACKUP : {display_path(record.source)} -> {display_path(record.destination)}")
        else:
            lines.append(f"MISSING: {display_path(record.source)}")
    return "\\n".join(lines)


def write_section(records: list[WriteRecord]) -> str:
    lines = [_rule("WRITING FILES")]
    if not records:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.extend(f"WROTE : {display_path(record.path)}" for record in records)
    return "\\n".join(lines)


def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        section = build_report_command_section(result)
        lines.extend(render_command_section(section))
    return "\\n".join(lines)


def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\\n".join(lines)
    for result in results:
        section = build_report_command_output_section(result)
        rendered = render_report_command_output_section(section)
        lines.extend(list(rendered))
    return "\\n".join(lines)


def failure_section(result: WorkflowResult) -> str:
    lines = [_rule("FAILURE DETAILS")]
    if result.failure is None:
        lines.append("(none)")
        return "\\n".join(lines)
    lines.append(f"Category : {result.failure.category}")
    lines.append(f"Message  : {result.failure.message}")
    if result.failure.details:
        lines.append(f"Details  : {result.failure.details}")
    return "\\n".join(lines)
"""

    command_sections_text = """from __future__ import annotations

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
        return "\\n".join(lines)
    for result in results:
        lines.extend(_render_output_tuple(build_report_command_output_section(result)))
    return "\\n".join(lines)


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
"""

    write_text(working_root / "content" / sections_rel, sections_text)
    write_text(working_root / "content" / command_sections_rel, command_sections_text)

    validation_targets = [
        "tests/test_reporting.py",
        "tests/test_reporting_command_sections_current.py",
        "tests/test_reporting_output_helper_current.py",
        "tests/test_summary_integrity_current.py",
        "tests/test_summary_derivation_lock_current.py",
        "tests/test_required_vs_tolerated_report_current.py",
        "tests/test_summary_integrity_workflow_current.py",
    ]

    manifest = {
        "manifest_version": "1",
        "patch_name": "mp15i_report_helper_export_restore",
        "active_profile": "generic_python",
        "target_project_root": str(wrapper_root),
        "backup_files": [
            str(sections_rel),
            str(command_sections_rel),
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
        ],
        "validation_commands": [
            {
                "name": "report_helper_restore_pytest",
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
            "report_dir": str((working_root / "inner_reports").resolve()),
            "report_name_prefix": "mp15i_report_helper_export_restore",
            "write_to_desktop": False,
        },
        "tags": ["maintenance", "pythonization", "mp15", "report_helper", "export_restore"],
        "notes": "Narrow MP15 repair. Restore the reporting module exports and keep the shared output helper compatible with both the legacy three-argument call and the reporting.sections monkeypatch contract.",
    }

    manifest_path = working_root / "patch_manifest.json"
    write_text(manifest_path, json.dumps(manifest, indent=2) + "\n")

    prepare_result = [
        "decision=mp15i_report_helper_export_restore",
        f"sections_path={wrapper_root / sections_rel}",
        f"command_sections_path={wrapper_root / command_sections_rel}",
        f"manifest_path={manifest_path}",
        "rationale=Restore command_group_section and build_report_command_section exports while keeping full_output_section monkeypatchable and the shared helper dual-signature compatible.",
        "validation_targets=" + ";".join(validation_targets),
    ]
    write_text(working_root / "prepare_result.txt", "\n".join(prepare_result) + "\n")

    print(str(manifest_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())