"""L24.7 first controlled hash proof for a real downloaded-archive candidate.

This follows accepted L24.6. It computes SHA-256 only for the controlled runtime
candidate fixture after explicit token authorization. It does not open, list,
extract, or read an archive as an archive, and it does not start a browser,
paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_hash_authorization_gate as l24_06
from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_proof as stat_proof

PATCH = "L24.7"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.7 Microsoft Edge real downloaded-archive candidate first controlled hash proof"
SOURCE_PATCH = "L24.6"
NEXT_PATCH = "L24.8 Microsoft Edge real downloaded-archive candidate hash broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = stat_proof.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_PROOF_TOKEN = "PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_FIRST_CONTROLLED_HASH_PROOF_AUTHORIZED"

ALWAYS_FALSE_FIELDS = (
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
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


def _l24_06_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_06.build_real_archive_candidate_hash_authorization_gate(
            repo_root,
            allow_real_archive_candidate_hash_authorization=True,
            authorization_token=l24_06.REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_AUTHORIZATION_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.6 hash authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l24_06_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l24_06_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_06_future_hash_authorized", "ok": source.get("real_archive_candidate_hash_authorization_granted_for_future_patch") is True},
        {"name": "source_l24_06_hash_execution_false", "ok": source.get("real_archive_candidate_path_hash_performed") is False},
        {"name": "default_hash_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_06_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_hash_authorized": source.get("real_archive_candidate_hash_authorization_granted_for_future_patch"),
            "hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "candidate_hash_proof_requested": False,
        "candidate_hash_proof_token_present": False,
        "candidate_hash_proof_token_valid": False,
        "real_archive_candidate_path_hash_allowed": False,
        "real_archive_candidate_path_hash_performed": False,
        "downloaded_file_bytes_read": False,
        "downloaded_file_hash_performed": False,
        "real_archive_candidate_sha256_read": False,
        "real_archive_candidate_sha256": None,
        "real_archive_candidate_bytes_read_count": 0,
        "candidate_hash_scope": "default_readback_only_no_hash",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "no_archive_open_permission_added_by_l24_7": True,
        "no_browser_permission_added_by_l24_7": True,
        "no_pasteback_or_package_run_permission_added_by_l24_7": True,
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


def build_real_archive_candidate_first_controlled_hash_proof(
    repo_root: str | Path | None = None,
    *,
    allow_real_archive_candidate_hash_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    if not allow_real_archive_candidate_hash_proof:
        return _default_payload(root, target_url)

    source = _l24_06_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_06_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_06_future_hash_authorized", "ok": source.get("real_archive_candidate_hash_authorization_granted_for_future_patch") is True},
        {"name": "source_l24_06_hash_execution_false", "ok": source.get("real_archive_candidate_path_hash_performed") is False},
        {"name": "source_l24_06_no_archive_browser_package", "ok": source.get("real_archive_candidate_opened") is False and source.get("browser_started") is False and source.get("package_run") is False},
        {"name": "hash_proof_token_present", "ok": token_present},
        {"name": "hash_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
        {"name": "candidate_exists_before_hash", "ok": candidate.exists()},
        {"name": "candidate_is_file_before_hash", "ok": candidate.is_file()},
    ]

    hash_allowed = bool(all(check.get("ok") for check in checks))
    digest: str | None = None
    byte_count = 0
    if hash_allowed:
        try:
            data = candidate.read_bytes()
            byte_count = len(data)
            digest = hashlib.sha256(data).hexdigest()
            checks.extend([
                {"name": "candidate_bytes_read_for_hash", "ok": byte_count > 0},
                {"name": "candidate_sha256_length", "ok": isinstance(digest, str) and len(digest) == 64},
                {"name": "candidate_sha256_hex", "ok": isinstance(digest, str) and all(ch in "0123456789abcdef" for ch in digest)},
            ])
        except Exception as exc:
            checks.append({"name": "candidate_hash_attempt", "ok": False, "error": f"{type(exc).__name__}: {exc}"})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_06_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_hash_authorized": source.get("real_archive_candidate_hash_authorization_granted_for_future_patch"),
            "hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "candidate_hash_proof_requested": True,
        "candidate_hash_proof_token_present": token_present,
        "candidate_hash_proof_token_valid": token_valid,
        "real_archive_candidate_path_hash_allowed": hash_allowed,
        "real_archive_candidate_path_hash_performed": hash_allowed,
        "downloaded_file_bytes_read": hash_allowed,
        "downloaded_file_hash_performed": hash_allowed,
        "real_archive_candidate_sha256_read": hash_allowed and digest is not None,
        "real_archive_candidate_sha256": digest,
        "real_archive_candidate_bytes_read_count": byte_count,
        "candidate_hash_scope": "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": str(candidate),
        "no_archive_open_permission_added_by_l24_7": True,
        "no_browser_permission_added_by_l24_7": True,
        "no_pasteback_or_package_run_permission_added_by_l24_7": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L24.7 computes SHA-256 only over the controlled runtime candidate fixture bytes.",
            "No archive open/list/extract/read, browser, pasteback, send/submit, or package-run activity is performed.",
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
        f"Hash Performed                : {payload.get('real_archive_candidate_path_hash_performed')}",
        f"Bytes Read                    : {payload.get('downloaded_file_bytes_read')}",
        f"SHA256 Read                   : {payload.get('real_archive_candidate_sha256_read')}",
        f"Archive Opened                : {payload.get('real_archive_opened')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-real-archive-candidate-hash-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_candidate_first_controlled_hash_proof(
        args.repo_root,
        allow_real_archive_candidate_hash_proof=args.allow_real_archive_candidate_hash_proof,
        authorization_token=args.authorization_token,
        candidate_archive_path=args.candidate_archive_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
