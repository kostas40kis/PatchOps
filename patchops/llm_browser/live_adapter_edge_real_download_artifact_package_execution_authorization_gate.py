"""L25.41 package-execution authorization gate.

This follows accepted L25.40. It validates the accepted L25.40 manifest-
validation final marker from a source payload and grants only future package-
execution authorization when an explicit flag and token are supplied.

L25.41 does not execute a package, invoke PatchOps run-package, open artifact
paths, read bytes, open ZIP members, extract archives, start browsers, trigger
downloads, paste/send, start localhost, use Selenium/CDP/DOM scraping, commit,
or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.41"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.41 Microsoft Edge controlled runtime real-download artifact package-execution authorization gate"
SOURCE_PATCH = "L25.40"
NEXT_PATCH = "L25.42 Microsoft Edge controlled runtime real-download artifact package-execution first controlled dry-run proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_PACKAGE_EXECUTION_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_PACKAGE_EXECUTION_AUTHORIZED_FUTURE_ONLY"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_MANIFEST_PATCH_NAME = "synthetic_l25_37_manifest_readback_fixture"
EXPECTED_MANIFEST_VERSION = "1"

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_41",
    "artifact_bytes_read_by_l25_41",
    "zip_member_opened_by_l25_41",
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
    "package_execution_performed_by_adapter",
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


def _normalize_l25_40_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "manifest_validation_final_acceptance_marker": source.get("manifest_validation_final_acceptance_marker"),
        "manifest_validation_ladder_final_acceptance": source.get("manifest_validation_ladder_final_acceptance"),
        "manifest_validation_final_acceptance_from_source_payload_only": source.get("manifest_validation_final_acceptance_from_source_payload_only"),
        "accepted_l25_35_real_artifact_authorization_gate": source.get("accepted_l25_35_real_artifact_authorization_gate"),
        "accepted_l25_36_artifact_readback_proof": source.get("accepted_l25_36_artifact_readback_proof"),
        "accepted_l25_37_manifest_member_readback_proof": source.get("accepted_l25_37_manifest_member_readback_proof"),
        "accepted_l25_38_manifest_validation_checkpoint": source.get("accepted_l25_38_manifest_validation_checkpoint"),
        "accepted_l25_39_manifest_validation_broad_checkpoint": source.get("accepted_l25_39_manifest_validation_broad_checkpoint"),
        "accepted_manifest_member_name": source.get("accepted_manifest_member_name"),
        "accepted_manifest_patch_name": source.get("accepted_manifest_patch_name"),
        "accepted_manifest_version": source.get("accepted_manifest_version"),
        "accepted_manifest_files_to_write_count": source.get("accepted_manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": source.get("accepted_manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": source.get("accepted_manifest_zero_writes"),
        "accepted_manifest_zero_validation_commands": source.get("accepted_manifest_zero_validation_commands"),
        "accepted_malformed_manifest_source_rejected": source.get("accepted_malformed_manifest_source_rejected"),
        "accepted_broad_checkpoint_rejects_missing_malformed_source_rejection": source.get("accepted_broad_checkpoint_rejects_missing_malformed_source_rejection"),
        "final_marker_rejects_nonzero_manifest_validation_commands": source.get("final_marker_rejects_nonzero_manifest_validation_commands"),
        "artifact_path_opened_by_l25_40": source.get("artifact_path_opened_by_l25_40", False),
        "artifact_bytes_read_by_l25_40": source.get("artifact_bytes_read_by_l25_40", False),
        "zip_member_opened_by_l25_40": source.get("zip_member_opened_by_l25_40", False),
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


def build_real_download_artifact_package_execution_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_package_execution_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_40_source(source_payload)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_PACKAGE_EXECUTION_AUTHORIZATION_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.40"
        and source.get("manifest_validation_final_acceptance_marker") is True
        and source.get("manifest_validation_ladder_final_acceptance") is True
        and source.get("manifest_validation_final_acceptance_from_source_payload_only") is True
        and source.get("accepted_l25_35_real_artifact_authorization_gate") is True
        and source.get("accepted_l25_36_artifact_readback_proof") is True
        and source.get("accepted_l25_37_manifest_member_readback_proof") is True
        and source.get("accepted_l25_38_manifest_validation_checkpoint") is True
        and source.get("accepted_l25_39_manifest_validation_broad_checkpoint") is True
        and source.get("accepted_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME
        and source.get("accepted_manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME
        and source.get("accepted_manifest_version") == EXPECTED_MANIFEST_VERSION
        and source.get("accepted_manifest_files_to_write_count") == 0
        and source.get("accepted_manifest_validation_commands_count") == 0
        and source.get("accepted_manifest_zero_writes") is True
        and source.get("accepted_manifest_zero_validation_commands") is True
        and source.get("accepted_malformed_manifest_source_rejected") is True
        and source.get("accepted_broad_checkpoint_rejects_missing_malformed_source_rejection") is True
        and source.get("final_marker_rejects_nonzero_manifest_validation_commands") is True
        and source.get("artifact_path_opened_by_l25_40") is False
        and source.get("artifact_bytes_read_by_l25_40") is False
        and source.get("zip_member_opened_by_l25_40") is False
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
    future_authorized = bool(source_ok and allow_package_execution_authorization and token_valid)
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_40_payload_ok", "ok": source_ok},
        {"name": "package_execution_authorization_token_present", "ok": token_present},
        {"name": "package_execution_authorization_token_valid", "ok": token_valid},
        {"name": "package_execution_authorization_explicitly_allowed", "ok": allow_package_execution_authorization is True},
        {"name": "future_package_execution_authorization_granted", "ok": future_authorized},
    ]
    if future_authorized:
        checks.extend([
            {"name": "manifest_validation_ladder_finalized", "ok": source.get("manifest_validation_ladder_final_acceptance") is True},
            {"name": "manifest_identity_stable", "ok": source.get("accepted_manifest_member_name") == EXPECTED_MANIFEST_MEMBER_NAME and source.get("accepted_manifest_patch_name") == EXPECTED_MANIFEST_PATCH_NAME and source.get("accepted_manifest_version") == EXPECTED_MANIFEST_VERSION},
            {"name": "manifest_zero_write_zero_validation_stable", "ok": source.get("accepted_manifest_zero_writes") is True and source.get("accepted_manifest_zero_validation_commands") is True},
            {"name": "malformed_manifest_rejection_stable", "ok": source.get("accepted_malformed_manifest_source_rejected") is True and source.get("accepted_broad_checkpoint_rejects_missing_malformed_source_rejection") is True and source.get("final_marker_rejects_nonzero_manifest_validation_commands") is True},
            {"name": "no_execution_performed_in_gate", "ok": source.get("package_execution_allowed") is False and source.get("package_run") is False and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False},
        ])
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "package_execution_authorization_gate": True,
        "package_execution_authorization_from_source_payload_only": True,
        "package_execution_authorization_requested": bool(allow_package_execution_authorization or token_present),
        "package_execution_authorization_token_present": token_present,
        "package_execution_authorization_token_valid": token_valid,
        "package_execution_authorization_granted_for_future_patch": future_authorized,
        "future_package_execution_requires_separate_l25_42_gate_and_token": True,
        "source_l25_40_summary": source,
        "accepted_manifest_validation_ladder_final_acceptance": source.get("manifest_validation_ladder_final_acceptance") is True,
        "accepted_manifest_member_name": source.get("accepted_manifest_member_name"),
        "accepted_manifest_patch_name": source.get("accepted_manifest_patch_name"),
        "accepted_manifest_version": source.get("accepted_manifest_version"),
        "accepted_manifest_files_to_write_count": source.get("accepted_manifest_files_to_write_count"),
        "accepted_manifest_validation_commands_count": source.get("accepted_manifest_validation_commands_count"),
        "accepted_manifest_zero_writes": source.get("accepted_manifest_zero_writes") is True,
        "accepted_manifest_zero_validation_commands": source.get("accepted_manifest_zero_validation_commands") is True,
        "artifact_path_opened_by_l25_41": False,
        "artifact_bytes_read_by_l25_41": False,
        "zip_member_opened_by_l25_41": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_execution_performed_by_adapter": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_41": True,
        "no_download_permission_added_by_l25_41": True,
        "no_artifact_or_zip_read_permission_added_by_l25_41": True,
        "no_archive_extraction_permission_added_by_l25_41": True,
        "no_package_execution_performed_by_l25_41": True,
        "no_patchops_run_package_permission_added_by_l25_41": True,
        "no_pasteback_permission_added_by_l25_41": True,
        "no_git_permission_added_by_l25_41": True,
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
        f"Future Package Exec Auth      : {payload.get('package_execution_authorization_granted_for_future_patch')}",
        f"Package Execution Allowed     : {payload.get('package_execution_allowed')}",
        f"PatchOps Run-Package          : {payload.get('patchops_cli_run_package_invoked_for_real_artifact')}",
        f"Artifact Opened By L25.41     : {payload.get('artifact_path_opened_by_l25_41')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-package-execution-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_package_execution_authorization_gate(
        args.repo_root,
        source_payload=source_payload,
        allow_package_execution_authorization=args.allow_package_execution_authorization,
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
