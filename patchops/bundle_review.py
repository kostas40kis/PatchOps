from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import zipfile


def _normalize_member_name(name: str) -> str:
    return str(name or "").replace("\\", "/").strip("/")


def _issue(code: str, message: str, *, path: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if path is not None:
        payload["path"] = path
    return payload


def _warning(code: str, message: str, *, path: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
    }
    if path is not None:
        payload["path"] = path
    return payload


def _top_level_roots(member_names: list[str]) -> list[str]:
    roots: list[str] = []
    seen: set[str] = set()
    for raw_name in member_names:
        name = _normalize_member_name(raw_name)
        if not name:
            continue
        root = name.split("/", 1)[0]
        if root not in seen:
            seen.add(root)
            roots.append(root)
    return roots


def _read_json_object_from_zip(zf: zipfile.ZipFile, member_name: str) -> dict[str, Any] | None:
    try:
        with zf.open(member_name, "r") as handle:
            raw = handle.read().decode("utf-8")
    except KeyError:
        return None
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"{member_name} must contain a JSON object.")
    return data


def check_bundle_cli_payload(*args: Any, **kwargs: Any) -> dict[str, Any]:
    if args and hasattr(args[0], "__dict__") and not isinstance(args[0], (str, Path)):
        namespace = args[0]
        bundle_zip_path = getattr(namespace, "bundle_zip_path", None)
        if bundle_zip_path is None:
            bundle_zip_path = getattr(namespace, "path", None)
        profile = getattr(namespace, "profile", None)
        if profile is None:
            profile = getattr(namespace, "profile_name", None)
        return check_bundle_payload(
            bundle_zip_path,
            getattr(namespace, "wrapper_root", None) or getattr(namespace, "wrapper_project_root", None),
            profile=profile,
            timestamp_token=getattr(namespace, "timestamp_token", None),
        )

    if "profile" not in kwargs and "profile_name" in kwargs:
        kwargs["profile"] = kwargs.pop("profile_name")
    return check_bundle_payload(*args, **kwargs)

def check_bundle_payload(
    bundle_zip_path: Path | str,
    wrapper_root: Path | str | None = None,
    profile: str | None = None,
    timestamp_token: str | None = None,
    requested_profile: str | None = None,
) -> dict[str, object]:
    import zipfile
    from pathlib import Path as _Path

    bundle_path = _Path(bundle_zip_path)
    effective_profile = requested_profile if requested_profile is not None else profile
    source_kind = "zip" if bundle_path.suffix.lower() == ".zip" else "directory"

    payload: dict[str, object] = {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": source_kind,
        "requested_profile": effective_profile,
        "ok": False,
        "issue_count": 0,
        "issues": [],
    }

    def build_issue(code: str, message: str, *, path: str | None = None) -> dict[str, object]:
        item: dict[str, object] = {"code": code, "message": message}
        if path is not None:
            item["path"] = path
        return item

    issues: list[dict[str, object]] = []
    launcher_issues: list[dict[str, object]] = []

    if not bundle_path.exists():
        payload["issues"] = [build_issue("missing_bundle", f"Bundle path does not exist: {bundle_path}", path=str(bundle_path))]
        payload["issue_count"] = 1
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []
        return payload

    if source_kind == "directory":
        from patchops.bundles import validate_extracted_bundle_dir
        from patchops.bundles.launcher_self_check import check_launcher_path

        validation = validate_extracted_bundle_dir(bundle_path)
        issues = [
            build_issue(message.code, message.message, path=message.path)
            for message in validation.errors
        ]

        manifest_path = bundle_path / "manifest.json"
        bundle_meta_path = bundle_path / "bundle_meta.json"
        content_root_path = bundle_path / "content"
        launcher_path = bundle_path / "run_with_patchops.ps1"

        payload["root_folder_name"] = bundle_path.name
        payload["manifest_path"] = str(manifest_path.resolve()) if manifest_path.exists() else None
        payload["bundle_meta_path"] = str(bundle_meta_path.resolve()) if bundle_meta_path.exists() else None
        payload["content_root_path"] = str(content_root_path.resolve()) if content_root_path.exists() else None
        payload["launcher_paths"] = ["run_with_patchops.ps1"] if launcher_path.exists() else []

        launcher_review = (
            check_launcher_path(launcher_path)
            if launcher_path.exists()
            else {"status": "reject", "launcher_path": None, "issue_count": 1, "issues": [build_issue("missing_root_launcher", f"Bundle root is missing saved root launcher: {launcher_path}", path=str(launcher_path))]}
        )
        payload["launcher_review"] = launcher_review
        payload["launcher_status"] = launcher_review["status"]
        payload["launcher_issue_count"] = launcher_review["issue_count"]
        payload["launcher_issue_codes"] = [item["code"] for item in launcher_review["issues"]]

        payload["issues"] = issues
        payload["issue_count"] = len(issues)
        payload["ok"] = len(issues) == 0 and payload["launcher_issue_count"] == 0
        return payload

    if source_kind != "zip":
        payload["issues"] = [build_issue("unsupported_source_kind", "Unsupported bundle source kind", path=str(bundle_path))]
        payload["issue_count"] = 1
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []
        return payload

    with zipfile.ZipFile(bundle_path) as zf:
        raw_members = [name for name in zf.namelist() if name and not name.endswith("/")]
    members = [name.replace("\\", "/") for name in raw_members]

    payload["member_count"] = len(members)
    roots = sorted({member.split("/", 1)[0] for member in members if "/" in member})
    payload["top_level_root"] = roots[0] if len(roots) == 1 else None

    if len(roots) != 1:
        issues.append(build_issue("invalid_root_count", f"Expected exactly one top-level root, found {len(roots)}", path=str(bundle_path)))
    else:
        root = roots[0]
        manifest_member = f"{root}/manifest.json"
        meta_member = f"{root}/bundle_meta.json"
        launcher_member = f"{root}/run_with_patchops.ps1"

        payload["manifest_path"] = manifest_member if manifest_member in members else None
        payload["launcher_path"] = launcher_member if launcher_member in members else None

        if manifest_member not in members:
            issues.append(build_issue("missing_manifest", f"Bundle zip is missing manifest.json under {root}", path=manifest_member))
        if meta_member not in members:
            issues.append(build_issue("missing_bundle_meta", f"Bundle zip is missing bundle_meta.json under {root}", path=meta_member))
        if launcher_member not in members:
            launcher_issues.append(build_issue("missing_root_launcher", f"Bundle zip is missing saved root launcher: {launcher_member}", path=launcher_member))

        payload["launcher_review"] = {
            "status": "safe" if not launcher_issues else "reject",
            "launcher_path": launcher_member if launcher_member in members else None,
            "issue_count": len(launcher_issues),
            "issues": launcher_issues,
        }
        payload["launcher_status"] = payload["launcher_review"]["status"]
        payload["launcher_issue_count"] = len(launcher_issues)
        payload["launcher_issue_codes"] = [item["code"] for item in launcher_issues]

    if "launcher_review" not in payload:
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []

    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = not issues and not launcher_issues
    return payload


def cli_check_bundle_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="patchops bundle_review")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = check_bundle_payload(
        args.bundle_zip_path,
        args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1

# PATCHOPS_CHECK_BUNDLE_EOF_OVERRIDE_START

def _patchops_check_bundle_payload_current(
    bundle_zip_path: Path | str,
    wrapper_root: Path | str | None = None,
    profile: str | None = None,
    timestamp_token: str | None = None,
    requested_profile: str | None = None,
) -> dict[str, object]:
    import zipfile
    from pathlib import Path as _Path

    bundle_path = _Path(bundle_zip_path)
    effective_profile = requested_profile if requested_profile is not None else profile
    source_kind = "zip" if bundle_path.suffix.lower() == ".zip" else "directory"

    payload: dict[str, object] = {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": source_kind,
        "requested_profile": effective_profile,
        "ok": False,
        "issue_count": 0,
        "issues": [],
    }

    def build_issue(code: str, message: str, *, path: str | None = None) -> dict[str, object]:
        item: dict[str, object] = {"code": code, "message": message}
        if path is not None:
            item["path"] = path
        return item

    issues: list[dict[str, object]] = []
    launcher_issues: list[dict[str, object]] = []

    if not bundle_path.exists():
        payload["issues"] = [build_issue("missing_bundle", f"Bundle path does not exist: {bundle_path}", path=str(bundle_path))]
        payload["issue_count"] = 1
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []
        return payload

    if source_kind != "zip":
        payload["issues"] = [build_issue("unsupported_source_kind", "check-bundle currently expects a bundle zip path", path=str(bundle_path))]
        payload["issue_count"] = 1
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []
        return payload

    with zipfile.ZipFile(bundle_path) as zf:
        raw_members = [name for name in zf.namelist() if name and not name.endswith("/")]
    members = [name.replace("\\", "/") for name in raw_members]

    payload["member_count"] = len(members)
    roots = sorted({member.split("/", 1)[0] for member in members if "/" in member})
    payload["top_level_root"] = roots[0] if len(roots) == 1 else None

    if len(roots) != 1:
        issues.append(build_issue("invalid_root_count", f"Expected exactly one top-level root, found {len(roots)}", path=str(bundle_path)))
    else:
        root = roots[0]
        manifest_member = f"{root}/manifest.json"
        meta_member = f"{root}/bundle_meta.json"
        launcher_member = f"{root}/run_with_patchops.ps1"

        payload["manifest_path"] = manifest_member if manifest_member in members else None
        payload["launcher_path"] = launcher_member if launcher_member in members else None

        if manifest_member not in members:
            issues.append(build_issue("missing_manifest", f"Bundle zip is missing manifest.json under {root}", path=manifest_member))
        if meta_member not in members:
            issues.append(build_issue("missing_bundle_meta", f"Bundle zip is missing bundle_meta.json under {root}", path=meta_member))
        if launcher_member not in members:
            launcher_issues.append(build_issue("missing_root_launcher", f"Bundle zip is missing saved root launcher: {launcher_member}", path=launcher_member))

        payload["launcher_review"] = {
            "status": "safe" if not launcher_issues else "reject",
            "launcher_path": launcher_member if launcher_member in members else None,
            "issue_count": len(launcher_issues),
            "issues": launcher_issues,
        }
        payload["launcher_status"] = payload["launcher_review"]["status"]
        payload["launcher_issue_count"] = len(launcher_issues)
        payload["launcher_issue_codes"] = [item["code"] for item in launcher_issues]

    if "launcher_review" not in payload:
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []

    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = not issues and not launcher_issues
    return payload


def _patchops_cli_check_bundle_main_current(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="patchops bundle_review")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = _patchops_check_bundle_payload_current(
        args.bundle_zip_path,
        args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1

check_bundle_payload = _patchops_check_bundle_payload_current
cli_check_bundle_main = _patchops_cli_check_bundle_main_current
# PATCHOPS_CHECK_BUNDLE_EOF_OVERRIDE_END

# PATCHOPS_CHECK_BUNDLE_RUNTIME_WRAPPER_START
import zipfile as _patchops_check_bundle_zipfile
from pathlib import Path as _PatchOpsCheckBundlePath

_PATCHOPS_CHECK_BUNDLE_ORIGINAL = check_bundle_payload


def _patchops_check_bundle_issue(code, message, path=None):
    item = {"code": code, "message": message}
    if path is not None:
        item["path"] = path
    return item


def check_bundle_payload(*args, **kwargs):
    payload = _PATCHOPS_CHECK_BUNDLE_ORIGINAL(*args, **kwargs)
    if not isinstance(payload, dict):
        payload = {}

    bundle_zip_path = None
    if args:
        bundle_zip_path = args[0]
    if bundle_zip_path is None:
        bundle_zip_path = kwargs.get("bundle_zip_path")
    if bundle_zip_path is None:
        bundle_zip_path = kwargs.get("bundle_path")

    requested_profile = kwargs.get("requested_profile")
    if requested_profile is None:
        requested_profile = kwargs.get("profile")

    bundle_path = _PatchOpsCheckBundlePath(bundle_zip_path)
    payload["path"] = str(bundle_path)
    payload["exists"] = bundle_path.exists()
    payload["source_kind"] = "zip" if bundle_path.suffix.lower() == ".zip" else "directory"
    payload["requested_profile"] = requested_profile

    issues = []
    launcher_issues = []

    if not bundle_path.exists():
        issues.append(_patchops_check_bundle_issue("missing_bundle", f"Bundle path does not exist: {bundle_path}", path=str(bundle_path)))
    elif bundle_path.suffix.lower() != ".zip":
        issues.append(_patchops_check_bundle_issue("unsupported_source_kind", "check-bundle currently expects a bundle zip path", path=str(bundle_path)))
    else:
        with _patchops_check_bundle_zipfile.ZipFile(bundle_path) as zf:
            members = [name.replace(chr(92), "/") for name in zf.namelist() if name and not name.endswith("/")]
        payload["member_count"] = len(members)
        roots = sorted({member.split("/", 1)[0] for member in members if "/" in member})
        payload["top_level_root"] = roots[0] if len(roots) == 1 else None

        if len(roots) != 1:
            issues.append(_patchops_check_bundle_issue("invalid_root_count", f"Expected exactly one top-level root, found {len(roots)}", path=str(bundle_path)))
        else:
            root = roots[0]
            manifest_member = f"{root}/manifest.json"
            meta_member = f"{root}/bundle_meta.json"
            launcher_member = f"{root}/run_with_patchops.ps1"
            payload["manifest_path"] = manifest_member if manifest_member in members else None
            payload["launcher_path"] = launcher_member if launcher_member in members else None

            if manifest_member not in members:
                issues.append(_patchops_check_bundle_issue("missing_manifest", f"Bundle zip is missing manifest.json under {root}", path=manifest_member))
            if meta_member not in members:
                issues.append(_patchops_check_bundle_issue("missing_bundle_meta", f"Bundle zip is missing bundle_meta.json under {root}", path=meta_member))
            if launcher_member not in members:
                launcher_issues.append(_patchops_check_bundle_issue("missing_root_launcher", f"Bundle zip is missing saved root launcher: {launcher_member}", path=launcher_member))

            payload["launcher_review"] = {
                "status": "safe" if not launcher_issues else "reject",
                "launcher_path": launcher_member if launcher_member in members else None,
                "issue_count": len(launcher_issues),
                "issues": launcher_issues,
            }
            payload["launcher_status"] = payload["launcher_review"]["status"]
            payload["launcher_issue_count"] = len(launcher_issues)
            payload["launcher_issue_codes"] = [item["code"] for item in launcher_issues]

    if "launcher_review" not in payload:
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = payload["launcher_review"]["status"]
        payload["launcher_issue_count"] = payload["launcher_review"]["issue_count"]
        payload["launcher_issue_codes"] = [item["code"] for item in payload["launcher_review"]["issues"]]

    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = not issues and payload["launcher_review"]["status"] != "reject"
    return payload


_PATCHOPS_CLI_CHECK_BUNDLE_MAIN_ORIGINAL = cli_check_bundle_main


def cli_check_bundle_main(argv=None):
    parser = argparse.ArgumentParser(prog="patchops bundle_review")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = check_bundle_payload(
        args.bundle_zip_path,
        args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1
# PATCHOPS_CHECK_BUNDLE_RUNTIME_WRAPPER_END

# PATCHOPS_TRUE_EOF_CHECK_BUNDLE_OVERRIDE_20260421

def _patchops_true_eof_build_issue(code, message, path=None):
    item = {"code": code, "message": message}
    if path is not None:
        item["path"] = path
    return item


def _patchops_true_eof_check_bundle_payload(
    bundle_zip_path,
    wrapper_root=None,
    profile=None,
    timestamp_token=None,
    requested_profile=None,
):
    import zipfile
    from pathlib import Path

    bundle_path = Path(bundle_zip_path).resolve()
    effective_profile = requested_profile if requested_profile is not None else profile
    source_kind = "zip" if bundle_path.suffix.lower() == ".zip" else "directory"

    payload = {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": source_kind,
        "requested_profile": effective_profile,
        "ok": False,
        "issue_count": 0,
        "issues": [],
        "root_folder_name": None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "content_root_path": None,
        "launcher_paths": [],
    }

    def issue(code, message, path=None):
        item = {"code": code, "message": message}
        if path is not None:
            item["path"] = path
        return item

    issues = []

    if not bundle_path.exists():
        issues.append(issue("missing_bundle", f"Bundle path does not exist: {bundle_path}", path=str(bundle_path)))
    elif source_kind != "zip":
        issues.append(issue("unsupported_source_kind", "check-bundle currently expects a bundle zip path", path=str(bundle_path)))
    else:
        with zipfile.ZipFile(bundle_path) as zf:
            members = [name.replace(chr(92), "/") for name in zf.namelist() if name and not name.endswith("/")]

        payload["member_count"] = len(members)
        roots = sorted({member.split("/", 1)[0] for member in members if "/" in member})
        payload["top_level_root"] = roots[0] if len(roots) == 1 else None
        payload["root_folder_name"] = payload["top_level_root"]

        if len(roots) != 1:
            issues.append(issue("invalid_root_count", f"Expected exactly one top-level root, found {len(roots)}", path=str(bundle_path)))
        else:
            root = roots[0]
            manifest_member = f"{root}/manifest.json"
            meta_member = f"{root}/bundle_meta.json"
            content_root = f"{root}/content"
            root_launcher = f"{root}/run_with_patchops.ps1"
            legacy_launchers = sorted(
                member
                for member in members
                if member.startswith(f"{root}/launchers/") and member.lower().endswith(".ps1")
            )
            launcher_paths = [root_launcher] if root_launcher in members else legacy_launchers

            payload["manifest_path"] = manifest_member if manifest_member in members else None
            payload["bundle_meta_path"] = meta_member if meta_member in members else None
            payload["content_root_path"] = content_root
            payload["launcher_paths"] = launcher_paths
            payload["launcher_path"] = launcher_paths[0] if launcher_paths else None

            if manifest_member not in members:
                issues.append(issue("missing_manifest", f"Bundle zip is missing manifest.json under {root}", path=manifest_member))
            if meta_member not in members:
                issues.append(issue("missing_bundle_meta", f"Bundle zip is missing bundle_meta.json under {root}", path=meta_member))
            if not any(member.startswith(f"{content_root}/") for member in members):
                issues.append(issue("missing_content_root", f"Bundle zip is missing content/ files under {root}", path=content_root))
            if not launcher_paths:
                issues.append(issue("missing_launcher", f"Bundle zip is missing a supported launcher under {root}", path=root))

    payload["launcher_review"] = {
        "status": "accept" if not any(item["code"] == "missing_launcher" for item in issues) else "reject",
        "launcher_path": payload.get("launcher_path"),
        "issue_count": sum(1 for item in issues if item["code"] == "missing_launcher"),
        "issues": [item for item in issues if item["code"] == "missing_launcher"],
    }
    payload["launcher_status"] = payload["launcher_review"]["status"]
    payload["launcher_issue_count"] = payload["launcher_review"]["issue_count"]
    payload["launcher_issue_codes"] = [item["code"] for item in payload["launcher_review"]["issues"]]
    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = len(issues) == 0
    return payload

check_bundle_payload = _patchops_true_eof_check_bundle_payload
cli_check_bundle_main = _patchops_cli_check_bundle_main_current
# PATCHOPS_FINAL_CHECK_BUNDLE_CLI_MAIN_20260421

def _patchops_final_check_bundle_cli_main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="patchops bundle_review")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = check_bundle_payload(
        args.bundle_zip_path,
        args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1

cli_check_bundle_main = _patchops_final_check_bundle_cli_main

# PATCHOPS_B1H_DIRECTORY_BUNDLE_OVERRIDE_20260422
from pathlib import Path as _PATCHOPS_B1H_Path

def _patchops_b1h_directory_payload(bundle_path: _PATCHOPS_B1H_Path, *, requested_profile: str | None = None) -> dict[str, object]:
    bundle_path = _PATCHOPS_B1H_Path(bundle_path)
    payload: dict[str, object] = {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": "directory",
        "requested_profile": requested_profile,
        "ok": False,
        "issue_count": 0,
        "issues": [],
    }

    def build_issue(code: str, message: str, *, path: str | None = None) -> dict[str, object]:
        item: dict[str, object] = {"code": code, "message": message}
        if path is not None:
            item["path"] = path
        return item

    if not bundle_path.exists():
        payload["issues"] = [build_issue("missing_bundle", f"Bundle path does not exist: {bundle_path}", path=str(bundle_path))]
        payload["issue_count"] = 1
        payload["launcher_review"] = {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []}
        payload["launcher_status"] = "reject"
        payload["launcher_issue_count"] = 0
        payload["launcher_issue_codes"] = []
        return payload

    manifest_path = bundle_path / "manifest.json"
    bundle_meta_path = bundle_path / "bundle_meta.json"
    content_root_path = bundle_path / "content"
    root_launcher_path = bundle_path / "run_with_patchops.ps1"
    legacy_launchers = sorted((bundle_path / "launchers").glob("*.ps1")) if (bundle_path / "launchers").exists() else []
    launcher_paths = [root_launcher_path] if root_launcher_path.exists() else legacy_launchers

    issues: list[dict[str, object]] = []
    launcher_issues: list[dict[str, object]] = []

    payload["root_folder_name"] = bundle_path.name
    payload["manifest_path"] = str(manifest_path.resolve()) if manifest_path.exists() else None
    payload["bundle_meta_path"] = str(bundle_meta_path.resolve()) if bundle_meta_path.exists() else None
    payload["content_root_path"] = str(content_root_path.resolve()) if content_root_path.exists() else None
    payload["launcher_paths"] = [str(path.resolve()) for path in launcher_paths]
    payload["launcher_path"] = payload["launcher_paths"][0] if payload["launcher_paths"] else None

    if not manifest_path.exists():
        issues.append(build_issue("missing_manifest", f"Bundle root is missing manifest.json: {manifest_path}", path=str(manifest_path)))
    if not bundle_meta_path.exists():
        issues.append(build_issue("missing_bundle_meta", f"Bundle root is missing bundle_meta.json: {bundle_meta_path}", path=str(bundle_meta_path)))
    if not content_root_path.exists() or not any(path.is_file() for path in content_root_path.rglob("*")):
        issues.append(build_issue("missing_content_root", f"Bundle root is missing content/ files: {content_root_path}", path=str(content_root_path)))
    if not launcher_paths:
        launcher_issues.append(build_issue("missing_root_launcher", f"Bundle root is missing saved root launcher: {root_launcher_path}", path=str(root_launcher_path)))

    launcher_status = "safe" if not launcher_issues else "reject"
    payload["launcher_review"] = {
        "status": launcher_status,
        "launcher_path": payload["launcher_path"],
        "issue_count": len(launcher_issues),
        "issues": launcher_issues,
    }
    payload["launcher_status"] = launcher_status
    payload["launcher_issue_count"] = len(launcher_issues)
    payload["launcher_issue_codes"] = [item["code"] for item in launcher_issues]
    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = len(issues) == 0 and launcher_status != "reject"
    return payload

_PATCHOPS_B1H_PREV_CHECK_BUNDLE_PAYLOAD = check_bundle_payload

def check_bundle_payload(
    bundle_zip_path,
    wrapper_root=None,
    profile=None,
    timestamp_token=None,
    requested_profile=None,
):
    bundle_path = _PATCHOPS_B1H_Path(bundle_zip_path)
    effective_profile = requested_profile if requested_profile is not None else profile
    if bundle_path.exists() and bundle_path.is_dir():
        return _patchops_b1h_directory_payload(bundle_path, requested_profile=effective_profile)
    return _PATCHOPS_B1H_PREV_CHECK_BUNDLE_PAYLOAD(
        bundle_zip_path,
        wrapper_root=wrapper_root,
        profile=profile,
        timestamp_token=timestamp_token,
        requested_profile=requested_profile,
    )

if "check_bundle_cli_payload_compat" in globals():
    def check_bundle_cli_payload_compat(*args, **kwargs):
        if "profile" not in kwargs and "profile_name" in kwargs:
            kwargs["profile"] = kwargs.pop("profile_name")
        return check_bundle_payload(*args, **kwargs)

# PATCHOPS_B5D_BUNDLE_REVIEW_PAYLOAD_NORMALIZATION_20260422
_PATCHOPS_B5D_PREV_CHECK_BUNDLE_PAYLOAD = check_bundle_payload

def check_bundle_payload(*args, **kwargs):
    payload = _PATCHOPS_B5D_PREV_CHECK_BUNDLE_PAYLOAD(*args, **kwargs)

    if isinstance(payload, dict):
        launcher_review = payload.get("launcher_review")
        if isinstance(launcher_review, dict):
            status = launcher_review.get("status")
            if status == "accept":
                status = "safe"
            launcher_review["status"] = status
            payload["launcher_review"] = launcher_review
            payload["launcher_status"] = status

            launcher_issues = launcher_review.get("issues", ())
            if not isinstance(launcher_issues, (list, tuple)):
                launcher_issues = []
            payload["launcher_issue_count"] = int(launcher_review.get("issue_count", len(launcher_issues)) or 0)

            codes = []
            for item in launcher_issues:
                if isinstance(item, dict) and item.get("code"):
                    codes.append(item["code"])
            payload["launcher_issue_codes"] = codes

            issues = payload.get("issues", ())
            if not isinstance(issues, (list, tuple)):
                issues = []
            payload["issue_count"] = int(payload.get("issue_count", len(issues)) or 0)
            payload["ok"] = bool(payload["issue_count"] == 0 and status != "reject")

    return payload

# PATCHOPS_B1_FINAL_CHECK_BUNDLE_CONTRACT_20260423
import argparse as _patchops_b1_argparse
import json as _patchops_b1_json
import zipfile as _patchops_b1_zipfile
from pathlib import Path as _patchops_b1_Path

def _patchops_b1_issue(code: str, message: str, path: str | None = None) -> dict[str, object]:
    item: dict[str, object] = {"code": code, "message": message}
    if path is not None:
        item["path"] = path
    return item

def _patchops_b1_warning(code: str, message: str, path: str | None = None) -> dict[str, object]:
    item: dict[str, object] = {"code": code, "message": message}
    if path is not None:
        item["path"] = path
    return item

def _patchops_b1_normalize(name: str) -> str:
    return str(name or "").replace("\\", "/").strip("/")

def _patchops_b1_zip_launcher_members(root: str, members: list[str]) -> list[str]:
    root_launcher = f"{root}/run_with_patchops.ps1"
    if root_launcher in members:
        return [root_launcher]
    launchers_prefix = f"{root}/launchers/"
    return sorted(
        member
        for member in members
        if member.startswith(launchers_prefix) and member.lower().endswith(".ps1")
    )

def _patchops_b1_directory_launcher_members(bundle_root: _patchops_b1_Path) -> list[_patchops_b1_Path]:
    root_launcher = bundle_root / "run_with_patchops.ps1"
    if root_launcher.is_file():
        return [root_launcher]
    launchers_root = bundle_root / "launchers"
    if launchers_root.is_dir():
        return sorted(path for path in launchers_root.rglob("*.ps1") if path.is_file())
    return []

def _patchops_b1_directory_payload(bundle_path: _patchops_b1_Path, *, requested_profile: str | None = None) -> dict[str, object]:
    bundle_path = bundle_path.resolve()
    payload: dict[str, object] = {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": "directory",
        "requested_profile": requested_profile,
        "profile": requested_profile,
        "ok": False,
        "issue_count": 0,
        "issues": [],
        "warning_count": 0,
        "warnings": [],
        "top_level_root": bundle_path.name if bundle_path.exists() else None,
        "root_folder_name": bundle_path.name if bundle_path.exists() else None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "content_root_path": None,
        "launcher_paths": [],
        "member_count": 0,
    }

    issues: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    if not bundle_path.exists():
        issues.append(_patchops_b1_issue("missing_bundle_zip", f"Bundle path does not exist: {bundle_path}", str(bundle_path)))
    else:
        manifest_path = bundle_path / "manifest.json"
        bundle_meta_path = bundle_path / "bundle_meta.json"
        content_root_path = bundle_path / "content"
        launcher_paths = _patchops_b1_directory_launcher_members(bundle_path)

        payload["manifest_path"] = str(manifest_path.resolve()) if manifest_path.is_file() else None
        payload["bundle_meta_path"] = str(bundle_meta_path.resolve()) if bundle_meta_path.is_file() else None
        payload["content_root_path"] = "content" if content_root_path.is_dir() else None
        payload["launcher_paths"] = [str(path.resolve()) for path in launcher_paths]
        payload["member_count"] = len(payload["launcher_paths"])

        duplicate_nested_root = bundle_path / bundle_path.name
        if duplicate_nested_root.is_dir():
            warnings.append(_patchops_b1_warning("duplicate_nested_root", "Bundle directory contains a duplicate nested root folder.", str(duplicate_nested_root)))

        if not manifest_path.is_file():
            issues.append(_patchops_b1_issue("missing_manifest", f"Bundle directory is missing manifest.json.", str(manifest_path)))

        if not bundle_meta_path.is_file():
            warnings.append(_patchops_b1_warning("missing_bundle_meta", f"Bundle directory is missing bundle_meta.json.", str(bundle_meta_path)))

        if not content_root_path.is_dir():
            issues.append(_patchops_b1_issue("missing_content_root", f"Bundle directory is missing the content/ root.", str(content_root_path)))

        if not launcher_paths:
            issues.append(_patchops_b1_issue("missing_launcher", f"Bundle directory is missing a supported launcher.", str(bundle_path)))

    launcher_review_issues = [item for item in issues if item["code"] == "missing_launcher"]
    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["warnings"] = warnings
    payload["warning_count"] = len(warnings)
    payload["launcher_review"] = {
        "status": "safe" if not launcher_review_issues else "reject",
        "launcher_path": payload["launcher_paths"][0] if payload["launcher_paths"] else None,
        "issue_count": len(launcher_review_issues),
        "issues": launcher_review_issues,
    }
    payload["launcher_status"] = payload["launcher_review"]["status"]
    payload["launcher_issue_count"] = payload["launcher_review"]["issue_count"]
    payload["launcher_issue_codes"] = [item["code"] for item in payload["launcher_review"]["issues"]]
    payload["ok"] = len(issues) == 0
    return payload

def _patchops_b1_zip_payload(bundle_path: _patchops_b1_Path, *, requested_profile: str | None = None) -> dict[str, object]:
    bundle_path = bundle_path.resolve()
    payload: dict[str, object] = {
        "path": str(bundle_path),
        "exists": bundle_path.exists(),
        "source_kind": "zip",
        "requested_profile": requested_profile,
        "profile": requested_profile,
        "ok": False,
        "issue_count": 0,
        "issues": [],
        "warning_count": 0,
        "warnings": [],
        "top_level_root": None,
        "root_folder_name": None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "content_root_path": None,
        "launcher_paths": [],
        "member_count": 0,
    }

    issues: list[dict[str, object]] = []
    warnings: list[dict[str, object]] = []

    if not bundle_path.exists():
        issues.append(_patchops_b1_issue("missing_bundle_zip", f"Bundle zip does not exist: {bundle_path}", str(bundle_path)))
    else:
        try:
            with _patchops_b1_zipfile.ZipFile(bundle_path, "r") as zf:
                members = [_patchops_b1_normalize(name) for name in zf.namelist() if _patchops_b1_normalize(name)]
        except _patchops_b1_zipfile.BadZipFile:
            issues.append(_patchops_b1_issue("invalid_zip", "Bundle zip could not be opened as a valid zip archive.", str(bundle_path)))
            members = []
        except Exception as exc:
            issues.append(_patchops_b1_issue("invalid_zip", f"Bundle zip could not be reviewed cleanly: {exc}", str(bundle_path)))
            members = []
        else:
            payload["member_count"] = len(members)
            roots = sorted({member.split("/", 1)[0] for member in members if "/" in member})
            if len(roots) != 1:
                issues.append(_patchops_b1_issue("multiple_roots", f"Expected exactly one top-level root, found {len(roots)}", str(bundle_path)))
            else:
                root = roots[0]
                payload["top_level_root"] = root
                payload["root_folder_name"] = root

                manifest_member = f"{root}/manifest.json"
                meta_member = f"{root}/bundle_meta.json"
                content_root_member = f"{root}/content"
                launcher_members = _patchops_b1_zip_launcher_members(root, members)

                payload["manifest_path"] = manifest_member if manifest_member in members else None
                payload["bundle_meta_path"] = meta_member if meta_member in members else None
                payload["content_root_path"] = content_root_member if any(member.startswith(f"{content_root_member}/") for member in members) else None
                payload["launcher_paths"] = launcher_members

                if manifest_member not in members:
                    issues.append(_patchops_b1_issue("missing_manifest", f"Bundle zip is missing manifest.json under {root}", manifest_member))
                if meta_member not in members:
                    warnings.append(_patchops_b1_warning("missing_bundle_meta", f"bundle_meta.json is absent under {root}; current compatibility treats this as a warning, not a top-level failure.", meta_member))
                if payload["content_root_path"] is None:
                    issues.append(_patchops_b1_issue("missing_content_root", f"Bundle zip is missing content/ files under {root}", content_root_member))
                if not launcher_members:
                    issues.append(_patchops_b1_issue("missing_launcher", f"Bundle zip is missing a supported launcher under {root}", root))

    launcher_review_issues = [item for item in issues if item["code"] == "missing_launcher"]
    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["warnings"] = warnings
    payload["warning_count"] = len(warnings)
    payload["launcher_review"] = {
        "status": "safe" if not launcher_review_issues else "reject",
        "launcher_path": payload["launcher_paths"][0] if payload["launcher_paths"] else None,
        "issue_count": len(launcher_review_issues),
        "issues": launcher_review_issues,
    }
    payload["launcher_status"] = payload["launcher_review"]["status"]
    payload["launcher_issue_count"] = payload["launcher_review"]["issue_count"]
    payload["launcher_issue_codes"] = [item["code"] for item in payload["launcher_review"]["issues"]]
    payload["ok"] = len(issues) == 0
    return payload

def _patchops_b1_check_bundle_payload(
    bundle_zip_path,
    wrapper_root=None,
    profile=None,
    timestamp_token=None,
    requested_profile=None,
):
    bundle_path = _patchops_b1_Path(bundle_zip_path)
    effective_profile = requested_profile if requested_profile is not None else profile
    if bundle_path.suffix.lower() == ".zip":
        return _patchops_b1_zip_payload(bundle_path, requested_profile=effective_profile)
    return _patchops_b1_directory_payload(bundle_path, requested_profile=effective_profile)

def _patchops_b1_check_bundle_cli_payload(*args, **kwargs):
    if args and hasattr(args[0], "__dict__") and not isinstance(args[0], (str, _patchops_b1_Path)):
        namespace = args[0]
        bundle_zip_path = getattr(namespace, "bundle_zip_path", None)
        if bundle_zip_path is None:
            bundle_zip_path = getattr(namespace, "path", None)
        profile_name = getattr(namespace, "profile", None)
        if profile_name is None:
            profile_name = getattr(namespace, "profile_name", None)
        return _patchops_b1_check_bundle_payload(
            bundle_zip_path,
            wrapper_root=getattr(namespace, "wrapper_root", None) or getattr(namespace, "wrapper_project_root", None),
            profile=profile_name,
            timestamp_token=getattr(namespace, "timestamp_token", None),
        )

    if "profile" not in kwargs and "profile_name" in kwargs:
        kwargs["profile"] = kwargs.pop("profile_name")
    if "wrapper_root" not in kwargs and "wrapper_project_root" in kwargs:
        kwargs["wrapper_root"] = kwargs.pop("wrapper_project_root")
    return _patchops_b1_check_bundle_payload(*args, **kwargs)

def _patchops_b1_cli_check_bundle_main(argv=None):
    parser = _patchops_b1_argparse.ArgumentParser(prog="patchops check-bundle")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = _patchops_b1_check_bundle_payload(
        args.bundle_zip_path,
        wrapper_root=args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(_patchops_b1_json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1

check_bundle_payload = _patchops_b1_check_bundle_payload
check_bundle_cli_payload = _patchops_b1_check_bundle_cli_payload
cli_check_bundle_main = _patchops_b1_cli_check_bundle_main

# PATCHOPS_B2_INSPECT_PLAN_CONTRACT_20260423
import argparse as _patchops_b2_argparse
import json as _patchops_b2_json
import zipfile as _patchops_b2_zipfile
from pathlib import Path as _patchops_b2_Path

def _patchops_b2_issue_texts_from_check(payload: dict[str, object]) -> list[str]:
    issue_texts: list[str] = []
    for item in list(payload.get("issues", [])):
        if isinstance(item, dict):
            message = str(item.get("message", "")).strip()
            if message:
                issue_texts.append(message)
        elif isinstance(item, str):
            text = item.strip()
            if text:
                issue_texts.append(text)
    return issue_texts

def _patchops_b2_launchers_from_directory(bundle_root: _patchops_b2_Path) -> list[str]:
    root_launcher = bundle_root / "run_with_patchops.ps1"
    if root_launcher.is_file():
        return [str(root_launcher.resolve())]
    launchers_root = bundle_root / "launchers"
    if launchers_root.is_dir():
        return [str(path.resolve()) for path in sorted(launchers_root.rglob("*.ps1")) if path.is_file()]
    return []

def _patchops_b2_launchers_from_zip(bundle_zip_path: _patchops_b2_Path, root: str) -> list[str]:
    launchers: list[str] = []
    with _patchops_b2_zipfile.ZipFile(bundle_zip_path, "r") as zf:
        members = [str(name or "").replace("\\", "/") for name in zf.namelist() if name and not name.endswith("/")]
    root_launcher = f"{root}/run_with_patchops.ps1"
    if root_launcher in members:
        launchers.append(root_launcher)
    launchers.extend(
        member for member in sorted(members)
        if member.startswith(f"{root}/launchers/") and member.lower().endswith(".ps1")
    )
    deduped: list[str] = []
    for item in launchers:
        if item not in deduped:
            deduped.append(item)
    return deduped

def _patchops_b2_directory_inspect_payload(bundle_path: _patchops_b2_Path, *, profile: str | None = None) -> dict[str, object]:
    bundle_path = bundle_path.resolve()
    payload: dict[str, object] = {
        "ok": False,
        "exists": bundle_path.exists(),
        "bundle_zip_path": str(bundle_path),
        "source_kind": "directory",
        "requested_profile": profile,
        "profile": profile,
        "root_folder": bundle_path.name if bundle_path.exists() else None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "readme_path": None,
        "content_prefix": None,
        "launchers": [],
        "launcher_review": {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []},
        "launcher_status": "reject",
        "launcher_issue_count": 0,
        "launcher_issue_codes": [],
        "issue_count": 0,
        "issues": [],
    }

    issues: list[str] = []
    launcher_issues: list[dict[str, object]] = []

    if not bundle_path.exists():
        issues.append(f"Bundle path does not exist: {bundle_path}")
    else:
        manifest_path = bundle_path / "manifest.json"
        bundle_meta_path = bundle_path / "bundle_meta.json"
        readme_path = bundle_path / "README.txt"
        content_root = bundle_path / "content"
        launchers = _patchops_b2_launchers_from_directory(bundle_path)

        payload["manifest_path"] = str(manifest_path.resolve()) if manifest_path.is_file() else None
        payload["bundle_meta_path"] = str(bundle_meta_path.resolve()) if bundle_meta_path.is_file() else None
        payload["readme_path"] = str(readme_path.resolve()) if readme_path.is_file() else None
        payload["content_prefix"] = "content/" if content_root.is_dir() else None
        payload["launchers"] = launchers

        if not manifest_path.is_file():
            issues.append(f"Bundle directory is missing manifest.json at {manifest_path}")
        if not bundle_meta_path.is_file():
            issues.append(f"Bundle directory is missing bundle_meta.json at {bundle_meta_path}")
        if not readme_path.is_file():
            issues.append(f"Bundle directory is missing README.txt at {readme_path}")
        if not content_root.is_dir():
            issues.append(f"Bundle directory is missing content/ at {content_root}")
        if not launchers:
            launcher_issues.append({"code": "missing_launcher", "message": f"Bundle directory is missing a supported launcher under {bundle_path}", "path": str(bundle_path)})

    payload["launcher_review"] = {
        "status": "safe" if not launcher_issues else "reject",
        "launcher_path": payload["launchers"][0] if payload["launchers"] else None,
        "issue_count": len(launcher_issues),
        "issues": launcher_issues,
    }
    payload["launcher_status"] = payload["launcher_review"]["status"]
    payload["launcher_issue_count"] = payload["launcher_review"]["issue_count"]
    payload["launcher_issue_codes"] = [item["code"] for item in launcher_issues]
    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = len(issues) == 0 and not launcher_issues
    return payload

def _patchops_b2_zip_inspect_payload(bundle_zip_path: _patchops_b2_Path, *, profile: str | None = None) -> dict[str, object]:
    bundle_zip_path = bundle_zip_path.resolve()
    payload: dict[str, object] = {
        "ok": False,
        "exists": bundle_zip_path.exists(),
        "bundle_zip_path": str(bundle_zip_path),
        "source_kind": "zip",
        "requested_profile": profile,
        "profile": profile,
        "root_folder": None,
        "manifest_path": None,
        "bundle_meta_path": None,
        "readme_path": None,
        "content_prefix": None,
        "launchers": [],
        "launcher_review": {"status": "reject", "launcher_path": None, "issue_count": 0, "issues": []},
        "launcher_status": "reject",
        "launcher_issue_count": 0,
        "launcher_issue_codes": [],
        "issue_count": 0,
        "issues": [],
    }

    issues: list[str] = []
    launcher_issues: list[dict[str, object]] = []

    if not bundle_zip_path.exists():
        issues.append(f"Bundle zip does not exist: {bundle_zip_path}")
    else:
        try:
            with _patchops_b2_zipfile.ZipFile(bundle_zip_path, "r") as zf:
                members = [str(name or "").replace("\\", "/") for name in zf.namelist() if name and not name.endswith("/")]
        except _patchops_b2_zipfile.BadZipFile:
            issues.append(f"Bundle zip could not be opened as a valid zip archive: {bundle_zip_path}")
            members = []
        except Exception as exc:
            issues.append(f"Bundle zip could not be inspected cleanly: {exc}")
            members = []
        else:
            roots = sorted({member.split("/", 1)[0] for member in members if "/" in member})
            if len(roots) != 1:
                issues.append(f"Expected exactly one top-level root, found {len(roots)}")
            else:
                root = roots[0]
                payload["root_folder"] = root
                manifest_member = f"{root}/manifest.json"
                bundle_meta_member = f"{root}/bundle_meta.json"
                readme_member = f"{root}/README.txt"
                content_prefix = f"{root}/content/"
                launchers = _patchops_b2_launchers_from_zip(bundle_zip_path, root)

                payload["manifest_path"] = manifest_member if manifest_member in members else None
                payload["bundle_meta_path"] = bundle_meta_member if bundle_meta_member in members else None
                payload["readme_path"] = readme_member if readme_member in members else None
                payload["content_prefix"] = content_prefix if any(member.startswith(content_prefix) for member in members) else None
                payload["launchers"] = launchers

                if manifest_member not in members:
                    issues.append(f"Bundle zip is missing manifest.json under {root}")
                if bundle_meta_member not in members:
                    issues.append(f"Bundle zip is missing bundle_meta.json under {root}")
                if readme_member not in members:
                    issues.append(f"Bundle zip is missing README.txt under {root}")
                if payload["content_prefix"] is None:
                    issues.append(f"Bundle zip is missing content/ files under {root}")
                if not launchers:
                    launcher_issues.append({"code": "missing_launcher", "message": f"Bundle zip is missing a supported launcher under {root}", "path": root})

    payload["launcher_review"] = {
        "status": "safe" if not launcher_issues else "reject",
        "launcher_path": payload["launchers"][0] if payload["launchers"] else None,
        "issue_count": len(launcher_issues),
        "issues": launcher_issues,
    }
    payload["launcher_status"] = payload["launcher_review"]["status"]
    payload["launcher_issue_count"] = payload["launcher_review"]["issue_count"]
    payload["launcher_issue_codes"] = [item["code"] for item in launcher_issues]
    payload["issues"] = issues
    payload["issue_count"] = len(issues)
    payload["ok"] = len(issues) == 0 and not launcher_issues
    return payload

def _patchops_b2_inspect_bundle_payload(bundle_zip_path, wrapper_root=None, profile=None, timestamp_token=None, requested_profile=None):
    bundle_path = _patchops_b2_Path(bundle_zip_path)
    effective_profile = requested_profile if requested_profile is not None else profile
    if bundle_path.suffix.lower() == ".zip":
        return _patchops_b2_zip_inspect_payload(bundle_path, profile=effective_profile)
    return _patchops_b2_directory_inspect_payload(bundle_path, profile=effective_profile)

def _patchops_b2_inspect_bundle_cli_payload(*args, **kwargs):
    if args and hasattr(args[0], "__dict__") and not isinstance(args[0], (str, _patchops_b2_Path)):
        namespace = args[0]
        bundle_zip_path = getattr(namespace, "bundle_zip_path", None)
        if bundle_zip_path is None:
            bundle_zip_path = getattr(namespace, "path", None)
        profile_name = getattr(namespace, "profile", None)
        if profile_name is None:
            profile_name = getattr(namespace, "profile_name", None)
        return _patchops_b2_inspect_bundle_payload(
            bundle_zip_path,
            wrapper_root=getattr(namespace, "wrapper_root", None) or getattr(namespace, "wrapper_project_root", None),
            profile=profile_name,
            timestamp_token=getattr(namespace, "timestamp_token", None),
        )
    if "profile" not in kwargs and "profile_name" in kwargs:
        kwargs["profile"] = kwargs.pop("profile_name")
    if "wrapper_root" not in kwargs and "wrapper_project_root" in kwargs:
        kwargs["wrapper_root"] = kwargs.pop("wrapper_project_root")
    return _patchops_b2_inspect_bundle_payload(*args, **kwargs)

def _patchops_b2_cli_inspect_bundle_main(argv=None):
    parser = _patchops_b2_argparse.ArgumentParser(prog="patchops inspect-bundle")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = _patchops_b2_inspect_bundle_payload(
        args.bundle_zip_path,
        wrapper_root=args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(_patchops_b2_json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1

def _patchops_b2_plan_bundle_payload(bundle_zip_path, wrapper_root=None, profile=None, timestamp_token=None, requested_profile=None):
    inspect_payload = _patchops_b2_inspect_bundle_payload(
        bundle_zip_path,
        wrapper_root=wrapper_root,
        profile=profile,
        timestamp_token=timestamp_token,
        requested_profile=requested_profile,
    )
    bundle_path = _patchops_b2_Path(bundle_zip_path).resolve()
    command_plan = [
        f"py -m patchops.cli check-bundle {bundle_path}",
        f"py -m patchops.cli inspect-bundle {bundle_path}",
        f"py -m patchops.cli plan-bundle {bundle_path}",
    ]
    payload: dict[str, object] = {
        "ok": bool(inspect_payload.get("ok")),
        "exists": inspect_payload.get("exists"),
        "bundle_zip_path": inspect_payload.get("bundle_zip_path"),
        "source_kind": inspect_payload.get("source_kind"),
        "requested_profile": inspect_payload.get("requested_profile"),
        "profile": inspect_payload.get("profile"),
        "root_folder": inspect_payload.get("root_folder"),
        "manifest_path": inspect_payload.get("manifest_path"),
        "bundle_meta_path": inspect_payload.get("bundle_meta_path"),
        "readme_path": inspect_payload.get("readme_path"),
        "content_prefix": inspect_payload.get("content_prefix"),
        "launchers": inspect_payload.get("launchers", []),
        "launcher_review": inspect_payload.get("launcher_review"),
        "launcher_status": inspect_payload.get("launcher_status"),
        "launcher_issue_count": inspect_payload.get("launcher_issue_count", 0),
        "launcher_issue_codes": inspect_payload.get("launcher_issue_codes", []),
        "issue_count": inspect_payload.get("issue_count", 0),
        "issues": list(inspect_payload.get("issues", [])),
        "command_plan": command_plan,
        "report_path_preview": None,
    }

    if payload["launcher_status"] == "reject":
        payload["ok"] = False
    return payload

def _patchops_b2_plan_bundle_cli_payload(*args, **kwargs):
    if args and hasattr(args[0], "__dict__") and not isinstance(args[0], (str, _patchops_b2_Path)):
        namespace = args[0]
        bundle_zip_path = getattr(namespace, "bundle_zip_path", None)
        if bundle_zip_path is None:
            bundle_zip_path = getattr(namespace, "path", None)
        profile_name = getattr(namespace, "profile", None)
        if profile_name is None:
            profile_name = getattr(namespace, "profile_name", None)
        return _patchops_b2_plan_bundle_payload(
            bundle_zip_path,
            wrapper_root=getattr(namespace, "wrapper_root", None) or getattr(namespace, "wrapper_project_root", None),
            profile=profile_name,
            timestamp_token=getattr(namespace, "timestamp_token", None),
        )
    if "profile" not in kwargs and "profile_name" in kwargs:
        kwargs["profile"] = kwargs.pop("profile_name")
    if "wrapper_root" not in kwargs and "wrapper_project_root" in kwargs:
        kwargs["wrapper_root"] = kwargs.pop("wrapper_project_root")
    return _patchops_b2_plan_bundle_payload(*args, **kwargs)

def _patchops_b2_cli_plan_bundle_main(argv=None):
    parser = _patchops_b2_argparse.ArgumentParser(prog="patchops plan-bundle")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = _patchops_b2_plan_bundle_payload(
        args.bundle_zip_path,
        wrapper_root=args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(_patchops_b2_json.dumps(payload, indent=2))
    return 0 if payload["ok"] else 1

inspect_bundle_payload = _patchops_b2_inspect_bundle_payload
inspect_bundle_cli_payload = _patchops_b2_inspect_bundle_cli_payload
cli_inspect_bundle_main = _patchops_b2_cli_inspect_bundle_main
plan_bundle_payload = _patchops_b2_plan_bundle_payload
plan_bundle_cli_payload = _patchops_b2_plan_bundle_cli_payload
cli_plan_bundle_main = _patchops_b2_cli_plan_bundle_main

# PATCHOPS_I1_CHECK_BUNDLE_LAUNCHER_REVIEW_CONSISTENCY_START

_PATCHOPS_P02_ORIGINAL_CHECK_BUNDLE_PAYLOAD = globals().get(
    "_PATCHOPS_P02_ORIGINAL_CHECK_BUNDLE_PAYLOAD",
    check_bundle_payload,
)


def _patchops_i1_issue_code(item):
    if isinstance(item, dict):
        return item.get("code")
    return None


def _patchops_i1_issue_message(item):
    if isinstance(item, dict):
        return str(item.get("message", "") or item.get("code", "") or item)
    return str(item)


def _patchops_i1_normalize_launcher_review(inspect_payload):
    if not isinstance(inspect_payload, dict):
        return {
            "status": "safe",
            "launcher_path": None,
            "issue_count": 0,
            "issues": [],
        }

    launcher_review = inspect_payload.get("launcher_review")
    if not isinstance(launcher_review, dict):
        launcher_review = {}

    status = inspect_payload.get("launcher_status") or launcher_review.get("status") or "safe"
    status = "safe" if status == "accept" else status

    issues = launcher_review.get("issues", [])
    if not isinstance(issues, list):
        issues = []

    issue_count = inspect_payload.get("launcher_issue_count")
    if issue_count is None:
        issue_count = launcher_review.get("issue_count", len(issues))

    normalized = {
        "status": status,
        "launcher_path": launcher_review.get("launcher_path"),
        "issue_count": int(issue_count or 0),
        "issues": issues,
    }
    return normalized


def _patchops_i1_merge_issues(existing, incoming):
    merged = []
    seen = set()

    for source in (existing or []), (incoming or []):
        if not isinstance(source, list):
            source = list(source) if isinstance(source, tuple) else [source]
        for item in source:
            key = repr(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def check_bundle_payload(*args, **kwargs):
    base_payload = _PATCHOPS_P02_ORIGINAL_CHECK_BUNDLE_PAYLOAD(*args, **kwargs)
    if not isinstance(base_payload, dict):
        base_payload = {}

    try:
        inspect_payload = inspect_bundle_payload(*args, **kwargs)
    except Exception:
        inspect_payload = {}

    launcher_review = _patchops_i1_normalize_launcher_review(inspect_payload)
    launcher_status = launcher_review.get("status") or "safe"

    inspect_issue_codes = inspect_payload.get("launcher_issue_codes", []) if isinstance(inspect_payload, dict) else []
    if not isinstance(inspect_issue_codes, list):
        inspect_issue_codes = []

    if not inspect_issue_codes:
        inspect_issue_codes = [
            code
            for code in (_patchops_i1_issue_code(item) for item in launcher_review.get("issues", []))
            if code
        ]

    base_payload["launcher_review"] = launcher_review
    base_payload["launcher_status"] = launcher_status
    base_payload["launcher_issue_count"] = int(launcher_review.get("issue_count", 0) or 0)
    base_payload["launcher_issue_codes"] = inspect_issue_codes

    existing_issues = base_payload.get("issues", [])
    if not isinstance(existing_issues, list):
        existing_issues = list(existing_issues) if isinstance(existing_issues, tuple) else [existing_issues]

    if launcher_status == "reject":
        inspect_issues = inspect_payload.get("issues", []) if isinstance(inspect_payload, dict) else []
        if not inspect_issues:
            inspect_issues = [
                _patchops_i1_issue_message(item)
                for item in launcher_review.get("issues", [])
            ]

        merged_issues = _patchops_i1_merge_issues(existing_issues, inspect_issues)
        base_payload["issues"] = merged_issues
        base_payload["issue_count"] = len(merged_issues)
        base_payload["ok"] = False
    else:
        base_payload["issues"] = existing_issues
        base_payload["issue_count"] = int(base_payload.get("issue_count", len(existing_issues)) or 0)
        base_payload["ok"] = bool(base_payload.get("ok")) and launcher_status != "reject"

    return base_payload


def cli_check_bundle_main(argv=None):
    import argparse as _patchops_i1_argparse
    import json as _patchops_i1_json

    parser = _patchops_i1_argparse.ArgumentParser(prog="patchops check-bundle")
    parser.add_argument("bundle_zip_path")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--wrapper-root", default=None)
    parser.add_argument("--timestamp-token", default=None)
    args = parser.parse_args(argv)

    payload = check_bundle_payload(
        args.bundle_zip_path,
        args.wrapper_root,
        profile=args.profile,
        timestamp_token=args.timestamp_token,
    )
    print(_patchops_i1_json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1

# PATCHOPS_I1_CHECK_BUNDLE_LAUNCHER_REVIEW_CONSISTENCY_END
