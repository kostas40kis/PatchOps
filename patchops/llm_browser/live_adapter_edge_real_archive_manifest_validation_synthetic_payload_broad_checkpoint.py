"""L23.8 broad checkpoint for the synthetic manifest payload ladder.

This module follows accepted L23.7. It replays only the accepted synthetic
manifest payload proof and summarizes the post-L22 L23 ladder. It does not read
non-manifest member payloads, extract files, touch real downloaded artifacts,
start a browser, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_first_synthetic_manifest_payload_proof as l23_07

PATCH = "L23.8"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.8 Microsoft Edge real downloaded-archive manifest validation synthetic payload broad checkpoint"
SOURCE_PATCH = "L23.7"
SOURCE_LADDER = (
    "L23.1 real downloaded-archive manifest authorization gate",
    "L23.2/L23.2a fixed synthetic archive path preflight",
    "L23.3 synthetic archive listing authorization gate",
    "L23.4/L23.4b first synthetic archive metadata listing proof",
    "L23.5 synthetic manifest-name proof gate",
    "L23.6 synthetic manifest payload authorization gate",
    "L23.7 first synthetic manifest payload proof",
)
NEXT_PATCH = "L23.9 Microsoft Edge real downloaded-archive manifest validation final synthetic acceptance marker"
DEFAULT_TARGET_URL = "https://chatgpt.com/"

ALWAYS_FALSE_FIELDS = (
    "non_manifest_member_bytes_read",
    "non_manifest_member_payload_read",
    "readme_member_payload_read",
    "downloaded_archive_extracted",
    "archive_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "candidate_archive_path_stat_performed",
    "candidate_archive_path_hash_performed",
    "synthetic_archive_hash_performed",
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


def _l23_07_default_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_07.build_first_synthetic_manifest_payload_proof(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.7 default readback failed: {type(exc).__name__}: {exc}"}


def _l23_07_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_07.build_first_synthetic_manifest_payload_proof(
            repo_root,
            allow_synthetic_manifest_payload_proof=True,
            authorization_token=l23_07.REQUIRED_SYNTHETIC_MANIFEST_PAYLOAD_PROOF_TOKEN,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.7 authorized readback failed: {type(exc).__name__}: {exc}"}


def build_synthetic_payload_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    default_payload = _l23_07_default_payload(root, target_url)
    authorized_payload = _l23_07_authorized_payload(root, target_url)

    checks: list[dict[str, Any]] = [
        {"name": "source_l23_07_default_payload_ok", "ok": default_payload.get("ok") is True},
        {"name": "source_l23_07_default_is_passive", "ok": default_payload.get("synthetic_manifest_payload_read_performed") is False},
        {"name": "source_l23_07_authorized_payload_ok", "ok": authorized_payload.get("ok") is True},
        {"name": "source_l23_07_patch_marker", "ok": authorized_payload.get("patch") == "L23.7"},
        {"name": "source_l23_07_payload_proof_allowed", "ok": authorized_payload.get("synthetic_manifest_payload_read_execution_allowed") is True},
        {"name": "source_l23_07_payload_read_performed", "ok": authorized_payload.get("synthetic_manifest_payload_read_performed") is True},
        {"name": "source_l23_07_manifest_member_only", "ok": authorized_payload.get("synthetic_manifest_member_name") == "manifest.json"},
        {"name": "source_l23_07_json_parsed", "ok": authorized_payload.get("synthetic_manifest_json_parsed") is True},
        {"name": "source_l23_07_shape_validated", "ok": authorized_payload.get("synthetic_manifest_shape_validated") is True},
        {"name": "source_l23_07_expected_patch_name", "ok": authorized_payload.get("synthetic_manifest_patch_name") == "l23_07_synthetic_manifest_payload_fixture"},
        {"name": "source_l23_07_scope_is_synthetic_only", "ok": authorized_payload.get("synthetic_manifest_scope") == "fixed_synthetic_archive_manifest_payload_only"},
        {"name": "source_l23_07_manifest_bytes_only", "ok": authorized_payload.get("manifest_member_bytes_read") is True and authorized_payload.get("manifest_member_payload_read") is True},
        {"name": "source_l23_07_no_non_manifest_member_read", "ok": authorized_payload.get("non_manifest_member_bytes_read") is False and authorized_payload.get("readme_member_payload_read") is False},
        {"name": "source_l23_07_no_extraction_real_archive_browser_package", "ok": authorized_payload.get("archive_extracted") is False and authorized_payload.get("real_archive_manifest_read") is False and authorized_payload.get("browser_started") is False and authorized_payload.get("package_run") is False},
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
        "synthetic_payload_ladder_checkpoint": True,
        "l23_synthetic_payload_ladder_complete": ok,
        "source_l23_07_default_summary": {
            "ok": default_payload.get("ok"),
            "patch": default_payload.get("patch"),
            "payload_read_performed": default_payload.get("synthetic_manifest_payload_read_performed"),
            "synthetic_scope": default_payload.get("synthetic_manifest_scope"),
        },
        "source_l23_07_authorized_summary": {
            "ok": authorized_payload.get("ok"),
            "patch": authorized_payload.get("patch"),
            "source_l23_06_ok": authorized_payload.get("source_l23_06_summary", {}).get("ok"),
            "source_l23_06_future_authorized": authorized_payload.get("source_l23_06_summary", {}).get("future_payload_authorized"),
            "payload_execution_allowed": authorized_payload.get("synthetic_manifest_payload_read_execution_allowed"),
            "payload_read_performed": authorized_payload.get("synthetic_manifest_payload_read_performed"),
            "manifest_member_name": authorized_payload.get("synthetic_manifest_member_name"),
            "synthetic_manifest_json_parsed": authorized_payload.get("synthetic_manifest_json_parsed"),
            "synthetic_manifest_shape_validated": authorized_payload.get("synthetic_manifest_shape_validated"),
            "synthetic_manifest_patch_name": authorized_payload.get("synthetic_manifest_patch_name"),
            "synthetic_scope": authorized_payload.get("synthetic_manifest_scope"),
            "manifest_member_bytes_read": authorized_payload.get("manifest_member_bytes_read"),
            "manifest_member_payload_read": authorized_payload.get("manifest_member_payload_read"),
            "non_manifest_member_bytes_read": authorized_payload.get("non_manifest_member_bytes_read"),
            "readme_member_payload_read": authorized_payload.get("readme_member_payload_read"),
            "archive_extracted": authorized_payload.get("archive_extracted"),
            "real_archive_manifest_read": authorized_payload.get("real_archive_manifest_read"),
            "browser_started": authorized_payload.get("browser_started"),
            "package_run": authorized_payload.get("package_run"),
        },
        "accepted_synthetic_payload_scope": "fixed_synthetic_archive_manifest_payload_only",
        "accepted_manifest_member_name": authorized_payload.get("synthetic_manifest_member_name"),
        "accepted_synthetic_manifest_patch_name": authorized_payload.get("synthetic_manifest_patch_name"),
        "manifest_member_bytes_read": authorized_payload.get("manifest_member_bytes_read") is True,
        "manifest_member_payload_read": authorized_payload.get("manifest_member_payload_read") is True,
        "manifest_member_content_read": authorized_payload.get("manifest_member_content_read") is True,
        "archive_member_bytes_read": authorized_payload.get("archive_member_bytes_read") is True,
        "archive_member_payload_read": authorized_payload.get("archive_member_payload_read") is True,
        "archive_member_content_read": authorized_payload.get("archive_member_content_read") is True,
        "synthetic_manifest_json_parsed": authorized_payload.get("synthetic_manifest_json_parsed") is True,
        "synthetic_manifest_shape_validated": authorized_payload.get("synthetic_manifest_shape_validated") is True,
        "no_real_archive_permission_added_by_l23_8": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.8 is a broad checkpoint over accepted L23.1-L23.7 synthetic-only work.",
            "The only accepted payload read remains manifest.json from the fixed synthetic archive fixture.",
            "No non-manifest member, extraction, real archive, browser, pasteback, send/submit, or package-run permission is added.",
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
        f"Ladder Complete               : {payload.get('l23_synthetic_payload_ladder_complete')}",
        f"Accepted Scope                : {payload.get('accepted_synthetic_payload_scope')}",
        f"Accepted Manifest Name        : {payload.get('accepted_manifest_member_name')}",
        f"Accepted Patch Name           : {payload.get('accepted_synthetic_manifest_patch_name')}",
        f"Manifest Payload Read         : {payload.get('manifest_member_payload_read')}",
        f"Non-Manifest Bytes Read       : {payload.get('non_manifest_member_bytes_read')}",
        f"Extraction                    : {payload.get('archive_extracted')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Package Run                   : {payload.get('package_run')}",
        f"Next Patch                    : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_synthetic_payload_broad_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
