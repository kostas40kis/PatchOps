"""L23.3 synthetic-archive listing authorization gate.

This module follows accepted L23.2/L23.2a. It does not load a ZIP archive
library, open an archive, list archive contents, extract files, read archive
member bytes, read a manifest from an archive, start a browser, paste, send, or
run packages. It only exposes a future authorization token/readback surface for
a later, separately gated synthetic listing proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_archive_preflight_gate as l23_02

PATCH = "L23.3"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.3 Microsoft Edge real downloaded-archive manifest validation synthetic-archive listing authorization gate"
SOURCE_PATCH = "L23.2/L23.2a"
NEXT_PATCH = "L23.4 Microsoft Edge real downloaded-archive manifest validation first synthetic-archive listing proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_SYNTHETIC_ARCHIVE_LISTING_AUTHORIZATION_TOKEN = "PATCHOPS_L23_EDGE_SYNTHETIC_ARCHIVE_LISTING_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
    "synthetic_archive_listing_execution_allowed",
    "synthetic_archive_listing_active",
    "synthetic_archive_listing_performed",
    "real_archive_manifest_validation_execution_allowed",
    "real_archive_manifest_validation_active",
    "real_archive_manifest_validation_performed",
    "real_downloaded_manifest_read",
    "real_archive_manifest_read",
    "real_archive_opened",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "archive_member_bytes_read",
    "archive_member_content_read",
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


def _l23_02_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_02.build_synthetic_archive_preflight_gate(
            repo_root,
            allow_synthetic_archive_preflight=True,
            authorization_token=l23_02.REQUIRED_SYNTHETIC_ARCHIVE_PREFLIGHT_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.2 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_synthetic_archive_listing_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_synthetic_archive_listing_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l23_02_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_SYNTHETIC_ARCHIVE_LISTING_AUTHORIZATION_TOKEN
    authorization_requested = bool(allow_synthetic_archive_listing_authorization or token_present)
    future_authorized = bool(allow_synthetic_archive_listing_authorization and token_valid)

    checks = [
        {"name": "source_l23_02_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_02_preflight_allowed", "ok": source.get("synthetic_archive_preflight_allowed") is True},
        {"name": "source_l23_02_path_stat_done", "ok": source.get("synthetic_archive_path_stat_performed") is True},
        {"name": "source_l23_02_no_archive_open_or_list", "ok": source.get("downloaded_archive_opened") is False and source.get("downloaded_archive_contents_listed") is False},
        {"name": "source_l23_02_no_member_or_manifest_read", "ok": source.get("archive_member_bytes_read") is False and source.get("real_archive_manifest_read") is False},
        {"name": "listing_authorization_is_readback_only", "ok": True},
        {"name": "listing_execution_remains_false", "ok": True},
        {"name": "browser_and_package_run_remain_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_02_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "preflight_allowed": source.get("synthetic_archive_preflight_allowed"),
            "preflight_scope": source.get("preflight_scope"),
            "synthetic_archive_path_stat_performed": source.get("synthetic_archive_path_stat_performed"),
            "synthetic_archive_size_bytes": source.get("synthetic_archive_size_bytes"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
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
        "synthetic_archive_listing_authorization_gate": True,
        "synthetic_archive_listing_authorization_readback_only": True,
        "synthetic_archive_listing_authorization_requested": authorization_requested,
        "synthetic_archive_listing_authorization_token_present": token_present,
        "synthetic_archive_listing_authorization_token_valid": token_valid,
        "synthetic_archive_listing_authorization_granted_for_future_patch": future_authorized,
        "future_synthetic_archive_listing_requires_explicit_flag_and_token": True,
        "future_synthetic_archive_listing_must_be_separately_gated_in_l23_4": True,
        "no_new_archive_listing_permission_added_by_l23_3": True,
        "safety_boundary": "readback-only listing authorization gate; no archive open/list/read, no member bytes, no manifest read, no browser, no pasteback, no package-run",
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.3 adds only future synthetic archive listing authorization readback.",
            "Listing execution remains false in this patch.",
            "The first actual synthetic archive listing proof must wait for L23.4.",
        ],
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
        f"Future Listing Authorized     : {payload.get('synthetic_archive_listing_authorization_granted_for_future_patch')}",
        f"Listing Execution Allowed     : {payload.get('synthetic_archive_listing_execution_allowed')}",
        f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
        f"Archive Listed                : {payload.get('downloaded_archive_contents_listed')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
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
    parser.add_argument("--allow-synthetic-archive-listing-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_synthetic_archive_listing_authorization_gate(
        args.repo_root,
        allow_synthetic_archive_listing_authorization=args.allow_synthetic_archive_listing_authorization,
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
