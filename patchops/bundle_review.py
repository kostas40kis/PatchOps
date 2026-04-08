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


def check_bundle_payload(
    bundle_zip_path: str | Path,
    wrapper_project_root: str | Path | None = None,
    *,
    profile: str | None = None,
    profile_name: str | None = None,
    timestamp_token: str | None = None,
    **_ignored: Any,
) -> dict[str, Any]:
    del wrapper_project_root, timestamp_token, _ignored

    if profile is None:
        profile = profile_name

    bundle_zip = Path(bundle_zip_path)
    exists = bundle_zip.exists()
    resolved_path = str(bundle_zip.resolve()) if exists else str(bundle_zip)

    issues: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    top_level_root: str | None = None
    bundle_meta_present = False
    recommended_profile: str | None = None

    if not exists:
        issues.append(
            _issue(
                "missing_bundle_zip",
                "Bundle zip was not found.",
                path=resolved_path,
            )
        )
        return {
            "ok": False,
            "exists": False,
            "path": resolved_path,
            "profile": profile,
            "top_level_root": None,
            "issue_count": len(issues),
            "issues": issues,
            "warning_count": len(warnings),
            "warnings": warnings,
            "bundle_meta_present": False,
            "recommended_profile": None,
        }

    try:
        with zipfile.ZipFile(bundle_zip, "r") as zf:
            member_names = [name for name in zf.namelist() if _normalize_member_name(name)]
            if not member_names:
                issues.append(
                    _issue(
                        "invalid_zip",
                        "Bundle zip is empty.",
                        path=resolved_path,
                    )
                )
            else:
                roots = _top_level_roots(member_names)
                if len(roots) != 1:
                    issues.append(
                        _issue(
                            "multiple_roots",
                            "Bundle zip must contain exactly one top-level root folder.",
                            path=resolved_path,
                        )
                    )
                else:
                    top_level_root = roots[0]
                    manifest_member = f"{top_level_root}/manifest.json"
                    bundle_meta_member = f"{top_level_root}/bundle_meta.json"

                    if manifest_member not in member_names:
                        issues.append(
                            _issue(
                                "missing_manifest",
                                "Bundle zip is missing manifest.json at the bundle root.",
                                path=manifest_member,
                            )
                        )

                    if bundle_meta_member in member_names:
                        bundle_meta_present = True
                        try:
                            bundle_meta = _read_json_object_from_zip(zf, bundle_meta_member)
                        except Exception as exc:
                            warnings.append(
                                _warning(
                                    "invalid_bundle_meta",
                                    f"bundle_meta.json could not be parsed cleanly: {exc}",
                                    path=bundle_meta_member,
                                )
                            )
                        else:
                            recommended_profile = (
                                None
                                if bundle_meta is None
                                else str(bundle_meta.get("recommended_profile") or "").strip() or None
                            )
                    else:
                        warnings.append(
                            _warning(
                                "missing_bundle_meta",
                                "bundle_meta.json is absent; current check-bundle compatibility treats this as a warning, not a top-level failure.",
                                path=bundle_meta_member,
                            )
                        )
    except zipfile.BadZipFile:
        issues.append(
            _issue(
                "invalid_zip",
                "Bundle zip could not be opened as a valid zip archive.",
                path=resolved_path,
            )
        )
    except Exception as exc:
        issues.append(
            _issue(
                "invalid_zip",
                f"Bundle zip could not be reviewed cleanly: {exc}",
                path=resolved_path,
            )
        )

    return {
        "ok": len(issues) == 0,
        "exists": exists,
        "path": resolved_path,
        "profile": profile,
        "top_level_root": top_level_root,
        "issue_count": len(issues),
        "issues": issues,
        "warning_count": len(warnings),
        "warnings": warnings,
        "bundle_meta_present": bundle_meta_present,
        "recommended_profile": recommended_profile,
    }


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
    return 0 if payload["ok"] else 1


__all__ = [
    "check_bundle_payload",
    "check_bundle_cli_payload",
    "cli_check_bundle_main",
]
