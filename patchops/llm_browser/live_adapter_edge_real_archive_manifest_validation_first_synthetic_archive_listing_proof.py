"""L23.4 first synthetic-archive listing proof.

This module follows accepted L23.3. It performs only a metadata listing of the
fixed synthetic archive fixture. It does not extract files, read member payloads,
read a manifest from an archive, touch real downloaded artifacts, start a
browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_synthetic_archive_listing_authorization_gate as l23_03

PATCH = "L23.4"
REPAIR_PATCH = "L23.4a"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.4 Microsoft Edge real downloaded-archive manifest validation first synthetic-archive listing proof"
SOURCE_PATCH = "L23.3"
NEXT_PATCH = "L23.5 Microsoft Edge real downloaded-archive manifest validation synthetic manifest-name proof gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l23_04_synthetic_archive_listing_fixture/patch_l23_04_synthetic_archive.zip"
REQUIRED_SYNTHETIC_ARCHIVE_LISTING_PROOF_TOKEN = "PATCHOPS_L23_EDGE_FIRST_SYNTHETIC_ARCHIVE_LISTING_PROOF_AUTHORIZED"
EXPECTED_SYNTHETIC_MEMBERS = ("manifest.json", "README.txt")

ALWAYS_FALSE_FIELDS = (
    "archive_member_bytes_read",
    "archive_member_content_read",
    "archive_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "manifest_member_bytes_read",
    "manifest_member_payload_read",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
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


def _l23_03_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_03.build_synthetic_archive_listing_authorization_gate(
            repo_root,
            allow_synthetic_archive_listing_authorization=True,
            authorization_token=l23_03.REQUIRED_SYNTHETIC_ARCHIVE_LISTING_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.3 authorized readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l23_03_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l23_03_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_03_future_listing_authorized", "ok": source.get("synthetic_archive_listing_authorization_granted_for_future_patch") is True},
        {"name": "source_l23_03_listing_execution_false", "ok": source.get("synthetic_archive_listing_execution_allowed") is False},
        {"name": "default_listing_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_03_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_listing_authorized": source.get("synthetic_archive_listing_authorization_granted_for_future_patch"),
            "listing_execution_allowed": source.get("synthetic_archive_listing_execution_allowed"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_archive_listing_proof_requested": False,
        "synthetic_archive_listing_proof_token_present": False,
        "synthetic_archive_listing_proof_token_valid": False,
        "synthetic_archive_listing_execution_allowed": False,
        "synthetic_archive_listing_active": False,
        "synthetic_archive_listing_performed": False,
        "synthetic_archive_fixture_only": True,
        "synthetic_archive_fixture_relative_path": DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
        "synthetic_archive_opened": False,
        "synthetic_archive_contents_listed": False,
        "synthetic_archive_member_names": [],
        "synthetic_archive_member_count": 0,
        "manifest_member_name_seen": False,
        "listing_scope": "default_readback_only_no_archive_open",
        "no_real_archive_permission_added_by_l23_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "next_patch": NEXT_PATCH,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    payload["downloaded_archive_opened"] = False
    payload["downloaded_archive_contents_listed"] = False
    return payload


def _list_synthetic_archive_names(path: Path) -> list[str]:
    zip_module = importlib.import_module("zipfile")
    with zip_module.ZipFile(path, "r") as archive:
        # Metadata-only listing from the central directory. No member payload is read.
        return list(archive.namelist())


def build_first_synthetic_archive_listing_proof(
    repo_root: str | Path | None = None,
    *,
    allow_synthetic_archive_listing_proof: bool = False,
    authorization_token: str | None = None,
    synthetic_archive_relative_path: str = DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    if not allow_synthetic_archive_listing_proof:
        return _default_payload(root, target_url)

    source = _l23_03_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_SYNTHETIC_ARCHIVE_LISTING_PROOF_TOKEN
    rel_is_fixed = synthetic_archive_relative_path == DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH
    fixture_path = root / synthetic_archive_relative_path

    checks: list[dict[str, Any]] = [
        {"name": "source_l23_03_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_03_future_listing_authorized", "ok": source.get("synthetic_archive_listing_authorization_granted_for_future_patch") is True},
        {"name": "source_l23_03_listing_execution_false", "ok": source.get("synthetic_archive_listing_execution_allowed") is False},
        {"name": "listing_proof_token_present", "ok": token_present},
        {"name": "listing_proof_token_valid", "ok": token_valid},
        {"name": "synthetic_archive_relative_path_is_fixed", "ok": rel_is_fixed},
        {"name": "synthetic_archive_fixture_exists", "ok": fixture_path.exists()},
        {"name": "synthetic_archive_suffix_is_zip", "ok": fixture_path.suffix.lower() == ".zip"},
    ]

    names: list[str] = []
    listing_allowed = bool(all(check.get("ok") for check in checks))
    if listing_allowed:
        try:
            names = _list_synthetic_archive_names(fixture_path)
            checks.append({"name": "synthetic_archive_listing_returned_expected_names", "ok": tuple(names) == EXPECTED_SYNTHETIC_MEMBERS})
            checks.append({"name": "manifest_member_name_seen_without_payload_read", "ok": "manifest.json" in names})
        except Exception as exc:
            checks.append({"name": "synthetic_archive_listing_metadata_only", "ok": False, "error": f"{type(exc).__name__}: {exc}"})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_03_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_listing_authorized": source.get("synthetic_archive_listing_authorization_granted_for_future_patch"),
            "listing_execution_allowed": source.get("synthetic_archive_listing_execution_allowed"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_archive_listing_proof_requested": True,
        "synthetic_archive_listing_proof_token_present": token_present,
        "synthetic_archive_listing_proof_token_valid": token_valid,
        "synthetic_archive_listing_execution_allowed": listing_allowed,
        "synthetic_archive_listing_active": listing_allowed,
        "synthetic_archive_listing_performed": listing_allowed,
        "synthetic_archive_fixture_only": True,
        "synthetic_archive_fixture_relative_path": DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
        "synthetic_archive_opened": listing_allowed,
        "synthetic_archive_contents_listed": listing_allowed,
        "synthetic_archive_member_names": names,
        "synthetic_archive_member_count": len(names),
        "manifest_member_name_seen": "manifest.json" in names,
        "listing_scope": "fixed_synthetic_archive_metadata_names_only",
        "no_real_archive_permission_added_by_l23_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.4 opens only the fixed synthetic archive fixture for central-directory metadata listing.",
            "No archive member payload is read and no extraction is performed.",
            "No real downloaded archive, browser, pasteback, send/submit, or package-run activity is performed.",
        ],
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    payload["downloaded_archive_opened"] = False
    payload["downloaded_archive_contents_listed"] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Repair Patch                  : {payload.get('repair_patch')}",
        f"Status                        : {payload.get('status')}",
        f"Listing Scope                 : {payload.get('listing_scope')}",
        f"Synthetic Archive Opened      : {payload.get('synthetic_archive_opened')}",
        f"Synthetic Names               : {payload.get('synthetic_archive_member_names')}",
        f"Manifest Name Seen            : {payload.get('manifest_member_name_seen')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Extraction                    : {payload.get('archive_extracted')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
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
    parser.add_argument("--allow-synthetic-archive-listing-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--synthetic-archive-relative-path", default=DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_first_synthetic_archive_listing_proof(
        args.repo_root,
        allow_synthetic_archive_listing_proof=args.allow_synthetic_archive_listing_proof,
        authorization_token=args.authorization_token,
        synthetic_archive_relative_path=args.synthetic_archive_relative_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
