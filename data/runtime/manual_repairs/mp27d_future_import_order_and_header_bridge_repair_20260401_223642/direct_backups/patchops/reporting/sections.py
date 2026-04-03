from patchops.reporting.metadata import build_report_header_metadata, render_report_header
from __future__ import annotations

import inspect
from dataclasses import asdict
from pathlib import Path

from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord
from patchops.reporting.command_sections import (
    build_report_command_sections,
    render_report_command_output_section,
)
from patchops.workflows.wrapper_retry import (
    WRAPPER_ONLY_RETRY_KIND,
    build_wrapper_only_retry_state,
    get_active_wrapper_only_retry_reason,
    render_wrapper_only_retry_report_lines,
)


def _rule(title: str) -> str:
    return f"\n{title}\n{'-' * len(title)}"


def display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def header_section(result: WorkflowResult) -> str:
    return render_report_header(build_report_header_metadata(result))

def _build_wrapper_retry_state(result: WorkflowResult):
    manifest_payload = asdict(result.manifest)
    reason = get_active_wrapper_only_retry_reason()
    signature = inspect.signature(build_wrapper_only_retry_state)
    if "reason" in signature.parameters:
        return build_wrapper_only_retry_state(
            manifest_payload,
            result.target_project_root,
            reason=reason,
        )
    return build_wrapper_only_retry_state(
        manifest_payload,
        result.target_project_root,
        reason,
    )


def wrapper_only_retry_section(result: WorkflowResult) -> str:
    if result.mode != WRAPPER_ONLY_RETRY_KIND:
        return ""

    state = _build_wrapper_retry_state(result)
    lines = [_rule("WRAPPER-ONLY RETRY")]
    lines.extend(render_wrapper_only_retry_report_lines(state))
    return "\n".join(lines)


def target_files_section(paths: list[Path]) -> str:
    lines = [_rule("TARGET FILES")]
    if not paths:
        lines.append("(none)")
        return "\n".join(lines)
    lines.extend(display_path(path) for path in paths)
    return "\n".join(lines)


def backup_section(records: list[BackupRecord]) -> str:
    lines = [_rule("BACKUP")]
    if not records:
        lines.append("(none)")
        return "\n".join(lines)
    for record in records:
        if record.existed and record.destination is not None:
            lines.append(
                f"BACKUP : {display_path(record.source)} -> {display_path(record.destination)}"
            )
        else:
            lines.append(f"MISSING: {display_path(record.source)}")
    return "\n".join(lines)


def write_section(records: list[WriteRecord]) -> str:
    lines = [_rule("WRITING FILES")]
    if not records:
        lines.append("(none)")
        return "\n".join(lines)
    lines.extend(f"WROTE : {display_path(record.path)}" for record in records)
    return "\n".join(lines)


def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for section in build_report_command_sections(results, section_label=title):
        lines.append(f"NAME    : {section.command_name}")
        lines.append(f"COMMAND : {section.command_text}")
        lines.append(f"CWD     : {section.working_directory}")
        lines.append(f"EXIT    : {section.exit_code}")
    return "\n".join(lines)


def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for section in build_report_command_sections(results, section_label=title):
        stdout_label, stdout_text, stderr_label, stderr_text = render_report_command_output_section(section)
        lines.append(stdout_label)
        lines.append(stdout_text if stdout_text else "")
        lines.append(stderr_label)
        lines.append(stderr_text if stderr_text else "")
    return "\n".join(lines)


def failure_section(result: WorkflowResult) -> str:
    lines = [_rule("FAILURE DETAILS")]
    if result.failure is None:
        lines.append("(none)")
        return "\n".join(lines)
    lines.append(f"Category : {result.failure.category}")
    lines.append(f"Message  : {result.failure.message}")
    if result.failure.details:
        lines.append(f"Details  : {result.failure.details}")
    return "\n".join(lines)
