"""L22.7 final acceptance marker for Edge downloaded-archive manifest validation.

This module closes the L22 stream by summarizing the accepted L22.3b,
L22.4/L22.4a, L22.5, and L22.6/L22.6a surfaces. It does not add any new
execution permission beyond the already accepted L22.5 synthetic manifest fixture
proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_broad_checkpoint as l22_06

PATCH = "L22.7"
PHASE = "L22"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L22.7 Microsoft Edge downloaded-archive manifest validation final acceptance marker"
SOURCE_PATCHES = ("L22.3b", "L22.4/L22.4a", "L22.5", "L22.6/L22.6a")
POST_L22_NEXT = "Post-L22: choose the next separately gated stream; L22 grants no real browser, archive, pasteback, or package-run permission"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

FORBIDDEN_TRUE_FIELDS = (
    "archive_extracted",
    "downloaded_archive_extracted",
    "downloaded_archive_opened",
    "archive_member_bytes_read",
    "member_bytes_read",
    "archive_member_content_read",
    "artifact_content_read",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
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


def _true_violations(payload: Mapping[str, Any], names: Sequence[str]) -> list[str]:
    return [name for name in names if payload.get(name) is True]


def _call_broad(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l22_06.build_manifest_validation_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover - defensive readback path
        return {"ok": False, "error": f"L22.6 broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_manifest_validation_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    broad_payload = _call_broad(root, target_url)
    safety_violations = _true_violations(broad_payload, FORBIDDEN_TRUE_FIELDS)

    checks: list[dict[str, Any]] = [
        {"name": "l22_06_broad_payload_ok", "ok": broad_payload.get("ok") is True},
        {"name": "l22_06_marker_present", "ok": broad_payload.get("patch") == "L22.6" and broad_payload.get("repair_patch") == "L22.6a"},
        {"name": "l22_06_failed_checks_empty", "ok": broad_payload.get("failed_checks") == []},
        {"name": "l22_03b_summary_ok", "ok": broad_payload.get("l22_03b_summary", {}).get("ok") is True},
        {"name": "l22_04_authorization_gate_ok", "ok": broad_payload.get("l22_04_authorized_summary", {}).get("manifest_validation_authorization_granted_for_future_patch") is True},
        {"name": "l22_05_default_remains_passive", "ok": broad_payload.get("l22_05_default_summary", {}).get("downloaded_manifest_read") is False},
        {"name": "l22_05_authorized_synthetic_manifest_read_ok", "ok": broad_payload.get("l22_05_authorized_summary", {}).get("synthetic_manifest_fixture_read") is True},
        {"name": "l22_05_manifest_validation_result_ok", "ok": broad_payload.get("manifest_validation_result") is True},
        {"name": "l22_manifest_scope_is_synthetic_fixture_only", "ok": broad_payload.get("manifest_validation_scope") == "synthetic_patchops_runtime_manifest_fixture_only"},
        {"name": "real_downloaded_manifest_read_stays_false", "ok": broad_payload.get("real_downloaded_manifest_read") is False},
        {"name": "real_archive_manifest_read_stays_false", "ok": broad_payload.get("real_archive_manifest_read") is False},
        {"name": "no_forbidden_side_effects", "ok": not safety_violations},
    ]
    failed_checks = [check for check in checks if not check.get("ok")]
    ok = not failed_checks

    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patches": list(SOURCE_PATCHES),
        "l22_final_acceptance_marker": True,
        "l22_downloaded_archive_manifest_validation_stream_complete": ok,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "accepted_scope": "synthetic_manifest_fixture_validation_only",
        "no_new_execution_permission_added_by_l22_7": True,
        "l22_06_summary": {
            "ok": broad_payload.get("ok"),
            "patch": broad_payload.get("patch"),
            "repair_patch": broad_payload.get("repair_patch"),
            "broad_checkpoint": broad_payload.get("broad_checkpoint"),
            "failed_checks": broad_payload.get("failed_checks"),
            "manifest_validation_scope": broad_payload.get("manifest_validation_scope"),
            "manifest_validation_result": broad_payload.get("manifest_validation_result"),
            "real_downloaded_manifest_read": broad_payload.get("real_downloaded_manifest_read"),
            "real_archive_manifest_read": broad_payload.get("real_archive_manifest_read"),
            "archive_extracted": broad_payload.get("archive_extracted"),
            "archive_member_bytes_read": broad_payload.get("archive_member_bytes_read"),
            "browser_started": broad_payload.get("browser_started"),
            "pasteback_workflow_active": broad_payload.get("pasteback_workflow_active"),
            "package_run": broad_payload.get("package_run"),
        },
        "l22_03b_summary": broad_payload.get("l22_03b_summary"),
        "l22_04_authorized_summary": broad_payload.get("l22_04_authorized_summary"),
        "l22_05_default_summary": broad_payload.get("l22_05_default_summary"),
        "l22_05_authorized_summary": broad_payload.get("l22_05_authorized_summary"),
        "manifest_validation_execution_allowed": broad_payload.get("manifest_validation_execution_allowed") is True,
        "manifest_validation_active": broad_payload.get("manifest_validation_active") is True,
        "manifest_validation_performed": broad_payload.get("manifest_validation_performed") is True,
        "downloaded_manifest_read": broad_payload.get("downloaded_manifest_read") is True,
        "manifest_read": broad_payload.get("manifest_read") is True,
        "synthetic_manifest_fixture_read": broad_payload.get("synthetic_manifest_fixture_read") is True,
        "synthetic_manifest_json_parsed": broad_payload.get("synthetic_manifest_json_parsed") is True,
        "manifest_shape_validated": broad_payload.get("manifest_shape_validated") is True,
        "manifest_validation_scope": broad_payload.get("manifest_validation_scope"),
        "manifest_validation_result": broad_payload.get("manifest_validation_result"),
        "real_downloaded_manifest_read": False,
        "real_archive_manifest_read": False,
        "safety_violations": safety_violations,
        "checks": checks,
        "failed_checks": failed_checks,
        "next_patch": POST_L22_NEXT,
        "notes": [
            "L22.7 is a final acceptance marker only.",
            "The only manifest read accepted by L22 is the synthetic runtime fixture proof from L22.5.",
            "L22 grants no permission for real browser/download/archive/pasteback/package-run execution.",
        ],
    }
    for field in FORBIDDEN_TRUE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"L22 Complete                  : {payload.get('l22_downloaded_archive_manifest_validation_stream_complete')}",
        f"Accepted Scope                : {payload.get('accepted_scope')}",
        f"Manifest Scope                : {payload.get('manifest_validation_scope')}",
        f"Manifest Result               : {payload.get('manifest_validation_result')}",
        f"Synthetic Fixture Read        : {payload.get('synthetic_manifest_fixture_read')}",
        f"Real Download Manifest Read   : {payload.get('real_downloaded_manifest_read')}",
        f"Archive Extracted             : {payload.get('archive_extracted')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next                          : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_manifest_validation_final_acceptance_marker(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
