from __future__ import annotations

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
    return f"\n{title}\n{'-' * len(title)}"


def display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def header_section(result: WorkflowResult) -> str:
    return "\n".join(
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
        if record.existed:
            lines.append(f"BACKUP : {display_path(record.source)} -> {display_path(record.destination)}")
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
    for result in results:
        section = build_report_command_section(result)
        lines.extend(render_command_section(section))
    return "\n".join(lines)


def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for result in results:
        section = build_report_command_output_section(result)
        rendered = render_report_command_output_section(section)
        lines.extend(list(rendered))
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
