from __future__ import annotations

from patchops.models import CommandResult, WorkflowResult
from patchops.result_integrity import derive_effective_summary_fields
from patchops.reporting.sections import (
    backup_section,
    command_group_section,
    failure_section,
    full_output_section,
    header_section,
    target_files_section,
    wrapper_only_retry_section,
    write_section,
)
from patchops.reporting.summary import render_summary


def _rule(title: str) -> str:
    return f"\n{title}\n{'-' * len(title)}"


def _safe_output_section(results: list[CommandResult], title: str) -> str:
    if not results:
        return "\n".join([_rule(title), "(none)"])
    return full_output_section(results, title)


def render_workflow_report(result: WorkflowResult) -> str:
    effective = derive_effective_summary_fields(result)
    target_paths = [
        result.target_project_root / spec.path
        for spec in result.manifest.files_to_write
    ]
    sections = [
        header_section(result),
        wrapper_only_retry_section(result),
        target_files_section(target_paths),
        backup_section(result.backup_records),
        write_section(result.write_records),
        command_group_section("VALIDATION COMMANDS", result.validation_results),
        _safe_output_section(result.validation_results, "FULL OUTPUT"),
        command_group_section("SMOKE COMMANDS", result.smoke_results),
        _safe_output_section(result.smoke_results, "SMOKE OUTPUT"),
        command_group_section("AUDIT COMMANDS", result.audit_results),
        _safe_output_section(result.audit_results, "AUDIT OUTPUT"),
        command_group_section("CLEANUP COMMANDS", result.cleanup_results),
        _safe_output_section(result.cleanup_results, "CLEANUP OUTPUT"),
        command_group_section("ARCHIVE COMMANDS", result.archive_results),
        _safe_output_section(result.archive_results, "ARCHIVE OUTPUT"),
        failure_section(result),
        render_summary(int(effective["exit_code"]), str(effective["result_label"])),
    ]
    return "\n\n".join(section for section in sections if section)

# PATCHOPS_C1E_FINAL_SAFE_EVIDENCE_OVERRIDE_20260423
_PATCHOPS_C1E_BASE_RENDER_WORKFLOW_REPORT = render_workflow_report

def _patchops_c1e_record_path(record, *names: str):
    for name in names:
        value = getattr(record, name, None)
        if value is not None:
            return value
    return None


def _patchops_c1e_norm_path(value) -> str | None:
    if value is None:
        return None
    try:
        return str(value).replace(chr(92), "/").lower()
    except Exception:
        return str(value).lower()


def _patchops_c1e_build_file_evidence_lines(result) -> list[str]:
    lines: list[str] = []

    backup_records = list(getattr(result, "backup_records", ()) or ())
    write_records = list(getattr(result, "write_records", ()) or ())

    written_targets: set[str] = set()
    for record in write_records:
        target = _patchops_c1e_record_path(
            record,
            "target",
            "target_path",
            "destination_path",
            "path",
        )
        normalized = _patchops_c1e_norm_path(target)
        if normalized:
            written_targets.add(normalized)

    for record in backup_records:
        source = _patchops_c1e_record_path(
            record,
            "source",
            "source_path",
            "target_path",
            "path",
        )
        destination = _patchops_c1e_record_path(record, "destination", "backup_path")
        existed = getattr(record, "existed", None)
        missing = bool(
            getattr(record, "missing", False)
            or getattr(record, "was_missing", False)
            or existed is False
            or str(getattr(record, "status", "") or "").upper() == "MISSING"
        )

        if missing and source is not None:
            lines.append(f"MISSING: {source}")
        elif source is not None and destination is not None:
            lines.append(f"BACKUP : {source} -> {destination}")

    for record in write_records:
        target = _patchops_c1e_record_path(
            record,
            "target",
            "target_path",
            "destination_path",
            "path",
        )
        if target is None:
            continue
        origin = _patchops_c1e_record_path(
            record,
            "content_source",
            "source_kind",
            "content_origin",
        )
        if origin is not None:
            lines.append(f"WROTE : {target} ({origin})")
        else:
            lines.append(f"WROTE : {target}")

    return lines


def render_workflow_report(result):
    report_text = _PATCHOPS_C1E_BASE_RENDER_WORKFLOW_REPORT(result)
    evidence_lines = _patchops_c1e_build_file_evidence_lines(result)
    if not evidence_lines:
        return report_text

    existing_lines = set(report_text.splitlines())
    pending = [line for line in evidence_lines if line not in existing_lines]
    if not pending:
        return report_text

    evidence_block = "FILE EVIDENCE\n-------------\n" + "\n".join(pending) + "\n\n"

    anchors = [
        "\nFAILURE DETAILS\n---------------\n",
        "\nSUMMARY\n-------\n",
    ]
    for anchor in anchors:
        if anchor in report_text:
            return report_text.replace(anchor, "\n" + evidence_block + anchor, 1)

    return report_text.rstrip() + "\n\n" + evidence_block


# PATCHOPS_D1A_LEGACY_RESULT_SUMMARY_LINE
_PATCHOPS_D1A_BASE_RENDER_WORKFLOW_REPORT = render_workflow_report


def _patchops_d1a_result_label_for_legacy_line(result) -> str:
    try:
        from patchops.result_integrity import derive_effective_summary_fields

        effective = derive_effective_summary_fields(result)
        return str(effective.get("result_label") or getattr(result, "result_label", "UNKNOWN"))
    except Exception:
        return str(getattr(result, "result_label", "UNKNOWN"))


def _patchops_d1a_add_legacy_result_summary_line(report_text: str, result) -> str:
    label = _patchops_d1a_result_label_for_legacy_line(result)
    compact_line = f"Result : {label}"
    canonical_line = f"Result   : {label}"

    if compact_line in report_text:
        return report_text

    if canonical_line in report_text:
        return report_text.replace(canonical_line, canonical_line + "\n" + compact_line, 1)

    summary_anchor = "\nSUMMARY\n-------\n"
    if summary_anchor in report_text:
        return report_text.replace(summary_anchor, summary_anchor + compact_line + "\n", 1)

    return report_text.rstrip() + "\n" + compact_line


def render_workflow_report(result):
    report_text = _PATCHOPS_D1A_BASE_RENDER_WORKFLOW_REPORT(result)
    return _patchops_d1a_add_legacy_result_summary_line(report_text, result)

# PATCHOPS_D1C_RELATIVE_WRITE_PATH_REPORT_COMPAT
_PATCHOPS_D1C_BASE_RENDER_WORKFLOW_REPORT = render_workflow_report


def _patchops_d1c_manifest_write_relative_paths(result) -> list[str]:
    manifest = getattr(result, "manifest", None)
    specs = getattr(manifest, "files_to_write", None) or []
    paths: list[str] = []
    for spec in specs:
        value = getattr(spec, "path", None)
        if value is None and isinstance(spec, dict):
            value = spec.get("path")
        if value is None:
            continue
        rendered = str(value).replace("\\", "/")
        if rendered and rendered not in paths:
            paths.append(rendered)
    return paths


def _patchops_d1c_insert_before_summary(rendered: str, block: str) -> str:
    marker = "\n\nSUMMARY\n-------"
    if marker in rendered:
        return rendered.replace(marker, "\n\n" + block + marker, 1)
    return rendered.rstrip() + "\n\n" + block


def _patchops_d1c_ensure_compact_result_line(rendered: str, result) -> str:
    try:
        effective = derive_effective_summary_fields(result)
        label = str(effective.get("result_label", getattr(result, "result_label", "")))
    except Exception:
        label = str(getattr(result, "result_label", ""))

    if not label:
        return rendered

    compact = f"Result : {label}"
    if compact in rendered:
        return rendered

    canonical = f"Result   : {label}"
    if canonical in rendered:
        return rendered.replace(canonical, canonical + "\n" + compact, 1)

    if rendered.endswith("\n"):
        return rendered + compact
    return rendered + "\n" + compact


def render_workflow_report(result) -> str:
    rendered = _PATCHOPS_D1C_BASE_RENDER_WORKFLOW_REPORT(result)
    relative_paths = _patchops_d1c_manifest_write_relative_paths(result)

    missing_paths = [path for path in relative_paths if path not in rendered]
    if missing_paths:
        lines = ["WRITE RELATIVE PATHS", "--------------------"]
        lines.extend(missing_paths)
        rendered = _patchops_d1c_insert_before_summary(rendered, "\n".join(lines))

    rendered = _patchops_d1c_ensure_compact_result_line(rendered, result)
    return rendered

# PATCHOPS_220_FILE_EVIDENCE_CREATED_VS_MISSING_TRUTH
def _patchops_220_file_evidence_key(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text.replace("\\", "/").rstrip("/").lower()


def _patchops_220_build_file_evidence_lines(result) -> list[str]:
    lines: list[str] = []

    backup_records = list(getattr(result, "backup_records", ()) or ())
    write_records = list(getattr(result, "write_records", ()) or ())

    write_targets: set[str] = set()
    for record in write_records:
        target = (
            getattr(record, "target", None)
            or getattr(record, "target_path", None)
            or getattr(record, "destination_path", None)
            or getattr(record, "path", None)
        )
        key = _patchops_220_file_evidence_key(target)
        if key is not None:
            write_targets.add(key)

    for record in backup_records:
        source = (
            getattr(record, "source", None)
            or getattr(record, "source_path", None)
            or getattr(record, "target_path", None)
            or getattr(record, "path", None)
        )
        destination = getattr(record, "destination", None) or getattr(record, "backup_path", None)
        existed = getattr(record, "existed", None)
        missing = bool(
            getattr(record, "missing", False)
            or getattr(record, "was_missing", False)
            or existed is False
            or str(getattr(record, "status", "") or "").upper() == "MISSING"
        )

        source_key = _patchops_220_file_evidence_key(source)
        if missing and source is not None:
            if source_key is not None and source_key in write_targets:
                lines.append(f"CREATED: {source}")
            else:
                lines.append(f"MISSING: {source}")
        elif source is not None and destination is not None:
            lines.append(f"BACKUP : {source} -> {destination}")

    for record in write_records:
        target = (
            getattr(record, "target", None)
            or getattr(record, "target_path", None)
            or getattr(record, "destination_path", None)
            or getattr(record, "path", None)
        )
        if target is None:
            continue
        origin = (
            getattr(record, "content_source", None)
            or getattr(record, "source_kind", None)
            or getattr(record, "content_origin", None)
        )
        if origin is not None:
            lines.append(f"WROTE : {target} ({origin})")
        else:
            lines.append(f"WROTE : {target}")

    return lines


# The C1E report wrapper looks up this global at render time. Rebinding it here
# preserves the existing wrapper chain while fixing created-vs-missing evidence.
_patchops_c1e_build_file_evidence_lines = _patchops_220_build_file_evidence_lines
# PATCHOPS_220_FILE_EVIDENCE_CREATED_VS_MISSING_TRUTH_END
