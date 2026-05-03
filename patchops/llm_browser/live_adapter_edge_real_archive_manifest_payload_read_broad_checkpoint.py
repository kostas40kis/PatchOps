"""L25.12 broad checkpoint for controlled archive manifest payload-read proof.

This follows accepted L25.11 plus L25.11a. It replays the controlled synthetic
manifest payload byte-read proof and summarizes the L25.10-L25.11 manifest
payload-read ladder. It does not parse JSON, validate schema, execute packages,
extract members, start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_first_controlled_proof as l25_11

PATCH = "L25.12"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.12 Microsoft Edge controlled runtime archive manifest payload-read broad checkpoint"
SOURCE_PATCH = "L25.11/L25.11a"
SOURCE_LADDER = (
    "L25.10 archive manifest payload-read authorization gate",
    "L25.11 first controlled synthetic manifest payload-read proof",
    "L25.11a validator AST scan repair",
)
NEXT_PATCH = "L25.13 Microsoft Edge controlled runtime archive manifest structure parse authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
TARGET_MANIFEST_MEMBER_NAME = l25_11.TARGET_MANIFEST_MEMBER_NAME
EXPECTED_MANIFEST_READ_SCOPE = "controlled_runtime_manifest_payload_bytes_only_no_validation_no_execution"

ALWAYS_FALSE_FIELDS = (
    "manifest_payload_json_parsed",
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


def _l25_11_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_11.build_archive_manifest_payload_read_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.11 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_11_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_11.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_11.build_archive_manifest_payload_read_first_controlled_proof(
            repo_root,
            allow_archive_manifest_payload_read_proof=True,
            authorization_token=l25_11.REQUIRED_ARCHIVE_MANIFEST_PAYLOAD_READ_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            member_name=TARGET_MANIFEST_MEMBER_NAME,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.11 authorized readback failed: {type(exc).__name__}: {exc}"}


def _is_lower_hex_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def build_archive_manifest_payload_read_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_11_default_payload(root, target_url)
    authorized_payload = _l25_11_authorized_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_11_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_11_default_is_passive", "ok": default_payload.get("manifest_payload_read") is False},
        {"name": "source_l25_11_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_11_patch_marker", "ok": authorized_payload.get("patch") == "L25.11"},
        {"name": "source_l25_11_manifest_payload_read_allowed", "ok": authorized_payload.get("archive_manifest_payload_read_allowed") is True},
        {"name": "source_l25_11_manifest_payload_read", "ok": authorized_payload.get("manifest_payload_read") is True},
        {"name": "source_l25_11_manifest_payload_bytes_read", "ok": authorized_payload.get("manifest_payload_bytes_read") is True},
        {"name": "source_l25_11_manifest_payload_sha256_read", "ok": authorized_payload.get("manifest_payload_sha256_read") is True and _is_lower_hex_sha256(authorized_payload.get("manifest_payload_sha256"))},
        {"name": "source_l25_11_manifest_member_name", "ok": authorized_payload.get("manifest_member_name_read") == TARGET_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_11_scope_bytes_only", "ok": authorized_payload.get("manifest_payload_read_scope") == EXPECTED_MANIFEST_READ_SCOPE},
        {"name": "source_l25_11_payload_count_positive", "ok": isinstance(authorized_payload.get("manifest_payload_byte_count"), int) and authorized_payload.get("manifest_payload_byte_count") > 0},
        {"name": "source_l25_11_no_json_parse_or_validation", "ok": authorized_payload.get("manifest_payload_json_parsed") is False and authorized_payload.get("manifest_payload_schema_validated") is False and authorized_payload.get("manifest_validation_performed") is False and authorized_payload.get("package_manifest_used_for_execution") is False},
        {"name": "source_l25_11_no_extract_browser_package", "ok": authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_manifest_payload_read_ladder_checkpoint": True,
        "l25_archive_manifest_payload_read_ladder_complete": ok,
        "source_l25_11_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "manifest_payload_read": default_payload.get("manifest_payload_read"),
            "manifest_payload_read_scope": default_payload.get("manifest_payload_read_scope"),
        },
        "source_l25_11_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_10_ok": authorized_payload.get("source_l25_10_summary", {}).get("ok"),
            "source_l25_10_future_authorized": authorized_payload.get("source_l25_10_summary", {}).get("future_manifest_payload_read_authorized"),
            "manifest_payload_read_allowed": authorized_payload.get("archive_manifest_payload_read_allowed"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read"),
            "manifest_payload_sha256_read": authorized_payload.get("manifest_payload_sha256_read"),
            "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
            "manifest_payload_sha256": authorized_payload.get("manifest_payload_sha256"),
            "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
            "manifest_payload_read_scope": authorized_payload.get("manifest_payload_read_scope"),
            "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed"),
            "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated"),
            "manifest_validation_performed": authorized_payload.get("manifest_validation_performed"),
            "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_manifest_payload_read_scope": EXPECTED_MANIFEST_READ_SCOPE,
        "accepted_manifest_payload_read_allowed": authorized_payload.get("archive_manifest_payload_read_allowed") is True,
        "accepted_manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "accepted_manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "accepted_manifest_payload_sha256_read": authorized_payload.get("manifest_payload_sha256_read") is True,
        "accepted_manifest_payload_sha256_is_lower_hex": _is_lower_hex_sha256(authorized_payload.get("manifest_payload_sha256")),
        "accepted_manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
        "accepted_manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "archive_manifest_payload_read_allowed": authorized_payload.get("archive_manifest_payload_read_allowed") is True,
        "manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "manifest_payload_bytes_read": authorized_payload.get("manifest_payload_bytes_read") is True,
        "manifest_payload_sha256_read": authorized_payload.get("manifest_payload_sha256_read") is True,
        "manifest_payload_byte_count": authorized_payload.get("manifest_payload_byte_count"),
        "manifest_payload_sha256": authorized_payload.get("manifest_payload_sha256"),
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "manifest_payload_read_scope": authorized_payload.get("manifest_payload_read_scope"),
        "no_manifest_json_parse_or_validation_added_by_l25_12": True,
        "no_archive_extraction_added_by_l25_12": True,
        "no_browser_permission_added_by_l25_12": True,
        "no_pasteback_or_package_run_permission_added_by_l25_12": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.12 is a broad checkpoint over accepted L25.10-L25.11/L25.11a manifest payload-read work.",
            "Only synthetic manifest payload bytes plus byte count and SHA-256 are accepted; JSON parsing, schema validation, execution, extraction, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_manifest_payload_read_ladder_complete')}",
        f"Manifest Payload Read         : {payload.get('manifest_payload_read')}",
        f"Manifest Member Name          : {payload.get('manifest_member_name_read')}",
        f"JSON Parsed                   : {payload.get('manifest_payload_json_parsed')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_payload_read_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
