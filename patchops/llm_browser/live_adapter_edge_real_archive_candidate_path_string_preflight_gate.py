"""L24.2 real downloaded-archive candidate path string preflight gate.

This follows accepted L24.1. It performs string-only candidate path checks after
explicit token authorization. It does not stat, hash, check existence, read size,
open/list/extract/read archives, start a browser, paste, send, or run packages.

L24.2a repairs the default/passive readback so no-token mode remains ok while
preflight is not requested.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_candidate_authorization_gate as l24_01

PATCH = "L24.2"
REPAIR_PATCH = "L24.2a"
PHASE = "L24"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L24.2 Microsoft Edge real downloaded-archive candidate path string preflight gate"
SOURCE_PATCH = "L24.1"
NEXT_PATCH = "L24.3 Microsoft Edge real downloaded-archive candidate filesystem stat authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_REAL_ARCHIVE_CANDIDATE_PATH_STRING_PREFLIGHT_TOKEN = "PATCHOPS_L24_EDGE_REAL_ARCHIVE_CANDIDATE_PATH_STRING_PREFLIGHT_AUTHORIZED"
DEFAULT_CANDIDATE_ARCHIVE_PATH = r"C:\Users\kostas\Downloads\future_real_patchops_bundle.zip"

FALSE_FIELDS = (
    "real_archive_candidate_path_stat_allowed",
    "real_archive_candidate_path_stat_performed",
    "real_archive_candidate_path_hash_allowed",
    "real_archive_candidate_path_hash_performed",
    "real_archive_candidate_exists",
    "real_archive_candidate_size_bytes_read",
    "real_archive_candidate_suffix_checked_on_filesystem",
    "real_archive_candidate_opened",
    "real_archive_candidate_listed",
    "real_archive_candidate_extracted",
    "real_archive_manifest_read",
    "real_downloaded_manifest_read",
    "real_archive_opened",
    "real_downloaded_artifact_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
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


def _l24_01_authorized_payload(repo_root: Path, candidate_archive_path: str | None, target_url: str) -> dict[str, Any]:
    try:
        return dict(l24_01.build_real_archive_candidate_authorization_gate(
            repo_root,
            allow_real_archive_candidate_authorization=True,
            authorization_token=l24_01.REQUIRED_REAL_ARCHIVE_CANDIDATE_AUTHORIZATION_TOKEN,
            candidate_archive_path=candidate_archive_path,
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L24.1 authorization readback failed: {type(exc).__name__}: {exc}"}


def _string_preflight(candidate_archive_path: str | None) -> dict[str, Any]:
    if candidate_archive_path is None:
        return {
            "candidate_path_string_present": False,
            "candidate_path_string_nonempty": False,
            "candidate_path_string_absolute_windows": False,
            "candidate_path_string_zip_suffix": False,
            "candidate_path_string_has_no_wildcards": False,
            "candidate_path_string_has_no_traversal_segments": False,
            "candidate_path_string_under_downloads_hint": False,
            "candidate_path_string_length": 0,
            "candidate_path_name": None,
            "candidate_path_parent_hint": None,
        }

    text = str(candidate_archive_path)
    parts = PureWindowsPath(text).parts
    parent_hint = str(PureWindowsPath(text).parent)
    return {
        "candidate_path_string_present": True,
        "candidate_path_string_nonempty": bool(text.strip()),
        "candidate_path_string_absolute_windows": bool(re.match(r"^[A-Za-z]:\\", text)),
        "candidate_path_string_zip_suffix": text.lower().endswith(".zip"),
        "candidate_path_string_has_no_wildcards": "*" not in text and "?" not in text,
        "candidate_path_string_has_no_traversal_segments": ".." not in parts,
        "candidate_path_string_under_downloads_hint": "\\Downloads\\" in text or text.lower().endswith("\\downloads\\future_real_patchops_bundle.zip"),
        "candidate_path_string_length": len(text),
        "candidate_path_name": PureWindowsPath(text).name,
        "candidate_path_parent_hint": parent_hint,
    }


def build_real_archive_candidate_path_string_preflight_gate(
    repo_root: str | Path | None = None,
    *,
    allow_candidate_path_string_preflight: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    candidate = candidate_archive_path or DEFAULT_CANDIDATE_ARCHIVE_PATH
    source = _l24_01_authorized_payload(root, candidate, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_ARCHIVE_CANDIDATE_PATH_STRING_PREFLIGHT_TOKEN
    requested = bool(allow_candidate_path_string_preflight or token_present)
    allowed = bool(allow_candidate_path_string_preflight and token_valid)
    string_data = _string_preflight(candidate if allowed else None)

    checks: list[dict[str, Any]] = [
        {"name": "source_l24_01_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l24_01_future_candidate_authorized", "ok": source.get("real_archive_candidate_authorization_granted_for_future_patch") is True},
        {"name": "source_l24_01_no_filesystem_touch", "ok": source.get("real_archive_candidate_path_stat_performed") is False and source.get("real_archive_candidate_path_hash_performed") is False},
        {"name": "source_l24_01_no_archive_browser_package", "ok": source.get("real_archive_opened") is False and source.get("browser_started") is False and source.get("package_run") is False},
    ]

    if requested or allow_candidate_path_string_preflight:
        checks.extend([
            {"name": "path_string_preflight_is_requested", "ok": requested},
            {"name": "path_string_preflight_token_present", "ok": token_present},
            {"name": "path_string_preflight_token_valid", "ok": token_valid},
        ])
    else:
        checks.append({"name": "default_passive_no_token_path_is_ok", "ok": True})

    if allowed:
        checks.extend([
            {"name": "candidate_path_string_present", "ok": string_data.get("candidate_path_string_present") is True},
            {"name": "candidate_path_string_nonempty", "ok": string_data.get("candidate_path_string_nonempty") is True},
            {"name": "candidate_path_string_absolute_windows", "ok": string_data.get("candidate_path_string_absolute_windows") is True},
            {"name": "candidate_path_string_zip_suffix", "ok": string_data.get("candidate_path_string_zip_suffix") is True},
            {"name": "candidate_path_string_no_wildcards", "ok": string_data.get("candidate_path_string_has_no_wildcards") is True},
            {"name": "candidate_path_string_no_traversal", "ok": string_data.get("candidate_path_string_has_no_traversal_segments") is True},
        ])

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l24_01_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_candidate_authorized": source.get("real_archive_candidate_authorization_granted_for_future_patch"),
            "candidate_path_recorded_as_string_only": source.get("candidate_archive_path_recorded_as_string_only"),
            "candidate_path_stat_performed": source.get("real_archive_candidate_path_stat_performed"),
            "candidate_path_hash_performed": source.get("real_archive_candidate_path_hash_performed"),
            "candidate_archive_opened": source.get("real_archive_candidate_opened"),
            "candidate_archive_listed": source.get("real_archive_candidate_listed"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "candidate_path_string_preflight_gate": True,
        "candidate_path_string_preflight_requested": requested,
        "candidate_path_string_preflight_token_present": token_present,
        "candidate_path_string_preflight_token_valid": token_valid,
        "candidate_path_string_preflight_allowed": allowed,
        "candidate_archive_path_recorded_as_string_only": candidate is not None,
        "candidate_archive_path": candidate,
        "candidate_path_string_checks": string_data,
        "candidate_path_string_preflight_scope": "string_only_no_filesystem_touch" if allowed else "default_readback_only_no_candidate_path_analysis",
        "future_real_archive_candidate_filesystem_stat_requires_explicit_flag_and_token": True,
        "future_real_archive_candidate_filesystem_stat_must_be_separately_gated_in_l24_3": True,
        "no_real_archive_candidate_filesystem_permission_added_by_l24_2": True,
        "no_archive_open_permission_added_by_l24_2": True,
        "no_browser_permission_added_by_l24_2": True,
        "no_pasteback_or_package_run_permission_added_by_l24_2": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "safety_boundary": "string-only candidate path preflight; no stat/hash/existence/size/open/list/extract/read, no browser, no pasteback, no package-run",
        "checks": checks,
        "failed_checks": [check for check in checks if not check.get("ok")],
        "next_patch": NEXT_PATCH,
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Repair Patch                  : {payload.get('repair_patch')}",
        f"Status                        : {payload.get('status')}",
        f"String Preflight Allowed      : {payload.get('candidate_path_string_preflight_allowed')}",
        f"Scope                         : {payload.get('candidate_path_string_preflight_scope')}",
        f"Candidate Path Stat           : {payload.get('real_archive_candidate_path_stat_performed')}",
        f"Candidate Path Hash           : {payload.get('real_archive_candidate_path_hash_performed')}",
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
    parser.add_argument("--allow-candidate-path-string-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=DEFAULT_CANDIDATE_ARCHIVE_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_candidate_path_string_preflight_gate(
        args.repo_root,
        allow_candidate_path_string_preflight=args.allow_candidate_path_string_preflight,
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
