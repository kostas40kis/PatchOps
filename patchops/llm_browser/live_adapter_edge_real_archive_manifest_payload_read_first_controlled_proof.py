"""L25.11 first controlled archive manifest payload-read proof.

This follows accepted L25.10. It reads bytes from exactly one controlled,
synthetic manifest member after explicit token authorization. It records byte
count and SHA-256 only. It does not perform manifest validation, execute a
package, extract members, start a browser, paste, or send.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_payload_read_authorization_gate as l25_10
from patchops.llm_browser import live_adapter_edge_real_archive_member_byte_read_first_controlled_proof as member_proof

PATCH = "L25.11"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.11 Microsoft Edge controlled runtime archive manifest payload-read first proof"
SOURCE_PATCH = "L25.10"
NEXT_PATCH = "L25.12 Microsoft Edge controlled runtime archive manifest payload-read broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = member_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_MANIFEST_PAYLOAD_READ_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MANIFEST_PAYLOAD_READ_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_MANIFEST_MEMBER_NAME = "bundle/manifest.json"
NON_MANIFEST_MEMBER_NAME = "bundle/run_with_patchops.ps1"

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


def _l25_10_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_10.build_archive_manifest_payload_read_authorization_gate(
            repo_root,
            allow_archive_manifest_payload_read_authorization=True,
            authorization_token=l25_10.REQUIRED_ARCHIVE_MANIFEST_PAYLOAD_READ_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.10 manifest payload-read authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_10_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_10_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_10_future_manifest_payload_read_authorized", "ok": source.get("archive_manifest_payload_read_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_10_manifest_payload_read_execution_false", "ok": source.get("manifest_payload_read") is False},
        {"name": "default_manifest_payload_read_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_10_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_manifest_payload_read_authorized": source.get("archive_manifest_payload_read_authorization_granted_for_future_patch"),
            "manifest_payload_read_allowed": source.get("archive_manifest_payload_read_allowed"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "manifest_payload_bytes_read": source.get("manifest_payload_bytes_read"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_payload_read_proof_requested": False,
        "archive_manifest_payload_read_proof_token_present": False,
        "archive_manifest_payload_read_proof_token_valid": False,
        "archive_manifest_payload_read_allowed": False,
        "manifest_payload_read": False,
        "manifest_payload_bytes_read": False,
        "manifest_payload_sha256_read": False,
        "manifest_payload_byte_count": 0,
        "manifest_payload_sha256": None,
        "manifest_member_name_read": None,
        "manifest_payload_read_scope": "default_readback_only_no_manifest_payload_read",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_11": True,
        "no_manifest_validation_added_by_l25_11": True,
        "no_archive_extraction_added_by_l25_11": True,
        "no_browser_permission_added_by_l25_11": True,
        "no_pasteback_or_package_run_permission_added_by_l25_11": True,
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


def build_archive_manifest_payload_read_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_manifest_payload_read_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_MANIFEST_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_manifest_payload_read_proof:
        return _default_payload(root, target_url)

    source = _l25_10_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MANIFEST_PAYLOAD_READ_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    member_is_allowed = member_name == TARGET_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_10_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_10_future_manifest_payload_read_authorized", "ok": source.get("archive_manifest_payload_read_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_10_manifest_payload_read_execution_false", "ok": source.get("manifest_payload_read") is False},
        {"name": "source_l25_10_no_extract_browser_package", "ok": source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "manifest_payload_read_proof_token_present", "ok": token_present},
        {"name": "manifest_payload_read_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_manifest_read", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_manifest_read", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_manifest_member", "ok": member_is_allowed},
    ]

    read_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    digest: str | None = None
    read_error: str | None = None
    if read_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_MANIFEST_MEMBER_NAME)
            digest = hashlib.sha256(data).hexdigest()
            checks.extend([
                {"name": "manifest_payload_read_succeeded", "ok": len(data) > 0},
                {"name": "manifest_payload_sha256_length", "ok": isinstance(digest, str) and len(digest) == 64},
                {"name": "manifest_payload_sha256_hex", "ok": isinstance(digest, str) and all(ch in "0123456789abcdef" for ch in digest)},
            ])
        except Exception as exc:
            read_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "manifest_payload_read_attempt", "ok": False, "error": read_error})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_10_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_manifest_payload_read_authorized": source.get("archive_manifest_payload_read_authorization_granted_for_future_patch"),
            "manifest_payload_read_allowed": source.get("archive_manifest_payload_read_allowed"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "manifest_payload_bytes_read": source.get("manifest_payload_bytes_read"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_manifest_payload_read_proof_requested": True,
        "archive_manifest_payload_read_proof_token_present": token_present,
        "archive_manifest_payload_read_proof_token_valid": token_valid,
        "archive_manifest_payload_read_allowed": read_allowed,
        "manifest_payload_read": read_allowed,
        "manifest_payload_bytes_read": read_allowed,
        "manifest_payload_sha256_read": read_allowed and digest is not None,
        "manifest_payload_byte_count": len(data),
        "manifest_payload_sha256": digest,
        "manifest_member_name_read": TARGET_MANIFEST_MEMBER_NAME if read_allowed else None,
        "manifest_payload_read_error": read_error,
        "manifest_payload_read_scope": "controlled_runtime_manifest_payload_bytes_only_no_validation_no_execution",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_11": True,
        "no_manifest_validation_added_by_l25_11": True,
        "no_archive_extraction_added_by_l25_11": True,
        "no_browser_permission_added_by_l25_11": True,
        "no_pasteback_or_package_run_permission_added_by_l25_11": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.11 reads bytes from exactly one controlled synthetic manifest member.",
            "Manifest schema validation, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
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
        f"Manifest Payload Read         : {payload.get('manifest_payload_read')}",
        f"Manifest Member Name          : {payload.get('manifest_member_name_read')}",
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
    parser.add_argument("--allow-archive-manifest-payload-read-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_MANIFEST_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_manifest_payload_read_first_controlled_proof(
        args.repo_root,
        allow_archive_manifest_payload_read_proof=args.allow_archive_manifest_payload_read_proof,
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
