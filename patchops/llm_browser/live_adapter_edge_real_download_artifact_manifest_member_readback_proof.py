"""L25.37 controlled artifact manifest-member readback proof.

This follows accepted L25.36. It opens a controlled artifact ZIP under the
browser-download runtime area and reads only `bundle/manifest.json` bytes, then
parses that JSON for metadata. It does not extract archives, execute packages,
invoke PatchOps run-package, start a browser, trigger downloads, paste/send,
start localhost, use Selenium/CDP/DOM scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

PATCH = "L25.37"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.37 Microsoft Edge controlled runtime real-download artifact manifest member readback proof"
SOURCE_PATCH = "L25.36"
NEXT_PATCH = "L25.38 Microsoft Edge controlled runtime real-download artifact manifest validation checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH = "data/runtime/browser_downloads/l25_37_real_artifact_manifest/future_real_downloaded_package.zip"
REQUIRED_MANIFEST_READBACK_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_MANIFEST_READBACK_AUTHORIZED"
EXPECTED_PACKAGE_RUN_SCOPE = "controlled_runtime_package_run_only_supported_bundle_shape_synthetic_launcher_no_browser_no_pasteback_no_real_artifact"
MANIFEST_MEMBER_NAME = "bundle/manifest.json"
MAX_ARTIFACT_BYTES = 262144
MAX_MANIFEST_BYTES = 65536

FALSE_FIELDS = (
    "real_archive_candidate_extracted",
    "adapter_archive_extraction_performed",
    "archive_member_extracted_to_project",
    "download_workflow_active",
    "download_workflow_execution_allowed",
    "real_browser_download_active",
    "browser_started",
    "edge_process_started",
    "browser_session_created",
    "selenium_imported",
    "cdp_used",
    "dom_scraping_used",
    "page_inspection_performed",
    "conversation_text_read",
    "prompt_text_extracted",
    "chatgpt_url_opened",
    "pasteback_workflow_active",
    "paste_performed",
    "send_or_submit_performed",
    "localhost_server_started",
    "browser_extension_used",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
    "package_run_performed_by_adapter",
    "package_run",
    "patchops_cli_run_package_invoked_for_real_artifact",
    "artifact_member_written_to_project",
    "git_commit_performed",
    "git_push_performed",
)


def _first(payload: Mapping[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return default


def _normalize_l25_36_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "first_real_download_artifact_readback_proof": source.get("first_real_download_artifact_readback_proof"),
        "artifact_readback_allowed": source.get("artifact_readback_allowed"),
        "candidate_artifact_under_runtime_downloads": source.get("candidate_artifact_under_runtime_downloads"),
        "real_downloaded_artifact_read": source.get("real_downloaded_artifact_read"),
        "real_downloaded_artifact_path_opened": source.get("real_downloaded_artifact_path_opened"),
        "real_downloaded_artifact_bytes_read": source.get("real_downloaded_artifact_bytes_read"),
        "real_downloaded_artifact_hash_computed": source.get("real_downloaded_artifact_hash_computed"),
        "artifact_zip_opened_for_member_names_only": source.get("artifact_zip_opened_for_member_names_only"),
        "artifact_zip_member_names_read": source.get("artifact_zip_member_names_read"),
        "artifact_required_member_names_present": source.get("artifact_required_member_names_present"),
        "real_downloaded_manifest_read": source.get("real_downloaded_manifest_read", False),
        "real_downloaded_manifest_member_opened": source.get("real_downloaded_manifest_member_opened", False),
        "real_downloaded_manifest_bytes_read": source.get("real_downloaded_manifest_bytes_read", False),
        "real_downloaded_manifest_json_parsed": source.get("real_downloaded_manifest_json_parsed", False),
        "real_archive_candidate_extracted": source.get("real_archive_candidate_extracted", False),
        "adapter_archive_extraction_performed": source.get("adapter_archive_extraction_performed", False),
        "browser_started": source.get("browser_started", False),
        "package_execution_allowed": source.get("package_execution_allowed", False),
        "package_run": source.get("package_run", False),
        "patchops_cli_run_package_invoked_for_real_artifact": source.get("patchops_cli_run_package_invoked_for_real_artifact", False),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=False),
    }


def _artifact_under_runtime(root: Path, artifact_path: Path) -> bool:
    try:
        base = (root / "data" / "runtime" / "browser_downloads" / "l25_37_real_artifact_manifest").resolve()
        return str(artifact_path.resolve()).startswith(str(base))
    except OSError:
        return False


def _read_manifest_member(artifact_path: Path) -> dict[str, Any]:
    artifact_data = artifact_path.read_bytes()
    with zipfile.ZipFile(artifact_path, "r") as archive:
        member_names = sorted(archive.namelist())
        manifest_bytes = archive.read(MANIFEST_MEMBER_NAME)
    manifest_text = manifest_bytes.decode("utf-8")
    manifest_json = json.loads(manifest_text)
    return {
        "artifact_byte_count": len(artifact_data),
        "artifact_sha256": hashlib.sha256(artifact_data).hexdigest(),
        "manifest_member_name": MANIFEST_MEMBER_NAME,
        "manifest_member_opened": True,
        "manifest_byte_count": len(manifest_bytes),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "manifest_json_parsed": True,
        "manifest_patch_name": manifest_json.get("patch_name"),
        "manifest_version": manifest_json.get("manifest_version"),
        "manifest_active_profile": manifest_json.get("active_profile"),
        "manifest_target_project_root_present": bool(manifest_json.get("target_project_root")),
        "manifest_files_to_write_count": len(manifest_json.get("files_to_write") or []),
        "manifest_validation_commands_count": len(manifest_json.get("validation_commands") or []),
        "artifact_zip_member_names": member_names,
    }


def build_real_download_artifact_manifest_member_readback_proof(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_manifest_member_readback: bool = False,
    authorization_token: str | None = None,
    candidate_artifact_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _normalize_l25_36_source(source_payload)
    artifact_path = Path(candidate_artifact_path) if candidate_artifact_path else root / DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_MANIFEST_READBACK_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.36"
        and source.get("first_real_download_artifact_readback_proof") is True
        and source.get("artifact_readback_allowed") is True
        and source.get("candidate_artifact_under_runtime_downloads") is True
        and source.get("real_downloaded_artifact_read") is True
        and source.get("real_downloaded_artifact_bytes_read") is True
        and source.get("real_downloaded_artifact_hash_computed") is True
        and source.get("artifact_zip_member_names_read") is True
        and source.get("artifact_required_member_names_present") is True
        and source.get("real_downloaded_manifest_read") is False
        and source.get("real_downloaded_manifest_member_opened") is False
        and source.get("real_downloaded_manifest_bytes_read") is False
        and source.get("real_downloaded_manifest_json_parsed") is False
        and source.get("real_archive_candidate_extracted") is False
        and source.get("adapter_archive_extraction_performed") is False
        and source.get("browser_started") is False
        and source.get("package_execution_allowed") is False
        and source.get("package_run") is False
        and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False
        and source.get("pasteback") is False
    )
    artifact_size_ok = artifact_path.exists() and artifact_path.stat().st_size <= MAX_ARTIFACT_BYTES
    readback_allowed = bool(
        source_ok
        and allow_manifest_member_readback
        and token_valid
        and artifact_path.exists()
        and artifact_path.is_file()
        and artifact_path.suffix.lower() == ".zip"
        and _artifact_under_runtime(root, artifact_path)
        and artifact_size_ok
    )

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_36_payload_ok", "ok": source_ok},
        {"name": "manifest_readback_token_present", "ok": token_present},
        {"name": "manifest_readback_token_valid", "ok": token_valid},
        {"name": "candidate_artifact_exists", "ok": artifact_path.exists()},
        {"name": "candidate_artifact_is_file", "ok": artifact_path.is_file()},
        {"name": "candidate_artifact_suffix_zip", "ok": artifact_path.suffix.lower() == ".zip"},
        {"name": "candidate_artifact_under_l25_37_runtime_downloads", "ok": _artifact_under_runtime(root, artifact_path)},
        {"name": "candidate_artifact_size_bounded", "ok": artifact_size_ok},
    ]

    manifest_summary: dict[str, Any] = {}
    if readback_allowed:
        manifest_summary = _read_manifest_member(artifact_path)
        checks.extend([
            {"name": "real_downloaded_manifest_read", "ok": True},
            {"name": "real_downloaded_manifest_member_opened", "ok": manifest_summary.get("manifest_member_opened") is True},
            {"name": "real_downloaded_manifest_bytes_read", "ok": 0 < int(manifest_summary.get("manifest_byte_count") or 0) <= MAX_MANIFEST_BYTES},
            {"name": "real_downloaded_manifest_json_parsed", "ok": manifest_summary.get("manifest_json_parsed") is True},
            {"name": "manifest_patch_name_expected", "ok": manifest_summary.get("manifest_patch_name") == "synthetic_l25_37_manifest_readback_fixture"},
            {"name": "manifest_version_expected", "ok": manifest_summary.get("manifest_version") == "1"},
            {"name": "manifest_no_target_writes", "ok": manifest_summary.get("manifest_files_to_write_count") == 0},
            {"name": "manifest_no_validation_commands", "ok": manifest_summary.get("manifest_validation_commands_count") == 0},
        ])

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "manifest_member_readback_proof": True,
        "source_l25_36_summary": source,
        "manifest_readback_requested": bool(allow_manifest_member_readback or token_present),
        "manifest_readback_token_present": token_present,
        "manifest_readback_token_valid": token_valid,
        "manifest_readback_allowed": readback_allowed,
        "candidate_artifact_path": str(artifact_path),
        "candidate_artifact_relative_path": DEFAULT_CONTROLLED_ARTIFACT_RELATIVE_PATH,
        "candidate_artifact_under_runtime_downloads": _artifact_under_runtime(root, artifact_path),
        "real_downloaded_artifact_read": readback_allowed,
        "real_downloaded_artifact_path_opened": readback_allowed,
        "real_downloaded_artifact_bytes_read": readback_allowed,
        "real_downloaded_artifact_hash_computed": readback_allowed,
        "real_downloaded_artifact_byte_count": manifest_summary.get("artifact_byte_count"),
        "real_downloaded_artifact_sha256": manifest_summary.get("artifact_sha256"),
        "artifact_zip_member_names_read": bool(manifest_summary.get("artifact_zip_member_names")),
        "artifact_zip_member_names": manifest_summary.get("artifact_zip_member_names", []),
        "real_downloaded_manifest_read": readback_allowed,
        "real_downloaded_manifest_member_opened": readback_allowed and manifest_summary.get("manifest_member_opened") is True,
        "real_downloaded_manifest_member_name": manifest_summary.get("manifest_member_name"),
        "real_downloaded_manifest_bytes_read": readback_allowed and int(manifest_summary.get("manifest_byte_count") or 0) > 0,
        "real_downloaded_manifest_byte_count": manifest_summary.get("manifest_byte_count"),
        "real_downloaded_manifest_hash_computed": readback_allowed and isinstance(manifest_summary.get("manifest_sha256"), str),
        "real_downloaded_manifest_sha256": manifest_summary.get("manifest_sha256"),
        "real_downloaded_manifest_json_parsed": readback_allowed and manifest_summary.get("manifest_json_parsed") is True,
        "manifest_patch_name": manifest_summary.get("manifest_patch_name"),
        "manifest_version": manifest_summary.get("manifest_version"),
        "manifest_active_profile": manifest_summary.get("manifest_active_profile"),
        "manifest_target_project_root_present": manifest_summary.get("manifest_target_project_root_present"),
        "manifest_files_to_write_count": manifest_summary.get("manifest_files_to_write_count"),
        "manifest_validation_commands_count": manifest_summary.get("manifest_validation_commands_count"),
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_37": True,
        "no_download_permission_added_by_l25_37": True,
        "no_archive_extraction_permission_added_by_l25_37": True,
        "no_package_execution_permission_added_by_l25_37": True,
        "no_pasteback_permission_added_by_l25_37": True,
        "no_git_permission_added_by_l25_37": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in FALSE_FIELDS:
        if field not in payload:
            payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    return "\n".join([
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Manifest Read                 : {payload.get('real_downloaded_manifest_read')}",
        f"Manifest Parsed               : {payload.get('real_downloaded_manifest_json_parsed')}",
        f"Manifest Patch                : {payload.get('manifest_patch_name')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-manifest-member-readback", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-artifact-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_manifest_member_readback_proof(
        args.repo_root,
        source_payload=source_payload,
        allow_manifest_member_readback=args.allow_manifest_member_readback,
        authorization_token=args.authorization_token,
        candidate_artifact_path=args.candidate_artifact_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
