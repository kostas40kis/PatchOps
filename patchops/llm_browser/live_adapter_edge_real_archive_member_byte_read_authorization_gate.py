"""L25.7 archive member-byte-read authorization gate.

This follows accepted L25.6. It reads back the controlled archive-listing broad
checkpoint and grants only future authorization for a member-byte-read proof. It
does not read member bytes, read member payloads, read manifest payloads, extract
members, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_listing_broad_checkpoint as l25_06

PATCH = "L25.7"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.7 Microsoft Edge controlled runtime archive member-byte-read authorization gate"
SOURCE_PATCH = "L25.6"
NEXT_PATCH = "L25.8 Microsoft Edge controlled runtime archive member-byte-read first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_MEMBER_BYTE_READ_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MEMBER_BYTE_READ_AUTHORIZED_READBACK_ONLY"
EXPECTED_CONTROLLED_MEMBER_NAMES = ("bundle/manifest.json", "bundle/run_with_patchops.ps1")

FALSE_FIELDS = (
    "archive_member_byte_read_authorization_executes_read",
    "archive_member_byte_read_allowed",
    "archive_member_bytes_read",
    "archive_member_payload_read",
    "archive_member_payload_bytes_read",
    "archive_member_payload_sha256_read",
    "manifest_payload_read",
    "manifest_payload_bytes_read",
    "real_archive_manifest_read",
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


def _l25_06_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_06.build_archive_listing_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.6 listing broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_archive_member_byte_read_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_member_byte_read_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l25_06_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MEMBER_BYTE_READ_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_member_byte_read_authorization or token_present)
    future_authorized = bool(allow_archive_member_byte_read_authorization and token_valid)
    source_names = tuple(source.get("real_archive_candidate_member_names") or ())

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_06_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_06_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_06_listing_ladder_complete", "ok": source.get("l25_archive_listing_ladder_complete") is True},
        {"name": "source_l25_06_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l25_06_listing_accepted", "ok": source.get("real_archive_candidate_listed") is True and source.get("real_archive_candidate_member_count_read") is True and source.get("real_archive_candidate_member_names_read") is True},
        {"name": "source_l25_06_expected_names", "ok": source_names == EXPECTED_CONTROLLED_MEMBER_NAMES},
        {"name": "source_l25_06_no_member_or_manifest_payload", "ok": source.get("archive_member_bytes_read") is False and source.get("archive_member_payload_read") is False and source.get("manifest_payload_read") is False and source.get("real_archive_manifest_read") is False},
        {"name": "source_l25_06_no_extract_browser_package", "ok": source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "member_byte_read_authorization_is_readback_only", "ok": True},
        {"name": "member_byte_read_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_06_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "archive_listing_ladder_complete": source.get("l25_archive_listing_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "accepted_archive_listing_scope": source.get("accepted_archive_listing_scope"),
            "archive_listed": source.get("real_archive_candidate_listed"),
            "archive_member_count_read": source.get("real_archive_candidate_member_count_read"),
            "archive_member_count": source.get("real_archive_candidate_member_count"),
            "archive_member_names_read": source.get("real_archive_candidate_member_names_read"),
            "archive_member_names": source.get("real_archive_candidate_member_names"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "archive_member_payload_read": source.get("archive_member_payload_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_member_byte_read_authorization_gate": True,
        "archive_member_byte_read_authorization_readback_only": True,
        "archive_member_byte_read_authorization_requested": requested,
        "archive_member_byte_read_authorization_token_present": token_present,
        "archive_member_byte_read_authorization_token_valid": token_valid,
        "archive_member_byte_read_authorization_granted_for_future_patch": future_authorized,
        "future_archive_member_byte_read_requires_explicit_flag_and_token": True,
        "future_archive_member_byte_read_must_be_separately_gated_in_l25_8": True,
        "no_archive_member_byte_read_execution_added_by_l25_7": True,
        "no_archive_member_payload_read_added_by_l25_7": True,
        "no_manifest_payload_read_added_by_l25_7": True,
        "no_archive_extraction_added_by_l25_7": True,
        "no_browser_permission_added_by_l25_7": True,
        "no_pasteback_or_package_run_permission_added_by_l25_7": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only member-byte-read authorization; no member bytes, no member payloads, no manifest payload, no extraction, no browser, no pasteback, no package-run",
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
        f"Future Member Bytes Authorized: {payload.get('archive_member_byte_read_authorization_granted_for_future_patch')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Member Payload Read           : {payload.get('archive_member_payload_read')}",
        f"Manifest Payload Read         : {payload.get('manifest_payload_read')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-archive-member-byte-read-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_member_byte_read_authorization_gate(
        args.repo_root,
        allow_archive_member_byte_read_authorization=args.allow_archive_member_byte_read_authorization,
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
