"""L23.5 synthetic manifest-name proof gate.

This module follows accepted L23.4/L23.4b. It selects the manifest entry by name
from the accepted synthetic archive metadata listing. It does not read manifest
contents, read member payload bytes, extract files, touch real downloaded
artifacts, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_first_synthetic_archive_listing_proof as l23_04

PATCH = "L23.5"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.5 Microsoft Edge real downloaded-archive manifest validation synthetic manifest-name proof gate"
SOURCE_PATCH = "L23.4/L23.4b"
NEXT_PATCH = "L23.6 Microsoft Edge real downloaded-archive manifest validation synthetic manifest payload authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_SYNTHETIC_MANIFEST_NAME_PROOF_TOKEN = "PATCHOPS_L23_EDGE_SYNTHETIC_MANIFEST_NAME_PROOF_AUTHORIZED"
EXPECTED_MANIFEST_MEMBER_NAME = "manifest.json"
EXPECTED_SYNTHETIC_MEMBERS = ("manifest.json", "README.txt")

ALWAYS_FALSE_FIELDS = (
    "synthetic_manifest_payload_authorization_granted_for_future_patch",
    "synthetic_manifest_payload_read_execution_allowed",
    "synthetic_manifest_payload_read_active",
    "synthetic_manifest_payload_read_performed",
    "archive_member_bytes_read",
    "archive_member_content_read",
    "archive_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "manifest_member_bytes_read",
    "manifest_member_payload_read",
    "manifest_member_content_read",
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


def _l23_04_listing_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_04.build_first_synthetic_archive_listing_proof(
            repo_root,
            allow_synthetic_archive_listing_proof=True,
            authorization_token=l23_04.REQUIRED_SYNTHETIC_ARCHIVE_LISTING_PROOF_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.4 listing readback failed: {type(exc).__name__}: {exc}"}


def _base_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l23_04_listing_payload(root, target_url)
    checks = [
        {"name": "source_l23_04_listing_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_04_metadata_listing_ok", "ok": source.get("synthetic_archive_contents_listed") is True},
        {"name": "source_l23_04_manifest_name_seen", "ok": source.get("manifest_member_name_seen") is True},
        {"name": "default_manifest_name_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_04_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "repair_patch": source.get("repair_patch"),
            "listing_scope": source.get("listing_scope"),
            "synthetic_archive_opened": source.get("synthetic_archive_opened"),
            "synthetic_archive_contents_listed": source.get("synthetic_archive_contents_listed"),
            "synthetic_archive_member_names": source.get("synthetic_archive_member_names"),
            "manifest_member_name_seen": source.get("manifest_member_name_seen"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_member_payload_read": source.get("manifest_member_payload_read"),
            "archive_extracted": source.get("archive_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_manifest_name_proof_requested": False,
        "synthetic_manifest_name_proof_token_present": False,
        "synthetic_manifest_name_proof_token_valid": False,
        "synthetic_manifest_name_proof_allowed": False,
        "synthetic_manifest_name_selected": False,
        "synthetic_manifest_selected_name": None,
        "synthetic_manifest_name_selection_scope": "default_readback_only_no_selection",
        "manifest_name_only": True,
        "no_new_payload_read_permission_added_by_l23_5": True,
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
    return payload


def build_synthetic_manifest_name_proof_gate(
    repo_root: str | Path | None = None,
    *,
    allow_synthetic_manifest_name_proof: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    if not allow_synthetic_manifest_name_proof:
        return _base_payload(root, target_url)

    source = _l23_04_listing_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_SYNTHETIC_MANIFEST_NAME_PROOF_TOKEN
    source_names = source.get("synthetic_archive_member_names")
    source_names_ok = source_names == list(EXPECTED_SYNTHETIC_MEMBERS)
    manifest_name_seen = EXPECTED_MANIFEST_MEMBER_NAME in source_names if isinstance(source_names, list) else False
    selected_name = EXPECTED_MANIFEST_MEMBER_NAME if manifest_name_seen else None

    checks: list[dict[str, Any]] = [
        {"name": "source_l23_04_listing_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_04_repair_marker_present", "ok": source.get("repair_patch") == "L23.4a"},
        {"name": "source_l23_04_metadata_listing_ok", "ok": source.get("synthetic_archive_contents_listed") is True},
        {"name": "source_l23_04_member_names_expected", "ok": source_names_ok},
        {"name": "source_l23_04_manifest_name_seen", "ok": source.get("manifest_member_name_seen") is True and manifest_name_seen},
        {"name": "source_l23_04_no_member_payload_read", "ok": source.get("archive_member_bytes_read") is False and source.get("manifest_member_payload_read") is False},
        {"name": "source_l23_04_no_extraction_or_browser_or_package", "ok": source.get("archive_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "manifest_name_proof_token_present", "ok": token_present},
        {"name": "manifest_name_proof_token_valid", "ok": token_valid},
        {"name": "manifest_name_selected_by_metadata_only", "ok": selected_name == EXPECTED_MANIFEST_MEMBER_NAME},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_04_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "repair_patch": source.get("repair_patch"),
            "listing_scope": source.get("listing_scope"),
            "synthetic_archive_opened": source.get("synthetic_archive_opened"),
            "synthetic_archive_contents_listed": source.get("synthetic_archive_contents_listed"),
            "synthetic_archive_member_names": source.get("synthetic_archive_member_names"),
            "manifest_member_name_seen": source.get("manifest_member_name_seen"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "manifest_member_payload_read": source.get("manifest_member_payload_read"),
            "archive_extracted": source.get("archive_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "synthetic_manifest_name_proof_requested": True,
        "synthetic_manifest_name_proof_token_present": token_present,
        "synthetic_manifest_name_proof_token_valid": token_valid,
        "synthetic_manifest_name_proof_allowed": ok,
        "synthetic_manifest_name_selected": selected_name == EXPECTED_MANIFEST_MEMBER_NAME,
        "synthetic_manifest_selected_name": selected_name,
        "synthetic_manifest_name_selection_scope": "metadata_member_name_only_no_payload_read",
        "manifest_name_only": True,
        "no_new_payload_read_permission_added_by_l23_5": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.5 selects manifest.json by metadata name only from the accepted L23.4 listing proof.",
            "No manifest payload, member bytes, extraction, real archive, browser, pasteback, or package-run activity is performed.",
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
        f"Manifest Name Selected        : {payload.get('synthetic_manifest_name_selected')}",
        f"Selected Name                 : {payload.get('synthetic_manifest_selected_name')}",
        f"Selection Scope               : {payload.get('synthetic_manifest_name_selection_scope')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Manifest Payload Read         : {payload.get('manifest_member_payload_read')}",
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
    parser.add_argument("--allow-synthetic-manifest-name-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_synthetic_manifest_name_proof_gate(
        args.repo_root,
        allow_synthetic_manifest_name_proof=args.allow_synthetic_manifest_name_proof,
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
