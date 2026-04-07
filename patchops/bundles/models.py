from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

DEFAULT_BUNDLE_META_FILENAME = "bundle_meta.json"
DEFAULT_BUNDLE_MANIFEST_FILENAME = "manifest.json"
DEFAULT_CONTENT_ROOT = "content"
DEFAULT_LAUNCHER_PATH = "run_with_patchops.ps1"


def _normalize_relative_path(value: str, field_name: str) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    if not text:
        raise ValueError(f"Bundle metadata field '{field_name}' must not be empty.")
    if text.startswith("/") or text.startswith("../") or "/../" in text:
        raise ValueError(
            f"Bundle metadata field '{field_name}' must stay relative to the bundle root: {value!r}"
        )
    return text


def _require_non_empty_string(raw: Mapping[str, Any], field_name: str) -> str:
    value = raw.get(field_name)
    text = str(value or "").strip()
    if not text:
        raise ValueError(f"Bundle metadata field '{field_name}' must not be empty.")
    return text


@dataclass(frozen=True)
class BundleMeta:
    bundle_schema_version: int
    patch_name: str
    target_project: str
    recommended_profile: str
    target_project_root: str
    wrapper_project_root: str
    content_root: str = DEFAULT_CONTENT_ROOT
    manifest_path: str = DEFAULT_BUNDLE_MANIFEST_FILENAME
    launcher_path: str = DEFAULT_LAUNCHER_PATH
    created_by: str | None = None

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "BundleMeta":
        if not isinstance(raw, Mapping):
            raise TypeError("Bundle metadata must be loaded from a mapping.")

        required_fields = [
            "bundle_schema_version",
            "patch_name",
            "target_project",
            "recommended_profile",
            "target_project_root",
            "wrapper_project_root",
        ]
        missing = [name for name in required_fields if name not in raw]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"Bundle metadata is missing required field(s): {joined}")

        try:
            bundle_schema_version = int(raw["bundle_schema_version"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Bundle metadata field 'bundle_schema_version' must be an integer.") from exc

        content_root = _normalize_relative_path(raw.get("content_root", DEFAULT_CONTENT_ROOT), "content_root")
        manifest_path = _normalize_relative_path(raw.get("manifest_path", DEFAULT_BUNDLE_MANIFEST_FILENAME), "manifest_path")
        launcher_path = _normalize_relative_path(raw.get("launcher_path", DEFAULT_LAUNCHER_PATH), "launcher_path")
        created_by = raw.get("created_by")
        if created_by is not None:
            created_by = str(created_by).strip() or None

        return cls(
            bundle_schema_version=bundle_schema_version,
            patch_name=_require_non_empty_string(raw, "patch_name"),
            target_project=_require_non_empty_string(raw, "target_project"),
            recommended_profile=_require_non_empty_string(raw, "recommended_profile"),
            target_project_root=_require_non_empty_string(raw, "target_project_root"),
            wrapper_project_root=_require_non_empty_string(raw, "wrapper_project_root"),
            content_root=content_root,
            manifest_path=manifest_path,
            launcher_path=launcher_path,
            created_by=created_by,
        )

    @classmethod
    def from_json_text(cls, text: str) -> "BundleMeta":
        raw = json.loads(text)
        return cls.from_mapping(raw)

    @property
    def normalized_content_root(self) -> str:
        return _normalize_relative_path(self.content_root, "content_root")

    @property
    def normalized_manifest_path(self) -> str:
        return _normalize_relative_path(self.manifest_path, "manifest_path")

    @property
    def normalized_launcher_path(self) -> str:
        return _normalize_relative_path(self.launcher_path, "launcher_path")


@dataclass(frozen=True)
class ExtractedBundleLayout:
    manifest_filename: str = DEFAULT_BUNDLE_MANIFEST_FILENAME
    metadata_filename: str = DEFAULT_BUNDLE_META_FILENAME
    content_root_name: str = DEFAULT_CONTENT_ROOT
    launcher_relative_path: str = DEFAULT_LAUNCHER_PATH

    def required_root_entries(self) -> tuple[str, ...]:
        return (
            self.manifest_filename,
            self.metadata_filename,
            self.content_root_name,
            self.launcher_relative_path.split("/", 1)[0],
        )


@dataclass(frozen=True)
class ResolvedBundleLayout:
    bundle_root: Path
    manifest_path: Path
    metadata_path: Path
    content_root_path: Path
    launcher_path: Path


def build_standard_extracted_bundle_layout() -> ExtractedBundleLayout:
    return ExtractedBundleLayout()


STANDARD_EXTRACTED_BUNDLE_LAYOUT = build_standard_extracted_bundle_layout()


def resolve_bundle_layout(
    bundle_root: str | Path,
    layout: ExtractedBundleLayout | None = None,
) -> ResolvedBundleLayout:
    root = Path(bundle_root)
    active_layout = layout or STANDARD_EXTRACTED_BUNDLE_LAYOUT
    return ResolvedBundleLayout(
        bundle_root=root,
        manifest_path=root / active_layout.manifest_filename,
        metadata_path=root / active_layout.metadata_filename,
        content_root_path=root / active_layout.content_root_name,
        launcher_path=root / active_layout.launcher_relative_path,
    )


def load_bundle_metadata(bundle_meta_path: str | Path) -> BundleMeta:
    metadata_path = Path(bundle_meta_path)
    raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    return BundleMeta.from_mapping(raw)
