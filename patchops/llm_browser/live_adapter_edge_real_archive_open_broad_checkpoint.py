"""L25.3 broad checkpoint for controlled archive-open proof.

This follows accepted L25.2. It replays the controlled empty ZIP open/close proof
and summarizes the L25.1a-L25.2 archive-open ladder. It does not list members,
extract members, read member names, read member bytes, read a manifest payload,
start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_open_first_controlled_proof as l25_02

PATCH = "L25.3"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.3 Microsoft Edge controlled runtime archive-open broad checkpoint"
SOURCE_PATCH = "L25.2"
SOURCE_LADDER = (
    "L25.1/L25.1a archive-open authorization gate",
    "L25.2 first controlled empty ZIP open/close proof",
)
NEXT_PATCH = "L25.4 Microsoft Edge controlled runtime archive listing authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

ALWAYS_FALSE_FIELDS = (
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_candidate_member_count_read",
    "real_archive_candidate_member_names_read",
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


def _l25_02_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_02.build_archive_open_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.2 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_02_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_02.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_02.build_archive_open_first_controlled_proof(
            repo_root,
            allow_archive_open_proof=True,
            authorization_token=l25_02.REQUIRED_ARCHIVE_OPEN_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.2 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_archive_open_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_02_default_payload(root, target_url)
    authorized_payload = _l25_02_authorized_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_02_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_02_default_is_passive", "ok": default_payload.get("real_archive_candidate_opened") is False},
        {"name": "source_l25_02_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_02_patch_marker", "ok": authorized_payload.get("patch") == "L25.2"},
        {"name": "source_l25_02_archive_open_allowed", "ok": authorized_payload.get("real_archive_candidate_open_allowed") is True},
        {"name": "source_l25_02_archive_opened", "ok": authorized_payload.get("real_archive_candidate_opened") is True and authorized_payload.get("real_archive_opened") is True},
        {"name": "source_l25_02_archive_closed", "ok": authorized_payload.get("archive_open_closed") is True},
        {"name": "source_l25_02_scope_open_close_only", "ok": authorized_payload.get("archive_open_scope") == "controlled_runtime_empty_zip_open_close_only_no_listing_no_member_read"},
        {"name": "source_l25_02_no_listing_or_member_names", "ok": authorized_payload.get("real_archive_candidate_listed") is False and authorized_payload.get("real_archive_candidate_member_names_read") is False and authorized_payload.get("real_archive_candidate_member_count_read") is False},
        {"name": "source_l25_02_no_extract_member_manifest", "ok": authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("archive_member_bytes_read") is False and authorized_payload.get("manifest_payload_read") is False and authorized_payload.get("real_archive_manifest_read") is False},
        {"name": "source_l25_02_no_browser_or_package", "ok": authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_open_ladder_checkpoint": True,
        "l25_archive_open_ladder_complete": ok,
        "source_l25_02_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "archive_opened": default_payload.get("real_archive_candidate_opened"),
            "archive_open_scope": default_payload.get("archive_open_scope"),
        },
        "source_l25_02_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_01_ok": authorized_payload.get("source_l25_01_summary", {}).get("ok"),
            "source_l25_01_repair_patch": authorized_payload.get("source_l25_01_summary", {}).get("repair_patch"),
            "source_l25_01_future_authorized": authorized_payload.get("source_l25_01_summary", {}).get("future_archive_open_authorized"),
            "archive_open_allowed": authorized_payload.get("real_archive_candidate_open_allowed"),
            "archive_opened": authorized_payload.get("real_archive_candidate_opened"),
            "real_archive_opened": authorized_payload.get("real_archive_opened"),
            "archive_open_closed": authorized_payload.get("archive_open_closed"),
            "archive_open_scope": authorized_payload.get("archive_open_scope"),
            "archive_listed": authorized_payload.get("real_archive_candidate_listed"),
            "archive_member_count_read": authorized_payload.get("real_archive_candidate_member_count_read"),
            "archive_member_names_read": authorized_payload.get("real_archive_candidate_member_names_read"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_archive_open_scope": "controlled_runtime_empty_zip_open_close_only_no_listing_no_member_read",
        "accepted_archive_open_allowed": authorized_payload.get("real_archive_candidate_open_allowed") is True,
        "accepted_archive_opened": authorized_payload.get("real_archive_candidate_opened") is True,
        "accepted_archive_closed": authorized_payload.get("archive_open_closed") is True,
        "real_archive_candidate_open_allowed": authorized_payload.get("real_archive_candidate_open_allowed") is True,
        "real_archive_candidate_opened": authorized_payload.get("real_archive_candidate_opened") is True,
        "real_archive_opened": authorized_payload.get("real_archive_opened") is True,
        "archive_open_closed": authorized_payload.get("archive_open_closed") is True,
        "archive_open_scope": authorized_payload.get("archive_open_scope"),
        "no_archive_listing_or_extraction_added_by_l25_3": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_3": True,
        "no_browser_permission_added_by_l25_3": True,
        "no_pasteback_or_package_run_permission_added_by_l25_3": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.3 is a broad checkpoint over accepted L25.1a-L25.2 archive-open work.",
            "Only controlled empty ZIP open/close is accepted; archive listing, member reads, extraction, manifest payload, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_open_ladder_complete')}",
        f"Archive Opened                : {payload.get('real_archive_candidate_opened')}",
        f"Archive Closed                : {payload.get('archive_open_closed')}",
        f"Archive Listed                : {payload.get('real_archive_candidate_listed')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_open_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
