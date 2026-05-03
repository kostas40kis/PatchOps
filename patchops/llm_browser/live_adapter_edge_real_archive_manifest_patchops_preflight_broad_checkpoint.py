"""L25.21 broad checkpoint for controlled archive manifest PatchOps preflight.

This follows accepted L25.20 plus L25.20a. It replays the controlled synthetic
archive manifest PatchOps check-only preflight proof and summarizes the
L25.19-L25.20 preflight ladder. It does not invoke PatchOps inspect, plan,
apply, run-package, package execution, extraction, browser automation,
pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_preflight_first_controlled_proof as l25_20

PATCH = "L25.21"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.21 Microsoft Edge controlled runtime archive manifest PatchOps preflight broad checkpoint"
SOURCE_PATCH = "L25.20/L25.20a"
SOURCE_LADDER = (
    "L25.19 archive manifest validation-to-PatchOps-preflight authorization gate",
    "L25.20 first controlled synthetic archive manifest PatchOps check-only preflight proof",
    "L25.20a dual-compatible controlled fixture repair",
)
NEXT_PATCH = "L25.22 Microsoft Edge controlled runtime archive manifest PatchOps inspect authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
TARGET_MANIFEST_MEMBER_NAME = l25_20.TARGET_MANIFEST_MEMBER_NAME
EXPECTED_PREFLIGHT_SCOPE = l25_20.PATCHOPS_PREFLIGHT_SCOPE
EXPECTED_SYNTHETIC_PATCH_NAME = "synthetic_l25_20_patchops_check_fixture"

ALWAYS_FALSE_FIELDS = (
    "patchops_cli_inspect_invoked_for_archive_manifest",
    "patchops_cli_plan_invoked_for_archive_manifest",
    "patchops_cli_apply_invoked_for_archive_manifest",
    "patchops_cli_run_package_invoked_for_archive_manifest",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
    "real_downloaded_manifest_read",
    "real_downloaded_artifact_read",
    "real_archive_candidate_extracted",
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
    "package_run_performed_by_adapter",
    "package_run",
    "localhost_server_started",
    "browser_extension_used",
    "git_commit_performed",
    "git_push_performed",
)


def _l25_20_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_20.build_archive_manifest_patchops_preflight_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.20 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_20_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_20.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_20.build_archive_manifest_patchops_preflight_first_controlled_proof(
            repo_root,
            allow_archive_manifest_patchops_preflight_proof=True,
            authorization_token=l25_20.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PREFLIGHT_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            member_name=TARGET_MANIFEST_MEMBER_NAME,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.20 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_patchops_preflight_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_20_default_payload(root, target_url)
    authorized_payload = _l25_20_authorized_payload(root, target_url)
    command_summary = authorized_payload.get("patchops_preflight_command_summary") or {}

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_20_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_20_default_is_passive", "ok": default_payload.get("patchops_manifest_preflight_performed") is False and default_payload.get("patchops_cli_check_invoked_for_archive_manifest") is False},
        {"name": "source_l25_20_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_20_patch_marker", "ok": authorized_payload.get("patch") == "L25.20"},
        {"name": "source_l25_20_preflight_allowed", "ok": authorized_payload.get("archive_manifest_patchops_preflight_allowed") is True},
        {"name": "source_l25_20_manifest_payload_read", "ok": authorized_payload.get("manifest_payload_read") is True and authorized_payload.get("manifest_payload_bytes_read") is True},
        {"name": "source_l25_20_temp_manifest_written", "ok": authorized_payload.get("manifest_temp_file_written_for_preflight") is True},
        {"name": "source_l25_20_patchops_check_invoked", "ok": authorized_payload.get("patchops_cli_check_invoked_for_archive_manifest") is True},
        {"name": "source_l25_20_patchops_check_exit_zero", "ok": authorized_payload.get("patchops_cli_check_exit_code") == 0},
        {"name": "source_l25_20_patchops_check_not_timed_out", "ok": authorized_payload.get("patchops_cli_check_timed_out") is False},
        {"name": "source_l25_20_patchops_check_ok", "ok": authorized_payload.get("patchops_cli_check_ok") is True},
        {"name": "source_l25_20_patchops_check_issue_count_zero", "ok": authorized_payload.get("patchops_cli_check_issue_count") == 0},
        {"name": "source_l25_20_patchops_check_patch_name", "ok": authorized_payload.get("patchops_cli_check_patch_name") == EXPECTED_SYNTHETIC_PATCH_NAME},
        {"name": "source_l25_20_member_name", "ok": authorized_payload.get("manifest_member_name_read") == TARGET_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_20_scope_check_only", "ok": authorized_payload.get("patchops_preflight_scope") == EXPECTED_PREFLIGHT_SCOPE},
        {"name": "source_l25_20_command_summary_check_only", "ok": command_summary.get("command_kind") == "py -m patchops.cli check" and command_summary.get("exit_code") == 0 and command_summary.get("timed_out") is False},
        {"name": "source_l25_20_no_inspect_plan_apply_run_package", "ok": authorized_payload.get("patchops_cli_inspect_invoked_for_archive_manifest") is False and authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is False and authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False and authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False},
        {"name": "source_l25_20_no_execution_extract_browser_package", "ok": authorized_payload.get("package_manifest_used_for_execution") is False and authorized_payload.get("package_execution_allowed") is False and authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_ladder": list(SOURCE_LADDER),
        "broad_checkpoint": True,
        "archive_manifest_patchops_preflight_ladder_checkpoint": True,
        "l25_archive_manifest_patchops_preflight_ladder_complete": ok,
        "source_l25_20_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "patchops_manifest_preflight_performed": default_payload.get("patchops_manifest_preflight_performed"),
            "patchops_cli_check_invoked_for_archive_manifest": default_payload.get("patchops_cli_check_invoked_for_archive_manifest"),
            "patchops_preflight_scope": default_payload.get("patchops_preflight_scope"),
        },
        "source_l25_20_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_19_ok": authorized_payload.get("source_l25_19_summary", {}).get("ok"),
            "source_l25_19_future_authorized": authorized_payload.get("source_l25_19_summary", {}).get("future_patchops_preflight_authorized"),
            "patchops_preflight_allowed": authorized_payload.get("archive_manifest_patchops_preflight_allowed"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read"),
            "manifest_temp_file_written_for_preflight": authorized_payload.get("manifest_temp_file_written_for_preflight"),
            "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
            "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
            "patchops_manifest_preflight_performed": authorized_payload.get("patchops_manifest_preflight_performed"),
            "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
            "patchops_cli_check_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_check_invoked_for_archive_manifest"),
            "patchops_cli_check_exit_code": authorized_payload.get("patchops_cli_check_exit_code"),
            "patchops_cli_check_timed_out": authorized_payload.get("patchops_cli_check_timed_out"),
            "patchops_cli_check_ok": authorized_payload.get("patchops_cli_check_ok"),
            "patchops_cli_check_issue_count": authorized_payload.get("patchops_cli_check_issue_count"),
            "patchops_cli_check_patch_name": authorized_payload.get("patchops_cli_check_patch_name"),
            "patchops_cli_check_active_profile": authorized_payload.get("patchops_cli_check_active_profile"),
            "patchops_preflight_scope": authorized_payload.get("patchops_preflight_scope"),
            "patchops_preflight_command_summary": command_summary,
            "patchops_cli_inspect_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_inspect_invoked_for_archive_manifest"),
            "patchops_cli_plan_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
            "patchops_cli_apply_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest"),
            "patchops_cli_run_package_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
            "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_patchops_preflight_scope": EXPECTED_PREFLIGHT_SCOPE,
        "accepted_patchops_preflight_allowed": authorized_payload.get("archive_manifest_patchops_preflight_allowed") is True,
        "accepted_manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "accepted_manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "accepted_manifest_temp_file_written_for_preflight": authorized_payload.get("manifest_temp_file_written_for_preflight") is True,
        "accepted_patchops_manifest_preflight_performed": authorized_payload.get("patchops_manifest_preflight_performed") is True,
        "accepted_patchops_manifest_validation_performed_check_only": authorized_payload.get("patchops_manifest_validation_performed") is True,
        "accepted_patchops_cli_check_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_check_invoked_for_archive_manifest") is True,
        "accepted_patchops_cli_check_exit_code": authorized_payload.get("patchops_cli_check_exit_code"),
        "accepted_patchops_cli_check_ok": authorized_payload.get("patchops_cli_check_ok"),
        "accepted_patchops_cli_check_issue_count": authorized_payload.get("patchops_cli_check_issue_count"),
        "accepted_patchops_cli_check_patch_name": authorized_payload.get("patchops_cli_check_patch_name"),
        "accepted_patchops_cli_check_active_profile": authorized_payload.get("patchops_cli_check_active_profile"),
        "archive_manifest_patchops_preflight_allowed": authorized_payload.get("archive_manifest_patchops_preflight_allowed") is True,
        "manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "manifest_temp_file_written_for_preflight": authorized_payload.get("manifest_temp_file_written_for_preflight") is True,
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "patchops_manifest_preflight_performed": authorized_payload.get("patchops_manifest_preflight_performed") is True,
        "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed") is True,
        "patchops_cli_check_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_check_invoked_for_archive_manifest") is True,
        "patchops_cli_check_exit_code": authorized_payload.get("patchops_cli_check_exit_code"),
        "patchops_cli_check_timed_out": authorized_payload.get("patchops_cli_check_timed_out"),
        "patchops_cli_check_ok": authorized_payload.get("patchops_cli_check_ok"),
        "patchops_cli_check_issue_count": authorized_payload.get("patchops_cli_check_issue_count"),
        "patchops_cli_check_patch_name": authorized_payload.get("patchops_cli_check_patch_name"),
        "patchops_preflight_scope": authorized_payload.get("patchops_preflight_scope"),
        "patchops_preflight_command_summary": command_summary,
        "no_patchops_inspect_plan_apply_run_package_added_by_l25_21": True,
        "no_package_execution_added_by_l25_21": True,
        "no_archive_extraction_added_by_l25_21": True,
        "no_browser_permission_added_by_l25_21": True,
        "no_pasteback_or_package_run_permission_added_by_l25_21": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.21 is a broad checkpoint over accepted L25.19-L25.20/L25.20a PatchOps check-only preflight work.",
            "Only PatchOps check on a runtime temp copy of the controlled synthetic archive manifest is accepted; inspect, plan, apply, run-package, execution, extraction, browser, pasteback, send/submit, and package-run remain separate future gates.",
        ],
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Ladder Complete               : {payload.get('l25_archive_manifest_patchops_preflight_ladder_complete')}",
        f"PatchOps Check Invoked        : {payload.get('patchops_cli_check_invoked_for_archive_manifest')}",
        f"PatchOps Check Exit           : {payload.get('patchops_cli_check_exit_code')}",
        f"PatchOps Check OK             : {payload.get('patchops_cli_check_ok')}",
        f"Inspect Invoked               : {payload.get('patchops_cli_inspect_invoked_for_archive_manifest')}",
        f"Plan Invoked                  : {payload.get('patchops_cli_plan_invoked_for_archive_manifest')}",
        f"Apply Invoked                 : {payload.get('patchops_cli_apply_invoked_for_archive_manifest')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_patchops_preflight_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
