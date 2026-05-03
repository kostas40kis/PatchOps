"""L25.1 archive-open authorization gate.

This starts a separate post-L24 stream. It reads back the accepted L24.9
metadata/hash final marker and grants only future authorization for an archive
open proof. It does not load archive-handling modules, open/list/extract/read an
archive, read a manifest payload, start a browser, paste, send, or run packages.

L25.1a repairs validator import scanning so prose cannot be mistaken for an
executable archive import.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_metadata_hash_final_acceptance_marker as l24_final

PATCH = "L25.1"
REPAIR_PATCH = "L25.1a"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.1 Microsoft Edge real downloaded-archive archive-open authorization gate"
SOURCE_PATCH = "L24.9"
NEXT_PATCH = "L25.2 Microsoft Edge controlled runtime archive-open first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_OPEN_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_OPEN_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
    "archive_open_authorization_executes_archive_open",
    "real_archive_candidate_open_allowed",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_candidate_member_count_read",
    "real_archive_candidate_member_names_read",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "archive_member_bytes_read",
    "archive_member_payload_read",
    "manifest_payload_read",
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


def _l24_final_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_final.build_metadata_hash_final_acceptance_marker(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.9 final marker readback failed: {type(exc).__name__}: {exc}"}


def build_archive_open_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_open_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l24_final_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_OPEN_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_open_authorization or token_present)
    future_authorized = bool(allow_archive_open_authorization and token_valid)

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_09_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_09_final_marker", "ok": source.get("final_metadata_hash_acceptance_marker") is True},
        {"name": "source_l24_09_metadata_hash_complete", "ok": source.get("l24_metadata_hash_stream_complete") is True},
        {"name": "source_l24_09_no_archive_open_permission", "ok": source.get("l24_archive_open_permission_granted") is False},
        {"name": "source_l24_09_no_archive_read_manifest_browser_package", "ok": source.get("l24_archive_member_read_permission_granted") is False and source.get("l24_manifest_payload_read_permission_granted") is False and source.get("l24_browser_permission_granted") is False and source.get("l24_package_run_permission_granted") is False},
        {"name": "archive_open_authorization_is_readback_only", "ok": True},
        {"name": "archive_open_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_09_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "final_metadata_hash_acceptance_marker": source.get("final_metadata_hash_acceptance_marker"),
            "l24_metadata_hash_complete": source.get("l24_metadata_hash_stream_complete"),
            "accepted_hash_scope": source.get("accepted_hash_scope"),
            "hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "bytes_read_for_hash": source.get("downloaded_file_bytes_read"),
            "sha256_read": source.get("real_archive_candidate_sha256_read"),
            "archive_open_permission": source.get("l24_archive_open_permission_granted"),
            "archive_listing_permission": source.get("l24_archive_listing_permission_granted"),
            "archive_extraction_permission": source.get("l24_archive_extraction_permission_granted"),
            "archive_member_read_permission": source.get("l24_archive_member_read_permission_granted"),
            "manifest_payload_read_permission": source.get("l24_manifest_payload_read_permission_granted"),
            "browser_permission": source.get("l24_browser_permission_granted"),
            "pasteback_permission": source.get("l24_pasteback_permission_granted"),
            "package_run_permission": source.get("l24_package_run_permission_granted"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "candidate_archive_listed": source.get("real_archive_candidate_listed"),
            "candidate_archive_extracted": source.get("real_archive_candidate_extracted"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_open_authorization_gate": True,
        "archive_open_authorization_readback_only": True,
        "archive_open_authorization_requested": requested,
        "archive_open_authorization_token_present": token_present,
        "archive_open_authorization_token_valid": token_valid,
        "archive_open_authorization_granted_for_future_patch": future_authorized,
        "future_archive_open_requires_explicit_flag_and_token": True,
        "future_archive_open_must_be_separately_gated_in_l25_2": True,
        "no_archive_open_execution_added_by_l25_1": True,
        "no_archive_listing_or_extraction_added_by_l25_1": True,
        "no_manifest_payload_read_added_by_l25_1": True,
        "no_browser_permission_added_by_l25_1": True,
        "no_pasteback_or_package_run_permission_added_by_l25_1": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only archive-open authorization; no archive open/list/extract/read, no manifest payload read, no browser, no pasteback, no package-run",
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
        f"Repair Patch                  : {payload.get('repair_patch')}",
        f"Status                        : {payload.get('status')}",
        f"Future Archive Open Authorized: {payload.get('archive_open_authorization_granted_for_future_patch')}",
        f"Archive Opened                : {payload.get('real_archive_candidate_opened')}",
        f"Archive Listed                : {payload.get('real_archive_candidate_listed')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Manifest Payload Read         : {payload.get('manifest_payload_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-archive-open-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_open_authorization_gate(
        args.repo_root,
        allow_archive_open_authorization=args.allow_archive_open_authorization,
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
