"""L24.6 real downloaded-archive candidate hash authorization gate.

This follows accepted L24.5. It grants only future authorization/readback for a
later candidate hash proof. It does not hash file contents, read file bytes,
open/list/extract/read archives, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_broad_checkpoint as l24_05

PATCH = "L24.6"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.6 Microsoft Edge real downloaded-archive candidate hash authorization gate"
SOURCE_PATCH = "L24.5"
NEXT_PATCH = "L24.7 Microsoft Edge real downloaded-archive candidate first controlled hash proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_AUTHORIZATION_TOKEN = "PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_HASH_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_sha256_read",
    "real_archive_candidate_sha256",
    "downloaded_file_bytes_read",
    "downloaded_file_hash_performed",
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


def _l24_05_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_05.build_real_archive_candidate_filesystem_stat_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.5 stat broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_real_archive_candidate_hash_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_real_archive_candidate_hash_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l24_05_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_AUTHORIZATION_TOKEN
    requested = bool(allow_real_archive_candidate_hash_authorization or token_present)
    future_authorized = bool(allow_real_archive_candidate_hash_authorization and token_valid)

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_05_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_05_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l24_05_stat_ladder_complete", "ok": source.get("l24_candidate_stat_ladder_complete") is True},
        {"name": "source_l24_05_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l24_05_metadata_stat_accepted", "ok": source.get("real_archive_candidate_path_stat_performed") is True and source.get("accepted_stat_scope") == "controlled_runtime_candidate_filesystem_metadata_only"},
        {"name": "source_l24_05_no_hash_or_file_bytes", "ok": source.get("real_archive_candidate_path_hash_performed") is False and source.get("downloaded_file_bytes_read") is False},
        {"name": "source_l24_05_no_archive_browser_package", "ok": source.get("real_archive_candidate_opened") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "hash_authorization_is_readback_only", "ok": True},
        {"name": "hash_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_05_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "ladder_complete": source.get("l24_candidate_stat_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "accepted_stat_scope": source.get("accepted_stat_scope"),
            "stat_performed": source.get("real_archive_candidate_path_stat_performed"),
            "candidate_exists": source.get("real_archive_candidate_exists"),
            "candidate_is_file": source.get("real_archive_candidate_is_file"),
            "candidate_size_read": source.get("real_archive_candidate_size_bytes_read"),
            "candidate_suffix": source.get("accepted_candidate_suffix"),
            "candidate_mtime_read": source.get("accepted_candidate_mtime_read"),
            "hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "candidate_archive_listed": source.get("real_archive_candidate_listed"),
            "candidate_archive_extracted": source.get("real_archive_candidate_extracted"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "real_archive_candidate_hash_authorization_gate": True,
        "real_archive_candidate_hash_authorization_readback_only": True,
        "real_archive_candidate_hash_authorization_requested": requested,
        "real_archive_candidate_hash_authorization_token_present": token_present,
        "real_archive_candidate_hash_authorization_token_valid": token_valid,
        "real_archive_candidate_hash_authorization_granted_for_future_patch": future_authorized,
        "future_real_archive_candidate_hash_requires_explicit_flag_and_token": True,
        "future_real_archive_candidate_hash_must_be_separately_gated_in_l24_7": True,
        "no_real_archive_candidate_hash_execution_added_by_l24_6": True,
        "no_file_byte_read_permission_added_by_l24_6": True,
        "no_archive_open_permission_added_by_l24_6": True,
        "no_browser_permission_added_by_l24_6": True,
        "no_pasteback_or_package_run_permission_added_by_l24_6": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only hash authorization; no hash execution, no file-byte read, no archive open/list/extract/read, no browser, no pasteback, no package-run",
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Future Hash Authorized        : {payload.get('real_archive_candidate_hash_authorization_granted_for_future_patch')}",
        f"Hash Performed                : {payload.get('real_archive_candidate_path_hash_performed')}",
        f"Downloaded Bytes Read         : {payload.get('downloaded_file_bytes_read')}",
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
    parser.add_argument("--allow-real-archive-candidate-hash-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_candidate_hash_authorization_gate(
        args.repo_root,
        allow_real_archive_candidate_hash_authorization=args.allow_real_archive_candidate_hash_authorization,
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
