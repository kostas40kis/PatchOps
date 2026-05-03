"""L25.43 broad checkpoint for package-execution dry-run.

This follows accepted L25.42. It validates the accepted L25.42 source payload
and summarizes the package-execution dry-run ladder. It is source-payload-only:
it does not invoke PatchOps run-package, execute packages, open artifact paths,
read bytes, open ZIP members, extract archives, start browsers, paste/send,
start localhost, use Selenium/CDP/DOM scraping, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L25.43"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.43 Microsoft Edge controlled runtime real-download artifact package-execution dry-run broad checkpoint"
SOURCE_PATCH = "L25.42"
NEXT_PATCH = "L25.44 Microsoft Edge controlled runtime real-download artifact package-execution dry-run final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_DRY_RUN_BROAD_CHECKPOINT_TOKEN = "PATCHOPS_L25_EDGE_REAL_DOWNLOAD_ARTIFACT_PACKAGE_EXECUTION_DRY_RUN_BROAD_AUTHORIZED"

FALSE_FIELDS = (
    "artifact_path_opened_by_l25_43",
    "artifact_bytes_read_by_l25_43",
    "zip_member_opened_by_l25_43",
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


def _normalize_l25_42_source(source_payload: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(source_payload or {})
    return {
        "ok": source.get("ok"),
        "patch": source.get("patch"),
        "package_execution_first_controlled_dry_run_proof": source.get("package_execution_first_controlled_dry_run_proof"),
        "package_execution_dry_run_only": source.get("package_execution_dry_run_only"),
        "package_execution_dry_run_from_source_payload_only": source.get("package_execution_dry_run_from_source_payload_only"),
        "package_execution_dry_run_allowed": source.get("package_execution_dry_run_allowed"),
        "candidate_artifact_suffix_zip": source.get("candidate_artifact_suffix_zip"),
        "candidate_artifact_under_l25_42_runtime": source.get("candidate_artifact_under_l25_42_runtime"),
        "would_run_command_rendered": source.get("would_run_command_rendered"),
        "would_run_command_program": source.get("would_run_command_program"),
        "would_invoke_patchops_run_package_in_future_patch": source.get("would_invoke_patchops_run_package_in_future_patch"),
        "dry_run_rejects_artifact_path_outside_l25_42_runtime": source.get("dry_run_rejects_artifact_path_outside_l25_42_runtime"),
        "artifact_path_opened_by_l25_42": source.get("artifact_path_opened_by_l25_42", False),
        "artifact_bytes_read_by_l25_42": source.get("artifact_bytes_read_by_l25_42", False),
        "zip_member_opened_by_l25_42": source.get("zip_member_opened_by_l25_42", False),
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


def build_real_download_artifact_package_execution_dry_run_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    source_payload: Mapping[str, Any] | None = None,
    allow_dry_run_broad_checkpoint: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    Path(repo_root or ".").resolve()
    source = _normalize_l25_42_source(source_payload)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_DRY_RUN_BROAD_CHECKPOINT_TOKEN
    source_ok = bool(
        source.get("ok") is True
        and source.get("patch") == "L25.42"
        and source.get("package_execution_first_controlled_dry_run_proof") is True
        and source.get("package_execution_dry_run_only") is True
        and source.get("package_execution_dry_run_from_source_payload_only") is True
        and source.get("package_execution_dry_run_allowed") is True
        and source.get("candidate_artifact_suffix_zip") is True
        and source.get("candidate_artifact_under_l25_42_runtime") is True
        and source.get("would_run_command_rendered") is True
        and source.get("would_run_command_program") == "py"
        and source.get("would_invoke_patchops_run_package_in_future_patch") is True
        and source.get("dry_run_rejects_artifact_path_outside_l25_42_runtime") is True
        and source.get("artifact_path_opened_by_l25_42") is False
        and source.get("artifact_bytes_read_by_l25_42") is False
        and source.get("zip_member_opened_by_l25_42") is False
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
    broad_allowed = bool(source_ok and allow_dry_run_broad_checkpoint and token_valid)
    checks: list[dict[str, Any]] = [
        {"name": "source_l25_42_payload_ok", "ok": source_ok},
        {"name": "dry_run_broad_token_present", "ok": token_present},
        {"name": "dry_run_broad_token_valid", "ok": token_valid},
        {"name": "dry_run_broad_explicitly_allowed", "ok": allow_dry_run_broad_checkpoint is True},
        {"name": "dry_run_broad_checkpoint_allowed", "ok": broad_allowed},
    ]
    if broad_allowed:
        checks.extend([
            {"name": "dry_run_proof_accepted", "ok": source.get("package_execution_first_controlled_dry_run_proof") is True},
            {"name": "dry_run_command_rendering_accepted", "ok": source.get("would_run_command_rendered") is True and source.get("would_run_command_program") == "py"},
            {"name": "future_run_package_intent_without_invocation", "ok": source.get("would_invoke_patchops_run_package_in_future_patch") is True and source.get("patchops_cli_run_package_invoked_for_real_artifact") is False},
            {"name": "dry_run_path_guard_accepted", "ok": source.get("candidate_artifact_suffix_zip") is True and source.get("candidate_artifact_under_l25_42_runtime") is True and source.get("dry_run_rejects_artifact_path_outside_l25_42_runtime") is True},
            {"name": "dry_run_no_artifact_reads", "ok": source.get("artifact_path_opened_by_l25_42") is False and source.get("artifact_bytes_read_by_l25_42") is False and source.get("zip_member_opened_by_l25_42") is False},
            {"name": "dry_run_no_execution_or_extraction", "ok": source.get("package_execution_allowed") is False and source.get("package_execution_performed_by_adapter") is False and source.get("package_run") is False and source.get("real_archive_candidate_extracted") is False},
        ])
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "package_execution_dry_run_broad_checkpoint": True,
        "package_execution_dry_run_broad_checkpoint_from_source_payload_only": True,
        "package_execution_dry_run_broad_checkpoint_requested": bool(allow_dry_run_broad_checkpoint or token_present),
        "package_execution_dry_run_broad_checkpoint_token_present": token_present,
        "package_execution_dry_run_broad_checkpoint_token_valid": token_valid,
        "package_execution_dry_run_broad_checkpoint_allowed": broad_allowed,
        "source_l25_42_summary": source,
        "accepted_package_execution_dry_run_only": source.get("package_execution_dry_run_only") is True,
        "accepted_package_execution_dry_run_allowed": source.get("package_execution_dry_run_allowed") is True,
        "accepted_candidate_artifact_suffix_zip": source.get("candidate_artifact_suffix_zip") is True,
        "accepted_candidate_artifact_under_l25_42_runtime": source.get("candidate_artifact_under_l25_42_runtime") is True,
        "accepted_would_run_command_rendered": source.get("would_run_command_rendered") is True,
        "accepted_would_run_command_program": source.get("would_run_command_program"),
        "accepted_would_invoke_patchops_run_package_in_future_patch": source.get("would_invoke_patchops_run_package_in_future_patch") is True,
        "accepted_dry_run_rejects_artifact_path_outside_l25_42_runtime": source.get("dry_run_rejects_artifact_path_outside_l25_42_runtime") is True,
        "dry_run_ladder_summary": [
            "L25.41 authorized only future package-execution work and did not execute packages",
            "L25.42 rendered a would-run PatchOps run-package command for a controlled artifact path only",
            "L25.42 rejected artifact paths outside its runtime folder",
            "L25.42 did not invoke run-package, execute packages, read artifacts, open ZIP members, extract archives, or start browsers",
        ],
        "artifact_path_opened_by_l25_43": False,
        "artifact_bytes_read_by_l25_43": False,
        "zip_member_opened_by_l25_43": False,
        "real_archive_candidate_extracted": False,
        "adapter_archive_extraction_performed": False,
        "archive_member_extracted_to_project": False,
        "artifact_member_written_to_project": False,
        "package_manifest_used_for_execution": False,
        "package_execution_allowed": False,
        "package_execution_performed_by_adapter": False,
        "package_run": False,
        "patchops_cli_run_package_invoked_for_real_artifact": False,
        "no_browser_permission_added_by_l25_43": True,
        "no_download_permission_added_by_l25_43": True,
        "no_artifact_or_zip_read_permission_added_by_l25_43": True,
        "no_archive_extraction_permission_added_by_l25_43": True,
        "no_package_execution_performed_by_l25_43": True,
        "no_patchops_run_package_invocation_by_l25_43": True,
        "no_pasteback_permission_added_by_l25_43": True,
        "no_git_permission_added_by_l25_43": True,
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
        f"Broad Checkpoint              : {payload.get('package_execution_dry_run_broad_checkpoint_allowed')}",
        f"Would Run Rendered            : {payload.get('accepted_would_run_command_rendered')}",
        f"PatchOps Run-Package Invoked  : {payload.get('patchops_cli_run_package_invoked_for_real_artifact')}",
        f"Package Execution Allowed     : {payload.get('package_execution_allowed')}",
        f"Artifact Opened By L25.43     : {payload.get('artifact_path_opened_by_l25_43')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--source-payload-json", default=None)
    parser.add_argument("--allow-dry-run-broad-checkpoint", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    source_payload = json.loads(args.source_payload_json) if args.source_payload_json else None
    payload = build_real_download_artifact_package_execution_dry_run_broad_checkpoint(
        args.repo_root,
        source_payload=source_payload,
        allow_dry_run_broad_checkpoint=args.allow_dry_run_broad_checkpoint,
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
