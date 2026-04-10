from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import BundleMeta, load_bundle_metadata


_ROOT_SINGLE_LAUNCHER = "run_with_patchops.ps1"
_LEGACY_APPLY_LAUNCHER = "launchers/apply_with_patchops.ps1"
_LEGACY_VERIFY_LAUNCHER = "launchers/verify_with_patchops.ps1"
_POWERSHELL_TOKENS_IN_PYTHON_HELPER = (
    "[CmdletBinding",
    "Write-Host",
    "Set-Location",
    "Start-Process",
    "powershell.exe",
    "powershell.EXE",
    "$args",
    "$PSScriptRoot",
    "$PSCommandPath",
)


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


def _unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve()) if path.exists() else str(path)
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def _supported_launcher_candidates(root: Path, *, metadata: BundleMeta | None, raw_meta: dict[str, Any] | None) -> list[Path]:
    candidates: list[Path] = [
        root / _ROOT_SINGLE_LAUNCHER,
        root / _LEGACY_APPLY_LAUNCHER,
        root / _LEGACY_VERIFY_LAUNCHER,
    ]
    if metadata is not None:
        candidates.append(root / metadata.normalized_launcher_path)
    launchers = raw_meta.get("launchers") if isinstance(raw_meta, dict) else None
    if isinstance(launchers, dict):
        for mode in ("apply", "verify"):
            value = launchers.get(mode)
            if isinstance(value, str) and value.strip():
                try:
                    candidates.append(root / _normalize_bundle_relative_path(value, f"launchers.{mode}"))
                except ValueError:
                    continue
    return _unique_paths(candidates)


def _existing_supported_launchers(root: Path, *, metadata: BundleMeta | None, raw_meta: dict[str, Any] | None) -> list[Path]:
    return [path for path in _supported_launcher_candidates(root, metadata=metadata, raw_meta=raw_meta) if path.is_file()]


def _read_manifest_mapping(manifest_path: Path) -> dict[str, Any]:
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Bundle manifest must be a JSON object.")
    return raw


def _read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8-sig")


def _iter_bundle_python_helpers(root: Path, *, content_root_path: Path) -> list[Path]:
    helpers: list[Path] = []
    for candidate in sorted(root.rglob("*.py")):
        if any(part == "__pycache__" for part in candidate.parts):
            continue
        if candidate == content_root_path or content_root_path in candidate.parents:
            continue
        helpers.append(candidate)
    return helpers


def _iter_bundle_powershell_helpers(
    root: Path,
    *,
    content_root_path: Path,
    metadata: BundleMeta | None,
    raw_meta: dict[str, Any] | None,
) -> list[Path]:
    supported_launchers = {
        path.resolve() if path.exists() else path
        for path in _supported_launcher_candidates(root, metadata=metadata, raw_meta=raw_meta)
    }
    helpers: list[Path] = []
    for candidate in sorted(root.rglob("*.ps1")):
        if candidate == content_root_path or content_root_path in candidate.parents:
            continue
        key = candidate.resolve() if candidate.exists() else candidate
        if key in supported_launchers:
            continue
        helpers.append(candidate)
    return helpers


def _python_syntax_error_message(path: Path) -> str | None:
    try:
        compile(_read_text_file(path), str(path), "exec")
    except SyntaxError as exc:
        return f"{exc.__class__.__name__}: {exc.msg} (line {exc.lineno}, offset {exc.offset})"
    return None


def _powershell_saved_script_shape_error(path: Path) -> str | None:
    text = _read_text_file(path)
    significant_lines = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        significant_lines.append(stripped)
    if not significant_lines:
        return None

    first_line = significant_lines[0]
    if first_line.startswith("& {"):
        return (
            "Saved PowerShell helper must not start with an inline script-block wrapper. "
            "Use a normal saved .ps1 shape that begins with param(...) or ordinary script statements."
        )

    if first_line.startswith("[CmdletBinding"):
        has_param_near_top = any(line.startswith("param(") or line.startswith("param ") for line in significant_lines[:3])
        if not has_param_near_top:
            return (
                "Saved PowerShell helper uses CmdletBinding without a top-level param(...) block near the top of the file."
            )
    return None


def _iter_generated_manifest_paths(manifest: dict[str, Any], root: Path, *, suffixes: tuple[str, ...]) -> list[Path]:
    generated: list[Path] = []
    files_to_write = manifest.get("files_to_write", [])
    if not isinstance(files_to_write, list):
        return generated

    for entry in files_to_write:
        if not isinstance(entry, dict):
            continue
        if entry.get("content") is not None:
            continue
        content_path = entry.get("content_path")
        if not isinstance(content_path, str) or not content_path.strip():
            continue
        try:
            relative_path = _normalize_bundle_relative_path(content_path, "generated.content_path")
        except ValueError:
            continue
        candidate = root / relative_path
        if not candidate.is_file():
            continue
        if candidate.suffix.lower() not in suffixes:
            continue
        generated.append(candidate)
    return _unique_paths(generated)


def _python_helper_contains_powershell_syntax(path: Path) -> bool:
    text = _read_text_file(path)
    for token in _POWERSHELL_TOKENS_IN_PYTHON_HELPER:
        if token in text:
            return True
    for line in text.splitlines():
        if line.lstrip().startswith("param("):
            return True
    return False


def validate_extracted_bundle_dir(bundle_root: str | Path) -> BundleValidationResult:
    root = Path(bundle_root)
    errors: list[BundleValidationMessage] = []
    warnings: list[BundleValidationMessage] = []
    metadata: BundleMeta | None = None
    raw_meta: dict[str, Any] | None = None

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

    existing_launchers = _existing_supported_launchers(root, metadata=None, raw_meta=None)
    if not existing_launchers:
        errors.append(
            BundleValidationMessage(
                code="launcher_missing",
                message=(
                    "Bundle launcher is missing. Expected a root run_with_patchops.ps1 or a legacy launcher under launchers/apply_with_patchops.ps1 or launchers/verify_with_patchops.ps1."
                ),
                path=str(default_launcher_path),
            )
        )

    manifest_path = default_manifest_path
    content_root_path = default_content_root

    if default_meta_path.exists():
        try:
            raw_meta = _read_manifest_mapping(default_meta_path)
        except Exception:
            raw_meta = None
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

            existing_launchers = _existing_supported_launchers(root, metadata=metadata, raw_meta=raw_meta)
            if not launcher_path.is_file() and not existing_launchers:
                errors.append(
                    BundleValidationMessage(
                        code="metadata_launcher_missing",
                        message="Bundle metadata points to a launcher path that does not exist and no supported fallback launcher was found.",
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
                        parent = candidate.parent
                        if not parent.exists():
                            errors.append(
                                BundleValidationMessage(
                                    code="content_subdirectory_missing",
                                    message=(
                                        "Bundle manifest references a content_path whose parent directory does not exist inside the bundle: "
                                        f"{parent.relative_to(root).as_posix()}"
                                    ),
                                    path=str(parent),
                                )
                            )
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

    effective_content_root = content_root_path if content_root_path.is_dir() else default_content_root
    prep_python_helpers = _iter_bundle_python_helpers(root, content_root_path=effective_content_root)
    prep_powershell_helpers = _iter_bundle_powershell_helpers(
        root,
        content_root_path=effective_content_root,
        metadata=metadata,
        raw_meta=raw_meta,
    )

    if prep_python_helpers and prep_powershell_helpers:
        errors.append(
            BundleValidationMessage(
                code="mixed_prep_helper_languages_forbidden",
                message=(
                    "Bundle prep helper generation must not mix Python and PowerShell helpers outside the normal launcher path. "
                    "Prefer direct staged files only, or one small Python prep helper with no embedded PowerShell syntax."
                ),
                path=str(root),
            )
        )

    if len(prep_python_helpers) > 1:
        errors.append(
            BundleValidationMessage(
                code="multiple_python_prep_helpers_forbidden",
                message=(
                    "Bundle normal path may stage at most one Python prep helper outside content/. "
                    f"Found {len(prep_python_helpers)} Python prep helpers."
                ),
                path=str(root),
            )
        )

    for helper_path in prep_powershell_helpers:
        errors.append(
            BundleValidationMessage(
                code="powershell_prep_helper_forbidden",
                message=(
                    "Bundle normal path must not stage extra PowerShell prep helpers outside the maintained launcher surface."
                ),
                path=str(helper_path),
            )
        )

    for helper_path in prep_python_helpers:
        syntax_error = _python_syntax_error_message(helper_path)
        if syntax_error is not None:
            errors.append(
                BundleValidationMessage(
                    code="helper_python_syntax_invalid",
                    message=f"Bundle Python helper is not syntax-valid: {syntax_error}",
                    path=str(helper_path),
                )
            )
            continue
        if _python_helper_contains_powershell_syntax(helper_path):
            errors.append(
                BundleValidationMessage(
                    code="python_prep_helper_contains_powershell_syntax",
                    message=(
                        "Bundle Python prep helper contains PowerShell-specific syntax or tokens. "
                        "Use one small language-pure Python helper or direct staged files only."
                    ),
                    path=str(helper_path),
                )
            )

    generated_python_files = []
    generated_powershell_files = []
    if manifest_path.is_file():
        try:
            manifest_for_generated_checks = _read_manifest_mapping(manifest_path)
        except Exception:
            manifest_for_generated_checks = None
        if isinstance(manifest_for_generated_checks, dict):
            generated_python_files = _iter_generated_manifest_paths(
                manifest_for_generated_checks,
                root,
                suffixes=(".py",),
            )
            generated_powershell_files = _iter_generated_manifest_paths(
                manifest_for_generated_checks,
                root,
                suffixes=(".ps1",),
            )

    for generated_python_path in generated_python_files:
        syntax_error = _python_syntax_error_message(generated_python_path)
        if syntax_error is not None:
            errors.append(
                BundleValidationMessage(
                    code="generated_python_syntax_invalid",
                    message=f"Generated Python bundle content is not syntax-valid: {syntax_error}",
                    path=str(generated_python_path),
                )
            )

    for generated_powershell_path in generated_powershell_files:
        shape_error = _powershell_saved_script_shape_error(generated_powershell_path)
        if shape_error is not None:
            errors.append(
                BundleValidationMessage(
                    code="generated_powershell_shape_invalid",
                    message=f"Generated PowerShell bundle content has an unsafe saved-script shape: {shape_error}",
                    path=str(generated_powershell_path),
                )
            )

    return BundleValidationResult(
        bundle_root=root,
        metadata=metadata,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


__all__ = [
    "BundleValidationMessage",
    "BundleValidationResult",
    "validate_extracted_bundle_dir",
]
