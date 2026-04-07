from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from patchops.bundles.shape_validation import validate_bundle_path


def _build_check_bundle_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="patchops check-bundle",
        description="Validate a patch bundle zip or bundle directory before execution.",
    )
    parser.add_argument("bundle_path", help="Path to the bundle zip or extracted bundle directory.")
    parser.add_argument("--profile", dest="profile", default=None, help="Optional expected profile for operator review.")
    return parser


def check_bundle_payload(bundle_path: Path, requested_profile: str | None = None) -> dict[str, Any]:
    result = validate_bundle_path(bundle_path)
    payload = result.to_dict()
    payload["checked_path"] = str(Path(bundle_path))
    payload["requested_profile"] = requested_profile
    return payload


def cli_check_bundle_main(argv: list[str] | None = None) -> int:
    parser = _build_check_bundle_parser()
    args = parser.parse_args(argv)
    payload = check_bundle_payload(Path(args.bundle_path), requested_profile=args.profile)
    print(json.dumps(payload, indent=2))
    return 0 if payload.get("ok") else 1


__all__ = [
    "check_bundle_payload",
    "cli_check_bundle_main",
]

# PATCHOPS_ZP07B_CHECK_BUNDLE_ADAPTER:START
def check_bundle_cli_payload(
    bundle_zip_path,
    wrapper_project_root=None,
    *,
    profile=None,
    scrubbed_profile=None,
    timestamp_token=None,
):
    import tempfile
    import zipfile
    from pathlib import Path

    def _issue(code, message, path=None):
        payload = {"code": str(code), "message": str(message)}
        if path not in (None, ""):
            payload["path"] = str(path)
        return payload

    def _message_dict(message):
        return {
            "code": str(getattr(message, "code", "unknown")),
            "message": str(getattr(message, "message", str(message))),
            "path": None if getattr(message, "path", None) in (None, "") else str(getattr(message, "path", None)),
        }

    bundle_path = Path(bundle_zip_path).resolve()
    effective_profile = scrubbed_profile or profile
    issues = []
    top_level_roots = []
    root_folder = None
    member_names = []
    strict_review = None

    if not bundle_path.exists():
        issues.append(_issue("missing_bundle_zip", f"Bundle zip path does not exist: {bundle_path}", bundle_path))
    elif bundle_path.is_dir():
        issues.append(_issue("bundle_path_is_directory", f"Bundle zip path is a directory, not a zip file: {bundle_path}", bundle_path))
    else:
        try:
            with zipfile.ZipFile(bundle_path, "r") as zf:
                member_names = [
                    name.replace("\", "/").strip("/")
                    for name in zf.namelist()
                    if name and name.strip("/")
                ]
        except zipfile.BadZipFile:
            issues.append(_issue("invalid_zip_archive", f"Bundle zip is not a valid zip archive: {bundle_path}", bundle_path))

    if bundle_path.exists() and bundle_path.is_file() and not issues:
        if not member_names:
            issues.append(_issue("empty_bundle_zip", "Bundle zip is empty.", bundle_path))
        else:
            top_level_roots = sorted({name.split("/", 1)[0] for name in member_names})
            if len(top_level_roots) != 1:
                issues.append(
                    _issue(
                        "top_level_root_count_invalid",
                        f"Bundle zip must contain exactly one top-level root folder. Found: {top_level_roots}",
                        bundle_path,
                    )
                )
            else:
                root_folder = top_level_roots[0]
                manifest_member = f"{root_folder}/manifest.json"
                if manifest_member not in set(member_names):
                    issues.append(_issue("missing_manifest", f"Missing required bundle file: {manifest_member}", manifest_member))

                try:
                    from patchops.bundles import validate_extracted_bundle_dir
                    with tempfile.TemporaryDirectory(prefix="patchops_check_bundle_") as td:
                        extracted_parent = Path(td) / "extracted_bundle"
                        extracted_parent.mkdir(parents=True, exist_ok=True)
                        with zipfile.ZipFile(bundle_path, "r") as zf:
                            zf.extractall(extracted_parent)
                        extracted_root = extracted_parent / root_folder
                        if extracted_root.exists():
                            result = validate_extracted_bundle_dir(extracted_root)
                            strict_review = {
                                "is_valid": bool(getattr(result, "is_valid", False)),
                                "issues": [_message_dict(msg) for msg in getattr(result, "errors", ())],
                                "warnings": [_message_dict(msg) for msg in getattr(result, "warnings", ())],
                            }
                        else:
                            strict_review = {
                                "is_valid": False,
                                "issues": [_issue("extracted_root_missing", f"Extracted bundle root was not found: {extracted_root}", extracted_root)],
                                "warnings": [],
                            }
                except Exception as exc:
                    strict_review = {
                        "is_valid": False,
                        "issues": [_issue("strict_review_error", f"Strict bundle review could not run: {exc}")],
                        "warnings": [],
                    }

    payload = {
        "ok": len(issues) == 0,
        "bundle_zip_path": str(bundle_path),
        "exists": bundle_path.exists(),
        "profile": effective_profile,
        "issue_count": len(issues),
        "issues": issues,
        "top_level_roots": top_level_roots,
        "root_folder": root_folder,
        "member_count": len(member_names),
        "bundle_review": strict_review,
        "compatibility_mode": "zip_root_and_manifest_first",
    }
    return payload

