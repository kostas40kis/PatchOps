"""L25.40 final acceptance marker for manifest validation.

This follows accepted L25.39. It validates the accepted L25.39 broad-checkpoint
source payload and marks the real-download-artifact manifest-validation ladder
complete. It is source-payload-only and does not open artifact paths, read bytes,
open ZIP members, extract archives, execute packages, invoke PatchOps
run-package, start browsers, paste/send, start localhost, use Selenium/CDP/DOM
scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.40"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.40 Microsoft Edge controlled runtime real-download artifact manifest validation final acceptance marker"
SOURCE_PATCH = "L25.39"
NEXT_PATCH = "L25.41 Microsoft Edge controlled runtime real-download artifact package-execution authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_FINAL_MARKER_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_MANIFEST_VALIDATION_FINAL_ACCEPTED"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_MANIFEST_PATCH_NAME = "synthetic_l25_37_manifest_readback_fixture"
EXPECTED_MANIFEST_VERSION = "1"

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_40",
    "artifact_bytes_read_by_l25_40",
    "zip_member_opened_by_l25_40",
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


def _normalize_l25_39_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "manifest_validation_broad_checkpoint": source.get("manifest_validation_broad_checkpoint"),
        "manifest_validation_broad_checkpoint_from_source_payload_only": source.get("manifest_validation_broad_checkpoint_from_source_payload_only"),
        "manifest_validation_broad_checkpoint_allowed": source.get("manifest_validation_broad_checkpoint_allowed"),
        "accepted_manifest_member_name": source.get("accepted_manifest_member_name"),
        "accepted_manifest_patch_name": source.get("accepted_manifest_patch_name"),
        "accepted_manifest_version": source.get("accepted_manifest_version"),
        "accepted_manifest_files_to_write_count": source.get("accepted_manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": source.get("accepted_manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": source.get("accepted_manifest_zero_writes"),
        "accepted_manifest_zero_validation_commands": source.get("accepted_manifest_zero_validation_commands"),
        "accepted_malformed_manifest_source_rejected": source.get("accepted_malformed_manifest_source_rejected"),
        "broad_checkpoint_rejects_missing_malformed_source_rejection": source.get("broad_checkpoint_rejects_missing_malformed_source_rejection"),
        "artifact_path_opened_by_l25_39": source.get("artifact_path_opened_by_l25_39", False),
        "artifact_bytes_read_by_l25_39": source.get("artifact_bytes_read_by_l25_39", False),
        "zip_member_opened_by_l25_39": source.get("zip_member_opened_by_l25_39", False),
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


def build_real_download_artifact_manifest_validation_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_final_acceptance_marker: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_39_source(source_payload)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_FINAL_MARKER_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.39"
        and source.get("manifest_validation_broad_checkpoint") is True
        and source.get("manifest_validation_broad_checkpoint_from_source_payload_only") is True
        and source.get("manifest_validation_broad_checkpoint_allowed") is True
        and source.get("accepted_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME
        and source.get("accepted_manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME
        and source.get("accepted_manifest_version") == EXPECTED_MANIFEST_VERSION
        and source.get("accepted_manifest_files_to_write_count") == 0
        and source.get("accepted_manifest_validation_commands_count") == 0
        and source.get("accepted_manifest_zero_writes") is True
        and source.get("accepted_manifest_zero_validation_commands") is True
        and source.get("accepted_malformed_manifest_source_rejected") is True
        and source.get("broad_checkpoint_rejects_missing_malformed_source_rejection") is True
        and source.get("artifact_path_opened_by_l25_39") is False
        and source.get("artifact_bytes_read_by_l25_39") is False
        and source.get("zip_member_opened_by_l25_39") is False
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
    final_allowed = bool(source_ok and allow_final_acceptance_marker and token_valid)
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_39_payload_ok", "ok": source_ok},
        {"name": "final_marker_token_present", "ok": token_present},
        {"name": "final_marker_token_valid", "ok": token_valid},
        {"name": "final_marker_explicitly_allowed", "ok": allow_final_acceptance_marker is True},
        {"name": "manifest_validation_final_acceptance_allowed", "ok": final_allowed},
    ]
    if final_allowed:
        checks.extend([
            {"name": "manifest_identity_finalized", "ok": source.get("accepted_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME and source.get("accepted_manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME and source.get("accepted_manifest_version") == EXPECTED_MANIFEST_VERSION},
            {"name": "manifest_zero_write_zero_validation_finalized", "ok": source.get("accepted_manifest_zero_writes") is True and source.get("accepted_manifest_zero_validation_commands") is True},
            {"name": "malformed_source_rejection_finalized", "ok": source.get("accepted_malformed_manifest_source_rejected") is True and source.get("broad_checkpoint_rejects_missing_malformed_source_rejection") is True},
            {"name": "source_payload_only_boundary_finalized", "ok": source.get("artifact_path_opened_by_l25_39") is False and source.get("artifact_bytes_read_by_l25_39") is False and source.get("zip_member_opened_by_l25_39") is False},
            {"name": "execution_extraction_browser_boundary_finalized", "ok": source.get("package_execution_allowed") is False and source.get("package_run") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False},
        ])
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "manifest_validation_final_acceptance_marker": True,
        "manifest_validation_ladder_final_acceptance": final_allowed,
        "manifest_validation_final_acceptance_from_source_payload_only": True,
        "manifest_validation_final_acceptance_requested": bool(allow_final_acceptance_marker or token_present),
        "manifest_validation_final_acceptance_token_present": token_present,
        "manifest_validation_final_acceptance_token_valid": token_valid,
        "source_l25_39_summary": source,
        "accepted_l25_35_real_artifact_authorization_gate": final_allowed,
        "accepted_l25_36_artifact_readback_proof": final_allowed,
        "accepted_l25_37_manifest_member_readback_proof": final_allowed,
        "accepted_l25_38_manifest_validation_checkpoint": final_allowed,
        "accepted_l25_39_manifest_validation_broad_checkpoint": final_allowed,
        "accepted_manifest_member_name": source.get("accepted_manifest_member_name"),
        "accepted_manifest_patch_name": source.get("accepted_manifest_patch_name"),
        "accepted_manifest_version": source.get("accepted_manifest_version"),
        "accepted_manifest_files_to_write_count": source.get("accepted_manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": source.get("accepted_manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": source.get("accepted_manifest_zero_writes") is True,
        "accepted_manifest_zero_validation_commands": source.get("accepted_manifest_zero_validation_commands") is True,
        "accepted_malformed_manifest_source_rejected": source.get("accepted_malformed_manifest_source_rejected") is True,
        "accepted_broad_checkpoint_rejects_missing_malformed_source_rejection": source.get("broad_checkpoint_rejects_missing_malformed_source_rejection") is True,
        "artifact_path_opened_by_l25_40": False,
        "artifact_bytes_read_by_l25_40": False,
        "zip_member_opened_by_l25_40": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_40": True,
        "no_download_permission_added_by_l25_40": True,
        "no_artifact_or_zip_read_permission_added_by_l25_40": True,
        "no_archive_extraction_permission_added_by_l25_40": True,
        "no_package_execution_permission_added_by_l25_40": True,
        "no_pasteback_permission_added_by_l25_40": True,
        "no_git_permission_added_by_l25_40": True,
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
        f"Final Acceptance              : {payload.get('manifest_validation_ladder_final_acceptance')}",
        f"Manifest Patch                : {payload.get('accepted_manifest_patch_name')}",
        f"Malformed Source Rejected     : {payload.get('accepted_malformed_manifest_source_rejected')}",
        f"Artifact Opened By L25.40     : {payload.get('artifact_path_opened_by_l25_40')}",
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
    parser.add_argument("--allow-final-acceptance-marker", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_manifest_validation_final_acceptance_marker(
        args.repo_root,
        source_payload=source_payload,
        allow_final_acceptance_marker=args.allow_final_acceptance_marker,
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
