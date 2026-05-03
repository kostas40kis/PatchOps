"""L25.27 broad checkpoint for controlled archive manifest PatchOps plan.

This follows accepted L25.26. It replays the controlled synthetic archive
manifest PatchOps plan-only proof and summarizes the L25.25-L25.26 plan ladder.
It does not invoke PatchOps apply, run-package, package execution, extraction,
browser automation, pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_patchops_plan_first_controlled_proof as l25_26

PATCH = "L25.27"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.27 Microsoft Edge controlled runtime archive manifest PatchOps plan broad checkpoint"
SOURCE_PATCH = "L25.26"
SOURCE_LADDER = (
    "L25.25 archive manifest PatchOps plan authorization gate",
    "L25.26 first controlled synthetic archive manifest PatchOps plan-only proof",
)
NEXT_PATCH = "L25.28 Microsoft Edge controlled runtime archive manifest PatchOps apply authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
TARGET_MANIFEST_MEMBER_NAME = l25_26.TARGET_MANIFEST_MEMBER_NAME
EXPECTED_PLAN_SCOPE = l25_26.PATCHOPS_PLAN_SCOPE
EXPECTED_SYNTHETIC_PATCH_NAME = "synthetic_l25_26_patchops_plan_fixture"

ALWAYS_FALSE_FIELDS = (
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


def _l25_26_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_26.build_archive_manifest_patchops_plan_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.26 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_26_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_26.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_26.build_archive_manifest_patchops_plan_first_controlled_proof(
            repo_root,
            allow_archive_manifest_patchops_plan_proof=True,
            authorization_token=l25_26.REQUIRED_ARCHIVE_MANIFEST_PATCHOPS_PLAN_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            member_name=TARGET_MANIFEST_MEMBER_NAME,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.26 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_patchops_plan_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_26_default_payload(root, target_url)
    authorized_payload = _l25_26_authorized_payload(root, target_url)
    command_summary = authorized_payload.get("patchops_plan_command_summary") or {}

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_26_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_26_default_is_passive", "ok": default_payload.get("patchops_manifest_plan_performed") is False and default_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is False},
        {"name": "source_l25_26_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_26_patch_marker", "ok": authorized_payload.get("patch") == "L25.26"},
        {"name": "source_l25_26_plan_fixture_isolated", "ok": authorized_payload.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures") is True},
        {"name": "source_l25_26_plan_allowed", "ok": authorized_payload.get("archive_manifest_patchops_plan_allowed") is True},
        {"name": "source_l25_26_manifest_payload_read", "ok": authorized_payload.get("manifest_payload_read") is True and authorized_payload.get("manifest_payload_bytes_read") is True},
        {"name": "source_l25_26_temp_manifest_written", "ok": authorized_payload.get("manifest_temp_file_written_for_plan") is True},
        {"name": "source_l25_26_patchops_plan_invoked", "ok": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is True},
        {"name": "source_l25_26_patchops_plan_exit_zero", "ok": authorized_payload.get("patchops_cli_plan_exit_code") == 0},
        {"name": "source_l25_26_patchops_plan_not_timed_out", "ok": authorized_payload.get("patchops_cli_plan_timed_out") is False},
        {"name": "source_l25_26_patchops_plan_json_object", "ok": authorized_payload.get("patchops_cli_plan_json_object") is True},
        {"name": "source_l25_26_patchops_plan_patch_name", "ok": authorized_payload.get("patchops_cli_plan_patch_name") == EXPECTED_SYNTHETIC_PATCH_NAME},
        {"name": "source_l25_26_patchops_plan_active_profile", "ok": authorized_payload.get("patchops_cli_plan_active_profile") == "generic_python"},
        {"name": "source_l25_26_patchops_plan_manifest_version", "ok": authorized_payload.get("patchops_cli_plan_manifest_version") == "1"},
        {"name": "source_l25_26_patchops_plan_mode", "ok": authorized_payload.get("patchops_cli_plan_mode") == "apply"},
        {"name": "source_l25_26_patchops_plan_target_files_empty", "ok": authorized_payload.get("patchops_cli_plan_target_files") == []},
        {"name": "source_l25_26_patchops_plan_validation_commands_empty", "ok": authorized_payload.get("patchops_cli_plan_validation_commands") == []},
        {"name": "source_l25_26_member_name", "ok": authorized_payload.get("manifest_member_name_read") == TARGET_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_26_scope_plan_only", "ok": authorized_payload.get("patchops_plan_scope") == EXPECTED_PLAN_SCOPE},
        {"name": "source_l25_26_command_summary_plan_only", "ok": command_summary.get("command_kind") == "py -m patchops.cli plan" and command_summary.get("exit_code") == 0 and command_summary.get("timed_out") is False},
        {"name": "source_l25_26_no_apply_run_package", "ok": authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest") is False and authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest") is False},
        {"name": "source_l25_26_no_execution_extract_browser_package", "ok": authorized_payload.get("package_manifest_used_for_execution") is False and authorized_payload.get("package_execution_allowed") is False and authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_manifest_patchops_plan_ladder_checkpoint": True,
        "l25_archive_manifest_patchops_plan_ladder_complete": ok,
        "source_l25_26_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "patchops_manifest_plan_performed": default_payload.get("patchops_manifest_plan_performed"),
            "patchops_cli_plan_invoked_for_archive_manifest": default_payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
            "patchops_plan_scope": default_payload.get("patchops_plan_scope"),
            "plan_fixture_isolated_from_preflight_and_inspect_fixtures": default_payload.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures"),
        },
        "source_l25_26_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_25_ok": authorized_payload.get("source_l25_25_summary", {}).get("ok"),
            "source_l25_25_future_authorized": authorized_payload.get("source_l25_25_summary", {}).get("future_patchops_plan_authorized"),
            "source_l25_25_source_l25_24_inspect_invoked": authorized_payload.get("source_l25_25_summary", {}).get("source_l25_24_inspect_invoked"),
            "patchops_plan_allowed": authorized_payload.get("archive_manifest_patchops_plan_allowed"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read"),
            "manifest_temp_file_written_for_plan": authorized_payload.get("manifest_temp_file_written_for_plan"),
            "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
            "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
            "patchops_manifest_plan_performed": authorized_payload.get("patchops_manifest_plan_performed"),
            "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
            "patchops_cli_plan_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest"),
            "patchops_cli_plan_exit_code": authorized_payload.get("patchops_cli_plan_exit_code"),
            "patchops_cli_plan_timed_out": authorized_payload.get("patchops_cli_plan_timed_out"),
            "patchops_cli_plan_json_object": authorized_payload.get("patchops_cli_plan_json_object"),
            "patchops_cli_plan_patch_name": authorized_payload.get("patchops_cli_plan_patch_name"),
            "patchops_cli_plan_active_profile": authorized_payload.get("patchops_cli_plan_active_profile"),
            "patchops_cli_plan_manifest_version": authorized_payload.get("patchops_cli_plan_manifest_version"),
            "patchops_cli_plan_mode": authorized_payload.get("patchops_cli_plan_mode"),
            "patchops_cli_plan_target_files": authorized_payload.get("patchops_cli_plan_target_files"),
            "patchops_cli_plan_validation_commands": authorized_payload.get("patchops_cli_plan_validation_commands"),
            "patchops_plan_scope": authorized_payload.get("patchops_plan_scope"),
            "patchops_plan_command_summary": command_summary,
            "plan_fixture_isolated_from_preflight_and_inspect_fixtures": authorized_payload.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures"),
            "patchops_cli_apply_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_apply_invoked_for_archive_manifest"),
            "patchops_cli_run_package_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_run_package_invoked_for_archive_manifest"),
            "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
            "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_patchops_plan_scope": EXPECTED_PLAN_SCOPE,
        "accepted_patchops_plan_allowed": authorized_payload.get("archive_manifest_patchops_plan_allowed") is True,
        "accepted_manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "accepted_manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "accepted_manifest_temp_file_written_for_plan": authorized_payload.get("manifest_temp_file_written_for_plan") is True,
        "accepted_patchops_manifest_plan_performed": authorized_payload.get("patchops_manifest_plan_performed") is True,
        "accepted_patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed") is False,
        "accepted_patchops_cli_plan_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is True,
        "accepted_patchops_cli_plan_exit_code": authorized_payload.get("patchops_cli_plan_exit_code"),
        "accepted_patchops_cli_plan_timed_out": authorized_payload.get("patchops_cli_plan_timed_out"),
        "accepted_patchops_cli_plan_json_object": authorized_payload.get("patchops_cli_plan_json_object"),
        "accepted_patchops_cli_plan_patch_name": authorized_payload.get("patchops_cli_plan_patch_name"),
        "accepted_patchops_cli_plan_active_profile": authorized_payload.get("patchops_cli_plan_active_profile"),
        "accepted_patchops_cli_plan_manifest_version": authorized_payload.get("patchops_cli_plan_manifest_version"),
        "accepted_patchops_cli_plan_mode": authorized_payload.get("patchops_cli_plan_mode"),
        "accepted_patchops_cli_plan_target_files": authorized_payload.get("patchops_cli_plan_target_files"),
        "accepted_patchops_cli_plan_validation_commands": authorized_payload.get("patchops_cli_plan_validation_commands"),
        "accepted_plan_fixture_isolated_from_preflight_and_inspect_fixtures": authorized_payload.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures") is True,
        "archive_manifest_patchops_plan_allowed": authorized_payload.get("archive_manifest_patchops_plan_allowed") is True,
        "manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "manifest_temp_file_written_for_plan": authorized_payload.get("manifest_temp_file_written_for_plan") is True,
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "patchops_manifest_plan_performed": authorized_payload.get("patchops_manifest_plan_performed") is True,
        "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed") is False,
        "patchops_cli_plan_invoked_for_archive_manifest": authorized_payload.get("patchops_cli_plan_invoked_for_archive_manifest") is True,
        "patchops_cli_plan_exit_code": authorized_payload.get("patchops_cli_plan_exit_code"),
        "patchops_cli_plan_timed_out": authorized_payload.get("patchops_cli_plan_timed_out"),
        "patchops_cli_plan_json_object": authorized_payload.get("patchops_cli_plan_json_object"),
        "patchops_cli_plan_patch_name": authorized_payload.get("patchops_cli_plan_patch_name"),
        "patchops_plan_scope": authorized_payload.get("patchops_plan_scope"),
        "patchops_plan_command_summary": command_summary,
        "plan_fixture_isolated_from_preflight_and_inspect_fixtures": authorized_payload.get("plan_fixture_isolated_from_preflight_and_inspect_fixtures") is True,
        "no_patchops_apply_run_package_added_by_l25_27": True,
        "no_package_execution_added_by_l25_27": True,
        "no_archive_extraction_added_by_l25_27": True,
        "no_browser_permission_added_by_l25_27": True,
        "no_pasteback_or_package_run_permission_added_by_l25_27": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.27 is a broad checkpoint over accepted L25.25-L25.26 PatchOps plan-only work.",
            "Only PatchOps plan on a runtime temp copy of the isolated controlled synthetic archive manifest is accepted; apply, run-package, execution, extraction, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_manifest_patchops_plan_ladder_complete')}",
        f"PatchOps Plan Invoked         : {payload.get('patchops_cli_plan_invoked_for_archive_manifest')}",
        f"PatchOps Plan Exit            : {payload.get('patchops_cli_plan_exit_code')}",
        f"PatchOps Plan Patch           : {payload.get('patchops_cli_plan_patch_name')}",
        f"Apply Invoked                 : {payload.get('patchops_cli_apply_invoked_for_archive_manifest')}",
        f"Run Package Invoked           : {payload.get('patchops_cli_run_package_invoked_for_archive_manifest')}",
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
    payload = build_archive_manifest_patchops_plan_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
