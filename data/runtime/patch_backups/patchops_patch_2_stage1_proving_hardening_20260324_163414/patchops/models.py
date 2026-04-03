from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


FailureCategory = Literal[
    "success",
    "target_project_failure",
    "wrapper_failure",
    "target_project_policy_failure",
]


@dataclass(slots=True)
class FileWriteSpec:
    path: str
    content: str | None = None
    content_path: str | None = None
    encoding: str = "utf-8"


@dataclass(slots=True)
class CommandSpec:
    name: str
    program: str | None = None
    args: list[str] = field(default_factory=list)
    working_directory: str | None = None
    use_profile_runtime: bool = False
    allowed_exit_codes: list[int] = field(default_factory=lambda: [0])


@dataclass(slots=True)
class ReportPreferences:
    report_dir: str | None = None
    report_name_prefix: str | None = None
    write_to_desktop: bool = True


@dataclass(slots=True)
class Manifest:
    manifest_version: str
    patch_name: str
    active_profile: str
    target_project_root: str | None = None
    backup_files: list[str] = field(default_factory=list)
    files_to_write: list[FileWriteSpec] = field(default_factory=list)
    validation_commands: list[CommandSpec] = field(default_factory=list)
    smoke_commands: list[CommandSpec] = field(default_factory=list)
    audit_commands: list[CommandSpec] = field(default_factory=list)
    cleanup_commands: list[CommandSpec] = field(default_factory=list)
    archive_commands: list[CommandSpec] = field(default_factory=list)
    failure_policy: dict[str, Any] = field(default_factory=dict)
    report_preferences: ReportPreferences = field(default_factory=ReportPreferences)
    tags: list[str] = field(default_factory=list)
    notes: str | None = None


@dataclass(slots=True)
class ResolvedProfile:
    name: str
    default_target_root: Path | None
    runtime_path: Path | None
    backup_root_name: str = "data/runtime/patch_backups"
    report_prefix: str = "patchops"
    encoding: str = "utf-8"
    strict_one_report: bool = True
    notes: str | None = None


@dataclass(slots=True)
class BackupRecord:
    source: Path
    destination: Path | None
    existed: bool


@dataclass(slots=True)
class WriteRecord:
    path: Path
    encoding: str


@dataclass(slots=True)
class CommandResult:
    name: str
    program: str
    args: list[str]
    working_directory: Path
    exit_code: int
    stdout: str
    stderr: str
    display_command: str
    phase: str = "validation"


@dataclass(slots=True)
class FailureInfo:
    category: FailureCategory
    message: str
    details: str | None = None


@dataclass(slots=True)
class WorkflowResult:
    mode: str
    manifest: Manifest
    resolved_profile: ResolvedProfile
    workspace_root: Path | None
    wrapper_project_root: Path
    target_project_root: Path
    runtime_path: Path | None
    backup_root: Path | None
    report_path: Path
    backup_records: list[BackupRecord]
    write_records: list[WriteRecord]
    validation_results: list[CommandResult]
    smoke_results: list[CommandResult]
    audit_results: list[CommandResult]
    cleanup_results: list[CommandResult]
    archive_results: list[CommandResult]
    failure: FailureInfo | None
    exit_code: int
    result_label: str
