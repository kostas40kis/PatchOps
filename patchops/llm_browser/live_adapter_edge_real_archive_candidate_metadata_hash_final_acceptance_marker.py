"""L24.9 final acceptance marker for controlled candidate metadata/hash work.

This follows accepted L24.8. It finalizes only the controlled runtime candidate
metadata/stat and SHA-256 ladder. It does not grant archive open/list/extract/read,
real archive manifest read, browser activity, pasteback, send/submit, or package-run
permission.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_hash_broad_checkpoint as l24_08

PATCH = "L24.9"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.9 Microsoft Edge real downloaded-archive candidate metadata/hash final acceptance marker"
SOURCE_PATCH = "L24.8"
ACCEPTED_LADDER = (
    "L24.1 real downloaded-archive candidate authorization gate",
    "L24.2/L24.2a candidate path string-only preflight gate",
    "L24.3 candidate filesystem stat authorization gate",
    "L24.4 controlled runtime candidate filesystem stat proof",
    "L24.5 controlled candidate filesystem stat broad checkpoint",
    "L24.6 candidate hash authorization gate",
    "L24.7 first controlled SHA-256 proof over controlled runtime fixture bytes",
    "L24.8 controlled hash broad checkpoint",
)
POST_L24_NEXT = "Post-L24: choose the next separately gated stream; L24 grants no archive open/list/extract/read, manifest payload read, browser, pasteback, send/submit, or package-run permission"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ACCEPTED_STAT_SCOPE = "controlled_runtime_candidate_filesystem_metadata_only"
ACCEPTED_HASH_SCOPE = "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open"

ALWAYS_FALSE_FIELDS = (
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
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


def _l24_08_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_08.build_real_archive_candidate_hash_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.8 hash broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_metadata_hash_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l24_08_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_08_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_08_patch_marker", "ok": source.get("patch") == "L24.8"},
        {"name": "source_l24_08_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l24_08_hash_ladder_complete", "ok": source.get("l24_candidate_hash_ladder_complete") is True},
        {"name": "source_l24_08_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l24_08_default_hash_passive", "ok": source.get("source_l24_07_default_summary", {}).get("hash_performed") is False},
        {"name": "source_l24_08_authorized_hash_performed", "ok": source.get("source_l24_07_authorized_summary", {}).get("hash_performed") is True},
        {"name": "source_l24_08_file_bytes_read_for_hash", "ok": source.get("downloaded_file_bytes_read") is True and source.get("downloaded_file_hash_performed") is True},
        {"name": "source_l24_08_sha256_read", "ok": source.get("real_archive_candidate_sha256_read") is True and source.get("accepted_sha256_is_lower_hex") is True},
        {"name": "source_l24_08_hash_scope", "ok": source.get("accepted_hash_scope") == ACCEPTED_HASH_SCOPE},
        {"name": "source_l24_08_no_archive_open_list_extract", "ok": source.get("real_archive_candidate_opened") is False and source.get("real_archive_candidate_listed") is False and source.get("real_archive_candidate_extracted") is False},
        {"name": "source_l24_08_no_manifest_browser_package", "ok": source.get("real_archive_manifest_read") is False and source.get("browser_started") is False and source.get("package_run") is False},
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
        "final_metadata_hash_acceptance_marker": True,
        "l24_metadata_hash_stream_complete": ok,
        "l24_archive_open_permission_granted": False,
        "l24_archive_listing_permission_granted": False,
        "l24_archive_extraction_permission_granted": False,
        "l24_archive_member_read_permission_granted": False,
        "l24_manifest_payload_read_permission_granted": False,
        "l24_browser_permission_granted": False,
        "l24_pasteback_permission_granted": False,
        "l24_package_run_permission_granted": False,
        "source_l24_08_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "hash_ladder_complete": source.get("l24_candidate_hash_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "accepted_hash_scope": source.get("accepted_hash_scope"),
            "default_hash_performed": source.get("source_l24_07_default_summary", {}).get("hash_performed"),
            "authorized_hash_performed": source.get("source_l24_07_authorized_summary", {}).get("hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_file_hash_performed": source.get("downloaded_file_hash_performed"),
            "sha256_read": source.get("real_archive_candidate_sha256_read"),
            "sha256_is_lower_hex": source.get("accepted_sha256_is_lower_hex"),
            "bytes_read_count": source.get("accepted_bytes_read_count"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "candidate_archive_listed": source.get("real_archive_candidate_listed"),
            "candidate_archive_extracted": source.get("real_archive_candidate_extracted"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "accepted_metadata_scope": ACCEPTED_STAT_SCOPE,
        "accepted_hash_scope": source.get("accepted_hash_scope"),
        "accepted_hash_performed": source.get("real_archive_candidate_path_hash_performed") is True,
        "accepted_file_bytes_read_for_hash": source.get("downloaded_file_bytes_read") is True,
        "accepted_sha256_read": source.get("real_archive_candidate_sha256_read") is True,
        "accepted_sha256_is_lower_hex": source.get("accepted_sha256_is_lower_hex") is True,
        "accepted_bytes_read_count": source.get("accepted_bytes_read_count"),
        "real_archive_candidate_path_hash_allowed": source.get("real_archive_candidate_path_hash_allowed") is True,
        "real_archive_candidate_path_hash_performed": source.get("real_archive_candidate_path_hash_performed") is True,
        "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read") is True,
        "downloaded_file_hash_performed": source.get("downloaded_file_hash_performed") is True,
        "real_archive_candidate_sha256_read": source.get("real_archive_candidate_sha256_read") is True,
        "real_archive_candidate_sha256": source.get("real_archive_candidate_sha256"),
        "no_archive_open_permission_added_by_l24_9": True,
        "no_browser_permission_added_by_l24_9": True,
        "no_pasteback_or_package_run_permission_added_by_l24_9": True,
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
        "next_patch": POST_L24_NEXT,
        "notes": [
            "L24.9 finalizes only controlled runtime candidate metadata/stat and SHA-256 work.",
            "Archive open/list/extract/read, manifest payload read, browser, pasteback, send/submit, and package-run remain separate future streams.",
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
        f"Final Marker                  : {payload.get('final_metadata_hash_acceptance_marker')}",
        f"L24 Complete                  : {payload.get('l24_metadata_hash_stream_complete')}",
        f"Accepted Hash Scope           : {payload.get('accepted_hash_scope')}",
        f"Hash Performed                : {payload.get('real_archive_candidate_path_hash_performed')}",
        f"Archive Open Permission       : {payload.get('l24_archive_open_permission_granted')}",
        f"Browser Permission            : {payload.get('l24_browser_permission_granted')}",
        f"Package Run Permission        : {payload.get('l24_package_run_permission_granted')}",
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
    payload = build_metadata_hash_final_acceptance_marker(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
