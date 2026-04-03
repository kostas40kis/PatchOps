from __future__ import annotations

from patchops.execution.failure_classifier import classify_command_failure
from patchops.models import WorkflowResult
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


def _derive_rendered_summary_state(result: WorkflowResult) -> tuple[int, str]:
    for command_specs, command_results in (
        (result.manifest.validation_commands, result.validation_results),
        (result.manifest.smoke_commands, result.smoke_results),
    ):
        for index, command_result in enumerate(command_results):
            allowed_exit_codes = [0]
            if index < len(command_specs):
                allowed_exit_codes = list(command_specs[index].allowed_exit_codes)
            command_failure = classify_command_failure(command_result, allowed_exit_codes)
            if command_failure is not None:
                return command_result.exit_code, "FAIL"
    return result.exit_code, result.result_label


def render_workflow_report(result: WorkflowResult) -> str:
    target_paths = [
        result.target_project_root / spec.path
        for spec in result.manifest.files_to_write
    ]
    summary_exit_code, summary_result_label = _derive_rendered_summary_state(result)
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
        render_summary(summary_exit_code, summary_result_label),
    ]
    return "\n\n".join(section for section in sections if section)