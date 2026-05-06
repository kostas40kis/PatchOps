from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any

from patchops.copilot_downloader.models import PASS_BUNDLE_VALIDATED_RUN_BLOCKED, ShapeValidationResult

BUNDLE_KIND = "patchops_bundle_zip"
INVALID_LABEL = "BLOCKED_INVALID_ARTIFACT"
DANGEROUS_LAUNCHER_EXTENSIONS: frozenset[str] = frozenset({".ps1", ".bat", ".cmd", ".vbs", ".js", ".wsf"})
DANGEROUS_LAUNCHER_PATTERNS: tuple[tuple[str, str], ...] = (
    ("encoded_command", r"(?i)-encodedcommand\b|\bencodedcommand\b"),
    ("hidden_download", r"(?i)\binvoke-webrequest\b|\biwr\b|\bstart-bitstransfer\b|downloadstring\s*\(|downloadfile\s*\(|\bcurl\b|\bwget\b"),
    ("destructive_remove", r"(?i)\bremove-item\b|\brd\s+/s\b|\brmdir\s+/s\b|\bdel\s+/[fsq]\b|\berase\b"),
    ("system_mutation", r"(?i)\bformat-volume\b|\bclear-disk\b|\bremove-partition\b|\bset-executionpolicy\b"),
)


def normalize_zip_name(name: str) -> str:
    return name.replace("\\", "/")


def zip_entry_path_issue(name: str) -> str | None:
    normalized = normalize_zip_name(name)
    if not normalized:
        return "empty_zip_entry_name"
    if normalized.startswith("/"):
        return "absolute_zip_entry_path"
    first_part = normalized.split("/", 1)[0]
    if ":" in first_part:
        return "absolute_or_drive_qualified_zip_entry_path"
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return "path_traversal_or_empty_zip_entry_part"
    if any(part in {".git", ".hg", ".svn", "__MACOSX"} for part in parts):
        return "unsafe_hidden_or_metadata_directory"
    return None


def _launcher_issue(name: str, content: str) -> str | None:
    lowered_name = normalize_zip_name(name).lower()
    extension = Path(lowered_name).suffix
    if extension not in DANGEROUS_LAUNCHER_EXTENSIONS:
        return None
    for issue_name, pattern in DANGEROUS_LAUNCHER_PATTERNS:
        if re.search(pattern, content):
            return f"dangerous_launcher_pattern:{issue_name}:{name}"
    return None


def validate_patchops_bundle_zip(path: str | Path, *, launcher_probe_bytes: int = 256 * 1024) -> ShapeValidationResult:
    bundle_path = Path(path).resolve(strict=False)
    issues: list[str] = []
    metadata: dict[str, Any] = {"zip_entries_preview": []}
    checks: dict[str, bool] = {
        "zip_can_open": False,
        "no_path_traversal": True,
        "no_absolute_paths": True,
        "manifest_or_bundle_metadata_present": False,
        "safe_root_shape": False,
        "launcher_not_obviously_dangerous": True,
        "zip_index_only_no_extract": True,
    }
    try:
        with zipfile.ZipFile(bundle_path) as archive:
            infos = archive.infolist()
            checks["zip_can_open"] = True
            names = tuple(normalize_zip_name(info.filename) for info in infos)
            metadata["zip_entry_count"] = len(names)
            metadata["zip_entries_preview"] = list(names[:25])
            if not names:
                issues.append("zip_empty")
            for name in names:
                issue = zip_entry_path_issue(name)
                if issue:
                    if "absolute" in issue:
                        checks["no_absolute_paths"] = False
                    else:
                        checks["no_path_traversal"] = False
                    issues.append(f"{issue}:{name}")
            lower_names = tuple(name.lower() for name in names)
            has_manifest = any(name.endswith("manifest.json") for name in lower_names)
            has_bundle_metadata = any(name.endswith("bundle_metadata.json") or name.endswith("patchops_bundle.json") for name in lower_names)
            checks["manifest_or_bundle_metadata_present"] = has_manifest or has_bundle_metadata
            if not checks["manifest_or_bundle_metadata_present"]:
                issues.append("missing_manifest_or_bundle_metadata")
            root_parts = {name.split("/", 1)[0] for name in names if name and not name.endswith("/")}
            checks["safe_root_shape"] = 1 <= len(root_parts) <= 10 and len(names) <= 1000
            metadata["root_parts"] = sorted(root_parts)
            if not checks["safe_root_shape"]:
                issues.append("unsafe_root_shape")
            for info in infos:
                name = normalize_zip_name(info.filename)
                extension = Path(name.lower()).suffix
                if extension in DANGEROUS_LAUNCHER_EXTENSIONS and info.file_size <= launcher_probe_bytes:
                    content = archive.read(info).decode("utf-8", errors="replace")
                    launcher_issue = _launcher_issue(name, content)
                    if launcher_issue:
                        checks["launcher_not_obviously_dangerous"] = False
                        issues.append(launcher_issue)
    except Exception as exc:
        checks["zip_can_open"] = False
        issues.append(f"zip_open_failed:{exc}")
    return ShapeValidationResult(
        result_label=PASS_BUNDLE_VALIDATED_RUN_BLOCKED if not issues else INVALID_LABEL,
        artifact_kind=BUNDLE_KIND,
        path=bundle_path,
        issues=tuple(issues),
        checks=checks,
        metadata=metadata,
    )