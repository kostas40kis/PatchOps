from __future__ import annotations

from patchops.reporting.sections import (
    backup_section,
    command_group_section,
    failure_section,
    full_output_section,
    header_section,
    target_files_section,
    write_section,
)
from patchops.reporting.summary import render_summary
from patchops.models import WorkflowResult


def render_workflow_report(result: WorkflowResult) -> str:
    all_outputs = [
        *result.validation_results,
        *result.smoke_results,
        *result.audit_results,
        *result.cleanup_results,
        *result.archive_results,
    ]
    sections = [
        header_section(result),
        target_files_section([record.path for record in result.write_records]),
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
        render_summary(result.exit_code, result.result_label),
    ]
    return "\n\n".join(section for section in sections if section)
