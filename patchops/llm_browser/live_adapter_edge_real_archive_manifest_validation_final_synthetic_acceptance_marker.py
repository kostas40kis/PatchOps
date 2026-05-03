"""L23.9 final synthetic acceptance marker for Edge archive-manifest validation.

This module follows accepted L23.8. It finalizes only the synthetic-manifest
payload ladder. It does not grant real downloaded archive handling, browser
activity, pasteback, send/submit, or package-run permission.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_payload_broad_checkpoint as l23_08

PATCH = "L23.9"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.9 Microsoft Edge real downloaded-archive manifest validation final synthetic acceptance marker"
SOURCE_PATCH = "L23.8"
ACCEPTED_LADDER = (
    "L23.1 real downloaded-archive manifest authorization gate",
    "L23.2/L23.2a fixed synthetic archive path preflight",
    "L23.3 synthetic archive listing authorization gate",
    "L23.4/L23.4b first synthetic archive metadata listing proof",
    "L23.5 synthetic manifest-name proof gate",
    "L23.6 synthetic manifest payload authorization gate",
    "L23.7 first synthetic manifest payload proof",
    "L23.8 synthetic payload broad checkpoint",
)
POST_L23_NEXT = "Post-L23: choose the next separately gated stream; L23 grants no real downloaded-archive, browser, pasteback, or package-run permission"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ACCEPTED_SYNTHETIC_SCOPE = "fixed_synthetic_archive_manifest_payload_only"
ACCEPTED_SYNTHETIC_PATCH_NAME = "l23_07_synthetic_manifest_payload_fixture"

ALWAYS_FALSE_FIELDS = (
    "non_manifest_member_bytes_read",
    "non_manifest_member_payload_read",
    "readme_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "candidate_archive_path_stat_performed",
    "candidate_archive_path_hash_performed",
    "synthetic_archive_hash_performed",
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


def _l23_08_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_08.build_synthetic_payload_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.8 broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_final_synthetic_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    broad_payload = _l23_08_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l23_08_payload_ok", "ok": broad_payload.get("ok") is True},
        {"name": "source_l23_08_patch_marker", "ok": broad_payload.get("patch") == "L23.8"},
        {"name": "source_l23_08_broad_checkpoint", "ok": broad_payload.get("broad_checkpoint") is True},
        {"name": "source_l23_08_ladder_complete", "ok": broad_payload.get("l23_synthetic_payload_ladder_complete") is True},
        {"name": "source_l23_08_failed_checks_empty", "ok": broad_payload.get("failed_checks") == []},
        {"name": "source_l23_08_default_remains_passive", "ok": broad_payload.get("source_l23_07_default_summary", {}).get("payload_read_performed") is False},
        {"name": "source_l23_08_authorized_payload_read", "ok": broad_payload.get("source_l23_07_authorized_summary", {}).get("payload_read_performed") is True},
        {"name": "source_l23_08_manifest_member_only", "ok": broad_payload.get("accepted_manifest_member_name") == "manifest.json"},
        {"name": "source_l23_08_synthetic_json_parsed", "ok": broad_payload.get("synthetic_manifest_json_parsed") is True},
        {"name": "source_l23_08_synthetic_shape_validated", "ok": broad_payload.get("synthetic_manifest_shape_validated") is True},
        {"name": "source_l23_08_synthetic_scope", "ok": broad_payload.get("accepted_synthetic_payload_scope") == ACCEPTED_SYNTHETIC_SCOPE},
        {"name": "source_l23_08_synthetic_patch_name", "ok": broad_payload.get("accepted_synthetic_manifest_patch_name") == ACCEPTED_SYNTHETIC_PATCH_NAME},
        {"name": "source_l23_08_no_non_manifest_or_readme_read", "ok": broad_payload.get("non_manifest_member_bytes_read") is False and broad_payload.get("readme_member_payload_read") is False},
        {"name": "source_l23_08_no_extraction_real_archive_browser_package", "ok": broad_payload.get("archive_extracted") is False and broad_payload.get("real_archive_manifest_read") is False and broad_payload.get("browser_started") is False and broad_payload.get("package_run") is False},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "accepted_ladder": list(ACCEPTED_LADDER),
        "final_synthetic_acceptance_marker": True,
        "l23_synthetic_manifest_validation_stream_complete": ok,
        "l23_real_downloaded_archive_permission_granted": False,
        "accepted_synthetic_payload_scope": broad_payload.get("accepted_synthetic_payload_scope"),
        "accepted_manifest_member_name": broad_payload.get("accepted_manifest_member_name"),
        "accepted_synthetic_manifest_patch_name": broad_payload.get("accepted_synthetic_manifest_patch_name"),
        "source_l23_08_summary": {
            "ok": broad_payload.get("ok"),
            "patch": broad_payload.get("patch"),
            "broad_checkpoint": broad_payload.get("broad_checkpoint"),
            "ladder_complete": broad_payload.get("l23_synthetic_payload_ladder_complete"),
            "failed_checks": broad_payload.get("failed_checks"),
            "default_payload_read_performed": broad_payload.get("source_l23_07_default_summary", {}).get("payload_read_performed"),
            "authorized_payload_read_performed": broad_payload.get("source_l23_07_authorized_summary", {}).get("payload_read_performed"),
            "manifest_member_name": broad_payload.get("accepted_manifest_member_name"),
            "synthetic_manifest_json_parsed": broad_payload.get("synthetic_manifest_json_parsed"),
            "synthetic_manifest_shape_validated": broad_payload.get("synthetic_manifest_shape_validated"),
            "manifest_member_payload_read": broad_payload.get("manifest_member_payload_read"),
            "non_manifest_member_bytes_read": broad_payload.get("non_manifest_member_bytes_read"),
            "readme_member_payload_read": broad_payload.get("readme_member_payload_read"),
            "archive_extracted": broad_payload.get("archive_extracted"),
            "real_archive_manifest_read": broad_payload.get("real_archive_manifest_read"),
            "browser_started": broad_payload.get("browser_started"),
            "pasteback": broad_payload.get("pasteback_workflow_active"),
            "package_run": broad_payload.get("package_run"),
        },
        "manifest_member_bytes_read": broad_payload.get("manifest_member_bytes_read") is True,
        "manifest_member_payload_read": broad_payload.get("manifest_member_payload_read") is True,
        "manifest_member_content_read": broad_payload.get("manifest_member_content_read") is True,
        "archive_member_bytes_read": broad_payload.get("archive_member_bytes_read") is True,
        "archive_member_payload_read": broad_payload.get("archive_member_payload_read") is True,
        "archive_member_content_read": broad_payload.get("archive_member_content_read") is True,
        "synthetic_manifest_json_parsed": broad_payload.get("synthetic_manifest_json_parsed") is True,
        "synthetic_manifest_shape_validated": broad_payload.get("synthetic_manifest_shape_validated") is True,
        "no_real_archive_permission_added_by_l23_9": True,
        "no_browser_permission_added_by_l23_9": True,
        "no_pasteback_or_package_run_permission_added_by_l23_9": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": POST_L23_NEXT,
        "notes": [
            "L23.9 finalizes only the synthetic L23 manifest-validation path.",
            "The only accepted payload read is manifest.json from the fixed synthetic archive fixture.",
            "Real downloaded archive validation, browser activity, pasteback, send/submit, and package-run remain separate future streams.",
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
        f"Final Marker                  : {payload.get('final_synthetic_acceptance_marker')}",
        f"L23 Synthetic Complete        : {payload.get('l23_synthetic_manifest_validation_stream_complete')}",
        f"Accepted Scope                : {payload.get('accepted_synthetic_payload_scope')}",
        f"Accepted Manifest Name        : {payload.get('accepted_manifest_member_name')}",
        f"Real Archive Permission       : {payload.get('l23_real_downloaded_archive_permission_granted')}",
        f"Non-Manifest Bytes Read       : {payload.get('non_manifest_member_bytes_read')}",
        f"Extraction                    : {payload.get('archive_extracted')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
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
    payload = build_final_synthetic_acceptance_marker(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
