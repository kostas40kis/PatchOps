from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .checker import BundleCheckResult, check_bundle_zip
from .models import BundleMeta, ResolvedBundleLayout, resolve_bundle_layout


@dataclass(frozen=True)
class BundleInspectResult:
    check: BundleCheckResult
    resolved_layout: ResolvedBundleLayout | None
    target_paths: tuple[str, ...]
    validation_command_names: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return self.check.is_valid

    @property
    def bundle_root(self) -> Path:
        return self.check.bundle_root

    @property
    def metadata(self) -> BundleMeta | None:
        return self.check.metadata


def _load_manifest_object(manifest_path: Path) -> dict[str, Any]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Bundle manifest must be a JSON object.")
    return raw


def _collect_target_paths(manifest: dict[str, Any]) -> tuple[str, ...]:
    entries = manifest.get("files_to_write", [])
    if not isinstance(entries, list):
        return ()

    target_paths: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        target_path = str(entry.get("target_path") or "").strip()
        if target_path:
            target_paths.append(target_path)
    return tuple(target_paths)


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


def inspect_bundle_zip(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path,
    *,
    timestamp_token: str | None = None,
) -> BundleInspectResult:
    check_result = check_bundle_zip(
        bundle_zip_path,
        wrapper_project_root,
        timestamp_token=timestamp_token,
    )
    if not check_result.is_valid:
        return BundleInspectResult(
            check=check_result,
            resolved_layout=None,
            target_paths=(),
            validation_command_names=(),
        )

    resolved_layout = resolve_bundle_layout(check_result.bundle_root)
    manifest = _load_manifest_object(resolved_layout.manifest_path)
    return BundleInspectResult(
        check=check_result,
        resolved_layout=resolved_layout,
        target_paths=_collect_target_paths(manifest),
        validation_command_names=_collect_validation_command_names(manifest),
    )
