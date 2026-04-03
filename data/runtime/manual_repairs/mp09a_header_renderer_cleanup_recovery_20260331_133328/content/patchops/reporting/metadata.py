from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from patchops.models import WorkflowResult


def _display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


@dataclass(frozen=True)
class ReportHeaderMetadata:
    title_line: str
    patch_name: str
    manifest_path: str
    workspace_root: str
    wrapper_project_root: str
    target_project_root: str
    active_profile: str
    runtime_path: str
    backup_root: str
    report_path: str
    manifest_version: str


def build_report_header_metadata(result: WorkflowResult) -> ReportHeaderMetadata:
    return ReportHeaderMetadata(
        title_line=f"PATCHOPS {result.mode.upper()}",
        patch_name=result.manifest.patch_name,
        manifest_path=_display_path(result.manifest_path),
        workspace_root=_display_path(result.workspace_root),
        wrapper_project_root=_display_path(result.wrapper_project_root),
        target_project_root=_display_path(result.target_project_root),
        active_profile=result.resolved_profile.name,
        runtime_path=_display_path(result.runtime_path),
        backup_root=_display_path(result.backup_root),
        report_path=_display_path(result.report_path),
        manifest_version=str(result.manifest.manifest_version),
    )


def render_report_header(metadata: ReportHeaderMetadata) -> str:
    return "\n".join(
        [
            metadata.title_line,
            f"Patch Name           : {metadata.patch_name}",
            f"Manifest Path        : {metadata.manifest_path}",
            f"Workspace Root       : {metadata.workspace_root}",
            f"Wrapper Project Root : {metadata.wrapper_project_root}",
            f"Target Project Root  : {metadata.target_project_root}",
            f"Active Profile       : {metadata.active_profile}",
            f"Runtime Path         : {metadata.runtime_path}",
            f"Backup Root          : {metadata.backup_root}",
            f"Report Path          : {metadata.report_path}",
            f"Manifest Version     : {metadata.manifest_version}",
        ]
    )
