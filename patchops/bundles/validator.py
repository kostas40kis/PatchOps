from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import BundleMeta, load_bundle_metadata


@dataclass(frozen=True)
class BundleValidationMessage:
    code: str
    message: str
    path: str | None = None
    severity: str = "error"


@dataclass(frozen=True)
class BundleValidationResult:
    bundle_root: Path
    metadata: BundleMeta | None
    errors: tuple[BundleValidationMessage, ...]
    warnings: tuple[BundleValidationMessage, ...] = ()

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _normalize_bundle_relative_path(value: str, field_name: str) -> str:
    text = str(value or "").strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    if not text:
        raise ValueError(f"Bundle relative path '{field_name}' must not be empty.")
    if text.startswith("/") or text.startswith("../") or "/../" in text:
        raise ValueError(
            f"Bundle relative path '{field_name}' must stay relative to the bundle root: {value!r}"
        )
    return text


def _read_manifest_mapping(manifest_path: Path) -> dict[str, Any]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Bundle manifest must be a JSON object.")
    return raw


def validate_extracted_bundle_dir(bundle_root: str | Path) -> BundleValidationResult:
    root = Path(bundle_root)
    errors: list[BundleValidationMessage] = []
    warnings: list[BundleValidationMessage] = []
    metadata: BundleMeta | None = None

    if not root.exists():
        errors.append(
            BundleValidationMessage(
                code="bundle_root_missing",
                message=f"Bundle root does not exist: {root}",
                path=str(root),
            )
        )
        return BundleValidationResult(bundle_root=root, metadata=None, errors=tuple(errors), warnings=tuple(warnings))

    if not root.is_dir():
        errors.append(
            BundleValidationMessage(
                code="bundle_root_not_directory",
                message=f"Bundle root is not a directory: {root}",
                path=str(root),
            )
        )
        return BundleValidationResult(bundle_root=root, metadata=None, errors=tuple(errors), warnings=tuple(warnings))

    default_manifest_path = root / "manifest.json"
    default_meta_path = root / "bundle_meta.json"
    default_content_root = root / "content"
    default_launcher_path = root / "run_with_patchops.ps1"

    duplicate_nested_root = root / root.name
    if duplicate_nested_root.is_dir() and (
        (duplicate_nested_root / "manifest.json").exists()
        or (duplicate_nested_root / "bundle_meta.json").exists()
        or (duplicate_nested_root / "content").exists()
    ):
        errors.append(
            BundleValidationMessage(
                code="duplicate_nested_root",
                message=(
                    "Bundle contains an extra duplicate parent folder inside the bundle root. "
                    f"Nested root candidate: {duplicate_nested_root}"
                ),
                path=str(duplicate_nested_root),
            )
        )

    if not default_manifest_path.exists():
        errors.append(
            BundleValidationMessage(
                code="manifest_missing",
                message="Bundle manifest.json is missing from the bundle root.",
                path=str(default_manifest_path),
            )
        )

    if not default_meta_path.exists():
        errors.append(
            BundleValidationMessage(
                code="bundle_meta_missing",
                message="Bundle bundle_meta.json is missing from the bundle root.",
                path=str(default_meta_path),
            )
        )

    if not default_content_root.is_dir():
        errors.append(
            BundleValidationMessage(
                code="content_root_missing",
                message="Bundle content root is missing from the bundle root.",
                path=str(default_content_root),
            )
        )

    if not default_launcher_path.is_file():
        errors.append(
            BundleValidationMessage(
                code="launcher_missing",
                message="Bundle launcher run_with_patchops.ps1 is missing from the bundle root.",
                path=str(default_launcher_path),
            )
        )

    manifest_path = default_manifest_path

    if default_meta_path.exists():
        try:
            metadata = load_bundle_metadata(default_meta_path)
        except Exception as exc:
            errors.append(
                BundleValidationMessage(
                    code="bundle_meta_invalid",
                    message=f"Bundle metadata could not be parsed: {exc}",
                    path=str(default_meta_path),
                )
            )
        else:
            manifest_path = root / metadata.normalized_manifest_path
            content_root_path = root / metadata.normalized_content_root
            launcher_path = root / metadata.normalized_launcher_path

            if not manifest_path.is_file():
                errors.append(
                    BundleValidationMessage(
                        code="metadata_manifest_missing",
                        message="Bundle metadata points to a manifest path that does not exist.",
                        path=str(manifest_path),
                    )
                )

            if not content_root_path.is_dir():
                errors.append(
                    BundleValidationMessage(
                        code="metadata_content_root_missing",
                        message="Bundle metadata points to a content root that does not exist.",
                        path=str(content_root_path),
                    )
                )

            if not launcher_path.is_file():
                errors.append(
                    BundleValidationMessage(
                        code="metadata_launcher_missing",
                        message="Bundle metadata points to a launcher path that does not exist.",
                        path=str(launcher_path),
                    )
                )

    if manifest_path.is_file():
        try:
            manifest = _read_manifest_mapping(manifest_path)
        except Exception as exc:
            errors.append(
                BundleValidationMessage(
                    code="manifest_invalid",
                    message=f"Bundle manifest could not be parsed: {exc}",
                    path=str(manifest_path),
                )
            )
        else:
            files_to_write = manifest.get("files_to_write", [])
            if not isinstance(files_to_write, list):
                errors.append(
                    BundleValidationMessage(
                        code="files_to_write_invalid",
                        message="Bundle manifest field 'files_to_write' must be a list when present.",
                        path=str(manifest_path),
                    )
                )
            else:
                for index, entry in enumerate(files_to_write):
                    if not isinstance(entry, dict):
                        errors.append(
                            BundleValidationMessage(
                                code="files_to_write_entry_invalid",
                                message=(
                                    "Bundle manifest contains a non-object files_to_write entry at index "
                                    f"{index}."
                                ),
                                path=str(manifest_path),
                            )
                        )
                        continue

                    if entry.get("content") is not None:
                        continue

                    if "content_path" not in entry:
                        continue

                    try:
                        relative_content_path = _normalize_bundle_relative_path(
                            str(entry.get("content_path", "")),
                            f"files_to_write[{index}].content_path",
                        )
                    except ValueError as exc:
                        errors.append(
                            BundleValidationMessage(
                                code="content_path_invalid",
                                message=str(exc),
                                path=str(manifest_path),
                            )
                        )
                        continue

                    candidate = root / relative_content_path
                    if not candidate.exists():
                        errors.append(
                            BundleValidationMessage(
                                code="content_path_missing",
                                message=(
                                    "Bundle manifest references a content_path that does not exist inside the bundle: "
                                    f"{relative_content_path}"
                                ),
                                path=str(candidate),
                            )
                        )

    return BundleValidationResult(
        bundle_root=root,
        metadata=metadata,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
