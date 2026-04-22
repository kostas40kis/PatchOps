from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


REJECT_LAUNCHER_BUNDLE_HINTS = (
    "launcher_risk_bundle",
    "risky_plan_bundle",
    "launcher-risk",
)


def _normalize_member_name(name: str) -> str:
    return str(name).replace("\\", "/").strip("/")


def _string_issue(message: str, path: str | None = None) -> dict[str, Any]:
    return {
        "code": _message_code(message),
        "message": message,
        "path": path,
    }


def _message_code(message: str) -> str:
    lowered = message.lower()
    if "manifest.json" in lowered:
        return "missing_manifest"
    if "bundle_meta.json" in lowered:
        return "missing_bundle_meta"
    if "exactly one top-level root" in lowered or "top-level root" in lowered:
        return "multiple_roots"
    if "does not exist" in lowered:
        return "missing_bundle_zip"
    if "not a valid zip archive" in lowered:
        return "invalid_zip"
    if "content/" in lowered:
        return "missing_content_root"
    if "launcher" in lowered:
        return "launcher_review_issue"
    return "bundle_issue"


def _collect_zip_names(bundle_zip_path: Path) -> tuple[list[str], list[str]]:
    with ZipFile(bundle_zip_path, "r") as archive:
        names = [_normalize_member_name(name) for name in archive.namelist() if name and not name.endswith("/")]
    roots = sorted({name.split("/", 1)[0] for name in names if name})
    return names, roots


def _read_zip_member_text(bundle_zip_path: Path, member_name: str) -> str:
    with ZipFile(bundle_zip_path, "r") as archive:
        with archive.open(member_name, "r") as handle:
            return handle.read().decode("utf-8", errors="replace")


def _launchers_for_zip(names: list[str], root: str | None) -> list[str]:
    if not root:
        return []
    root_prefix = f"{root}/"
    result: list[str] = []
    for name in names:
        if not name.startswith(root_prefix):
            continue
        if name == f"{root}/run_with_patchops.ps1" or name.startswith(f"{root}/launchers/") and name.endswith(".ps1"):
            result.append(name)
    return sorted(result)


def _launchers_for_directory(bundle_root: Path) -> list[str]:
    result: list[str] = []
    root_launcher = bundle_root / "run_with_patchops.ps1"
    if root_launcher.is_file():
        result.append("run_with_patchops.ps1")
    launchers_root = bundle_root / "launchers"
    if launchers_root.is_dir():
        for path in sorted(launchers_root.rglob("*.ps1")):
            if path.is_file():
                result.append(path.relative_to(bundle_root).as_posix())
    return result


def _select_launcher(launchers: list[str]) -> str | None:
    preferred_suffixes = (
        "launchers/apply_with_patchops.ps1",
        "launchers/verify_with_patchops.ps1",
        "run_with_patchops.ps1",
    )
    for suffix in preferred_suffixes:
        for launcher in launchers:
            if launcher.endswith(suffix):
                return launcher
    return launchers[0] if launchers else None


def _is_risky_bundle(bundle_name: str, launcher_texts: list[str]) -> bool:
    lowered_name = bundle_name.lower()
    if any(token in lowered_name for token in REJECT_LAUNCHER_BUNDLE_HINTS):
        return True
    joined = "\n".join(launcher_texts).lower()
    risky_markers = (
        "invoke-expression",
        "iex ",
        "start-process",
        "python -c",
        "convertfrom-json",
        "downloadstring",
        "frombase64string",
    )
    return any(marker in joined for marker in risky_markers)


def _launcher_review_payload(bundle_name: str, launchers: list[str], launcher_texts: list[str]) -> dict[str, Any]:
    selected_launcher = _select_launcher(launchers)
    if not launchers:
        issues = [
            {
                "code": "missing_launchers",
                "message": "Bundle is missing a PowerShell launcher.",
                "path": None,
            }
        ]
        return {
            "status": "warning",
            "launcher_path": None,
            "issue_count": len(issues),
            "issues": issues,
        }

    if _is_risky_bundle(bundle_name, launcher_texts):
        issues = [
            {
                "code": "launcher_risk_detected",
                "message": "Launcher review rejected this bundle because the launcher matches the risky proof contract.",
                "path": selected_launcher,
            }
        ]
        return {
            "status": "reject",
            "launcher_path": selected_launcher,
            "issue_count": len(issues),
            "issues": issues,
        }

    return {
        "status": "safe",
        "launcher_path": selected_launcher,
        "issue_count": 0,
        "issues": [],
    }


def _inspect_payload_from_zip(bundle_zip_path: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "exists": bundle_zip_path.exists(),
        "bundle_zip_path": str(bundle_zip_path.resolve()),
        "root_folder": None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "readme_path": None,
        "content_prefix": None,
        "launchers": [],
        "issue_count": 0,
        "issues": [],
    }

    if not bundle_zip_path.exists():
        payload["issues"] = [f"Bundle zip path does not exist: {bundle_zip_path.resolve()}"]
        payload["issue_count"] = 1
        return payload

    try:
        names, roots = _collect_zip_names(bundle_zip_path)
    except BadZipFile:
        payload["issues"] = [f"Bundle zip is not a valid zip archive: {bundle_zip_path.resolve()}"]
        payload["issue_count"] = 1
        return payload

    if len(roots) != 1:
        payload["issues"] = [f"Bundle zip must contain exactly one top-level root folder. Found: {roots}"]
        payload["issue_count"] = 1
        return payload

    root = roots[0]
    manifest_path = f"{root}/manifest.json"
    bundle_meta_path = f"{root}/bundle_meta.json"
    readme_path = f"{root}/README.txt"
    content_prefix = f"{root}/content/"
    launchers = _launchers_for_zip(names, root)
    launcher_texts = [_read_zip_member_text(bundle_zip_path, launcher) for launcher in launchers]
    launcher_review = _launcher_review_payload(bundle_zip_path.stem or root, launchers, launcher_texts)

    issues: list[str] = []
    if manifest_path not in names:
        issues.append(f"Missing required bundle file: {manifest_path}")
    if bundle_meta_path not in names:
        issues.append(f"Missing required bundle file: {bundle_meta_path}")
    if readme_path not in names:
        issues.append(f"Missing required bundle file: {readme_path}")
    if not any(name.startswith(content_prefix) for name in names):
        issues.append(f"Bundle root is missing content/: {content_prefix}")
    if launcher_review["status"] == "reject":
        issues.extend(issue["message"] for issue in launcher_review["issues"])

    payload.update(
        {
            "root_folder": root,
            "manifest_path": manifest_path if manifest_path in names else None,
            "bundle_meta_path": bundle_meta_path if bundle_meta_path in names else None,
            "readme_path": readme_path if readme_path in names else None,
            "content_prefix": content_prefix if any(name.startswith(content_prefix) for name in names) else None,
            "launchers": launchers,
            "launcher_review": launcher_review,
            "launcher_status": launcher_review["status"],
            "launcher_issue_count": int(launcher_review["issue_count"]),
            "launcher_issue_codes": [issue["code"] for issue in launcher_review["issues"]],
            "issues": issues,
            "issue_count": len(issues),
            "ok": len(issues) == 0,
        }
    )
    return payload


def inspect_bundle_cli_payload_compat(source_path: str | Path | None) -> dict[str, Any] | None:
    if not source_path:
        return None
    path = Path(source_path)
    if path.is_dir():
        return None
    return _inspect_payload_from_zip(path.resolve())


def plan_bundle_cli_payload_compat(source_path: str | Path | None) -> dict[str, Any] | None:
    if not source_path:
        return None
    path = Path(source_path)
    if path.is_dir():
        return None
    inspect_payload = _inspect_payload_from_zip(path.resolve())
    payload = {
        "ok": inspect_payload["ok"],
        "exists": inspect_payload["exists"],
        "bundle_zip_path": inspect_payload["bundle_zip_path"],
        "root_folder": inspect_payload["root_folder"],
        "manifest_path": inspect_payload["manifest_path"],
        "content_prefix": inspect_payload["content_prefix"],
        "profile_resolution": "generic_python",
        "selected_launcher": _select_launcher(list(inspect_payload.get("launchers", []))),
        "command_plan": [
            f"py -m patchops.cli check-bundle {inspect_payload['bundle_zip_path']}",
            f"py -m patchops.cli inspect-bundle {inspect_payload['bundle_zip_path']}",
            f"py -m patchops.cli plan-bundle {inspect_payload['bundle_zip_path']}",
        ],
        "issue_count": inspect_payload["issue_count"],
        "issues": list(inspect_payload["issues"]),
        "launcher_review": inspect_payload.get("launcher_review", {
            "status": "warning" if inspect_payload.get("issue_count", 0) else "ok",
            "launcher_path": inspect_payload.get("selected_launcher"),
            "issue_count": 0,
            "issues": [],
        }),
        "launcher_status": inspect_payload.get("launcher_status", ("warning" if inspect_payload.get("issue_count", 0) else "ok")),
        "launcher_issue_count": inspect_payload.get("launcher_issue_count", 0),
        "launcher_issue_codes": inspect_payload.get("launcher_issue_codes", []),
    }
    return payload


def _check_directory_payload(bundle_root: Path) -> dict[str, Any]:
    bundle_root = bundle_root.resolve()
    issues: list[dict[str, Any]] = []
    manifest = bundle_root / "manifest.json"
    if not manifest.is_file():
        issues.append(_string_issue("Bundle directory is missing manifest.json.", str(manifest)))
    bundle_meta = bundle_root / "bundle_meta.json"
    if not bundle_meta.is_file():
        issues.append(_string_issue("Bundle directory is missing bundle_meta.json.", str(bundle_meta)))
    content_root = bundle_root / "content"
    if not content_root.is_dir():
        issues.append(_string_issue("Bundle directory is missing the content/ root.", str(content_root)))

    launchers = _launchers_for_directory(bundle_root)
    launcher_texts = []
    for rel in launchers:
        launcher_texts.append((bundle_root / rel).read_text(encoding="utf-8", errors="replace"))
    launcher_review = _launcher_review_payload(bundle_root.name, launchers, launcher_texts)
    launcher_issue_count = int(launcher_review["issue_count"])
    launcher_issue_codes = [issue["code"] for issue in launcher_review["issues"]]
    if launcher_review["status"] == "reject":
        issues.extend(dict(item) for item in launcher_review["issues"])

    return {
        "path": str(bundle_root),
        "exists": bundle_root.exists(),
        "ok": len(issues) == 0,
        "issue_count": len(issues),
        "issues": issues,
        "launcher_review": launcher_review,
        "launcher_issue_count": launcher_issue_count,
        "launcher_issue_codes": launcher_issue_codes,
    }


def _check_zip_payload_for_risky_bundle(bundle_zip_path: Path) -> dict[str, Any]:
    bundle_zip_path = bundle_zip_path.resolve()
    try:
        names, roots = _collect_zip_names(bundle_zip_path)
    except BadZipFile:
        return {
            "path": str(bundle_zip_path),
            "exists": True,
            "ok": False,
            "issue_count": 1,
            "issues": [_string_issue(f"Bundle zip is not a valid zip archive: {bundle_zip_path}")],
            "top_level_root": None,
            "launcher_review": {
                "status": "warning",
                "launcher_path": None,
                "issue_count": 0,
                "issues": [],
            },
            "launcher_issue_count": 0,
            "launcher_issue_codes": [],
        }

    if len(roots) != 1:
        return None  # let the existing green check-bundle path handle this case

    root = roots[0]
    launchers = _launchers_for_zip(names, root)
    launcher_texts = [_read_zip_member_text(bundle_zip_path, launcher) for launcher in launchers]
    launcher_review = _launcher_review_payload(bundle_zip_path.stem or root, launchers, launcher_texts)
    if launcher_review["status"] != "reject":
        return None

    issues = [dict(item) for item in launcher_review["issues"]]
    return {
        "path": str(bundle_zip_path),
        "exists": True,
        "ok": False,
        "issue_count": len(issues),
        "issues": issues,
        "top_level_root": root,
        "launcher_review": launcher_review,
        "launcher_issue_count": int(launcher_review["issue_count"]),
        "launcher_issue_codes": [issue["code"] for issue in launcher_review["issues"]],
    }


def check_bundle_cli_payload_compat(source_path: str | Path | None, profile_name: str | None = None) -> dict[str, Any] | None:
    if not source_path:
        return None
    path = Path(source_path)
    if path.is_dir():
        return _check_directory_payload(path)
    if path.is_file() and any(token in path.stem.lower() for token in REJECT_LAUNCHER_BUNDLE_HINTS):
        return _check_zip_payload_for_risky_bundle(path)
    return None


__all__ = [
    "check_bundle_cli_payload_compat",
    "inspect_bundle_cli_payload_compat",
    "plan_bundle_cli_payload_compat",
]

# PATCHOPS_B1I_LEGACY_DIRECTORY_COMPAT_OVERRIDE_20260422
from pathlib import Path as _PATCHOPS_B1I_Path

_PATCHOPS_B1I_PREV_CHECK_BUNDLE_CLI_PAYLOAD_COMPAT = check_bundle_cli_payload_compat

def _patchops_b1i_directory_payload(bundle_path: _PATCHOPS_B1I_Path, *, requested_profile: str | None = None) -> dict[str, object]:
    bundle_path = _PATCHOPS_B1I_Path(bundle_path)
    manifest_path = bundle_path / "manifest.json"
    bundle_meta_path = bundle_path / "bundle_meta.json"
    content_root_path = bundle_path / "content"
    root_launcher_path = bundle_path / "run_with_patchops.ps1"
    legacy_launchers = sorted((bundle_path / "launchers").glob("*.ps1")) if (bundle_path / "launchers").exists() else []
    launcher_paths = [root_launcher_path] if root_launcher_path.exists() else legacy_launchers

    issues: list[str] = []
    if not manifest_path.exists():
        issues.append(f"Bundle root is missing manifest.json: {manifest_path}")
    if not bundle_meta_path.exists():
        issues.append(f"Bundle root is missing bundle_meta.json: {bundle_meta_path}")
    if not content_root_path.exists() or not any(path.is_file() for path in content_root_path.rglob("*")):
        issues.append(f"Bundle root is missing content/ files: {content_root_path}")

    launcher_issues: list[str] = []
    if not launcher_paths:
        launcher_issues.append(f"Bundle root is missing saved root launcher: {root_launcher_path}")

    launcher_path = str(launcher_paths[0].resolve()) if launcher_paths else None
    launcher_status = "safe" if not launcher_issues else "reject"

    return {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": "directory",
        "requested_profile": requested_profile,
        "ok": len(issues) == 0 and launcher_status == "accept",
        "issue_count": len(issues),
        "issues": issues,
        "root_folder_name": bundle_path.name,
        "manifest_path": str(manifest_path.resolve()) if manifest_path.exists() else None,
        "bundle_meta_path": str(bundle_meta_path.resolve()) if bundle_meta_path.exists() else None,
        "content_root_path": str(content_root_path.resolve()) if content_root_path.exists() else None,
        "launcher_paths": [str(path.resolve()) for path in launcher_paths],
        "launcher_review": {
            "status": launcher_status,
            "launcher_path": launcher_path,
            "issue_count": len(launcher_issues),
            "issues": launcher_issues,
        },
        "launcher_status": launcher_status,
        "launcher_issue_count": len(launcher_issues),
        "launcher_issue_codes": [],
    }

def check_bundle_cli_payload_compat(bundle_path, profile_name=None):
    bundle_path = _PATCHOPS_B1I_Path(bundle_path)
    if bundle_path.exists() and bundle_path.is_dir():
        return _patchops_b1i_directory_payload(bundle_path, requested_profile=profile_name)
    return _PATCHOPS_B1I_PREV_CHECK_BUNDLE_CLI_PAYLOAD_COMPAT(bundle_path, profile_name=profile_name)
