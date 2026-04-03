from __future__ import annotations

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
    return f"\n{title}\n{'-' * len(title)}"


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
    return "\n".join(lines)


def target_files_section(result: WorkflowResult) -> str:
    lines = [_rule("TARGET FILES")]
    files = [result.target_project_root / spec.path for spec in result.manifest.files_to_write]
    if not files:
        lines.append("(none)")
        return "\n".join(lines)
    for file_path in files:
        lines.append(display_path(file_path))
    return "\n".join(lines)


def backup_section(result: WorkflowResult) -> str:
    lines = [_rule("BACKUP")]
    if not result.backups:
        lines.append("(none)")
        return "\n".join(lines)
    for record in result.backups:
        if record.missing:
            lines.append(f"MISSING: {display_path(record.source)}")
        else:
            lines.append(f"BACKUP : {display_path(record.source)} -> {display_path(record.destination)}")
    return "\n".join(lines)


def writing_files_section(result: WorkflowResult) -> str:
    lines = [_rule("WRITING FILES")]
    if not result.writes:
        lines.append("(none)")
        return "\n".join(lines)
    for record in result.writes:
        lines.append(f"WROTE : {display_path(record.path)}")
    return "\n".join(lines)


def command_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for result in results:
        lines.append(f"NAME    : {result.name}")
        lines.append(f"COMMAND : {result.display_command}")
        lines.append(f"CWD     : {display_path(result.working_directory)}")
        lines.append(f"EXIT    : {result.exit_code}")
    return "\n".join(lines)


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
        return "\n".join([_rule(title), "(none)"])
    section = _ReportCommandOutputSection(title=title, results=list(results), rule=_rule)
    rendered = render_report_command_output_section(section)
    if isinstance(rendered, str):
        return rendered
    return "\n".join(rendered)


def failure_section(result: WorkflowResult) -> str:
    lines = [_rule("FAILURE DETAILS")]
    if result.failure is None:
        lines.append("(none)")
        return "\n".join(lines)
    lines.append(f"Category : {result.failure.category}")
    lines.append(f"Message  : {result.failure.message}")
    return "\n".join(lines)


def summary_section(result: WorkflowResult) -> str:
    lines = [_rule("SUMMARY")]
    lines.append(f"ExitCode : {result.exit_code}")
    lines.append(f"Result   : {result.result_label}")
    return "\n".join(lines)


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

    return "\n".join(sections) + "\n"
