"""L24.4 real downloaded-archive candidate filesystem stat proof.

This follows accepted L24.3. It performs only a filesystem metadata stat proof for
an explicitly authorized candidate path. It does not hash file contents, read file
bytes, open/list/extract/read an archive, start a browser, paste, send, or run
packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_filesystem_stat_authorization_gate as l24_03

PATCH = "L24.4"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.4 Microsoft Edge real downloaded-archive candidate filesystem stat proof"
SOURCE_PATCH = "L24.3"
NEXT_PATCH = "L24.5 Microsoft Edge real downloaded-archive candidate filesystem stat broad checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l24_04_candidate_stat_fixture/future_real_patchops_bundle.zip"
REQUIRED_REAL_ARCHIVE_CANDIDATE_STAT_PROOF_TOKEN = "PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_FILESYSTEM_STAT_PROOF_AUTHORIZED"

ALWAYS_FALSE_FIELDS = (
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_hash_performed",
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


def _l24_03_authorized_payload(repo_root: Path, candidate_archive_path: str | None, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_03.build_real_archive_candidate_filesystem_stat_authorization_gate(
            repo_root,
            allow_real_archive_candidate_stat_authorization=True,
            authorization_token=l24_03.REQUIRED_REAL_ARCHIVE_CANDIDATE_STAT_AUTHORIZATION_TOKEN,
            candidate_archive_path=candidate_archive_path,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.3 stat authorization readback failed: {type(exc).__name__}: {exc}"}


def _default_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l24_03_authorized_payload(root, str(root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH), target_url)
    checks = [
        {"name": "source_l24_03_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_03_future_stat_authorized", "ok": source.get("real_archive_candidate_stat_authorization_granted_for_future_patch") is True},
        {"name": "source_l24_03_stat_execution_false", "ok": source.get("real_archive_candidate_path_stat_performed") is False},
        {"name": "default_stat_proof_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_03_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_stat_authorized": source.get("real_archive_candidate_stat_authorization_granted_for_future_patch"),
            "stat_performed": source.get("real_archive_candidate_path_stat_performed"),
            "hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "candidate_exists_checked": source.get("real_archive_candidate_exists"),
            "candidate_size_read": source.get("real_archive_candidate_size_bytes_read"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "candidate_filesystem_stat_proof_requested": False,
        "candidate_filesystem_stat_proof_token_present": False,
        "candidate_filesystem_stat_proof_token_valid": False,
        "real_archive_candidate_path_stat_allowed": False,
        "real_archive_candidate_path_stat_performed": False,
        "real_archive_candidate_exists": False,
        "real_archive_candidate_is_file": False,
        "real_archive_candidate_size_bytes_read": False,
        "real_archive_candidate_size_bytes": None,
        "real_archive_candidate_suffix_checked_on_filesystem": False,
        "real_archive_candidate_suffix": None,
        "real_archive_candidate_mtime_read": False,
        "real_archive_candidate_mtime_ns": None,
        "candidate_stat_scope": "default_readback_only_no_filesystem_stat",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "no_hash_or_archive_open_permission_added_by_l24_4": True,
        "no_browser_permission_added_by_l24_4": True,
        "no_pasteback_or_package_run_permission_added_by_l24_4": True,
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


def build_real_archive_candidate_filesystem_stat_proof(
    repo_root: str | Path | None = None,
    *,
    allow_real_archive_candidate_stat_proof: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = Path(candidate_archive_path) if candidate_archive_path else root / DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
    candidate_text = str(candidate)
    if not allow_real_archive_candidate_stat_proof:
        return _default_payload(root, target_url)

    source = _l24_03_authorized_payload(root, candidate_text, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_ARCHIVE_CANDIDATE_STAT_PROOF_TOKEN
    candidate_under_runtime = str(candidate.resolve()).startswith(str((root / "data" / "runtime" / "browser_downloads").resolve()))

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_03_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_03_future_stat_authorized", "ok": source.get("real_archive_candidate_stat_authorization_granted_for_future_patch") is True},
        {"name": "source_l24_03_stat_execution_false", "ok": source.get("real_archive_candidate_path_stat_performed") is False},
        {"name": "stat_proof_token_present", "ok": token_present},
        {"name": "stat_proof_token_valid", "ok": token_valid},
        {"name": "candidate_path_under_runtime_browser_downloads", "ok": candidate_under_runtime},
    ]

    stat_allowed = bool(all(check.get("ok") for check in checks))
    exists = False
    is_file = False
    size_bytes: int | None = None
    suffix: str | None = None
    mtime_ns: int | None = None
    if stat_allowed:
        try:
            exists = candidate.exists()
            is_file = candidate.is_file()
            suffix = candidate.suffix
            if exists and is_file:
                stat_result = candidate.stat()
                size_bytes = int(stat_result.st_size)
                mtime_ns = int(stat_result.st_mtime_ns)
            checks.extend([
                {"name": "candidate_exists_checked_true", "ok": exists is True},
                {"name": "candidate_is_file_true", "ok": is_file is True},
                {"name": "candidate_suffix_is_zip_by_filesystem_stat_proof", "ok": suffix == ".zip"},
                {"name": "candidate_size_read_positive", "ok": isinstance(size_bytes, int) and size_bytes > 0},
                {"name": "candidate_mtime_read", "ok": isinstance(mtime_ns, int) and mtime_ns > 0},
            ])
        except Exception as exc:
            checks.append({"name": "candidate_filesystem_stat_attempt", "ok": False, "error": f"{type(exc).__name__}: {exc}"})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_03_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_stat_authorized": source.get("real_archive_candidate_stat_authorization_granted_for_future_patch"),
            "stat_performed": source.get("real_archive_candidate_path_stat_performed"),
            "hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "candidate_exists_checked": source.get("real_archive_candidate_exists"),
            "candidate_size_read": source.get("real_archive_candidate_size_bytes_read"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "candidate_filesystem_stat_proof_requested": True,
        "candidate_filesystem_stat_proof_token_present": token_present,
        "candidate_filesystem_stat_proof_token_valid": token_valid,
        "real_archive_candidate_path_stat_allowed": stat_allowed,
        "real_archive_candidate_path_stat_performed": stat_allowed,
        "real_archive_candidate_exists": exists,
        "real_archive_candidate_is_file": is_file,
        "real_archive_candidate_size_bytes_read": stat_allowed and isinstance(size_bytes, int),
        "real_archive_candidate_size_bytes": size_bytes,
        "real_archive_candidate_suffix_checked_on_filesystem": stat_allowed,
        "real_archive_candidate_suffix": suffix,
        "real_archive_candidate_mtime_read": stat_allowed and isinstance(mtime_ns, int),
        "real_archive_candidate_mtime_ns": mtime_ns,
        "candidate_stat_scope": "controlled_runtime_candidate_filesystem_metadata_only",
        "controlled_runtime_candidate_fixture": True,
        "controlled_candidate_relative_path": DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH,
        "candidate_archive_path": candidate_text,
        "no_hash_or_archive_open_permission_added_by_l24_4": True,
        "no_browser_permission_added_by_l24_4": True,
        "no_pasteback_or_package_run_permission_added_by_l24_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L24.4 reads only filesystem metadata for a controlled runtime candidate fixture.",
            "No file hash, downloaded file bytes, archive open/list/extract/read, browser, pasteback, send/submit, or package-run activity is performed.",
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
        f"Stat Performed                : {payload.get('real_archive_candidate_path_stat_performed')}",
        f"Candidate Exists              : {payload.get('real_archive_candidate_exists')}",
        f"Candidate Size Read           : {payload.get('real_archive_candidate_size_bytes_read')}",
        f"Candidate Size Bytes          : {payload.get('real_archive_candidate_size_bytes')}",
        f"Hash Performed                : {payload.get('real_archive_candidate_path_hash_performed')}",
        f"Real Archive Opened           : {payload.get('real_archive_opened')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--allow-real-archive-candidate-stat-proof", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_candidate_filesystem_stat_proof(
        args.repo_root,
        allow_real_archive_candidate_stat_proof=args.allow_real_archive_candidate_stat_proof,
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
