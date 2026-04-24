from __future__ import annotations

import inspect
from dataclasses import asdict
from pathlib import Path

from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord
from patchops.reporting.command_sections import (
    ReportCommandOutputSection,
    build_report_command_sections,
    render_report_command_output_section,
)
from patchops.reporting.continuation import build_failure_continuation_metadata
from patchops.reporting.metadata import render_report_header
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
    return render_report_header(result)


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


def _backup_line(record: BackupRecord) -> str:
    source = display_path(getattr(record, "source_path", None))
    backup = display_path(getattr(record, "backup_path", None))
    if source == "(none)":
        source = display_path(getattr(record, "path", None))
    if backup == "(none)":
        backup = display_path(getattr(record, "destination_path", None))
    status = str(getattr(record, "status", "") or "").upper()
    if status == "MISSING":
        return f"MISSING: {source}"
    if backup == "(none)":
        return f"BACKUP : {source}"
    return f"BACKUP : {source} -> {backup}"


def backup_section(records: list[BackupRecord]) -> str:
    lines = [_rule("BACKUP")]
    if not records:
        lines.append("(none)")
        return "\n".join(lines)
    lines.extend(_backup_line(record) for record in records)
    return "\n".join(lines)


def _write_line(record: WriteRecord) -> str:
    target = display_path(getattr(record, "target_path", None))
    if target == "(none)":
        target = display_path(getattr(record, "path", None))
    status = str(getattr(record, "status", "") or "").upper()
    if status and status not in {"WROTE", "WRITE"}:
        return f"{status} : {target}"
    return f"WROTE : {target}"


def write_section(records: list[WriteRecord]) -> str:
    lines = [_rule("WRITING FILES")]
    if not records:
        lines.append("(none)")
        return "\n".join(lines)
    lines.extend(_write_line(record) for record in records)
    return "\n".join(lines)


def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)

    sections = build_report_command_sections(results, section_label=title)
    for section in sections:
        lines.extend(
            [
                f"NAME    : {section.command_name}",
                f"COMMAND : {section.command_text}",
                f"CWD     : {section.working_directory}",
                f"EXIT    : {section.exit_code}",
                "",
            ]
        )
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def full_output_section(results: list[CommandResult], title: str) -> str:
    if not results:
        return "\n".join([_rule(title), "(none)"])
    section = ReportCommandOutputSection(
        title=title,
        results=list(results),
        rule=lambda section_title: section_title,
    )
    return render_report_command_output_section(section)


def failure_section(result: WorkflowResult) -> str:
    lines = [_rule("FAILURE DETAILS")]
    metadata = build_failure_continuation_metadata(result)
    if metadata is None:
        lines.append("(none)")
        return "\n".join(lines)

    lines.append(f"Failure Class : {metadata.failure_class}")
    lines.append(f"Failure Reason: {metadata.failure_reason}")
    if metadata.recommended_next_mode:
        lines.append(f"Recommended Next Mode : {metadata.recommended_next_mode}")
    lines.append(f"Category : {metadata.category_display}")
    lines.append(f"Message  : {metadata.message_display}")
    if metadata.details_display:
        lines.append(f"Details  : {metadata.details_display}")
    return "\n".join(lines)

# PATCHOPS_C1A_BACKUP_WRITE_EVIDENCE_SECTIONS_OVERRIDE_20260422
def _patchops_c1a_backup_write_lines(result) -> list[str]:
    lines: list[str] = []

    backup_records = list(getattr(result, "backup_records", ()) or ())
    write_records = list(getattr(result, "write_records", ()) or ())

    for record in backup_records:
        source_path = getattr(record, "source_path", None) or getattr(record, "target_path", None) or getattr(record, "path", None)
        backup_path = getattr(record, "backup_path", None)
        missing = bool(getattr(record, "missing", False) or getattr(record, "was_missing", False))
        if missing and source_path is not None:
            lines.append(f"MISSING: {source_path}")
        elif source_path is not None and backup_path is not None:
            lines.append(f"BACKUP : {source_path} -> {backup_path}")

    for record in write_records:
        target_path = getattr(record, "target_path", None) or getattr(record, "destination_path", None) or getattr(record, "path", None)
        if target_path is None:
            continue
        origin = getattr(record, "content_source", None) or getattr(record, "source_kind", None) or getattr(record, "content_origin", None)
        if origin:
            lines.append(f"WRITE  : {target_path} ({origin})")
        else:
            lines.append(f"WRITE  : {target_path}")

    return lines

try:
    _PATCHOPS_C1A_PREV_RENDER_APPLY_SUMMARY_LINES = render_apply_summary_lines  # type: ignore[name-defined]

    def render_apply_summary_lines(result):  # type: ignore[override]
        lines = list(_PATCHOPS_C1A_PREV_RENDER_APPLY_SUMMARY_LINES(result))
        evidence_lines = _patchops_c1a_backup_write_lines(result)
        if evidence_lines:
            existing = set(lines)
            lines.append("")
            for line in evidence_lines:
                if line not in existing:
                    lines.append(line)
                    existing.add(line)
        return lines
except NameError:
    pass

# PATCHOPS_C1A_BACKUP_WRITE_EVIDENCE_SECTIONS_OVERRIDE_20260423
def _patchops_c1a_backup_write_lines(result) -> list[str]:
    lines: list[str] = []

    backup_records = list(getattr(result, "backup_records", ()) or ())
    write_records = list(getattr(result, "write_records", ()) or ())

    for record in backup_records:
        source_path = (
            getattr(record, "source", None)
            or getattr(record, "source_path", None)
            or getattr(record, "target_path", None)
            or getattr(record, "path", None)
        )
        backup_path = getattr(record, "destination", None) or getattr(record, "backup_path", None)
        existed = getattr(record, "existed", None)
        missing = bool(
            getattr(record, "missing", False)
            or getattr(record, "was_missing", False)
            or existed is False
            or str(getattr(record, "status", "") or "").upper() == "MISSING"
        )

        if missing and source_path is not None:
            lines.append(f"MISSING: {source_path}")
        elif source_path is not None and backup_path is not None:
            lines.append(f"BACKUP : {source_path} -> {backup_path}")

    for record in write_records:
        target_path = (
            getattr(record, "target", None)
            or getattr(record, "target_path", None)
            or getattr(record, "destination_path", None)
            or getattr(record, "path", None)
        )
        if target_path is None:
            continue
        origin = (
            getattr(record, "content_source", None)
            or getattr(record, "source_kind", None)
            or getattr(record, "content_origin", None)
        )
        if origin is not None:
            lines.append(f"WRITE  : {target_path} ({origin})")
        else:
            lines.append(f"WRITE  : {target_path}")

    return lines

# PATCHOPS_PATCH_31_V1_START
_PATCHOPS_MP46_ORIGINAL_FAILURE_SECTION = failure_section


def _patchops_mp46_detect_artifact_path(result) -> str | None:
    for attr_name in (
        "suspicious_run_artifact_path",
        "suspicious_artifact_path",
        "bug_artifact_path",
    ):
        value = getattr(result, attr_name, None)
        if value:
            return str(value)
    return None


def failure_section(result) -> str:
    rendered = _PATCHOPS_MP46_ORIGINAL_FAILURE_SECTION(result)
    artifact_path = _patchops_mp46_detect_artifact_path(result)
    if not artifact_path:
        return rendered

    line = f"Suspicious Run Artifact : {artifact_path}"
    if line in rendered:
        return rendered

    if rendered.endswith("\n"):
        return rendered + line + "\n"
    return rendered + "\n" + line + "\n"
# PATCHOPS_PATCH_31_V1_END
