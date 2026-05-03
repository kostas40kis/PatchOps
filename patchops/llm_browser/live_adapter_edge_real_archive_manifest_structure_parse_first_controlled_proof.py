"""L25.14 first controlled archive manifest structure-parse proof.

This follows accepted L25.13. It reads exactly one controlled synthetic manifest
member, parses its JSON structure, and reports non-sensitive structural metadata
(top-level type, keys, and scalar value-type names). It does not perform schema
validation, PatchOps manifest validation, package execution, extraction, browser
automation, pasteback, or package-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_structure_parse_authorization_gate as l25_13
from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_first_controlled_proof as manifest_proof

PATCH = "L25.14"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.14 Microsoft Edge controlled runtime archive manifest structure parse first proof"
SOURCE_PATCH = "L25.13"
NEXT_PATCH = "L25.15 Microsoft Edge controlled runtime archive manifest structure parse broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = manifest_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_STRUCTURE_PARSE_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
MANIFEST_STRUCTURE_PARSE_SCOPE = "controlled_runtime_manifest_json_structure_parse_only_no_schema_validation_no_execution"

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


def _l25_13_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_13.build_archive_manifest_structure_parse_authorization_gate(
            repo_root,
            allow_archive_manifest_structure_parse_authorization=True,
            authorization_token=l25_13.REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.13 manifest structure parse authorization readback failed: {type(exc).__name__}: {exc}"}


def _shape_summary(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        keys = sorted(str(key) for key in value.keys())
        scalar_value_types = {str(key): type(value[key]).__name__ for key in keys if not isinstance(value.get(key), (dict, list))}
        nested_keys = sorted(str(key) for key in keys if isinstance(value.get(key), (dict, list)))
        return {
            "top_level_type": "object",
            "top_level_key_count": len(keys),
            "top_level_keys": keys,
            "scalar_value_types": scalar_value_types,
            "nested_keys": nested_keys,
        }
    if isinstance(value, list):
        return {"top_level_type": "array", "top_level_length": len(value), "top_level_keys": []}
    return {"top_level_type": type(value).__name__, "top_level_keys": []}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_13_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_13_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_13_future_structure_parse_authorized", "ok": source.get("archive_manifest_structure_parse_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_13_parse_execution_false", "ok": source.get("manifest_payload_json_parsed") is False and source.get("manifest_structure_parsed") is False},
        {"name": "default_manifest_structure_parse_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_13_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_manifest_structure_parse_authorized": source.get("archive_manifest_structure_parse_authorization_granted_for_future_patch"),
            "manifest_structure_parse_allowed": source.get("archive_manifest_structure_parse_allowed"),
            "manifest_payload_json_parsed": source.get("manifest_payload_json_parsed"),
            "manifest_structure_parsed": source.get("manifest_structure_parsed"),
            "manifest_validation_performed": source.get("manifest_validation_performed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_structure_parse_proof_requested": False,
        "archive_manifest_structure_parse_proof_token_present": False,
        "archive_manifest_structure_parse_proof_token_valid": False,
        "archive_manifest_structure_parse_allowed": False,
        "manifest_payload_read": False,
        "manifest_payload_bytes_read": False,
        "manifest_payload_json_parsed": False,
        "manifest_structure_parsed": False,
        "manifest_member_name_read": None,
        "manifest_structure_parse_scope": "default_readback_only_no_json_parse",
        "manifest_structure_summary": {},
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_14": True,
        "json_loads_allowed_by_l25_14": True,
        "no_manifest_schema_validation_added_by_l25_14": True,
        "no_package_execution_added_by_l25_14": True,
        "no_archive_extraction_added_by_l25_14": True,
        "no_browser_permission_added_by_l25_14": True,
        "no_pasteback_or_package_run_permission_added_by_l25_14": True,
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


def build_archive_manifest_structure_parse_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_structure_parse_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_MANIFEST_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_structure_parse_proof:
        return _default_payload(root, target_url)

    source = _l25_13_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_STRUCTURE_PARSE_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    member_is_allowed = member_name == TARGET_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_13_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_13_future_structure_parse_authorized", "ok": source.get("archive_manifest_structure_parse_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_13_parse_execution_false", "ok": source.get("manifest_payload_json_parsed") is False and source.get("manifest_structure_parsed") is False},
        {"name": "source_l25_13_no_validation_extract_browser_package", "ok": source.get("manifest_validation_performed") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "manifest_structure_parse_proof_token_present", "ok": token_present},
        {"name": "manifest_structure_parse_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_parse", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_parse", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_manifest_member", "ok": member_is_allowed},
    ]

    parse_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    parsed: Any = None
    summary: dict[str, Any] = {}
    parse_error: str | None = None
    if parse_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_MANIFEST_MEMBER_NAME)
            parsed = json.loads(data.decode("utf-8"))
            summary = _shape_summary(parsed)
            checks.extend([
                {"name": "manifest_payload_read_succeeded", "ok": len(data) > 0},
                {"name": "manifest_json_parse_succeeded", "ok": parsed is not None},
                {"name": "manifest_structure_summary_top_level_object", "ok": summary.get("top_level_type") == "object"},
                {"name": "manifest_structure_summary_has_keys", "ok": isinstance(summary.get("top_level_keys"), list) and len(summary.get("top_level_keys", [])) > 0},
            ])
        except Exception as exc:
            parse_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "manifest_structure_parse_attempt", "ok": False, "error": parse_error})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_13_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_manifest_structure_parse_authorized": source.get("archive_manifest_structure_parse_authorization_granted_for_future_patch"),
            "manifest_structure_parse_allowed": source.get("archive_manifest_structure_parse_allowed"),
            "manifest_payload_json_parsed": source.get("manifest_payload_json_parsed"),
            "manifest_structure_parsed": source.get("manifest_structure_parsed"),
            "manifest_validation_performed": source.get("manifest_validation_performed"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_structure_parse_proof_requested": True,
        "archive_manifest_structure_parse_proof_token_present": token_present,
        "archive_manifest_structure_parse_proof_token_valid": token_valid,
        "archive_manifest_structure_parse_allowed": parse_allowed,
        "manifest_payload_read": parse_allowed,
        "manifest_payload_bytes_read": parse_allowed,
        "manifest_payload_json_parsed": parse_allowed and parsed is not None,
        "manifest_structure_parsed": parse_allowed and bool(summary),
        "manifest_member_name_read": TARGET_MANIFEST_MEMBER_NAME if parse_allowed else None,
        "manifest_payload_byte_count": len(data),
        "manifest_structure_parse_error": parse_error,
        "manifest_structure_parse_scope": MANIFEST_STRUCTURE_PARSE_SCOPE,
        "manifest_structure_summary": summary,
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_14": True,
        "json_loads_allowed_by_l25_14": True,
        "no_manifest_schema_validation_added_by_l25_14": True,
        "no_package_execution_added_by_l25_14": True,
        "no_archive_extraction_added_by_l25_14": True,
        "no_browser_permission_added_by_l25_14": True,
        "no_pasteback_or_package_run_permission_added_by_l25_14": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.14 parses exactly one controlled synthetic manifest payload as JSON and reports structural metadata only.",
            "Schema validation, PatchOps manifest validation, package execution, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
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
        f"Manifest JSON Parsed          : {payload.get('manifest_payload_json_parsed')}",
        f"Manifest Structure Parsed     : {payload.get('manifest_structure_parsed')}",
        f"Manifest Validation           : {payload.get('manifest_validation_performed')}",
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
    parser.add_argument("--allow-archive-manifest-structure-parse-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_MANIFEST_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_structure_parse_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_structure_parse_proof=args.allow_archive_manifest_structure_parse_proof,
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
