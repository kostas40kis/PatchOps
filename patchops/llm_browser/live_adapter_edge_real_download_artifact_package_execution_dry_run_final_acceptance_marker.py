"""L25.44 final acceptance marker for package-execution dry-run.

This follows accepted L25.43. It validates the accepted L25.43 source payload
and marks the package-execution dry-run ladder complete. It is source-payload-only:
it does not invoke PatchOps run-package, execute packages, open artifact paths,
read bytes, open ZIP members, extract archives, start browsers, paste/send,
start localhost, use Selenium/CDP/DOM scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.44"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.44 Microsoft Edge controlled runtime real-download artifact package-execution dry-run final acceptance marker"
SOURCE_PATCH = "L25.43"
NEXT_PATCH = "L25.45 Microsoft Edge controlled runtime real-download artifact package-execution first controlled run-package proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_DRY_RUN_FINAL_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_PACKAGE_EXECUTION_DRY_RUN_FINAL_ACCEPTED"

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_44",
    "artifact_bytes_read_by_l25_44",
    "zip_member_opened_by_l25_44",
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


def _normalize_l25_43_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "package_execution_dry_run_broad_checkpoint": source.get("package_execution_dry_run_broad_checkpoint"),
        "package_execution_dry_run_broad_checkpoint_from_source_payload_only": source.get("package_execution_dry_run_broad_checkpoint_from_source_payload_only"),
        "package_execution_dry_run_broad_checkpoint_allowed": source.get("package_execution_dry_run_broad_checkpoint_allowed"),
        "accepted_package_execution_dry_run_only": source.get("accepted_package_execution_dry_run_only"),
        "accepted_package_execution_dry_run_allowed": source.get("accepted_package_execution_dry_run_allowed"),
        "accepted_candidate_artifact_suffix_zip": source.get("accepted_candidate_artifact_suffix_zip"),
        "accepted_candidate_artifact_under_l25_42_runtime": source.get("accepted_candidate_artifact_under_l25_42_runtime"),
        "accepted_would_run_command_rendered": source.get("accepted_would_run_command_rendered"),
        "accepted_would_run_command_program": source.get("accepted_would_run_command_program"),
        "accepted_would_invoke_patchops_run_package_in_future_patch": source.get("accepted_would_invoke_patchops_run_package_in_future_patch"),
        "accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime": source.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime"),
        "broad_checkpoint_rejects_source_that_invoked_run_package": source.get("broad_checkpoint_rejects_source_that_invoked_run_package"),
        "artifact_path_opened_by_l25_43": source.get("artifact_path_opened_by_l25_43", False),
        "artifact_bytes_read_by_l25_43": source.get("artifact_bytes_read_by_l25_43", False),
        "zip_member_opened_by_l25_43": source.get("zip_member_opened_by_l25_43", False),
        "real_archive_candidate_extracted": source.get("real_archive_candidate_extracted", False),
        "adapter_archive_extraction_performed": source.get("adapter_archive_extraction_performed", False),
        "archive_member_extracted_to_project": source.get("archive_member_extracted_to_project", False),
        "artifact_member_written_to_project": source.get("artifact_member_written_to_project", False),
        "browser_started": source.get("browser_started", False),
        "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution", False),
        "package_execution_allowed": source.get("package_execution_allowed", False),
        "package_execution_performed_by_adapter": source.get("package_execution_performed_by_adapter", False),
        "package_run": source.get("package_run", False),
        "patchops_cli_run_package_invoked_for_real_artifact": source.get("patchops_cli_run_package_invoked_for_real_artifact", False),
        "pasteback": _first(source, "pasteback", "pasteback_workflow_active", default=False),
    }


def build_real_download_artifact_package_execution_dry_run_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_dry_run_final_acceptance_marker: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_43_source(source_payload)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_DRY_RUN_FINAL_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.43"
        and source.get("package_execution_dry_run_broad_checkpoint") is True
        and source.get("package_execution_dry_run_broad_checkpoint_from_source_payload_only") is True
        and source.get("package_execution_dry_run_broad_checkpoint_allowed") is True
        and source.get("accepted_package_execution_dry_run_only") is True
        and source.get("accepted_package_execution_dry_run_allowed") is True
        and source.get("accepted_candidate_artifact_suffix_zip") is True
        and source.get("accepted_candidate_artifact_under_l25_42_runtime") is True
        and source.get("accepted_would_run_command_rendered") is True
        and source.get("accepted_would_run_command_program") == "py"
        and source.get("accepted_would_invoke_patchops_run_package_in_future_patch") is True
        and source.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime") is True
        and source.get("broad_checkpoint_rejects_source_that_invoked_run_package") is True
        and source.get("artifact_path_opened_by_l25_43") is False
        and source.get("artifact_bytes_read_by_l25_43") is False
        and source.get("zip_member_opened_by_l25_43") is False
        and source.get("real_archive_candidate_extracted") is False
        and source.get("adapter_archive_extraction_performed") is False
        and source.get("archive_member_extracted_to_project") is False
        and source.get("artifact_member_written_to_project") is False
        and source.get("browser_started") is False
        and source.get("package_manifest_used_for_execution") is False
        and source.get("package_execution_allowed") is False
        and source.get("package_execution_performed_by_adapter") is False
        and source.get("package_run") is False
        and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False
        and source.get("pasteback") is False
    )
    final_allowed = bool(source_ok and allow_dry_run_final_acceptance_marker and token_valid)
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_43_payload_ok", "ok": source_ok},
        {"name": "dry_run_final_token_present", "ok": token_present},
        {"name": "dry_run_final_token_valid", "ok": token_valid},
        {"name": "dry_run_final_explicitly_allowed", "ok": allow_dry_run_final_acceptance_marker is True},
        {"name": "dry_run_final_acceptance_allowed", "ok": final_allowed},
    ]
    if final_allowed:
        checks.extend([
            {"name": "dry_run_broad_checkpoint_finalized", "ok": source.get("package_execution_dry_run_broad_checkpoint_allowed") is True},
            {"name": "would_run_command_finalized_without_invocation", "ok": source.get("accepted_would_run_command_rendered") is True and source.get("accepted_would_invoke_patchops_run_package_in_future_patch") is True and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False},
            {"name": "dry_run_path_guard_finalized", "ok": source.get("accepted_candidate_artifact_suffix_zip") is True and source.get("accepted_candidate_artifact_under_l25_42_runtime") is True and source.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime") is True},
            {"name": "source_that_invoked_run_package_rejection_finalized", "ok": source.get("broad_checkpoint_rejects_source_that_invoked_run_package") is True},
            {"name": "no_execution_extraction_browser_finalized", "ok": source.get("package_execution_allowed") is False and source.get("package_execution_performed_by_adapter") is False and source.get("package_run") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False},
        ])
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "package_execution_dry_run_final_acceptance_marker": True,
        "package_execution_dry_run_ladder_final_acceptance": final_allowed,
        "package_execution_dry_run_final_acceptance_from_source_payload_only": True,
        "package_execution_dry_run_final_acceptance_requested": bool(allow_dry_run_final_acceptance_marker or token_present),
        "package_execution_dry_run_final_acceptance_token_present": token_present,
        "package_execution_dry_run_final_acceptance_token_valid": token_valid,
        "source_l25_43_summary": source,
        "accepted_l25_41_package_execution_authorization_gate": final_allowed,
        "accepted_l25_42_package_execution_dry_run_proof": final_allowed,
        "accepted_l25_43_package_execution_dry_run_broad_checkpoint": final_allowed,
        "accepted_package_execution_dry_run_only": source.get("accepted_package_execution_dry_run_only") is True,
        "accepted_package_execution_dry_run_allowed": source.get("accepted_package_execution_dry_run_allowed") is True,
        "accepted_candidate_artifact_suffix_zip": source.get("accepted_candidate_artifact_suffix_zip") is True,
        "accepted_candidate_artifact_under_l25_42_runtime": source.get("accepted_candidate_artifact_under_l25_42_runtime") is True,
        "accepted_would_run_command_rendered": source.get("accepted_would_run_command_rendered") is True,
        "accepted_would_run_command_program": source.get("accepted_would_run_command_program"),
        "accepted_would_invoke_patchops_run_package_in_future_patch": source.get("accepted_would_invoke_patchops_run_package_in_future_patch") is True,
        "accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime": source.get("accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime") is True,
        "accepted_broad_checkpoint_rejects_source_that_invoked_run_package": source.get("broad_checkpoint_rejects_source_that_invoked_run_package") is True,
        "artifact_path_opened_by_l25_44": False,
        "artifact_bytes_read_by_l25_44": False,
        "zip_member_opened_by_l25_44": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_execution_performed_by_adapter": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_44": True,
        "no_download_permission_added_by_l25_44": True,
        "no_artifact_or_zip_read_permission_added_by_l25_44": True,
        "no_archive_extraction_permission_added_by_l25_44": True,
        "no_package_execution_performed_by_l25_44": True,
        "no_patchops_run_package_invocation_by_l25_44": True,
        "no_pasteback_permission_added_by_l25_44": True,
        "no_git_permission_added_by_l25_44": True,
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
        f"Final Acceptance              : {payload.get('package_execution_dry_run_ladder_final_acceptance')}",
        f"Would Run Rendered            : {payload.get('accepted_would_run_command_rendered')}",
        f"PatchOps Run-Package Invoked  : {payload.get('patchops_cli_run_package_invoked_for_real_artifact')}",
        f"Package Execution Allowed     : {payload.get('package_execution_allowed')}",
        f"Artifact Opened By L25.44     : {payload.get('artifact_path_opened_by_l25_44')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-dry-run-final-acceptance-marker", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_package_execution_dry_run_final_acceptance_marker(
        args.repo_root,
        source_payload=source_payload,
        allow_dry_run_final_acceptance_marker=args.allow_dry_run_final_acceptance_marker,
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
