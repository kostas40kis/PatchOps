from __future__ import annotations

from pathlib import Path

from patchops.models import BackupRecord, CommandResult, WorkflowResult, WriteRecord


def _rule(title: str) -> str:
    return f"\n{title}\n{'-' * len(title)}"


def header_section(result: WorkflowResult) -> str:
    return "\n".join(
        [
            f"PATCHOPS {result.mode.upper()}",
            f"Patch Name           : {result.manifest.patch_name}",
            f"Workspace Root       : {result.workspace_root if result.workspace_root else '(unknown)'}",
            f"Wrapper Project Root : {result.wrapper_project_root}",
            f"Target Project Root  : {result.target_project_root}",
            f"Active Profile       : {result.resolved_profile.name}",
            f"Runtime Path         : {result.runtime_path if result.runtime_path else '(none)'}",
            f"Backup Root          : {result.backup_root if result.backup_root else '(not used)'}",
            f"Report Path          : {result.report_path}",
            f"Manifest Version     : {result.manifest.manifest_version}",
        ]
    )


def target_files_section(target_paths: list[Path]) -> str:
    lines = [_rule("TARGET FILES")]
    if not target_paths:
        lines.append("(none)")
        return "\n".join(lines)
    lines.extend(str(path) for path in target_paths)
    return "\n".join(lines)


def backup_section(records: list[BackupRecord]) -> str:
    lines = [_rule("BACKUP")]
    if not records:
        lines.append("(none)")
        return "\n".join(lines)
    for record in records:
        if record.existed and record.destination is not None:
            lines.append(f"BACKUP : {record.source} -> {record.destination}")
        else:
            lines.append(f"MISSING: {record.source}")
    return "\n".join(lines)


def write_section(records: list[WriteRecord]) -> str:
    lines = [_rule("WRITING FILES")]
    if not records:
        lines.append("(none)")
        return "\n".join(lines)
    lines.extend(f"WROTE : {record.path}" for record in records)
    return "\n".join(lines)


def command_group_section(title: str, results: list[CommandResult]) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for result in results:
        lines.append(f"NAME    : {result.name}")
        lines.append(f"COMMAND : {result.display_command}")
        lines.append(f"CWD     : {result.working_directory}")
        lines.append(f"EXIT    : {result.exit_code}")
    return "\n".join(lines)


def full_output_section(results: list[CommandResult], title: str) -> str:
    lines = [_rule(title)]
    if not results:
        lines.append("(none)")
        return "\n".join(lines)
    for result in results:
        lines.append(f"[{result.name}][stdout]")
        lines.append(result.stdout if result.stdout else "")
        lines.append(f"[{result.name}][stderr]")
        lines.append(result.stderr if result.stderr else "")
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
