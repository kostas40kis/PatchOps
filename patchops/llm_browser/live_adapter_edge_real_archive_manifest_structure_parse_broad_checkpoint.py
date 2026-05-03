"""L25.15 broad checkpoint for controlled archive manifest structure parse proof.

This follows accepted L25.14. It replays the controlled synthetic manifest JSON
structure parse proof and summarizes the L25.13-L25.14 structure-parse ladder.
It does not perform schema validation, PatchOps manifest validation, package
execution, extraction, browser automation, pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_structure_parse_first_controlled_proof as l25_14

PATCH = "L25.15"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.15 Microsoft Edge controlled runtime archive manifest structure parse broad checkpoint"
SOURCE_PATCH = "L25.14"
SOURCE_LADDER = (
    "L25.13 archive manifest structure parse authorization gate",
    "L25.14 first controlled synthetic manifest JSON structure parse proof",
)
NEXT_PATCH = "L25.16 Microsoft Edge controlled runtime archive manifest schema validation authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
TARGET_MANIFEST_MEMBER_NAME = l25_14.TARGET_MANIFEST_MEMBER_NAME
EXPECTED_PARSE_SCOPE = l25_14.MANIFEST_STRUCTURE_PARSE_SCOPE
EXPECTED_TOP_LEVEL_TYPE = "object"

ALWAYS_FALSE_FIELDS = (
    "manifest_payload_schema_validated",
    "manifest_validation_performed",
    "patchops_manifest_validation_performed",
    "package_manifest_used_for_execution",
    "package_execution_allowed",
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


def _l25_14_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_14.build_archive_manifest_structure_parse_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.14 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_14_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_14.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_14.build_archive_manifest_structure_parse_first_controlled_proof(
            repo_root,
            allow_archive_manifest_structure_parse_proof=True,
            authorization_token=l25_14.REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            member_name=TARGET_MANIFEST_MEMBER_NAME,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.14 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_structure_parse_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_14_default_payload(root, target_url)
    authorized_payload = _l25_14_authorized_payload(root, target_url)
    summary = authorized_payload.get("manifest_structure_summary") or {}
    top_level_keys = summary.get("top_level_keys") or []

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_14_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_14_default_is_passive", "ok": default_payload.get("manifest_payload_json_parsed") is False and default_payload.get("manifest_structure_parsed") is False},
        {"name": "source_l25_14_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_14_patch_marker", "ok": authorized_payload.get("patch") == "L25.14"},
        {"name": "source_l25_14_parse_allowed", "ok": authorized_payload.get("archive_manifest_structure_parse_allowed") is True},
        {"name": "source_l25_14_manifest_payload_read", "ok": authorized_payload.get("manifest_payload_read") is True and authorized_payload.get("manifest_payload_bytes_read") is True},
        {"name": "source_l25_14_json_parsed", "ok": authorized_payload.get("manifest_payload_json_parsed") is True},
        {"name": "source_l25_14_structure_parsed", "ok": authorized_payload.get("manifest_structure_parsed") is True},
        {"name": "source_l25_14_member_name", "ok": authorized_payload.get("manifest_member_name_read") == TARGET_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_14_scope_parse_only", "ok": authorized_payload.get("manifest_structure_parse_scope") == EXPECTED_PARSE_SCOPE},
        {"name": "source_l25_14_top_level_object", "ok": summary.get("top_level_type") == EXPECTED_TOP_LEVEL_TYPE},
        {"name": "source_l25_14_keys_non_empty", "ok": isinstance(top_level_keys, list) and len(top_level_keys) > 0},
        {"name": "source_l25_14_no_schema_validation", "ok": authorized_payload.get("manifest_payload_schema_validated") is False and authorized_payload.get("manifest_validation_performed") is False and authorized_payload.get("patchops_manifest_validation_performed") is False},
        {"name": "source_l25_14_no_execution_extract_browser_package", "ok": authorized_payload.get("package_manifest_used_for_execution") is False and authorized_payload.get("package_execution_allowed") is False and authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_manifest_structure_parse_ladder_checkpoint": True,
        "l25_archive_manifest_structure_parse_ladder_complete": ok,
        "source_l25_14_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "manifest_payload_json_parsed": default_payload.get("manifest_payload_json_parsed"),
            "manifest_structure_parsed": default_payload.get("manifest_structure_parsed"),
            "manifest_structure_parse_scope": default_payload.get("manifest_structure_parse_scope"),
        },
        "source_l25_14_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_13_ok": authorized_payload.get("source_l25_13_summary", {}).get("ok"),
            "source_l25_13_future_authorized": authorized_payload.get("source_l25_13_summary", {}).get("future_manifest_structure_parse_authorized"),
            "manifest_structure_parse_allowed": authorized_payload.get("archive_manifest_structure_parse_allowed"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read"),
            "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed"),
            "manifest_structure_parsed": authorized_payload.get("manifest_structure_parsed"),
            "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
            "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
            "manifest_structure_parse_scope": authorized_payload.get("manifest_structure_parse_scope"),
            "manifest_structure_summary": summary,
            "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated"),
            "manifest_validation_performed": authorized_payload.get("manifest_validation_performed"),
            "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
            "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
            "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_manifest_structure_parse_scope": EXPECTED_PARSE_SCOPE,
        "accepted_manifest_structure_parse_allowed": authorized_payload.get("archive_manifest_structure_parse_allowed") is True,
        "accepted_manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "accepted_manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "accepted_manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed") is True,
        "accepted_manifest_structure_parsed": authorized_payload.get("manifest_structure_parsed") is True,
        "accepted_manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "accepted_manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
        "accepted_manifest_top_level_type": summary.get("top_level_type"),
        "accepted_manifest_top_level_keys": top_level_keys,
        "accepted_manifest_scalar_value_types": summary.get("scalar_value_types") or {},
        "archive_manifest_structure_parse_allowed": authorized_payload.get("archive_manifest_structure_parse_allowed") is True,
        "manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed") is True,
        "manifest_structure_parsed": authorized_payload.get("manifest_structure_parsed") is True,
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
        "manifest_structure_parse_scope": authorized_payload.get("manifest_structure_parse_scope"),
        "manifest_structure_summary": summary,
        "no_manifest_schema_validation_added_by_l25_15": True,
        "no_patchops_manifest_validation_added_by_l25_15": True,
        "no_package_execution_added_by_l25_15": True,
        "no_archive_extraction_added_by_l25_15": True,
        "no_browser_permission_added_by_l25_15": True,
        "no_pasteback_or_package_run_permission_added_by_l25_15": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.15 is a broad checkpoint over accepted L25.13-L25.14 manifest structure parse work.",
            "Only JSON structure parsing of the controlled synthetic manifest is accepted; schema validation, PatchOps manifest validation, execution, extraction, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_manifest_structure_parse_ladder_complete')}",
        f"Manifest JSON Parsed          : {payload.get('manifest_payload_json_parsed')}",
        f"Manifest Structure Parsed     : {payload.get('manifest_structure_parsed')}",
        f"Manifest Validation           : {payload.get('manifest_validation_performed')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
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
    payload = build_archive_manifest_structure_parse_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
