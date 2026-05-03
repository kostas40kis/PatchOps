"""L25.6 broad checkpoint for controlled archive-listing proof.

This follows accepted L25.5. It replays the controlled ZIP member-name/member-count
listing proof and summarizes the L25.4-L25.5 listing ladder. It does not extract
members, read member bytes, read member payloads, read manifest payloads, start a
browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_listing_first_controlled_proof as l25_05

PATCH = "L25.6"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.6 Microsoft Edge controlled runtime archive listing broad checkpoint"
SOURCE_PATCH = "L25.5"
SOURCE_LADDER = (
    "L25.4 archive listing authorization gate",
    "L25.5 first controlled member-name/member-count listing proof",
)
NEXT_PATCH = "L25.7 Microsoft Edge controlled runtime archive member-byte-read authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
EXPECTED_CONTROLLED_MEMBER_NAMES = ("bundle/manifest.json", "bundle/run_with_patchops.ps1")

ALWAYS_FALSE_FIELDS = (
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


def _l25_05_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_05.build_archive_listing_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.5 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_05_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_05.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_05.build_archive_listing_first_controlled_proof(
            repo_root,
            allow_archive_listing_proof=True,
            authorization_token=l25_05.REQUIRED_ARCHIVE_LISTING_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.5 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_archive_listing_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_05_default_payload(root, target_url)
    authorized_payload = _l25_05_authorized_payload(root, target_url)
    names = authorized_payload.get("real_archive_candidate_member_names")

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_05_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_05_default_is_passive", "ok": default_payload.get("real_archive_candidate_listed") is False},
        {"name": "source_l25_05_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_05_patch_marker", "ok": authorized_payload.get("patch") == "L25.5"},
        {"name": "source_l25_05_listing_allowed", "ok": authorized_payload.get("real_archive_candidate_listing_allowed") is True},
        {"name": "source_l25_05_archive_listed", "ok": authorized_payload.get("real_archive_candidate_listed") is True},
        {"name": "source_l25_05_member_count_read", "ok": authorized_payload.get("real_archive_candidate_member_count_read") is True and authorized_payload.get("real_archive_candidate_member_count") == len(EXPECTED_CONTROLLED_MEMBER_NAMES)},
        {"name": "source_l25_05_member_names_read", "ok": authorized_payload.get("real_archive_candidate_member_names_read") is True and tuple(names or ()) == EXPECTED_CONTROLLED_MEMBER_NAMES},
        {"name": "source_l25_05_scope_names_count_only", "ok": authorized_payload.get("archive_listing_scope") == "controlled_runtime_zip_member_names_and_count_only_no_member_bytes"},
        {"name": "source_l25_05_no_extract_member_manifest", "ok": authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("archive_member_bytes_read") is False and authorized_payload.get("archive_member_payload_read") is False and authorized_payload.get("manifest_payload_read") is False and authorized_payload.get("real_archive_manifest_read") is False},
        {"name": "source_l25_05_no_browser_or_package", "ok": authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_listing_ladder_checkpoint": True,
        "l25_archive_listing_ladder_complete": ok,
        "source_l25_05_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "archive_listed": default_payload.get("real_archive_candidate_listed"),
            "archive_listing_scope": default_payload.get("archive_listing_scope"),
        },
        "source_l25_05_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_04_ok": authorized_payload.get("source_l25_04_summary", {}).get("ok"),
            "source_l25_04_future_authorized": authorized_payload.get("source_l25_04_summary", {}).get("future_listing_authorized"),
            "listing_allowed": authorized_payload.get("real_archive_candidate_listing_allowed"),
            "archive_listed": authorized_payload.get("real_archive_candidate_listed"),
            "archive_member_count_read": authorized_payload.get("real_archive_candidate_member_count_read"),
            "archive_member_count": authorized_payload.get("real_archive_candidate_member_count"),
            "archive_member_names_read": authorized_payload.get("real_archive_candidate_member_names_read"),
            "archive_member_names": authorized_payload.get("real_archive_candidate_member_names"),
            "archive_listing_scope": authorized_payload.get("archive_listing_scope"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
            "archive_member_payload_read": authorized_payload.get("archive_member_payload_read"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_archive_listing_scope": "controlled_runtime_zip_member_names_and_count_only_no_member_bytes",
        "accepted_listing_allowed": authorized_payload.get("real_archive_candidate_listing_allowed") is True,
        "accepted_archive_listed": authorized_payload.get("real_archive_candidate_listed") is True,
        "accepted_member_count_read": authorized_payload.get("real_archive_candidate_member_count_read") is True,
        "accepted_member_count": authorized_payload.get("real_archive_candidate_member_count"),
        "accepted_member_names_read": authorized_payload.get("real_archive_candidate_member_names_read") is True,
        "accepted_member_names": authorized_payload.get("real_archive_candidate_member_names"),
        "real_archive_candidate_listing_allowed": authorized_payload.get("real_archive_candidate_listing_allowed") is True,
        "real_archive_candidate_listed": authorized_payload.get("real_archive_candidate_listed") is True,
        "real_archive_candidate_member_count_read": authorized_payload.get("real_archive_candidate_member_count_read") is True,
        "real_archive_candidate_member_count": authorized_payload.get("real_archive_candidate_member_count"),
        "real_archive_candidate_member_names_read": authorized_payload.get("real_archive_candidate_member_names_read") is True,
        "real_archive_candidate_member_names": authorized_payload.get("real_archive_candidate_member_names"),
        "archive_listing_scope": authorized_payload.get("archive_listing_scope"),
        "no_archive_extraction_added_by_l25_6": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_6": True,
        "no_browser_permission_added_by_l25_6": True,
        "no_pasteback_or_package_run_permission_added_by_l25_6": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.6 is a broad checkpoint over accepted L25.4-L25.5 archive-listing work.",
            "Only controlled ZIP member names/count are accepted; extraction, member-byte reads, manifest payload reads, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_listing_ladder_complete')}",
        f"Archive Listed                : {payload.get('real_archive_candidate_listed')}",
        f"Member Count Read             : {payload.get('real_archive_candidate_member_count_read')}",
        f"Member Names Read             : {payload.get('real_archive_candidate_member_names_read')}",
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
    payload = build_archive_listing_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
