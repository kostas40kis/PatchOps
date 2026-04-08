from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Optional
import zipfile


ROOT_LAUNCHER_NAME = "run_with_patchops.ps1"
LEGACY_LAUNCHER_PATHS = (
    "launchers/apply_with_patchops.ps1",
    "launchers/verify_with_patchops.ps1",
)


@dataclass(frozen=True)
class BundleShapeIssue:
    code: str
    message: str
    path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass
class BundleShapeResult:
    ok: bool
    source_path: str
    source_kind: str
    root_folder_name: Optional[str]
    manifest_path: Optional[str]
    bundle_meta_path: Optional[str]
    content_root_path: Optional[str]
    launcher_paths: list[str]
    issue_count: int
    issues: list[BundleShapeIssue]

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "source_path": self.source_path,
            "source_kind": self.source_kind,
            "root_folder_name": self.root_folder_name,
            "manifest_path": self.manifest_path,
            "bundle_meta_path": self.bundle_meta_path,
            "content_root_path": self.content_root_path,
            "launcher_paths": list(self.launcher_paths),
            "issue_count": self.issue_count,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _normalize_member_name(name: str) -> str:
    return name.replace("\\", "/").lstrip("/")


def _top_level_roots(member_names: Iterable[str]) -> list[str]:
    roots: set[str] = set()
    for name in member_names:
        normalized = _normalize_member_name(name)
        if not normalized:
            continue
        parts = [part for part in PurePosixPath(normalized).parts if part not in ("", ".")]
        if parts:
            roots.add(parts[0])
    return sorted(roots)


def _finalize(
    *,
    source_path: Path,
    source_kind: str,
    root_folder_name: Optional[str],
    manifest_path: Optional[str],
    bundle_meta_path: Optional[str],
    content_root_path: Optional[str],
    launcher_paths: list[str],
    issues: list[BundleShapeIssue],
) -> BundleShapeResult:
    return BundleShapeResult(
        ok=(len(issues) == 0),
        source_path=str(source_path),
        source_kind=source_kind,
        root_folder_name=root_folder_name,
        manifest_path=manifest_path,
        bundle_meta_path=bundle_meta_path,
        content_root_path=content_root_path,
        launcher_paths=launcher_paths,
        issue_count=len(issues),
        issues=issues,
    )


def _allowed_launcher_paths(root_folder_name: str | None = None) -> tuple[str, ...]:
    if root_folder_name is None:
        return (ROOT_LAUNCHER_NAME, *LEGACY_LAUNCHER_PATHS)
    return (
        f"{root_folder_name}/{ROOT_LAUNCHER_NAME}",
        *(f"{root_folder_name}/{item}" for item in LEGACY_LAUNCHER_PATHS),
    )


def _is_content_file(normalized_path: str, *, root_folder_name: str | None = None) -> bool:
    prefix = "content/"
    if root_folder_name:
        prefix = f"{root_folder_name}/content/"
    return normalized_path.startswith(prefix)


def _collect_zip_launcher_paths(member_names: list[str], root_folder_name: str) -> tuple[list[str], list[str]]:
    allowed = set(_allowed_launcher_paths(root_folder_name))
    launcher_paths = sorted(path for path in member_names if path in allowed)

    misplaced = sorted(
        path
        for path in member_names
        if path.lower().endswith(".ps1")
        and not _is_content_file(path, root_folder_name=root_folder_name)
        and path not in allowed
    )
    return launcher_paths, misplaced


def _collect_directory_launcher_paths(bundle_root: Path) -> tuple[list[str], list[str]]:
    allowed = {
        bundle_root / ROOT_LAUNCHER_NAME,
        *(bundle_root / Path(item) for item in LEGACY_LAUNCHER_PATHS),
    }
    launcher_paths = sorted(
        path.relative_to(bundle_root).as_posix()
        for path in allowed
        if path.is_file()
    )

    misplaced = sorted(
        path.relative_to(bundle_root).as_posix()
        for path in bundle_root.rglob("*.ps1")
        if path.is_file()
        and not (bundle_root / "content") in path.parents
        and path not in allowed
    )
    return launcher_paths, misplaced


def validate_bundle_zip(zip_path: Path) -> BundleShapeResult:
    zip_path = Path(zip_path)
    issues: list[BundleShapeIssue] = []

    if not zip_path.exists():
        issues.append(BundleShapeIssue(code="zip_missing", message="Bundle zip does not exist.", path=str(zip_path)))
        return _finalize(
            source_path=zip_path,
            source_kind="zip",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    if not zip_path.is_file():
        issues.append(BundleShapeIssue(code="zip_not_file", message="Bundle zip path is not a file.", path=str(zip_path)))
        return _finalize(
            source_path=zip_path,
            source_kind="zip",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            member_names = sorted(
                _normalize_member_name(info.filename)
                for info in archive.infolist()
                if not info.is_dir()
            )
    except zipfile.BadZipFile:
        issues.append(BundleShapeIssue(code="bad_zip", message="Bundle zip could not be opened as a zip archive.", path=str(zip_path)))
        return _finalize(
            source_path=zip_path,
            source_kind="zip",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    roots = _top_level_roots(member_names)
    if not roots:
        issues.append(BundleShapeIssue(code="empty_zip", message="Bundle zip does not contain any file entries.", path=str(zip_path)))
        return _finalize(
            source_path=zip_path,
            source_kind="zip",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    if len(roots) != 1:
        issues.append(
            BundleShapeIssue(
                code="multiple_root_folders",
                message="Bundle zip must contain exactly one top-level root folder.",
                path=str(zip_path),
            )
        )
        return _finalize(
            source_path=zip_path,
            source_kind="zip",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    root_folder_name = roots[0]
    manifest_path = f"{root_folder_name}/manifest.json"
    bundle_meta_path = f"{root_folder_name}/bundle_meta.json"
    content_root_path = f"{root_folder_name}/content"

    if any(name.startswith(f"{root_folder_name}/{root_folder_name}/") for name in member_names):
        issues.append(
            BundleShapeIssue(
                code="duplicate_nested_root",
                message="Bundle zip contains a duplicate nested root folder.",
                path=f"{root_folder_name}/{root_folder_name}",
            )
        )

    if manifest_path not in member_names:
        issues.append(BundleShapeIssue(code="missing_manifest", message="Bundle zip is missing manifest.json.", path=manifest_path))

    if bundle_meta_path not in member_names:
        issues.append(BundleShapeIssue(code="missing_bundle_meta", message="Bundle zip is missing bundle_meta.json.", path=bundle_meta_path))

    if not any(name.startswith(f"{content_root_path}/") for name in member_names):
        issues.append(
            BundleShapeIssue(
                code="missing_content_root",
                message="Bundle zip is missing the content/ root.",
                path=f"{content_root_path}/",
            )
        )

    launcher_paths, misplaced_launcher_paths = _collect_zip_launcher_paths(member_names, root_folder_name)
    if not launcher_paths:
        if misplaced_launcher_paths:
            issues.append(
                BundleShapeIssue(
                    code="wrong_launcher_location",
                    message="Bundle zip contains a PowerShell launcher outside the maintained root launcher locations.",
                    path=misplaced_launcher_paths[0],
                )
            )
        else:
            issues.append(
                BundleShapeIssue(
                    code="missing_launcher",
                    message="Bundle zip is missing the maintained root launcher run_with_patchops.ps1.",
                    path=f"{root_folder_name}/{ROOT_LAUNCHER_NAME}",
                )
            )

    return _finalize(
        source_path=zip_path,
        source_kind="zip",
        root_folder_name=root_folder_name,
        manifest_path=manifest_path if manifest_path in member_names else None,
        bundle_meta_path=bundle_meta_path if bundle_meta_path in member_names else None,
        content_root_path=content_root_path if any(name.startswith(f"{content_root_path}/") for name in member_names) else None,
        launcher_paths=launcher_paths,
        issues=issues,
    )


def validate_bundle_directory(bundle_root: Path) -> BundleShapeResult:
    bundle_root = Path(bundle_root)
    issues: list[BundleShapeIssue] = []

    if not bundle_root.exists():
        issues.append(BundleShapeIssue(code="bundle_root_missing", message="Bundle root directory does not exist.", path=str(bundle_root)))
        return _finalize(
            source_path=bundle_root,
            source_kind="directory",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    if not bundle_root.is_dir():
        issues.append(BundleShapeIssue(code="bundle_root_not_directory", message="Bundle root path is not a directory.", path=str(bundle_root)))
        return _finalize(
            source_path=bundle_root,
            source_kind="directory",
            root_folder_name=None,
            manifest_path=None,
            bundle_meta_path=None,
            content_root_path=None,
            launcher_paths=[],
            issues=issues,
        )

    root_folder_name = bundle_root.name
    manifest = bundle_root / "manifest.json"
    bundle_meta = bundle_root / "bundle_meta.json"
    content_root = bundle_root / "content"
    duplicate_nested_root = bundle_root / root_folder_name

    if duplicate_nested_root.exists() and duplicate_nested_root.is_dir():
        issues.append(
            BundleShapeIssue(
                code="duplicate_nested_root",
                message="Bundle directory contains a duplicate nested root folder.",
                path=str(duplicate_nested_root),
            )
        )

    if not manifest.is_file():
        issues.append(BundleShapeIssue(code="missing_manifest", message="Bundle directory is missing manifest.json.", path=str(manifest)))

    if not bundle_meta.is_file():
        issues.append(BundleShapeIssue(code="missing_bundle_meta", message="Bundle directory is missing bundle_meta.json.", path=str(bundle_meta)))

    if not content_root.exists() or not content_root.is_dir():
        issues.append(BundleShapeIssue(code="missing_content_root", message="Bundle directory is missing the content/ root.", path=str(content_root)))

    launcher_paths, misplaced_launcher_paths = _collect_directory_launcher_paths(bundle_root)
    if not launcher_paths:
        if misplaced_launcher_paths:
            issues.append(
                BundleShapeIssue(
                    code="wrong_launcher_location",
                    message="Bundle directory contains a PowerShell launcher outside the maintained root launcher locations.",
                    path=str(bundle_root / misplaced_launcher_paths[0]),
                )
            )
        else:
            issues.append(
                BundleShapeIssue(
                    code="missing_launcher",
                    message="Bundle directory is missing the maintained root launcher run_with_patchops.ps1.",
                    path=str(bundle_root / ROOT_LAUNCHER_NAME),
                )
            )

    return _finalize(
        source_path=bundle_root,
        source_kind="directory",
        root_folder_name=root_folder_name,
        manifest_path="manifest.json" if manifest.is_file() else None,
        bundle_meta_path="bundle_meta.json" if bundle_meta.is_file() else None,
        content_root_path="content" if content_root.is_dir() else None,
        launcher_paths=launcher_paths,
        issues=issues,
    )


def validate_bundle_path(path: Path) -> BundleShapeResult:
    path = Path(path)
    if path.suffix.lower() == ".zip":
        return validate_bundle_zip(path)
    return validate_bundle_directory(path)


__all__ = [
    "BundleShapeIssue",
    "BundleShapeResult",
    "validate_bundle_directory",
    "validate_bundle_path",
    "validate_bundle_zip",
]
