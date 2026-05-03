"""L25.5 first controlled archive-listing proof.

This follows accepted L25.4. It opens a controlled runtime ZIP fixture and lists
only member names/count after explicit token authorization. It does not extract
members, read member bytes, read manifest payloads, start a browser, paste,
send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_listing_authorization_gate as l25_04
from patchops.llm_browser import live_adapter_edge_real_archive_open_first_controlled_proof as open_proof

PATCH = "L25.5"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.5 Microsoft Edge controlled runtime archive listing first proof"
SOURCE_PATCH = "L25.4"
NEXT_PATCH = "L25.6 Microsoft Edge controlled runtime archive listing broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = open_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_LISTING_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_LISTING_FIRST_CONTROLLED_PROOF_AUTHORIZED"
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


def _l25_04_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_04.build_archive_listing_authorization_gate(
            repo_root,
            allow_archive_listing_authorization=True,
            authorization_token=l25_04.REQUIRED_ARCHIVE_LISTING_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.4 archive-listing authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_04_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_04_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_04_future_listing_authorized", "ok": source.get("archive_listing_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_04_listing_execution_false", "ok": source.get("real_archive_candidate_listed") is False},
        {"name": "default_listing_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_04_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_listing_authorized": source.get("archive_listing_authorization_granted_for_future_patch"),
            "listing_allowed": source.get("real_archive_candidate_listing_allowed"),
            "archive_listed": source.get("real_archive_candidate_listed"),
            "archive_member_count_read": source.get("real_archive_candidate_member_count_read"),
            "archive_member_names_read": source.get("real_archive_candidate_member_names_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_listing_proof_requested": False,
        "archive_listing_proof_token_present": False,
        "archive_listing_proof_token_valid": False,
        "real_archive_candidate_listing_allowed": False,
        "real_archive_candidate_listed": False,
        "real_archive_candidate_member_count_read": False,
        "real_archive_candidate_member_count": None,
        "real_archive_candidate_member_names_read": False,
        "real_archive_candidate_member_names": [],
        "archive_listing_scope": "default_readback_only_no_listing",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_5": True,
        "no_archive_extraction_added_by_l25_5": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_5": True,
        "no_browser_permission_added_by_l25_5": True,
        "no_pasteback_or_package_run_permission_added_by_l25_5": True,
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


def build_archive_listing_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_listing_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_listing_proof:
        return _default_payload(root, target_url)

    source = _l25_04_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_LISTING_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_04_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_04_future_listing_authorized", "ok": source.get("archive_listing_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_04_listing_execution_false", "ok": source.get("real_archive_candidate_listed") is False},
        {"name": "source_l25_04_no_extract_member_manifest_browser_package", "ok": source.get("real_archive_candidate_extracted") is False and source.get("archive_member_bytes_read") is False and source.get("manifest_payload_read") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "archive_listing_proof_token_present", "ok": token_present},
        {"name": "archive_listing_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_listing", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_listing", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
    ]

    listing_allowed = bool(all(check.get("ok") for check in checks))
    listed = False
    names: list[str] = []
    listing_error: str | None = None
    if listing_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                names = sorted(archive.namelist())
                listed = True
            checks.extend([
                {"name": "archive_listing_succeeded", "ok": listed is True},
                {"name": "archive_member_count_matches_expected", "ok": len(names) == len(EXPECTED_CONTROLLED_MEMBER_NAMES)},
                {"name": "archive_member_names_match_expected", "ok": tuple(names) == EXPECTED_CONTROLLED_MEMBER_NAMES},
            ])
        except Exception as exc:
            listing_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "archive_listing_attempt", "ok": False, "error": listing_error})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_04_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_listing_authorized": source.get("archive_listing_authorization_granted_for_future_patch"),
            "listing_allowed": source.get("real_archive_candidate_listing_allowed"),
            "archive_listed": source.get("real_archive_candidate_listed"),
            "archive_member_count_read": source.get("real_archive_candidate_member_count_read"),
            "archive_member_names_read": source.get("real_archive_candidate_member_names_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_listing_proof_requested": True,
        "archive_listing_proof_token_present": token_present,
        "archive_listing_proof_token_valid": token_valid,
        "real_archive_candidate_listing_allowed": listing_allowed,
        "real_archive_candidate_listed": listed,
        "real_archive_candidate_member_count_read": listed,
        "real_archive_candidate_member_count": len(names) if listed else None,
        "real_archive_candidate_member_names_read": listed,
        "real_archive_candidate_member_names": names,
        "archive_listing_error": listing_error,
        "archive_listing_scope": "controlled_runtime_zip_member_names_and_count_only_no_member_bytes",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_5": True,
        "no_archive_extraction_added_by_l25_5": True,
        "no_archive_member_or_manifest_payload_read_added_by_l25_5": True,
        "no_browser_permission_added_by_l25_5": True,
        "no_pasteback_or_package_run_permission_added_by_l25_5": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.5 lists only member names/count from the controlled runtime ZIP fixture.",
            "No extraction, member bytes, manifest payload, browser, pasteback, send/submit, or package-run activity is performed.",
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
        f"Archive Listed                : {payload.get('real_archive_candidate_listed')}",
        f"Member Count Read             : {payload.get('real_archive_candidate_member_count_read')}",
        f"Member Names Read             : {payload.get('real_archive_candidate_member_names_read')}",
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
    parser.add_argument("--allow-archive-listing-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_listing_first_controlled_proof(
        args.repo_root,
        allow_archive_listing_proof=args.allow_archive_listing_proof,
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
