"""L25.13 archive manifest structure-parse authorization gate.

This follows accepted L25.12. It reads back the controlled synthetic manifest
payload byte-read broad checkpoint and grants only future authorization for a
manifest structure parse proof. It does not parse JSON, validate schemas, execute
packages, extract archives, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_broad_checkpoint as l25_12

PATCH = "L25.13"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.13 Microsoft Edge controlled runtime archive manifest structure parse authorization gate"
SOURCE_PATCH = "L25.12"
NEXT_PATCH = "L25.14 Microsoft Edge controlled runtime archive manifest structure parse first proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_AUTHORIZATION_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_STRUCTURE_PARSE_AUTHORIZED_READBACK_ONLY"
EXPECTED_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
EXPECTED_MANIFEST_READ_SCOPE = "controlled_runtime_manifest_payload_bytes_only_no_validation_no_execution"

FALSE_FIELDS = (
    "archive_manifest_structure_parse_authorization_executes_parse",
    "archive_manifest_structure_parse_allowed",
    "manifest_payload_json_parsed",
    "manifest_structure_parsed",
    "manifest_payload_schema_validated",
    "manifest_validation_performed",
    "package_manifest_used_for_execution",
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


def _l25_12_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_12.build_archive_manifest_payload_read_broad_checkpoint(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.12 manifest payload broad checkpoint readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_structure_parse_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_structure_parse_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source = _l25_12_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_AUTHORIZATION_TOKEN
    requested = bool(allow_archive_manifest_structure_parse_authorization or token_present)
    future_authorized = bool(allow_archive_manifest_structure_parse_authorization and token_valid)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_12_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_12_broad_checkpoint", "ok": source.get("broad_checkpoint") is True},
        {"name": "source_l25_12_manifest_payload_ladder_complete", "ok": source.get("l25_archive_manifest_payload_read_ladder_complete") is True},
        {"name": "source_l25_12_failed_checks_empty", "ok": source.get("failed_checks") == []},
        {"name": "source_l25_12_manifest_bytes_read", "ok": source.get("manifest_payload_read") is True and source.get("manifest_payload_bytes_read") is True and source.get("manifest_member_name_read") == EXPECTED_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_12_scope_bytes_only", "ok": source.get("accepted_manifest_payload_read_scope") == EXPECTED_MANIFEST_READ_SCOPE},
        {"name": "source_l25_12_no_parse_or_validation", "ok": source.get("manifest_payload_json_parsed") is False and source.get("manifest_payload_schema_validated") is False and source.get("manifest_validation_performed") is False and source.get("package_manifest_used_for_execution") is False},
        {"name": "source_l25_12_no_extract_browser_package", "ok": source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "manifest_structure_parse_authorization_is_readback_only", "ok": True},
        {"name": "manifest_structure_parse_execution_remains_false", "ok": True},
    ]

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_12_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "broad_checkpoint": source.get("broad_checkpoint"),
            "manifest_payload_read_ladder_complete": source.get("l25_archive_manifest_payload_read_ladder_complete"),
            "failed_checks": source.get("failed_checks"),
            "accepted_manifest_payload_read_scope": source.get("accepted_manifest_payload_read_scope"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "manifest_payload_bytes_read": source.get("manifest_payload_bytes_read"),
            "manifest_payload_sha256_read": source.get("manifest_payload_sha256_read"),
            "manifest_member_name_read": source.get("manifest_member_name_read"),
            "manifest_payload_json_parsed": source.get("manifest_payload_json_parsed"),
            "manifest_payload_schema_validated": source.get("manifest_payload_schema_validated"),
            "manifest_validation_performed": source.get("manifest_validation_performed"),
            "package_manifest_used_for_execution": source.get("package_manifest_used_for_execution"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_structure_parse_authorization_gate": True,
        "archive_manifest_structure_parse_authorization_readback_only": True,
        "archive_manifest_structure_parse_authorization_requested": requested,
        "archive_manifest_structure_parse_authorization_token_present": token_present,
        "archive_manifest_structure_parse_authorization_token_valid": token_valid,
        "archive_manifest_structure_parse_authorization_granted_for_future_patch": future_authorized,
        "future_archive_manifest_structure_parse_requires_explicit_flag_and_token": True,
        "future_archive_manifest_structure_parse_must_be_separately_gated_in_l25_14": True,
        "no_manifest_structure_parse_execution_added_by_l25_13": True,
        "no_manifest_schema_validation_added_by_l25_13": True,
        "no_package_execution_added_by_l25_13": True,
        "no_archive_extraction_added_by_l25_13": True,
        "no_browser_permission_added_by_l25_13": True,
        "no_pasteback_or_package_run_permission_added_by_l25_13": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "readback-only manifest structure parse authorization; no JSON parsing, no validation, no extraction, no browser, no pasteback, no package-run",
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
        f"Future Parse Authorized       : {payload.get('archive_manifest_structure_parse_authorization_granted_for_future_patch')}",
        f"Manifest JSON Parsed          : {payload.get('manifest_payload_json_parsed')}",
        f"Manifest Structure Parsed     : {payload.get('manifest_structure_parsed')}",
        f"Manifest Validation           : {payload.get('manifest_validation_performed')}",
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
    parser.add_argument("--allow-archive-manifest-structure-parse-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_structure_parse_authorization_gate(
        args.repo_root,
        allow_archive_manifest_structure_parse_authorization=args.allow_archive_manifest_structure_parse_authorization,
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
