"""L24.8 broad checkpoint for controlled candidate hash proof.

This follows accepted L24.7. It replays the accepted controlled runtime candidate
SHA-256 proof and summarizes the L24.6-L24.7 hash ladder. It does not open,
list, extract, or read an archive as an archive, and it does not start a browser,
paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_first_controlled_hash_proof as l24_07

PATCH = "L24.8"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.8 Microsoft Edge real downloaded-archive candidate hash broad checkpoint"
SOURCE_PATCH = "L24.7"
SOURCE_LADDER = (
    "L24.6 candidate hash authorization gate",
    "L24.7 first controlled SHA-256 proof over controlled runtime fixture bytes",
)
NEXT_PATCH = "L24.9 Microsoft Edge real downloaded-archive candidate metadata/hash final acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

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


def _l24_07_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_07.build_real_archive_candidate_first_controlled_hash_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.7 default readback failed: {type(exc).__name__}: {exc}"}


def _l24_07_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l24_07.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l24_07.build_real_archive_candidate_first_controlled_hash_proof(
            repo_root,
            allow_real_archive_candidate_hash_proof=True,
            authorization_token=l24_07.REQUIRED_REAL_ARCHIVE_CANDIDATE_HASH_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.7 authorized readback failed: {type(exc).__name__}: {exc}"}


def _is_lower_hex_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def build_real_archive_candidate_hash_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l24_07_default_payload(root, target_url)
    authorized_payload = _l24_07_authorized_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_07_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l24_07_default_is_passive", "ok": default_payload.get("real_archive_candidate_path_hash_performed") is False},
        {"name": "source_l24_07_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l24_07_patch_marker", "ok": authorized_payload.get("patch") == "L24.7"},
        {"name": "source_l24_07_hash_allowed", "ok": authorized_payload.get("real_archive_candidate_path_hash_allowed") is True},
        {"name": "source_l24_07_hash_performed", "ok": authorized_payload.get("real_archive_candidate_path_hash_performed") is True},
        {"name": "source_l24_07_bytes_read_for_hash", "ok": authorized_payload.get("downloaded_file_bytes_read") is True and authorized_payload.get("downloaded_file_hash_performed") is True},
        {"name": "source_l24_07_sha256_read", "ok": authorized_payload.get("real_archive_candidate_sha256_read") is True and _is_lower_hex_sha256(authorized_payload.get("real_archive_candidate_sha256"))},
        {"name": "source_l24_07_byte_count_positive", "ok": isinstance(authorized_payload.get("real_archive_candidate_bytes_read_count"), int) and authorized_payload.get("real_archive_candidate_bytes_read_count") > 0},
        {"name": "source_l24_07_scope_file_bytes_no_archive_open", "ok": authorized_payload.get("candidate_hash_scope") == "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open"},
        {"name": "source_l24_07_no_archive_open_list_extract", "ok": authorized_payload.get("real_archive_candidate_opened") is False and authorized_payload.get("real_archive_candidate_listed") is False and authorized_payload.get("real_archive_candidate_extracted") is False},
        {"name": "source_l24_07_no_manifest_browser_package", "ok": authorized_payload.get("real_archive_manifest_read") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "hash_ladder_checkpoint": True,
        "l24_candidate_hash_ladder_complete": ok,
        "source_l24_07_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "hash_performed": default_payload.get("real_archive_candidate_path_hash_performed"),
            "hash_scope": default_payload.get("candidate_hash_scope"),
        },
        "source_l24_07_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l24_06_ok": authorized_payload.get("source_l24_06_summary", {}).get("ok"),
            "source_l24_06_future_authorized": authorized_payload.get("source_l24_06_summary", {}).get("future_hash_authorized"),
            "hash_allowed": authorized_payload.get("real_archive_candidate_path_hash_allowed"),
            "hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed"),
            "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read"),
            "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed"),
            "sha256_read": authorized_payload.get("real_archive_candidate_sha256_read"),
            "sha256": authorized_payload.get("real_archive_candidate_sha256"),
            "bytes_read_count": authorized_payload.get("real_archive_candidate_bytes_read_count"),
            "hash_scope": authorized_payload.get("candidate_hash_scope"),
            "candidate_archive_opened": authorized_payload.get("real_archive_candidate_opened"),
            "candidate_archive_listed": authorized_payload.get("real_archive_candidate_listed"),
            "candidate_archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_hash_scope": "controlled_runtime_candidate_sha256_file_bytes_only_no_archive_open",
        "accepted_hash_allowed": authorized_payload.get("real_archive_candidate_path_hash_allowed") is True,
        "accepted_hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed") is True,
        "accepted_file_bytes_read_for_hash": authorized_payload.get("downloaded_file_bytes_read") is True,
        "accepted_downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed") is True,
        "accepted_sha256_read": authorized_payload.get("real_archive_candidate_sha256_read") is True,
        "accepted_sha256_is_lower_hex": _is_lower_hex_sha256(authorized_payload.get("real_archive_candidate_sha256")),
        "accepted_bytes_read_count": authorized_payload.get("real_archive_candidate_bytes_read_count"),
        "real_archive_candidate_path_hash_allowed": authorized_payload.get("real_archive_candidate_path_hash_allowed") is True,
        "real_archive_candidate_path_hash_performed": authorized_payload.get("real_archive_candidate_path_hash_performed") is True,
        "downloaded_file_bytes_read": authorized_payload.get("downloaded_file_bytes_read") is True,
        "downloaded_file_hash_performed": authorized_payload.get("downloaded_file_hash_performed") is True,
        "real_archive_candidate_sha256_read": authorized_payload.get("real_archive_candidate_sha256_read") is True,
        "real_archive_candidate_sha256": authorized_payload.get("real_archive_candidate_sha256"),
        "real_archive_candidate_bytes_read_count": authorized_payload.get("real_archive_candidate_bytes_read_count"),
        "no_archive_open_permission_added_by_l24_8": True,
        "no_browser_permission_added_by_l24_8": True,
        "no_pasteback_or_package_run_permission_added_by_l24_8": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L24.8 is a broad checkpoint over accepted L24.6-L24.7 hash work.",
            "The only accepted byte read is controlled runtime fixture bytes for SHA-256; no archive open/list/extract/read, browser, pasteback, send/submit, or package-run permission is added.",
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
        f"Ladder Complete               : {payload.get('l24_candidate_hash_ladder_complete')}",
        f"Accepted Scope                : {payload.get('accepted_hash_scope')}",
        f"Hash Performed                : {payload.get('real_archive_candidate_path_hash_performed')}",
        f"Bytes Read                    : {payload.get('downloaded_file_bytes_read')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_candidate_hash_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
