"""L25.18 broad checkpoint for controlled archive manifest schema validation.

This follows accepted L25.17. It replays the controlled synthetic manifest tiny
internal schema-validation proof and summarizes the L25.16-L25.17 schema ladder.
It does not perform PatchOps manifest validation, package execution, extraction,
browser automation, pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_first_controlled_proof as l25_17

PATCH = "L25.18"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.18 Microsoft Edge controlled runtime archive manifest schema validation broad checkpoint"
SOURCE_PATCH = "L25.17"
SOURCE_LADDER = (
    "L25.16 archive manifest schema validation authorization gate",
    "L25.17 first controlled synthetic manifest tiny internal schema validation proof",
)
NEXT_PATCH = "L25.19 Microsoft Edge controlled runtime archive manifest validation-to-PatchOps-preflight authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
TARGET_MANIFEST_MEMBER_NAME = l25_17.TARGET_MANIFEST_MEMBER_NAME
EXPECTED_SCHEMA_SCOPE = l25_17.SCHEMA_VALIDATION_SCOPE
EXPECTED_REQUIRED_KEYS = sorted(l25_17.REQUIRED_SCHEMA)

ALWAYS_FALSE_FIELDS = (
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


def _l25_17_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_17.build_archive_manifest_schema_validation_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.17 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_17_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_17.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_17.build_archive_manifest_schema_validation_first_controlled_proof(
            repo_root,
            allow_archive_manifest_schema_validation_proof=True,
            authorization_token=l25_17.REQUIRED_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            member_name=TARGET_MANIFEST_MEMBER_NAME,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.17 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_archive_manifest_schema_validation_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_17_default_payload(root, target_url)
    authorized_payload = _l25_17_authorized_payload(root, target_url)
    schema_summary = authorized_payload.get("manifest_schema_validation_summary") or {}
    required_keys = schema_summary.get("required_keys") or []
    validated_keys = schema_summary.get("validated_keys") or []

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_17_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_17_default_is_passive", "ok": default_payload.get("manifest_schema_validated") is False and default_payload.get("manifest_payload_schema_validated") is False},
        {"name": "source_l25_17_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_17_patch_marker", "ok": authorized_payload.get("patch") == "L25.17"},
        {"name": "source_l25_17_schema_validation_allowed", "ok": authorized_payload.get("archive_manifest_schema_validation_allowed") is True},
        {"name": "source_l25_17_payload_read_and_parsed", "ok": authorized_payload.get("manifest_payload_read") is True and authorized_payload.get("manifest_payload_json_parsed") is True},
        {"name": "source_l25_17_schema_validated", "ok": authorized_payload.get("manifest_payload_schema_validated") is True and authorized_payload.get("manifest_schema_validated") is True and authorized_payload.get("manifest_validation_performed") is True},
        {"name": "source_l25_17_member_name", "ok": authorized_payload.get("manifest_member_name_read") == TARGET_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_17_scope_tiny_internal_only", "ok": authorized_payload.get("manifest_schema_validation_scope") == EXPECTED_SCHEMA_SCOPE},
        {"name": "source_l25_17_schema_summary_ok", "ok": schema_summary.get("ok") is True},
        {"name": "source_l25_17_required_keys", "ok": required_keys == EXPECTED_REQUIRED_KEYS},
        {"name": "source_l25_17_validated_keys", "ok": validated_keys == EXPECTED_REQUIRED_KEYS},
        {"name": "source_l25_17_schema_errors_empty", "ok": schema_summary.get("errors") == []},
        {"name": "source_l25_17_no_patchops_validation", "ok": authorized_payload.get("patchops_manifest_validation_performed") is False},
        {"name": "source_l25_17_no_execution_extract_browser_package", "ok": authorized_payload.get("package_manifest_used_for_execution") is False and authorized_payload.get("package_execution_allowed") is False and authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_manifest_schema_validation_ladder_checkpoint": True,
        "l25_archive_manifest_schema_validation_ladder_complete": ok,
        "source_l25_17_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "manifest_payload_schema_validated": default_payload.get("manifest_payload_schema_validated"),
            "manifest_schema_validated": default_payload.get("manifest_schema_validated"),
            "manifest_validation_performed": default_payload.get("manifest_validation_performed"),
            "manifest_schema_validation_scope": default_payload.get("manifest_schema_validation_scope"),
        },
        "source_l25_17_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_16_ok": authorized_payload.get("source_l25_16_summary", {}).get("ok"),
            "source_l25_16_future_authorized": authorized_payload.get("source_l25_16_summary", {}).get("future_schema_validation_authorized"),
            "schema_validation_allowed": authorized_payload.get("archive_manifest_schema_validation_allowed"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed"),
            "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated"),
            "manifest_schema_validated": authorized_payload.get("manifest_schema_validated"),
            "manifest_validation_performed": authorized_payload.get("manifest_validation_performed"),
            "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
            "manifest_schema_validation_scope": authorized_payload.get("manifest_schema_validation_scope"),
            "manifest_schema_validation_summary": schema_summary,
            "patchops_manifest_validation_performed": authorized_payload.get("patchops_manifest_validation_performed"),
            "package_manifest_used_for_execution": authorized_payload.get("package_manifest_used_for_execution"),
            "package_execution_allowed": authorized_payload.get("package_execution_allowed"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_schema_validation_scope": EXPECTED_SCHEMA_SCOPE,
        "accepted_schema_validation_allowed": authorized_payload.get("archive_manifest_schema_validation_allowed") is True,
        "accepted_manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "accepted_manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed") is True,
        "accepted_manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated") is True,
        "accepted_manifest_schema_validated": authorized_payload.get("manifest_schema_validated") is True,
        "accepted_manifest_validation_performed": authorized_payload.get("manifest_validation_performed") is True,
        "accepted_manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "accepted_schema_summary_ok": schema_summary.get("ok"),
        "accepted_schema_required_keys": required_keys,
        "accepted_schema_validated_keys": validated_keys,
        "accepted_schema_errors": schema_summary.get("errors") or [],
        "archive_manifest_schema_validation_allowed": authorized_payload.get("archive_manifest_schema_validation_allowed") is True,
        "manifest_payload_read": authorized_payload.get("manifest_payload_read") is True,
        "manifest_payload_json_parsed": authorized_payload.get("manifest_payload_json_parsed") is True,
        "manifest_payload_schema_validated": authorized_payload.get("manifest_payload_schema_validated") is True,
        "manifest_schema_validated": authorized_payload.get("manifest_schema_validated") is True,
        "manifest_validation_performed": authorized_payload.get("manifest_validation_performed") is True,
        "manifest_member_name_read": authorized_payload.get("manifest_member_name_read"),
        "manifest_schema_validation_scope": authorized_payload.get("manifest_schema_validation_scope"),
        "manifest_schema_validation_summary": schema_summary,
        "no_patchops_manifest_validation_added_by_l25_18": True,
        "no_package_execution_added_by_l25_18": True,
        "no_archive_extraction_added_by_l25_18": True,
        "no_browser_permission_added_by_l25_18": True,
        "no_pasteback_or_package_run_permission_added_by_l25_18": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.18 is a broad checkpoint over accepted L25.16-L25.17 schema validation work.",
            "Only tiny internal schema validation of the controlled synthetic manifest is accepted; PatchOps manifest validation, execution, extraction, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_manifest_schema_validation_ladder_complete')}",
        f"Manifest Schema Validated     : {payload.get('manifest_schema_validated')}",
        f"PatchOps Manifest Validation  : {payload.get('patchops_manifest_validation_performed')}",
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
    payload = build_archive_manifest_schema_validation_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
