from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .inspector import BundleInspectResult, inspect_bundle_zip
from .models import BundleMeta, ResolvedBundleLayout


@dataclass(frozen=True)
class BundlePlanResult:
    inspect: BundleInspectResult
    backup_targets: tuple[str, ...]
    write_targets: tuple[str, ...]
    validation_command_names: tuple[str, ...]
    resolved_profile: str | None
    target_project_root: str | None
    report_path_preview: str | None

    @property
    def is_valid(self) -> bool:
        return self.inspect.is_valid

    @property
    def bundle_root(self) -> Path:
        return self.inspect.bundle_root

    @property
    def metadata(self) -> BundleMeta | None:
        return self.inspect.metadata

    @property
    def resolved_layout(self) -> ResolvedBundleLayout | None:
        return self.inspect.resolved_layout


def _load_manifest_object(manifest_path: Path) -> dict[str, Any]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Bundle manifest must be a JSON object.")
    return raw


def _collect_write_targets(manifest: dict[str, Any]) -> tuple[str, ...]:
    entries = manifest.get("files_to_write", [])
    if not isinstance(entries, list):
        return ()

    targets: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        target_path = str(entry.get("path") or entry.get("target_path") or "").strip()
        if target_path:
            targets.append(target_path)
    return tuple(targets)


def _collect_validation_command_names(manifest: dict[str, Any]) -> tuple[str, ...]:
    commands = manifest.get("validation_commands", [])
    if not isinstance(commands, list):
        return ()

    names: list[str] = []
    for index, entry in enumerate(commands):
        if isinstance(entry, dict):
            name = str(entry.get("name") or "").strip()
            if name:
                names.append(name)
                continue
        names.append(f"validation_command_{index}")
    return tuple(names)


def _resolve_profile(manifest: dict[str, Any], metadata: BundleMeta | None) -> str | None:
    active_profile = str(manifest.get("active_profile") or "").strip()
    if active_profile:
        return active_profile
    if metadata is not None:
        profile = str(metadata.recommended_profile or "").strip()
        if profile:
            return profile
    return None


def _resolve_target_project_root(manifest: dict[str, Any], metadata: BundleMeta | None) -> str | None:
    target_root = str(manifest.get("target_project_root") or "").strip()
    if target_root:
        return target_root
    if metadata is not None:
        root = str(metadata.target_project_root or "").strip()
        if root:
            return root
    return None


def _build_report_path_preview(patch_name: str | None, run_root: Path) -> str:
    normalized_patch_name = str(patch_name or "bundle_plan").strip() or "bundle_plan"
    return str(run_root / f"{normalized_patch_name}_bundle_plan.txt")


def plan_bundle_zip(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> BundlePlanResult:
    inspect_result = inspect_bundle_zip(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )
    if not inspect_result.is_valid or inspect_result.resolved_layout is None:
        return BundlePlanResult(
            inspect=inspect_result,
            backup_targets=(),
            write_targets=(),
            validation_command_names=(),
            resolved_profile=None,
            target_project_root=None,
            report_path_preview=None,
        )

    manifest = _load_manifest_object(inspect_result.resolved_layout.manifest_path)
    write_targets = _collect_write_targets(manifest)
    validation_command_names = _collect_validation_command_names(manifest)
    patch_name = str(manifest.get("patch_name") or (inspect_result.metadata.patch_name if inspect_result.metadata else "")).strip()
    return BundlePlanResult(
        inspect=inspect_result,
        backup_targets=write_targets,
        write_targets=write_targets,
        validation_command_names=validation_command_names,
        resolved_profile=_resolve_profile(manifest, inspect_result.metadata),
        target_project_root=_resolve_target_project_root(manifest, inspect_result.metadata),
        report_path_preview=_build_report_path_preview(patch_name, inspect_result.check.extraction.run_root),
    )
