"""L25.4 archive listing authorization gate.

This follows accepted L25.3. It reads back the controlled archive open/close
broad checkpoint and grants only future authorization for an archive listing
proof. It does not list members, read member names, read member count, extract
members, read member bytes, read a manifest payload, start a browser, paste,
send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_open_broad_checkpoint as l25_03

PATCH = "L25.4"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.4 Microsoft Edge controlled runtime archive listing authorization gate"
SOURCE_PATCH = "L25.3"
NEXT_PATCH = "L25.5 Microsoft Edge controlled runtime archive listing first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_LISTING_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_LISTING_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
    "archive_listing_authorization_executes_listing",
    "real_archive_candidate_listing_allowed",
    "real_archive_candidate_listed",
    "real_archive_candidate_member_count_read",
    "real_archive_candidate_member_names_read",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
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


def _l25_03_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_03.build_archive_open_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.3 archive-open broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_archive_listing_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_listing_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l25_03_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_LISTING_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_listing_authorization or token_present)
    future_authorized = bool(allow_archive_listing_authorization and token_valid)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_03_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_03_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_03_archive_open_ladder_complete", "ok": source.get("l25_archive_open_ladder_complete") is True},
        {"name": "source_l25_03_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l25_03_archive_opened_and_closed", "ok": source.get("real_archive_candidate_opened") is True and source.get("archive_open_closed") is True},
        {"name": "source_l25_03_no_listing_member_manifest", "ok": source.get("real_archive_candidate_listed") is False and source.get("real_archive_candidate_member_count_read") is False and source.get("real_archive_candidate_member_names_read") is False and source.get("archive_member_bytes_read") is False and source.get("manifest_payload_read") is False},
        {"name": "source_l25_03_no_extract_browser_package", "ok": source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "listing_authorization_is_readback_only", "ok": True},
        {"name": "listing_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_03_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "archive_open_ladder_complete": source.get("l25_archive_open_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "accepted_archive_open_scope": source.get("accepted_archive_open_scope"),
            "archive_open_allowed": source.get("real_archive_candidate_open_allowed"),
            "archive_opened": source.get("real_archive_candidate_opened"),
            "real_archive_opened": source.get("real_archive_opened"),
            "archive_open_closed": source.get("archive_open_closed"),
            "archive_listed": source.get("real_archive_candidate_listed"),
            "archive_member_count_read": source.get("real_archive_candidate_member_count_read"),
            "archive_member_names_read": source.get("real_archive_candidate_member_names_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_listing_authorization_gate": True,
        "archive_listing_authorization_readback_only": True,
        "archive_listing_authorization_requested": requested,
        "archive_listing_authorization_token_present": token_present,
        "archive_listing_authorization_token_valid": token_valid,
        "archive_listing_authorization_granted_for_future_patch": future_authorized,
        "future_archive_listing_requires_explicit_flag_and_token": True,
        "future_archive_listing_must_be_separately_gated_in_l25_5": True,
        "no_archive_listing_execution_added_by_l25_4": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_4": True,
        "no_archive_extraction_added_by_l25_4": True,
        "no_browser_permission_added_by_l25_4": True,
        "no_pasteback_or_package_run_permission_added_by_l25_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only archive listing authorization; no listing/member names/member count/member bytes/extraction/manifest payload/browser/pasteback/package-run",
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
        f"Future Listing Authorized     : {payload.get('archive_listing_authorization_granted_for_future_patch')}",
        f"Archive Listed                : {payload.get('real_archive_candidate_listed')}",
        f"Member Count Read             : {payload.get('real_archive_candidate_member_count_read')}",
        f"Member Names Read             : {payload.get('real_archive_candidate_member_names_read')}",
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
    parser.add_argument("--allow-archive-listing-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_listing_authorization_gate(
        args.repo_root,
        allow_archive_listing_authorization=args.allow_archive_listing_authorization,
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
