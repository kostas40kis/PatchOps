"""L25.8 first controlled archive member-byte-read proof.

This follows accepted L25.7. It reads bytes from exactly one controlled,
non-manifest synthetic archive member after explicit token authorization. It does
not read manifest payload bytes, extract members, start a browser, paste, send,
or run packages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence
import zipfile

from patchops.llm_browser import live_adapter_edge_real_archive_member_byte_read_authorization_gate as l25_07
from patchops.llm_browser import live_adapter_edge_real_archive_listing_first_controlled_proof as listing_proof

PATCH = "L25.8"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.8 Microsoft Edge controlled runtime archive member-byte-read first proof"
SOURCE_PATCH = "L25.7"
NEXT_PATCH = "L25.9 Microsoft Edge controlled runtime archive member-byte-read broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = listing_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_ARCHIVE_MEMBER_BYTE_READ_PROOF_TOKEN = "PATCHOPS_L25_EDGE_REAL_ARCHIVE_MEMBER_BYTE_READ_FIRST_CONTROLLED_PROOF_AUTHORIZED"
TARGET_CONTROLLED_MEMBER_NAME = "bundle/run_with_patchops.ps1"
FORBIDDEN_MANIFEST_MEMBER_NAME = "bundle/manifest.json"

ALWAYS_FALSE_FIELDS = (
    "manifest_payload_read",
    "manifest_payload_bytes_read",
    "real_archive_manifest_read",
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


def _l25_07_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_07.build_archive_member_byte_read_authorization_gate(
            repo_root,
            allow_archive_member_byte_read_authorization=True,
            authorization_token=l25_07.REQUIRED_ARCHIVE_MEMBER_BYTE_READ_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.7 member-byte-read authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l25_07_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l25_07_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_07_future_member_byte_read_authorized", "ok": source.get("archive_member_byte_read_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_07_member_byte_read_execution_false", "ok": source.get("archive_member_bytes_read") is False},
        {"name": "default_member_byte_read_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_07_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_member_byte_read_authorized": source.get("archive_member_byte_read_authorization_granted_for_future_patch"),
            "member_byte_read_allowed": source.get("archive_member_byte_read_allowed"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "archive_member_payload_read": source.get("archive_member_payload_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_member_byte_read_proof_requested": False,
        "archive_member_byte_read_proof_token_present": False,
        "archive_member_byte_read_proof_token_valid": False,
        "archive_member_byte_read_allowed": False,
        "archive_member_bytes_read": False,
        "archive_member_payload_read": False,
        "archive_member_payload_bytes_read": False,
        "archive_member_payload_sha256_read": False,
        "archive_member_payload_byte_count": 0,
        "archive_member_payload_sha256": None,
        "archive_member_name_read": None,
        "archive_member_read_scope": "default_readback_only_no_member_byte_read",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "zipfile_import_allowed_by_l25_8": True,
        "no_manifest_payload_read_added_by_l25_8": True,
        "no_archive_extraction_added_by_l25_8": True,
        "no_browser_permission_added_by_l25_8": True,
        "no_pasteback_or_package_run_permission_added_by_l25_8": True,
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


def build_archive_member_byte_read_first_controlled_proof(
    repo_root: str | Path | None = None,
    *,
    allow_archive_member_byte_read_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    member_name: str = TARGET_CONTROLLED_MEMBER_NAME,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_archive_member_byte_read_proof:
        return _default_payload(root, target_url)

    source = _l25_07_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_ARCHIVE_MEMBER_BYTE_READ_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))
    member_is_allowed = member_name == TARGET_CONTROLLED_MEMBER_NAME and member_name != FORBIDDEN_MANIFEST_MEMBER_NAME

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_07_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l25_07_future_member_byte_read_authorized", "ok": source.get("archive_member_byte_read_authorization_granted_for_future_patch") is True},
        {"name": "source_l25_07_member_byte_read_execution_false", "ok": source.get("archive_member_bytes_read") is False},
        {"name": "source_l25_07_no_manifest_extract_browser_package", "ok": source.get("manifest_payload_read") is False and source.get("real_archive_candidate_extracted") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "member_byte_read_proof_token_present", "ok": token_present},
        {"name": "member_byte_read_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_member_read", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_member_read", "ok": candidate.is_file()},
        {"name": "candidate_suffix_is_zip", "ok": candidate.suffix == ".zip"},
        {"name": "target_member_is_non_manifest_controlled_member", "ok": member_is_allowed},
    ]

    read_allowed = bool(all(check.get("ok") for check in checks))
    data = b""
    digest: str | None = None
    read_error: str | None = None
    if read_allowed:
        try:
            with zipfile.ZipFile(candidate, mode="r") as archive:
                data = archive.read(TARGET_CONTROLLED_MEMBER_NAME)
            digest = hashlib.sha256(data).hexdigest()
            checks.extend([
                {"name": "member_byte_read_succeeded", "ok": len(data) > 0},
                {"name": "member_payload_sha256_length", "ok": isinstance(digest, str) and len(digest) == 64},
                {"name": "member_payload_sha256_hex", "ok": isinstance(digest, str) and all(ch in "0123456789abcdef" for ch in digest)},
            ])
        except Exception as exc:
            read_error = f"{type(exc).__name__}: {exc}"
            checks.append({"name": "member_byte_read_attempt", "ok": False, "error": read_error})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l25_07_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_member_byte_read_authorized": source.get("archive_member_byte_read_authorization_granted_for_future_patch"),
            "member_byte_read_allowed": source.get("archive_member_byte_read_allowed"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "archive_member_payload_read": source.get("archive_member_payload_read"),
            "manifest_payload_read": source.get("manifest_payload_read"),
            "archive_extracted": source.get("real_archive_candidate_extracted"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "archive_member_byte_read_proof_requested": True,
        "archive_member_byte_read_proof_token_present": token_present,
        "archive_member_byte_read_proof_token_valid": token_valid,
        "archive_member_byte_read_allowed": read_allowed,
        "archive_member_bytes_read": read_allowed,
        "archive_member_payload_read": read_allowed,
        "archive_member_payload_bytes_read": read_allowed,
        "archive_member_payload_sha256_read": read_allowed and digest is not None,
        "archive_member_payload_byte_count": len(data),
        "archive_member_payload_sha256": digest,
        "archive_member_name_read": TARGET_CONTROLLED_MEMBER_NAME if read_allowed else None,
        "archive_member_read_error": read_error,
        "archive_member_read_scope": "controlled_runtime_non_manifest_member_bytes_only_no_manifest_payload",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "zipfile_import_allowed_by_l25_8": True,
        "no_manifest_payload_read_added_by_l25_8": True,
        "no_archive_extraction_added_by_l25_8": True,
        "no_browser_permission_added_by_l25_8": True,
        "no_pasteback_or_package_run_permission_added_by_l25_8": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.8 reads bytes from exactly one controlled non-manifest member.",
            "Manifest payload, extraction, browser, pasteback, send/submit, and package-run remain disabled.",
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
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
        f"Member Payload Read           : {payload.get('archive_member_payload_read')}",
        f"Member Name Read              : {payload.get('archive_member_name_read')}",
        f"Manifest Payload Read         : {payload.get('manifest_payload_read')}",
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
    parser.add_argument("--allow-archive-member-byte-read-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--member-name", default=TARGET_CONTROLLED_MEMBER_NAME)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_member_byte_read_first_controlled_proof(
        args.repo_root,
        allow_archive_member_byte_read_proof=args.allow_archive_member_byte_read_proof,
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
