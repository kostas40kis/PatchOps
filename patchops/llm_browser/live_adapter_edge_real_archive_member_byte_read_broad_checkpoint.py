"""L25.9 broad checkpoint for controlled archive member-byte-read proof.

This follows accepted L25.8. It replays the controlled non-manifest member-byte
read proof and summarizes the L25.7-L25.8 member-byte-read ladder. It does not
read manifest payload bytes, extract members, start a browser, paste, send, or
run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_member_byte_read_first_controlled_proof as l25_08

PATCH = "L25.9"
PHASE = "L25"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L25.9 Microsoft Edge controlled runtime archive member-byte-read broad checkpoint"
SOURCE_PATCH = "L25.8"
SOURCE_LADDER = (
    "L25.7 archive member-byte-read authorization gate",
    "L25.8 first controlled non-manifest member-byte-read proof",
)
NEXT_PATCH = "L25.10 Microsoft Edge controlled runtime archive manifest payload-read authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
TARGET_CONTROLLED_MEMBER_NAME = l25_08.TARGET_CONTROLLED_MEMBER_NAME
FORBIDDEN_MANIFEST_MEMBER_NAME = l25_08.FORBIDDEN_MANIFEST_MEMBER_NAME
EXPECTED_MEMBER_READ_SCOPE = "controlled_runtime_non_manifest_member_bytes_only_no_manifest_payload"

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


def _l25_08_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l25_08.build_archive_member_byte_read_first_controlled_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.8 default readback failed: {type(exc).__name__}: {exc}"}


def _l25_08_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        candidate = repo_root / l25_08.DEFAULT_CONTROLLED_CANDIDATE_RELATIVE_PATH
        return dict(l25_08.build_archive_member_byte_read_first_controlled_proof(
            repo_root,
            allow_archive_member_byte_read_proof=True,
            authorization_token=l25_08.REQUIRED_ARCHIVE_MEMBER_BYTE_READ_PROOF_TOKEN,
            candidate_archive_path=str(candidate),
            member_name=TARGET_CONTROLLED_MEMBER_NAME,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L25.8 authorized readback failed: {type(exc).__name__}: {exc}"}


def _is_lower_hex_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def build_archive_member_byte_read_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l25_08_default_payload(root, target_url)
    authorized_payload = _l25_08_authorized_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l25_08_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l25_08_default_is_passive", "ok": default_payload.get("archive_member_bytes_read") is False},
        {"name": "source_l25_08_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l25_08_patch_marker", "ok": authorized_payload.get("patch") == "L25.8"},
        {"name": "source_l25_08_member_byte_read_allowed", "ok": authorized_payload.get("archive_member_byte_read_allowed") is True},
        {"name": "source_l25_08_member_bytes_read", "ok": authorized_payload.get("archive_member_bytes_read") is True},
        {"name": "source_l25_08_member_payload_read", "ok": authorized_payload.get("archive_member_payload_read") is True and authorized_payload.get("archive_member_payload_bytes_read") is True},
        {"name": "source_l25_08_member_payload_sha256_read", "ok": authorized_payload.get("archive_member_payload_sha256_read") is True and _is_lower_hex_sha256(authorized_payload.get("archive_member_payload_sha256"))},
        {"name": "source_l25_08_target_member_name", "ok": authorized_payload.get("archive_member_name_read") == TARGET_CONTROLLED_MEMBER_NAME},
        {"name": "source_l25_08_not_manifest_member", "ok": authorized_payload.get("archive_member_name_read") != FORBIDDEN_MANIFEST_MEMBER_NAME},
        {"name": "source_l25_08_scope_non_manifest_only", "ok": authorized_payload.get("archive_member_read_scope") == EXPECTED_MEMBER_READ_SCOPE},
        {"name": "source_l25_08_payload_count_positive", "ok": isinstance(authorized_payload.get("archive_member_payload_byte_count"), int) and authorized_payload.get("archive_member_payload_byte_count") > 0},
        {"name": "source_l25_08_no_manifest_payload", "ok": authorized_payload.get("manifest_payload_read") is False and authorized_payload.get("real_archive_manifest_read") is False},
        {"name": "source_l25_08_no_extract_browser_package", "ok": authorized_payload.get("real_archive_candidate_extracted") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "archive_member_byte_read_ladder_checkpoint": True,
        "l25_archive_member_byte_read_ladder_complete": ok,
        "source_l25_08_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "archive_member_bytes_read": default_payload.get("archive_member_bytes_read"),
            "archive_member_read_scope": default_payload.get("archive_member_read_scope"),
        },
        "source_l25_08_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l25_07_ok": authorized_payload.get("source_l25_07_summary", {}).get("ok"),
            "source_l25_07_future_authorized": authorized_payload.get("source_l25_07_summary", {}).get("future_member_byte_read_authorized"),
            "member_byte_read_allowed": authorized_payload.get("archive_member_byte_read_allowed"),
            "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read"),
            "archive_member_payload_read": authorized_payload.get("archive_member_payload_read"),
            "archive_member_payload_bytes_read": authorized_payload.get("archive_member_payload_bytes_read"),
            "archive_member_payload_sha256_read": authorized_payload.get("archive_member_payload_sha256_read"),
            "archive_member_payload_byte_count": authorized_payload.get("archive_member_payload_byte_count"),
            "archive_member_payload_sha256": authorized_payload.get("archive_member_payload_sha256"),
            "archive_member_name_read": authorized_payload.get("archive_member_name_read"),
            "archive_member_read_scope": authorized_payload.get("archive_member_read_scope"),
            "manifest_payload_read": authorized_payload.get("manifest_payload_read"),
            "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
            "archive_extracted": authorized_payload.get("real_archive_candidate_extracted"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_member_read_scope": EXPECTED_MEMBER_READ_SCOPE,
        "accepted_member_byte_read_allowed": authorized_payload.get("archive_member_byte_read_allowed") is True,
        "accepted_member_bytes_read": authorized_payload.get("archive_member_bytes_read") is True,
        "accepted_member_payload_read": authorized_payload.get("archive_member_payload_read") is True,
        "accepted_member_payload_bytes_read": authorized_payload.get("archive_member_payload_bytes_read") is True,
        "accepted_member_payload_sha256_read": authorized_payload.get("archive_member_payload_sha256_read") is True,
        "accepted_member_payload_sha256_is_lower_hex": _is_lower_hex_sha256(authorized_payload.get("archive_member_payload_sha256")),
        "accepted_member_payload_byte_count": authorized_payload.get("archive_member_payload_byte_count"),
        "accepted_member_name_read": authorized_payload.get("archive_member_name_read"),
        "accepted_manifest_member_not_read": authorized_payload.get("archive_member_name_read") != FORBIDDEN_MANIFEST_MEMBER_NAME,
        "archive_member_byte_read_allowed": authorized_payload.get("archive_member_byte_read_allowed") is True,
        "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read") is True,
        "archive_member_payload_read": authorized_payload.get("archive_member_payload_read") is True,
        "archive_member_payload_bytes_read": authorized_payload.get("archive_member_payload_bytes_read") is True,
        "archive_member_payload_sha256_read": authorized_payload.get("archive_member_payload_sha256_read") is True,
        "archive_member_payload_byte_count": authorized_payload.get("archive_member_payload_byte_count"),
        "archive_member_payload_sha256": authorized_payload.get("archive_member_payload_sha256"),
        "archive_member_name_read": authorized_payload.get("archive_member_name_read"),
        "archive_member_read_scope": authorized_payload.get("archive_member_read_scope"),
        "no_manifest_payload_read_added_by_l25_9": True,
        "no_archive_extraction_added_by_l25_9": True,
        "no_browser_permission_added_by_l25_9": True,
        "no_pasteback_or_package_run_permission_added_by_l25_9": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L25.9 is a broad checkpoint over accepted L25.7-L25.8 member-byte-read work.",
            "Only the controlled non-manifest member payload read is accepted; manifest payload reads, extraction, browser, pasteback, send/submit, and package-run remain separate future gates.",
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
        f"Ladder Complete               : {payload.get('l25_archive_member_byte_read_ladder_complete')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_archive_member_byte_read_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
