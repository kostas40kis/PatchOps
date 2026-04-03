from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from patchops.models import WorkflowResult


@dataclass(slots=True)
class ReportHeaderMetadata:
    mode: str
    patch_name: str
    timestamp: datetime | None
    manifest_path: Path | None
    workspace_root: Path | None
    wrapper_project_root: Path | None
    target_project_root: Path | None
    active_profile: str | None
    runtime_path: Path | None
    backup_root: Path | None
    report_path: Path | None
    manifest_version: str | None


def build_report_header_metadata(
    result: WorkflowResult,
    *,
    timestamp: datetime | None = None,
) -> ReportHeaderMetadata:
    return ReportHeaderMetadata(
        mode=result.mode,
        patch_name=result.manifest.patch_name,
        timestamp=timestamp,
        manifest_path=result.manifest_path,
        workspace_root=result.workspace_root,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
        active_profile=result.resolved_profile.name if result.resolved_profile else None,
        runtime_path=result.runtime_path,
        backup_root=result.backup_root,
        report_path=result.report_path,
        manifest_version=result.manifest.manifest_version,
    )


def _display_path(value: Path | None) -> str:
    if value is None:
        return "(none)"
    return str(value)


def render_report_header_lines(metadata: ReportHeaderMetadata) -> tuple[str, ...]:
    lines = [
        f"PATCHOPS {metadata.mode.upper()}",
        f"Patch Name           : {metadata.patch_name}",
    ]
    if metadata.timestamp is not None:
        lines.append(f"Timestamp            : {metadata.timestamp:%Y-%m-%d %H:%M:%S}")
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
