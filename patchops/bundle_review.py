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
