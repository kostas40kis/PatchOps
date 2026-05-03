"""L23.2 synthetic-archive preflight gate.

This patch advances from L23.1 authorization to a fixed synthetic archive path
preflight. It may stat only the synthetic fixture path created by PatchOps to
prove existence and size. It does not load the ZIP archive module, open/list/extract archives,
read archive member bytes, read a manifest from an archive, start a browser,
paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_archive_manifest_validation_authorization_gate as l23_01

PATCH = "L23.2"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.2 Microsoft Edge real downloaded-archive manifest validation synthetic-archive preflight gate"
SOURCE_PATCH = "L23.1"
NEXT_PATCH = "L23.3 Microsoft Edge real downloaded-archive manifest validation synthetic-archive listing authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH = "data/runtime/browser_downloads/patch_l23_02_synthetic_archive_preflight_fixture/patch_l23_02_synthetic_archive.zip"
REQUIRED_SYNTHETIC_ARCHIVE_PREFLIGHT_TOKEN = "PATCHOPS_L23_EDGE_SYNTHETIC_ARCHIVE_PREFLIGHT_AUTHORIZED"

ALWAYS_FALSE_FIELDS = (
    "real_archive_manifest_validation_execution_allowed",
    "real_archive_manifest_validation_active",
    "real_archive_manifest_validation_performed",
    "real_downloaded_manifest_read",
    "real_archive_manifest_read",
    "real_archive_opened",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "archive_member_bytes_read",
    "archive_member_content_read",
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


def _l23_01_authorized_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l23_01.build_real_archive_manifest_validation_authorization_gate(
            repo_root,
            allow_real_archive_manifest_validation_authorization=True,
            authorization_token=l23_01.REQUIRED_REAL_ARCHIVE_MANIFEST_AUTHORIZATION_TOKEN,
            candidate_archive_path=str(repo_root / DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH),
            target_url=target_url,
        ))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L23.1 authorized readback failed: {type(exc).__name__}: {exc}"}


def _base_payload(root: Path, target_url: str) -> dict[str, Any]:
    source = _l23_01_authorized_payload(root, target_url)
    checks = [
        {"name": "source_l23_01_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_01_future_authorization_granted", "ok": source.get("real_archive_manifest_authorization_granted_for_future_patch") is True},
        {"name": "source_l23_01_execution_still_false", "ok": source.get("real_archive_manifest_validation_execution_allowed") is False},
        {"name": "default_preflight_is_passive", "ok": True},
    ]
    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_01_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_authorized": source.get("real_archive_manifest_authorization_granted_for_future_patch"),
            "execution_allowed": source.get("real_archive_manifest_validation_execution_allowed"),
            "real_archive_opened": source.get("real_archive_opened"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "synthetic_archive_preflight_requested": False,
        "synthetic_archive_preflight_token_present": False,
        "synthetic_archive_preflight_token_valid": False,
        "synthetic_archive_preflight_allowed": False,
        "synthetic_archive_fixture_only": True,
        "synthetic_archive_fixture_relative_path": DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
        "synthetic_archive_path_recorded": False,
        "synthetic_archive_path_is_fixed": False,
        "synthetic_archive_path_exists": False,
        "synthetic_archive_path_stat_performed": False,
        "synthetic_archive_size_bytes": None,
        "synthetic_archive_suffix_valid": False,
        "preflight_scope": "default_readback_only_no_path_stat",
        "no_new_real_archive_permission_added_by_l23_2": True,
        "checks": checks,
        "next_patch": NEXT_PATCH,
    }
    for field in ALWAYS_FALSE_FIELDS:
        payload[field] = False
    return payload


def build_synthetic_archive_preflight_gate(
    repo_root: str | Path | None = None,
    *,
    allow_synthetic_archive_preflight: bool = False,
    authorization_token: str | None = None,
    synthetic_archive_relative_path: str = DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    if not allow_synthetic_archive_preflight:
        return _base_payload(root, target_url)

    source = _l23_01_authorized_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_SYNTHETIC_ARCHIVE_PREFLIGHT_TOKEN
    rel_is_fixed = synthetic_archive_relative_path == DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH
    fixture_path = root / synthetic_archive_relative_path

    checks: list[dict[str, Any]] = [
        {"name": "source_l23_01_authorized_payload_ok", "ok": source.get("ok") is True},
        {"name": "source_l23_01_future_authorization_granted", "ok": source.get("real_archive_manifest_authorization_granted_for_future_patch") is True},
        {"name": "source_l23_01_execution_still_false", "ok": source.get("real_archive_manifest_validation_execution_allowed") is False},
        {"name": "preflight_token_present", "ok": token_present},
        {"name": "preflight_token_valid", "ok": token_valid},
        {"name": "synthetic_archive_relative_path_is_fixed", "ok": rel_is_fixed},
        {"name": "synthetic_archive_suffix_is_zip", "ok": fixture_path.suffix.lower() == ".zip"},
        {"name": "synthetic_archive_fixture_exists", "ok": fixture_path.exists()},
    ]

    size_bytes: int | None = None
    stat_allowed = bool(all(check.get("ok") for check in checks))
    if stat_allowed:
        st = fixture_path.stat()
        size_bytes = int(st.st_size)
        checks.append({"name": "synthetic_archive_size_positive", "ok": size_bytes > 0})

    ok = bool(all(check.get("ok") for check in checks))
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l23_01_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_authorized": source.get("real_archive_manifest_authorization_granted_for_future_patch"),
            "execution_allowed": source.get("real_archive_manifest_validation_execution_allowed"),
            "real_archive_opened": source.get("real_archive_opened"),
            "real_archive_manifest_read": source.get("real_archive_manifest_read"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "browser_started": source.get("browser_started"),
            "package_run": source.get("package_run"),
        },
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "synthetic_archive_preflight_requested": True,
        "synthetic_archive_preflight_token_present": token_present,
        "synthetic_archive_preflight_token_valid": token_valid,
        "synthetic_archive_preflight_allowed": ok,
        "synthetic_archive_fixture_only": True,
        "synthetic_archive_fixture_relative_path": DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH,
        "synthetic_archive_path_recorded": True,
        "synthetic_archive_path_is_fixed": rel_is_fixed,
        "synthetic_archive_path_exists": fixture_path.exists(),
        "synthetic_archive_path_stat_performed": stat_allowed,
        "synthetic_archive_size_bytes": size_bytes,
        "synthetic_archive_suffix_valid": fixture_path.suffix.lower() == ".zip",
        "preflight_scope": "fixed_synthetic_archive_path_existence_and_size_only",
        "no_new_real_archive_permission_added_by_l23_2": True,
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.2 stats only the fixed synthetic archive fixture path.",
            "The synthetic archive fixture is not opened, listed, extracted, or read.",
            "No real archive path is statted or hashed and no browser/package activity is performed.",
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
        f"Preflight Allowed             : {payload.get('synthetic_archive_preflight_allowed')}",
        f"Preflight Scope               : {payload.get('preflight_scope')}",
        f"Synthetic Path Stat           : {payload.get('synthetic_archive_path_stat_performed')}",
        f"Synthetic Size Bytes          : {payload.get('synthetic_archive_size_bytes')}",
        f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
        f"Archive Listed                : {payload.get('downloaded_archive_contents_listed')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
        f"Member Bytes Read             : {payload.get('archive_member_bytes_read')}",
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
    parser.add_argument("--allow-synthetic-archive-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--synthetic-archive-relative-path", default=DEFAULT_SYNTHETIC_ARCHIVE_RELATIVE_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_synthetic_archive_preflight_gate(
        args.repo_root,
        allow_synthetic_archive_preflight=args.allow_synthetic_archive_preflight,
        authorization_token=args.authorization_token,
        synthetic_archive_relative_path=args.synthetic_archive_relative_path,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
