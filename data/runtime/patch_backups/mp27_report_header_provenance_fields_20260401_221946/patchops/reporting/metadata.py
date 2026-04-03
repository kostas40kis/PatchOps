from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from patchops.models import WorkflowResult


@dataclass(slots=True)
class RunOriginMetadata:
    workflow_mode: str
    manifest_path: Path
    active_profile: str | None = None
    resolved_runtime: Path | None = None
    wrapper_project_root: Path | None = None
    target_project_root: Path | None = None


def build_run_origin_metadata(result: WorkflowResult) -> RunOriginMetadata:
    return RunOriginMetadata(
        workflow_mode=result.mode,
        manifest_path=result.manifest_path,
        active_profile=result.resolved_profile.name if result.resolved_profile else None,
        resolved_runtime=result.runtime_path,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
    )


@dataclass(slots=True)
class ReportHeaderMetadata:
    patch_name: str
    timestamp: str | None = None
    workspace_root: Path | None = None
    wrapper_project_root: Path | None = None
    target_project_root: Path | None = None
    active_profile: str | None = None
    runtime_path: Path | None = None
    report_path: Path | None = None
    manifest_path: Path | None = None
    mode: str | None = field(default=None, compare=False)
    backup_root: Path | None = field(default=None, compare=False)
    manifest_version: str | None = field(default=None, compare=False)

    @property
    def manifest_identity(self) -> str | None:
        if self.manifest_path is None:
            return None
        return str(self.manifest_path)


def build_report_header_metadata(
    result: WorkflowResult,
    *,
    timestamp: datetime | None = None,
) -> ReportHeaderMetadata:
    rendered_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp is not None else None
    return ReportHeaderMetadata(
        patch_name=result.manifest.patch_name,
        timestamp=rendered_timestamp,
        workspace_root=result.workspace_root,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
        active_profile=result.resolved_profile.name if result.resolved_profile else None,
        runtime_path=result.runtime_path,
        report_path=result.report_path,
        manifest_path=result.manifest_path,
        mode=result.mode,
        backup_root=result.backup_root,
        manifest_version=str(result.manifest.manifest_version) if result.manifest.manifest_version is not None else None,
    )


def _display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def render_report_header_lines(metadata: ReportHeaderMetadata) -> tuple[str, ...]:
    lines = [
        f"PATCHOPS {(metadata.mode or 'apply').upper()}",
        f"Patch Name           : {metadata.patch_name}",
    ]
    if metadata.timestamp is not None:
        lines.append(f"Timestamp            : {metadata.timestamp}")
    lines.extend(
        [
            f"Manifest Path        : {_display_path(metadata.manifest_path)}",
            f"Workspace Root       : {_display_path(metadata.workspace_root)}",
            f"Wrapper Project Root : {_display_path(metadata.wrapper_project_root)}",
            f"Target Project Root  : {_display_path(metadata.target_project_root)}",
            f"Active Profile       : {metadata.active_profile or '(none)'}",
            f"Runtime Path         : {_display_path(metadata.runtime_path)}",
            f"Backup Root          : {_display_path(metadata.backup_root)}",
            f"Report Path          : {_display_path(metadata.report_path)}",
            f"Manifest Version     : {metadata.manifest_version or '(none)'}",
        ]
    )
    return tuple(lines)


def render_report_header(
    value: WorkflowResult | ReportHeaderMetadata,
    *,
    timestamp: datetime | None = None,
) -> str:
    metadata = value if isinstance(value, ReportHeaderMetadata) else build_report_header_metadata(value, timestamp=timestamp)
    return "\n".join(render_report_header_lines(metadata))
