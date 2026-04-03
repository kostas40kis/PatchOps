from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from patchops.models import WorkflowResult


@dataclass(frozen=True)
class ReportHeaderMetadata:
    patch_name: str
    timestamp: str | None
    workspace_root: Path | None
    wrapper_project_root: Path | None
    target_project_root: Path
    active_profile: str
    runtime_path: Path | None
    report_path: Path
    manifest_path: Path | None

    @property
    def manifest_identity(self) -> str | None:
        if self.manifest_path is None:
            return None
        return str(self.manifest_path)


def _normalize_timestamp(value: datetime | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value)


def build_report_header_metadata(
    result: WorkflowResult,
    *,
    timestamp: datetime | str | None = None,
) -> ReportHeaderMetadata:
    return ReportHeaderMetadata(
        patch_name=result.manifest.patch_name,
        timestamp=_normalize_timestamp(timestamp),
        workspace_root=result.workspace_root,
        wrapper_project_root=result.wrapper_project_root,
        target_project_root=result.target_project_root,
        active_profile=result.resolved_profile.name,
        runtime_path=result.runtime_path,
        report_path=result.report_path,
        manifest_path=result.manifest_path,
    )
