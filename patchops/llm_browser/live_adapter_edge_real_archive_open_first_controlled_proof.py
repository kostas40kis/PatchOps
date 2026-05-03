"""L25.2 first controlled archive-open proof.

This follows accepted L25.1a. It opens and closes only a controlled runtime empty
ZIP fixture after explicit token authorization. It does not list members, extract
members, read member names, read member bytes, read a manifest payload, start a
browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_open_authorization_gate as l25_01
from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_proof as stat_proof

PATCH = "L25.2"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.2 Microsoft Edge controlled runtime archive-open first proof"
SOURCE_PATCH = "L25.1a"
NEXT_PATCH = "L25.3 Microsoft Edge controlled runtime archive-open broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = stat_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_OPEN_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_OPEN_FIRST_CONTROLLED_PROOF_AUTHORIZED"

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


def _l25_01_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_01.build_archive_open_authorization_gate(
            repo_root,
            allow_archive_open_authorization=True,
            authorization_token=l25_01.REQUIRED_ARCHIVE_OPEN_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.1a archive-open authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_01_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_01_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_01_repair_marker", "ok": source.get("repair_patch") == "L25.1a"},
        {"name": "source_l25_01_future_archive_open_authorized", "ok": source.get("archive_open_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_01_archive_open_execution_false", "ok": source.get("real_archive_candidate_opened") is False},
        {"name": "default_archive_open_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_01_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "repair_patch": source.get("repair_patch"),
            "future_archive_open_authorized": source.get("archive_open_authorization_granted_for_future_patch"),
            "archive_opened": source.get("real_archive_candidate_opened"),
            "archive_listed": source.get("real_archive_candidate_listed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_open_proof_requested": False,
        "archive_open_proof_token_present": False,
        "archive_open_proof_token_valid": False,
        "real_archive_candidate_open_allowed": False,
        "real_archive_candidate_opened": False,
        "real_archive_opened": False,
        "archive_open_closed": False,
        "archive_open_mode": None,
        "archive_open_scope": "default_readback_only_no_archive_open",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_2": True,
        "no_archive_listing_or_extraction_added_by_l25_2": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_2": True,
        "no_browser_permission_added_by_l25_2": True,
        "no_pasteback_or_package_run_permission_added_by_l25_2": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def build_archive_open_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_open_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_open_proof:
        return _default_payload(root, target_url)

    source = _l25_01_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_OPEN_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_01_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_01_repair_marker", "ok": source.get("repair_patch") == "L25.1a"},
        {"name": "source_l25_01_future_archive_open_authorized", "ok": source.get("archive_open_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_01_archive_open_execution_false", "ok": source.get("real_archive_candidate_opened") is False},
        {"name": "source_l25_01_no_listing_extract_member_manifest_browser_package", "ok": source.get("real_archive_candidate_listed") is False and source.get("real_archive_candidate_extracted") is False and source.get("archive_member_bytes_read") is False and source.get("manifest_payload_read") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "archive_open_proof_token_present", "ok": token_present},
        {"name": "archive_open_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_archive_open", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_archive_open", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
    ]

    open_allowed = bool(all(check.get("ok") for check in checks))
    archive_opened = False
    archive_open_closed = False
    open_error: str | None = None
    if open_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                archive_opened = True
                archive_open_closed = False
            archive_open_closed = True
            checks.append({"name": "archive_open_succeeded", "ok": archive_opened is True})
            checks.append({"name": "archive_closed_after_open", "ok": archive_open_closed is True})
        except Exception as exc:
            open_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "archive_open_attempt", "ok": False, "error": open_error})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_01_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "repair_patch": source.get("repair_patch"),
            "future_archive_open_authorized": source.get("archive_open_authorization_granted_for_future_patch"),
            "archive_opened": source.get("real_archive_candidate_opened"),
            "archive_listed": source.get("real_archive_candidate_listed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_open_proof_requested": True,
        "archive_open_proof_token_present": token_present,
        "archive_open_proof_token_valid": token_valid,
        "real_archive_candidate_open_allowed": open_allowed,
        "real_archive_candidate_opened": archive_opened,
        "real_archive_opened": archive_opened,
        "archive_open_closed": archive_open_closed,
        "archive_open_error": open_error,
        "archive_open_mode": "read_only_open_close",
        "archive_open_scope": "controlled_runtime_empty_zip_open_close_only_no_listing_no_member_read",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_2": True,
        "no_archive_listing_or_extraction_added_by_l25_2": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_2": True,
        "no_browser_permission_added_by_l25_2": True,
        "no_pasteback_or_package_run_permission_added_by_l25_2": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.2 opens and closes only the controlled runtime empty ZIP fixture.",
            "No archive listing, extraction, member names, member bytes, manifest payload, browser, pasteback, send/submit, or package-run activity is performed.",
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
        f"Archive Opened                : {payload.get('real_archive_candidate_opened')}",
        f"Archive Closed                : {payload.get('archive_open_closed')}",
        f"Archive Listed                : {payload.get('real_archive_candidate_listed')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
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
    parser.add_argument("--allow-archive-open-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_open_first_controlled_proof(
        args.repo_root,
        allow_archive_open_proof=args.allow_archive_open_proof,
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
