"""L25.17 first controlled archive manifest schema-validation proof.

This follows accepted L25.16. It reads exactly one controlled synthetic manifest,
parses JSON, and validates that parsed object against a tiny internal schema
made only for the synthetic fixture. It does not call PatchOps manifest
validation, use the manifest for execution, extract archives, start a browser,
paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_schema_validation_authorization_gate as l25_16
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_structure_parse_first_controlled_proof as parse_proof

PATCH = "L25.17"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.17 Microsoft Edge controlled runtime archive manifest schema validation first proof"
SOURCE_PATCH = "L25.16"
NEXT_PATCH = "L25.18 Microsoft Edge controlled runtime archive manifest schema validation broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = parse_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
SCHEMA_VALIDATION_SCOPE = "controlled_runtime_manifest_tiny_internal_schema_validation_only_no_patchops_validation_no_execution"
REQUIRED_SCHEMA = {
    "bundle_schema_version": str,
    "manifest_version": str,
    "patch_name": str,
    "purpose": str,
    "synthetic": bool,
}

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


def _l25_16_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_16.build_archive_manifest_schema_validation_authorization_gate(
            repo_root,
            allow_archive_manifest_schema_validation_authorization=True,
            authorization_token=l25_16.REQUIRED_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.16 schema validation authorization readback failed: {type(exc).__name__}: {exc}"}


def _validate_internal_schema(value: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(value, dict):
        errors.append("top-level value is not an object")
        return {"ok": False, "required_keys": sorted(REQUIRED_SCHEMA), "validated_keys": [], "errors": errors}
    validated_keys: list[str] = []
    for key, expected_type in REQUIRED_SCHEMA.items():
        if key not in value:
            errors.append(f"missing key: {key}")
            continue
        if not isinstance(value[key], expected_type):
            errors.append(f"wrong type for {key}: expected {expected_type.__name__}, got {type(value[key]).__name__}")
            continue
        validated_keys.append(key)
    return {
        "ok": not errors,
        "required_keys": sorted(REQUIRED_SCHEMA),
        "validated_keys": sorted(validated_keys),
        "errors": errors,
        "type_expectations": {key: expected.__name__ for key, expected in REQUIRED_SCHEMA.items()},
    }


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_16_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_16_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_16_future_schema_validation_authorized", "ok": source.get("archive_manifest_schema_validation_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_16_schema_validation_execution_false", "ok": source.get("archive_manifest_schema_validation_allowed") is False and source.get("manifest_schema_validated") is False},
        {"name": "default_schema_validation_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_16_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_schema_validation_authorized": source.get("archive_manifest_schema_validation_authorization_granted_for_future_patch"),
            "schema_validation_allowed": source.get("archive_manifest_schema_validation_allowed"),
            "manifest_schema_validated": source.get("manifest_schema_validated"),
            "manifest_validation_performed": source.get("manifest_validation_performed"),
            "patchops_manifest_validation_performed": source.get("patchops_manifest_validation_performed"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_schema_validation_proof_requested": False,
        "archive_manifest_schema_validation_proof_token_present": False,
        "archive_manifest_schema_validation_proof_token_valid": False,
        "archive_manifest_schema_validation_allowed": False,
        "manifest_payload_read": False,
        "manifest_payload_bytes_read": False,
        "manifest_payload_json_parsed": False,
        "manifest_structure_parsed": False,
        "manifest_payload_schema_validated": False,
        "manifest_schema_validated": False,
        "manifest_validation_performed": False,
        "manifest_member_name_read": None,
        "manifest_schema_validation_scope": "default_readback_only_no_schema_validation",
        "manifest_schema_validation_summary": {},
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_17": True,
        "json_loads_allowed_by_l25_17": True,
        "internal_schema_validation_allowed_by_l25_17": True,
        "no_patchops_manifest_validation_added_by_l25_17": True,
        "no_package_execution_added_by_l25_17": True,
        "no_archive_extraction_added_by_l25_17": True,
        "no_browser_permission_added_by_l25_17": True,
        "no_pasteback_or_package_run_permission_added_by_l25_17": True,
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


def build_archive_manifest_schema_validation_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_schema_validation_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_MANIFEST_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_schema_validation_proof:
        return _default_payload(root, target_url)

    source = _l25_16_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_SCHEMA_VALIDATION_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    member_is_allowed = member_name == TARGET_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_16_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_16_future_schema_validation_authorized", "ok": source.get("archive_manifest_schema_validation_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_16_schema_validation_execution_false", "ok": source.get("archive_manifest_schema_validation_allowed") is False and source.get("manifest_schema_validated") is False},
        {"name": "source_l25_16_no_patchops_validation_execution_extract_browser_package", "ok": source.get("patchops_manifest_validation_performed") is False and source.get("package_execution_allowed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "schema_validation_proof_token_present", "ok": token_present},
        {"name": "schema_validation_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_validation", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_validation", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_manifest_member", "ok": member_is_allowed},
    ]

    validation_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    parsed: Any = None
    schema_summary: dict[str, Any] = {}
    validation_error: str | None = None
    if validation_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_MANIFEST_MEMBER_NAME)
            parsed = json.loads(data.decode("utf-8"))
            schema_summary = _validate_internal_schema(parsed)
            checks.extend([
                {"name": "manifest_payload_read_succeeded", "ok": len(data) > 0},
                {"name": "manifest_json_parse_succeeded", "ok": parsed is not None},
                {"name": "manifest_internal_schema_validation_succeeded", "ok": schema_summary.get("ok") is True},
                {"name": "manifest_internal_schema_validated_all_required_keys", "ok": sorted(schema_summary.get("validated_keys") or []) == sorted(REQUIRED_SCHEMA)},
            ])
        except Exception as exc:
            validation_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "manifest_schema_validation_attempt", "ok": False, "error": validation_error})

    schema_ok = bool(schema_summary.get("ok") is True)
    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_16_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_schema_validation_authorized": source.get("archive_manifest_schema_validation_authorization_granted_for_future_patch"),
            "schema_validation_allowed": source.get("archive_manifest_schema_validation_allowed"),
            "manifest_schema_validated": source.get("manifest_schema_validated"),
            "manifest_validation_performed": source.get("manifest_validation_performed"),
            "patchops_manifest_validation_performed": source.get("patchops_manifest_validation_performed"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_schema_validation_proof_requested": True,
        "archive_manifest_schema_validation_proof_token_present": token_present,
        "archive_manifest_schema_validation_proof_token_valid": token_valid,
        "archive_manifest_schema_validation_allowed": validation_allowed,
        "manifest_payload_read": validation_allowed,
        "manifest_payload_bytes_read": validation_allowed,
        "manifest_payload_json_parsed": validation_allowed and parsed is not None,
        "manifest_structure_parsed": validation_allowed and isinstance(parsed, dict),
        "manifest_payload_schema_validated": validation_allowed and schema_ok,
        "manifest_schema_validated": validation_allowed and schema_ok,
        "manifest_validation_performed": validation_allowed and schema_ok,
        "manifest_member_name_read": TARGET_MANIFEST_MEMBER_NAME if validation_allowed else None,
        "manifest_payload_byte_count": len(data),
        "manifest_schema_validation_error": validation_error,
        "manifest_schema_validation_scope": SCHEMA_VALIDATION_SCOPE,
        "manifest_schema_validation_summary": schema_summary,
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_17": True,
        "json_loads_allowed_by_l25_17": True,
        "internal_schema_validation_allowed_by_l25_17": True,
        "no_patchops_manifest_validation_added_by_l25_17": True,
        "no_package_execution_added_by_l25_17": True,
        "no_archive_extraction_added_by_l25_17": True,
        "no_browser_permission_added_by_l25_17": True,
        "no_pasteback_or_package_run_permission_added_by_l25_17": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.17 validates exactly one controlled synthetic manifest against a tiny internal schema.",
            "PatchOps manifest validation, package execution, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
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
        f"Schema Validated              : {payload.get('manifest_schema_validated')}",
        f"PatchOps Manifest Validation  : {payload.get('patchops_manifest_validation_performed')}",
        f"Package Execution             : {payload.get('package_run')}",
        f"Archive Extracted             : {payload.get('real_archive_candidate_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-archive-manifest-schema-validation-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_MANIFEST_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_schema_validation_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_schema_validation_proof=args.allow_archive_manifest_schema_validation_proof,
        authorization_token=args.authorization_token,
        candidate_archive_path=args.candidate_archive_path,
        member_name=args.member_name,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
