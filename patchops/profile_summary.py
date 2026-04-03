from __future__ import annotations

from pathlib import Path

from patchops.models import Manifest
from patchops.profiles.base import PROFILE_FACTORIES, resolve_profile


def _render_path(value: Path | None) -> str | None:
    if value is None:
        return None
    return str(value)


def _stub_manifest(profile_name: str) -> Manifest:
    return Manifest(
        manifest_version="1",
        patch_name="profile_preview",
        active_profile=profile_name,
    )


def list_profile_summaries(wrapper_project_root: str | Path | None = None) -> list[dict]:
    wrapper_root = Path(wrapper_project_root).resolve() if wrapper_project_root else Path(__file__).resolve().parents[1]
    summaries: list[dict] = []

    for profile_name in sorted(PROFILE_FACTORIES):
        manifest = _stub_manifest(profile_name)
        resolved_profile = resolve_profile(manifest, wrapper_root)
        summaries.append(
            {
                "name": resolved_profile.name,
                "default_target_root": _render_path(resolved_profile.default_target_root),
                "runtime_path": _render_path(resolved_profile.runtime_path),
                "backup_root_name": resolved_profile.backup_root_name,
                "report_prefix": resolved_profile.report_prefix,
                "encoding": resolved_profile.encoding,
                "strict_one_report": resolved_profile.strict_one_report,
                "notes": resolved_profile.notes,
            }
        )

    return summaries


def get_profile_summary(profile_name: str, wrapper_project_root: str | Path | None = None) -> dict:
    for item in list_profile_summaries(wrapper_project_root=wrapper_project_root):
        if item["name"] == profile_name:
            return item
    raise ValueError(f"Unknown profile: {profile_name}")