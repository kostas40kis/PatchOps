from __future__ import annotations

from pathlib import Path
from typing import Any
import zipfile


REQUIRED_ROOT_FILES = ("manifest.json", "bundle_meta.json", "README.txt")
REQUIRED_ROOT_DIR_PREFIXES = ("content/", "launchers/")


def _normalize_member_name(name: str) -> str:
    return name.replace("\\", "/").strip("/")


def inspect_bundle_path(bundle_zip_path: str | Path) -> dict[str, Any]:
    bundle_path = Path(bundle_zip_path).resolve()
    payload: dict[str, Any] = {
        "bundle_zip_path": str(bundle_path),
        "exists": bundle_path.exists(),
        "ok": False,
        "issue_count": 0,
        "issues": [],
        "top_level_roots": [],
        "root_folder": None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "readme_path": None,
        "launchers": [],
        "content_prefix": None,
    }

    issues: list[str] = []

    if not bundle_path.exists():
        issues.append(f"Bundle zip path does not exist: {bundle_path}")
        payload["issues"] = issues
        payload["issue_count"] = len(issues)
        return payload

    if bundle_path.is_dir():
        issues.append(f"Bundle zip path is a directory, not a zip file: {bundle_path}")
        payload["issues"] = issues
        payload["issue_count"] = len(issues)
        return payload

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            member_names = []
            for info in zf.infolist():
                normalized = _normalize_member_name(info.filename)
                if normalized:
                    member_names.append(normalized)

            top_level_roots = sorted({name.split("/", 1)[0] for name in member_names})
            payload["top_level_roots"] = top_level_roots

            if len(top_level_roots) != 1:
                issues.append(
                    f"Bundle zip must contain exactly one top-level root folder. Found: {top_level_roots}"
                )
            else:
                root = top_level_roots[0]
                payload["root_folder"] = root
                root_prefix = f"{root}/"

                for required_file in REQUIRED_ROOT_FILES:
                    candidate = f"{root_prefix}{required_file}"
                    if candidate not in member_names:
                        issues.append(f"Missing required root file: {candidate}")
                    else:
                        if required_file == "manifest.json":
                            payload["manifest_path"] = candidate
                        elif required_file == "bundle_meta.json":
                            payload["bundle_meta_path"] = candidate
                        elif required_file == "README.txt":
                            payload["readme_path"] = candidate

                for required_prefix in REQUIRED_ROOT_DIR_PREFIXES:
                    candidate_prefix = f"{root_prefix}{required_prefix}"
                    if not any(name.startswith(candidate_prefix) for name in member_names):
                        issues.append(f"Missing required bundle directory: {candidate_prefix}")
                    else:
                        if required_prefix == "content/":
                            payload["content_prefix"] = candidate_prefix

                launchers_prefix = f"{root_prefix}launchers/"
                launchers = sorted(
                    name
                    for name in member_names
                    if name.startswith(launchers_prefix) and not name.endswith("/")
                )
                payload["launchers"] = launchers
    except zipfile.BadZipFile:
        issues.append(f"Bundle zip is not a valid zip archive: {bundle_path}")

    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = len(issues) == 0
    return payload
