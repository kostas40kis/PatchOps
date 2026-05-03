"""L24.5 broad checkpoint for controlled candidate filesystem stat.

This follows accepted L24.4. It replays the accepted controlled runtime candidate
filesystem metadata stat proof and summarizes the L24.1-L24.4 ladder. It does
not hash file contents, read file bytes, open/list/extract/read an archive, start
a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_proof as l24_04

PATCH = "L24.5"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.5 Microsoft Edge real downloaded-archive candidate filesystem stat broad checkpoint"
SOURCE_PATCH = "L24.4"
SOURCE_LADDER = (
    "L24.1 real downloaded-archive candidate authorization gate",
    "L24.2/L24.2a candidate path string-only preflight gate",
    "L24.3 candidate filesystem stat authorization gate",
    "L24.4 controlled runtime candidate filesystem stat proof",
)
NEXT_PATCH = "L24.6 Microsoft Edge real downloaded-archive candidate hash authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

ALWAYS_FALSE_FIELDS = (
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
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


def _l24_04_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_04.build_real_archive_candidate_filesystem_stat_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.4 default readback failed: {type(exc).__name__}: {exc}"}


def _l24_04_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l24_04.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l24_04.build_real_archive_candidate_filesystem_stat_proof(
            repo_root,
            allow_real_archive_candidate_stat_proof=True,
            authorization_token=l24_04.REQUIRED_REAL_ARCHIVE_CANDIDATE_STAT_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.4 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_real_archive_candidate_filesystem_stat_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l24_04_default_payload(root, target_url)
    authorized_payload = _l24_04_authorized_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_04_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l24_04_default_is_passive", "ok": default_payload.get("real_archive_candidate_path_stat_performed") is False},
        {"name": "source_l24_04_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l24_04_patch_marker", "ok": authorized_payload.get("patch") == "L24.4"},
        {"name": "source_l24_04_stat_allowed", "ok": authorized_payload.get("real_archive_candidate_path_stat_allowed") is True},
        {"name": "source_l24_04_stat_performed", "ok": authorized_payload.get("real_archive_candidate_path_stat_performed") is True},
        {"name": "source_l24_04_candidate_exists_and_file", "ok": authorized_payload.get("real_archive_candidate_exists") is True and authorized_payload.get("real_archive_candidate_is_file") is True},
        {"name": "source_l24_04_size_and_suffix_metadata", "ok": authorized_payload.get("real_archive_candidate_size_bytes_read") is True and isinstance(authorized_payload.get("real_archive_candidate_size_bytes"), int) and authorized_payload.get("real_archive_candidate_size_bytes") > 0 and authorized_payload.get("real_archive_candidate_suffix") == ".zip"},
        {"name": "source_l24_04_mtime_read", "ok": authorized_payload.get("real_archive_candidate_mtime_read") is True},
        {"name": "source_l24_04_scope_metadata_only", "ok": authorized_payload.get("candidate_stat_scope") == "controlled_runtime_candidate_filesystem_metadata_only"},
        {"name": "source_l24_04_no_hash_or_bytes", "ok": authorized_payload.get("real_archive_candidate_path_hash_performed") is False and authorized_payload.get("downloaded_file_bytes_read") is False},
        {"name": "source_l24_04_no_archive_open_list_extract", "ok": authorized_payload.get("real_archive_candidate_opened") is False and authorized_payload.get("real_archive_candidate_listed") is False and authorized_payload.get("real_archive_candidate_extracted") is False},
        {"name": "source_l24_04_no_manifest_browser_package", "ok": authorized_payload.get("real_archive_manifest_read") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "filesystem_stat_ladder_checkpoint": True,
        "l24_candidate_stat_ladder_complete": ok,
        "source_l24_04_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "stat_performed": default_payload.get("real_archive_candidate_path_stat_performed"),
            "stat_scope": default_payload.get("candidate_stat_scope"),
        },
        "source_l24_04_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l24_03_ok": authorized_payload.get("source_l24_03_summary", {}).get("ok"),
            "source_l24_03_future_authorized": authorized_payload.get("source_l24_03_summary", {}).get("future_stat_authorized"),
            "stat_allowed": authorized_payload.get("real_archive_candidate_path_stat_allowed"),
            "stat_performed": authorized_payload.get("real_archive_candidate_path_stat_performed"),
            "candidate_exists": authorized_payload.get("real_archive_candidate_exists"),
            "candidate_is_file": authorized_payload.get("real_archive_candidate_is_file"),
            "candidate_size_read": authorized_payload.get("real_archive_candidate_size_bytes_read"),
            "candidate_size_bytes": authorized_payload.get("real_archive_candidate_size_bytes"),
            "candidate_suffix_checked": authorized_payload.get("real_archive_candidate_suffix_checked_on_filesystem"),
            "candidate_suffix": authorized_payload.get("real_archive_candidate_suffix"),
            "candidate_mtime_read": authorized_payload.get("real_archive_candidate_mtime_read"),
            "stat_scope": authorized_payload.get("candidate_stat_scope"),
            "hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed"),
            "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
            "candidate_archive_opened": authorized_payload.get("real_archive_candidate_opened"),
            "candidate_archive_listed": authorized_payload.get("real_archive_candidate_listed"),
            "candidate_archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_stat_scope": "controlled_runtime_candidate_filesystem_metadata_only",
        "accepted_candidate_exists": authorized_payload.get("real_archive_candidate_exists") is True,
        "accepted_candidate_is_file": authorized_payload.get("real_archive_candidate_is_file") is True,
        "accepted_candidate_size_bytes_read": authorized_payload.get("real_archive_candidate_size_bytes_read") is True,
        "accepted_candidate_size_bytes": authorized_payload.get("real_archive_candidate_size_bytes"),
        "accepted_candidate_suffix": authorized_payload.get("real_archive_candidate_suffix"),
        "accepted_candidate_mtime_read": authorized_payload.get("real_archive_candidate_mtime_read") is True,
        "real_archive_candidate_path_stat_allowed": authorized_payload.get("real_archive_candidate_path_stat_allowed") is True,
        "real_archive_candidate_path_stat_performed": authorized_payload.get("real_archive_candidate_path_stat_performed") is True,
        "real_archive_candidate_exists": authorized_payload.get("real_archive_candidate_exists") is True,
        "real_archive_candidate_is_file": authorized_payload.get("real_archive_candidate_is_file") is True,
        "real_archive_candidate_size_bytes_read": authorized_payload.get("real_archive_candidate_size_bytes_read") is True,
        "real_archive_candidate_suffix_checked_on_filesystem": authorized_payload.get("real_archive_candidate_suffix_checked_on_filesystem") is True,
        "real_archive_candidate_mtime_read": authorized_payload.get("real_archive_candidate_mtime_read") is True,
        "no_hash_or_archive_open_permission_added_by_l24_5": True,
        "no_browser_permission_added_by_l24_5": True,
        "no_pasteback_or_package_run_permission_added_by_l24_5": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L24.5 is a broad checkpoint over accepted L24.1-L24.4 controlled candidate stat work.",
            "Only filesystem metadata stat is accepted; no hash, file byte read, archive open/list/extract/read, browser, pasteback, send/submit, or package-run permission is added.",
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
        f"Ladder Complete               : {payload.get('l24_candidate_stat_ladder_complete')}",
        f"Accepted Scope                : {payload.get('accepted_stat_scope')}",
        f"Stat Performed                : {payload.get('real_archive_candidate_path_stat_performed')}",
        f"Candidate Exists              : {payload.get('real_archive_candidate_exists')}",
        f"Hash Performed                : {payload.get('real_archive_candidate_path_hash_performed')}",
        f"Real Archive Opened           : {payload.get('real_archive_opened')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
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
    payload = build_real_archive_candidate_filesystem_stat_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
