"""L24.1 real downloaded-archive candidate authorization gate.

This starts a new separately gated post-L23 stream. It proves only that L23 ended
as a synthetic-only stream, then exposes a future real downloaded-archive
candidate authorization token. It does not stat, hash, open, list, extract, or
read a real candidate path, and it does not start a browser, paste, send, or run
packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_final_synthetic_acceptance_marker as l23_final

PATCH = "L24.1"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.1 Microsoft Edge real downloaded-archive candidate authorization gate"
SOURCE_PATCH = "L23.9"
NEXT_PATCH = "L24.2 Microsoft Edge real downloaded-archive candidate path string preflight gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_REAL_ARCHIVE_CANDIDATE_AUTHORIZATION_TOKEN = "PATCHOPS_L24_EDGE_REAL_DOWNLOADED_ARCHIVE_CANDIDATE_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
    "real_archive_candidate_path_stat_allowed",
    "real_archive_candidate_path_stat_performed",
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_exists",
    "real_archive_candidate_size_bytes_read",
    "real_archive_candidate_suffix_checked_on_filesystem",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
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


def _l23_final_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_final.build_final_synthetic_acceptance_marker(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.9 final readback failed: {type(exc).__name__}: {exc}"}


def build_real_archive_candidate_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_real_archive_candidate_authorization: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l23_final_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_ARCHIVE_CANDIDATE_AUTHORIZATION_TOKEN
    authorization_requested = bool(allow_real_archive_candidate_authorization or token_present)
    future_authorized = bool(allow_real_archive_candidate_authorization and token_valid)

    checks = [
        {"name": "source_l23_09_final_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_09_final_marker", "ok": source.get("final_synthetic_acceptance_marker") is True},
        {"name": "source_l23_09_synthetic_complete", "ok": source.get("l23_synthetic_manifest_validation_stream_complete") is True},
        {"name": "source_l23_09_no_real_archive_permission", "ok": source.get("l23_real_downloaded_archive_permission_granted") is False},
        {"name": "source_l23_09_no_browser_or_package_permission", "ok": source.get("no_browser_permission_added_by_l23_9") is True and source.get("no_pasteback_or_package_run_permission_added_by_l23_9") is True},
        {"name": "candidate_authorization_is_readback_only", "ok": True},
        {"name": "candidate_path_filesystem_touch_remains_false", "ok": True},
        {"name": "real_archive_browser_package_remain_false", "ok": True},
    ]
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_09_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "final_synthetic_acceptance_marker": source.get("final_synthetic_acceptance_marker"),
            "l23_synthetic_complete": source.get("l23_synthetic_manifest_validation_stream_complete"),
            "real_downloaded_archive_permission_granted": source.get("l23_real_downloaded_archive_permission_granted"),
            "accepted_scope": source.get("accepted_synthetic_payload_scope"),
            "accepted_manifest_member_name": source.get("accepted_manifest_member_name"),
            "non_manifest_member_bytes_read": source.get("non_manifest_member_bytes_read"),
            "archive_extracted": source.get("archive_extracted"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "real_archive_candidate_authorization_gate": True,
        "real_archive_candidate_authorization_readback_only": True,
        "real_archive_candidate_authorization_requested": authorization_requested,
        "real_archive_candidate_authorization_token_present": token_present,
        "real_archive_candidate_authorization_token_valid": token_valid,
        "real_archive_candidate_authorization_granted_for_future_patch": future_authorized,
        "candidate_archive_path_recorded_as_string_only": candidate_archive_path is not None,
        "candidate_archive_path": candidate_archive_path,
        "future_real_archive_candidate_path_preflight_requires_explicit_flag_and_token": True,
        "future_real_archive_candidate_path_preflight_must_be_separately_gated_in_l24_2": True,
        "no_real_archive_candidate_filesystem_permission_added_by_l24_1": True,
        "no_browser_permission_added_by_l24_1": True,
        "no_pasteback_or_package_run_permission_added_by_l24_1": True,
        "safety_boundary": "readback-only real archive candidate authorization gate; no stat/hash/open/list/extract/read, no browser, no pasteback, no package-run",
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
        f"Future Candidate Authorized   : {payload.get('real_archive_candidate_authorization_granted_for_future_patch')}",
        f"Candidate Path Recorded       : {payload.get('candidate_archive_path_recorded_as_string_only')}",
        f"Candidate Path Stat           : {payload.get('real_archive_candidate_path_stat_performed')}",
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
    parser.add_argument("--allow-real-archive-candidate-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_candidate_authorization_gate(
        args.repo_root,
        allow_real_archive_candidate_authorization=args.allow_real_archive_candidate_authorization,
        authorization_token=args.authorization_token,
        candidate_archive_path=args.candidate_archive_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
