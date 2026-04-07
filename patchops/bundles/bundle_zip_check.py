from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


def _make_result(path: Path, issues: list[str], *, exists: bool, top_level_root: str | None, member_count: int) -> dict[str, Any]:
    return {
        "path": str(path),
        "exists": exists,
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "top_level_root": top_level_root,
        "member_count": member_count,
    }



def check_bundle_zip(path: str | Path) -> dict[str, Any]:
    bundle_path = Path(path).resolve()
    if not bundle_path.exists():
        return _make_result(
            bundle_path,
            [f"Bundle zip path does not exist: {bundle_path}"],
            exists=False,
            top_level_root=None,
            member_count=0,
        )
    if bundle_path.is_dir():
        return _make_result(
            bundle_path,
            [f"Bundle zip path is a directory, not a zip file: {bundle_path}"],
            exists=True,
            top_level_root=None,
            member_count=0,
        )

    try:
        with ZipFile(bundle_path, "r") as zf:
            raw_names = [name for name in zf.namelist() if name and not name.endswith("/")]
    except BadZipFile:
        return _make_result(
            bundle_path,
            [f"Bundle zip is not a valid zip archive: {bundle_path}"],
            exists=True,
            top_level_root=None,
            member_count=0,
        )

    issues: list[str] = []
    if not raw_names:
        issues.append("Bundle zip is empty.")
        return _make_result(bundle_path, issues, exists=True, top_level_root=None, member_count=0)

    roots = sorted({name.split("/", 1)[0] for name in raw_names if "/" in name or name})
    if len(roots) != 1:
        issues.append("Bundle zip must contain exactly one top-level root folder.")
        return _make_result(bundle_path, issues, exists=True, top_level_root=None, member_count=len(raw_names))

    root = roots[0]
    members = set(raw_names)
    required_files = [f"{root}/manifest.json", f"{root}/bundle_meta.json"]
    for required in required_files:
        if required not in members:
            issues.append(f"Missing required bundle file: {required}")

    has_content = any(name.startswith(f"{root}/content/") for name in raw_names)
    has_launchers = any(name.startswith(f"{root}/launchers/") for name in raw_names)
    if not has_content:
        issues.append(f"Bundle root is missing content/: {root}/content/")
    if not has_launchers:
        issues.append(f"Bundle root is missing launchers/: {root}/launchers/")

    return _make_result(bundle_path, issues, exists=True, top_level_root=root, member_count=len(raw_names))
