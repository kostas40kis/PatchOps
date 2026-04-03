from __future__ import annotations

from patchops.models import WorkflowResult
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
        full_output_section(result.validation_results, "FULL OUTPUT"),
        command_group_section("SMOKE COMMANDS", result.smoke_results),
        full_output_section(result.smoke_results, "SMOKE OUTPUT"),
        command_group_section("AUDIT COMMANDS", result.audit_results),
        full_output_section(result.audit_results, "AUDIT OUTPUT"),
        command_group_section("CLEANUP COMMANDS", result.cleanup_results),
        full_output_section(result.cleanup_results, "CLEANUP OUTPUT"),
        command_group_section("ARCHIVE COMMANDS", result.archive_results),
        full_output_section(result.archive_results, "ARCHIVE OUTPUT"),
        failure_section(result),
        render_summary(int(effective["exit_code"]), str(effective["result_label"])),
    ]
    return "\n\n".join(section for section in sections if section)

