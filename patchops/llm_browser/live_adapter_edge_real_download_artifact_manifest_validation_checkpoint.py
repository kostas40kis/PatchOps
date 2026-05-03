"""L25.38 manifest validation checkpoint.

This follows accepted L25.37. It validates already-read manifest metadata from a
source payload only. It does not open artifact paths, read ZIP members, extract
archives, execute packages, invoke PatchOps run-package, start a browser,
trigger downloads, paste/send, start localhost, use Selenium/CDP/DOM scraping,
commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.38"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.38 Microsoft Edge controlled runtime real-download artifact manifest validation checkpoint"
SOURCE_PATCH = "L25.37"
NEXT_PATCH = "L25.39 Microsoft Edge controlled runtime real-download artifact manifest validation broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_MANIFEST_VALIDATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_MANIFEST_VALIDATION_AUTHORIZED"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_MANIFEST_PATCH_NAME = "synthetic_l25_37_manifest_readback_fixture"
EXPECTED_MANIFEST_VERSION = "1"

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_38",
    "artifact_bytes_read_by_l25_38",
    "zip_member_opened_by_l25_38",
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


def _normalize_l25_37_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "manifest_member_readback_proof": source.get("manifest_member_readback_proof"),
        "manifest_readback_allowed": source.get("manifest_readback_allowed"),
        "candidate_artifact_under_runtime_downloads": source.get("candidate_artifact_under_runtime_downloads"),
        "real_downloaded_artifact_read": source.get("real_downloaded_artifact_read"),
        "real_downloaded_artifact_path_opened": source.get("real_downloaded_artifact_path_opened"),
        "real_downloaded_artifact_bytes_read": source.get("real_downloaded_artifact_bytes_read"),
        "real_downloaded_artifact_hash_computed": source.get("real_downloaded_artifact_hash_computed"),
        "real_downloaded_manifest_read": source.get("real_downloaded_manifest_read"),
        "real_downloaded_manifest_member_opened": source.get("real_downloaded_manifest_member_opened"),
        "real_downloaded_manifest_member_name": source.get("real_downloaded_manifest_member_name"),
        "real_downloaded_manifest_bytes_read": source.get("real_downloaded_manifest_bytes_read"),
        "real_downloaded_manifest_hash_computed": source.get("real_downloaded_manifest_hash_computed"),
        "real_downloaded_manifest_json_parsed": source.get("real_downloaded_manifest_json_parsed"),
        "manifest_patch_name": source.get("manifest_patch_name"),
        "manifest_version": source.get("manifest_version"),
        "manifest_files_to_write_count": source.get("manifest_files_to_write_count"),
        "manifest_validation_commands_count": source.get("manifest_validation_commands_count"),
        "real_archive_candidate_extracted": source.get("real_archive_candidate_extracted", False),
        "adapter_archive_extraction_performed": source.get("adapter_archive_extraction_performed", False),
        "archive_member_extracted_to_project": source.get("archive_member_extracted_to_project", False),
        "artifact_member_written_to_project": source.get("artifact_member_written_to_project", False),
        "browser_started": source.get("browser_started", False),
        "package_execution_allowed": source.get("package_execution_allowed", False),
        "package_run": source.get("package_run", False),
        "patchops_cli_run_package_invoked_for_real_artifact": source.get("patchops_cli_run_package_invoked_for_real_artifact", False),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=False),
    }


def build_real_download_artifact_manifest_validation_checkpoint(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_manifest_validation: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_37_source(source_payload)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_MANIFEST_VALIDATION_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.37"
        and source.get("manifest_member_readback_proof") is True
        and source.get("manifest_readback_allowed") is True
        and source.get("candidate_artifact_under_runtime_downloads") is True
        and source.get("real_downloaded_artifact_read") is True
        and source.get("real_downloaded_artifact_path_opened") is True
        and source.get("real_downloaded_artifact_bytes_read") is True
        and source.get("real_downloaded_artifact_hash_computed") is True
        and source.get("real_downloaded_manifest_read") is True
        and source.get("real_downloaded_manifest_member_opened") is True
        and source.get("real_downloaded_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME
        and source.get("real_downloaded_manifest_bytes_read") is True
        and source.get("real_downloaded_manifest_hash_computed") is True
        and source.get("real_downloaded_manifest_json_parsed") is True
        and source.get("manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME
        and source.get("manifest_version") == EXPECTED_MANIFEST_VERSION
        and source.get("manifest_files_to_write_count") == 0
        and source.get("manifest_validation_commands_count") == 0
        and source.get("real_archive_candidate_extracted") is False
        and source.get("adapter_archive_extraction_performed") is False
        and source.get("archive_member_extracted_to_project") is False
        and source.get("artifact_member_written_to_project") is False
        and source.get("browser_started") is False
        and source.get("package_execution_allowed") is False
        and source.get("package_run") is False
        and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False
        and source.get("pasteback") is False
    )
    validation_allowed = bool(source_ok and allow_manifest_validation and token_valid)
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_37_payload_ok", "ok": source_ok},
        {"name": "manifest_validation_token_present", "ok": token_present},
        {"name": "manifest_validation_token_valid", "ok": token_valid},
        {"name": "manifest_validation_explicitly_allowed", "ok": allow_manifest_validation is True},
        {"name": "manifest_validation_allowed", "ok": validation_allowed},
    ]
    if validation_allowed:
        checks.extend([
            {"name": "manifest_member_name_expected", "ok": source.get("real_downloaded_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME},
            {"name": "manifest_patch_name_expected", "ok": source.get("manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME},
            {"name": "manifest_version_expected", "ok": source.get("manifest_version") == EXPECTED_MANIFEST_VERSION},
            {"name": "manifest_zero_writes", "ok": source.get("manifest_files_to_write_count") == 0},
            {"name": "manifest_zero_validation_commands", "ok": source.get("manifest_validation_commands_count") == 0},
            {"name": "manifest_readback_boundary_no_execution", "ok": source.get("package_execution_allowed") is False and source.get("package_run") is False and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False},
            {"name": "manifest_readback_boundary_no_extraction", "ok": source.get("real_archive_candidate_extracted") is False and source.get("adapter_archive_extraction_performed") is False and source.get("archive_member_extracted_to_project") is False},
        ])
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "manifest_validation_checkpoint": True,
        "manifest_validation_from_source_payload_only": True,
        "manifest_validation_requested": bool(allow_manifest_validation or token_present),
        "manifest_validation_token_present": token_present,
        "manifest_validation_token_valid": token_valid,
        "manifest_validation_allowed": validation_allowed,
        "source_l25_37_summary": source,
        "accepted_manifest_member_name": source.get("real_downloaded_manifest_member_name"),
        "accepted_manifest_patch_name": source.get("manifest_patch_name"),
        "accepted_manifest_version": source.get("manifest_version"),
        "accepted_manifest_files_to_write_count": source.get("manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": source.get("manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": source.get("manifest_files_to_write_count") == 0,
        "accepted_manifest_zero_validation_commands": source.get("manifest_validation_commands_count") == 0,
        "artifact_path_opened_by_l25_38": False,
        "artifact_bytes_read_by_l25_38": False,
        "zip_member_opened_by_l25_38": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_38": True,
        "no_download_permission_added_by_l25_38": True,
        "no_artifact_or_zip_read_permission_added_by_l25_38": True,
        "no_archive_extraction_permission_added_by_l25_38": True,
        "no_package_execution_permission_added_by_l25_38": True,
        "no_pasteback_permission_added_by_l25_38": True,
        "no_git_permission_added_by_l25_38": True,
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
        f"Manifest Validation           : {payload.get('manifest_validation_allowed')}",
        f"Manifest Patch                : {payload.get('accepted_manifest_patch_name')}",
        f"Manifest Writes               : {payload.get('accepted_manifest_files_to_write_count')}",
        f"Manifest Validations          : {payload.get('accepted_manifest_validation_commands_count')}",
        f"Artifact Opened By L25.38     : {payload.get('artifact_path_opened_by_l25_38')}",
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
    parser.add_argument("--allow-manifest-validation", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_manifest_validation_checkpoint(
        args.repo_root,
        source_payload=source_payload,
        allow_manifest_validation=args.allow_manifest_validation,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
