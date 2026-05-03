"""L23.1 authorization gate for future real downloaded-archive manifest validation.

This starts a new separately gated post-L22 stream. It does not open archives,
list archive contents, read archive member bytes, read a real downloaded manifest,
start a browser, import Selenium, paste, send, or run packages.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_final_marker as l22_final

PATCH = "L23.1"
PHASE = "L23"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L23.1 Microsoft Edge real downloaded-archive manifest validation authorization gate"
SOURCE_PATCH = "L22.7"
NEXT_PATCH = "L23.2 Microsoft Edge real downloaded-archive manifest validation synthetic-archive preflight gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_REAL_ARCHIVE_MANIFEST_AUTHORIZATION_TOKEN = "PATCHOPS_L23_EDGE_REAL_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_AUTHORIZED_READBACK_ONLY"

FALSE_FIELDS = (
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


def _l22_final_payload(repo_root: Path, target_url: str) -> dict[str, Any]:
    try:
        return dict(l22_final.build_manifest_validation_final_acceptance_marker(repo_root, target_url=target_url))
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"L22.7 final readback failed: {type(exc).__name__}: {exc}"}


def build_real_archive_manifest_validation_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_real_archive_manifest_validation_authorization: bool = False,
    authorization_token: str | None = None,
    candidate_archive_path: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    l22 = _l22_final_payload(root, target_url)
    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_REAL_ARCHIVE_MANIFEST_AUTHORIZATION_TOKEN
    authorization_requested = bool(allow_real_archive_manifest_validation_authorization or token_present)
    future_authorized = bool(allow_real_archive_manifest_validation_authorization and token_valid)

    checks = [
        {"name": "source_l22_07_final_payload_ok", "ok": l22.get("ok") is True},
        {"name": "source_l22_07_complete", "ok": l22.get("l22_downloaded_archive_manifest_validation_stream_complete") is True},
        {"name": "source_l22_07_scope_is_synthetic_only", "ok": l22.get("accepted_scope") == "synthetic_manifest_fixture_validation_only"},
        {"name": "source_l22_07_added_no_new_execution_permission", "ok": l22.get("no_new_execution_permission_added_by_l22_7") is True},
        {"name": "authorization_is_readback_only", "ok": True},
        {"name": "real_archive_manifest_execution_remains_false", "ok": True},
        {"name": "real_archive_is_not_opened", "ok": True},
        {"name": "archive_members_are_not_listed_or_read", "ok": True},
        {"name": "browser_and_package_run_remain_false", "ok": True},
    ]

    payload: dict[str, Any] = {
        "ok": bool(all(check.get("ok") for check in checks)),
        "status": STATUS_PASS if all(check.get("ok") for check in checks) else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_l22_07_summary": {
            "ok": l22.get("ok"),
            "patch": l22.get("patch"),
            "l22_final_acceptance_marker": l22.get("l22_final_acceptance_marker"),
            "l22_complete": l22.get("l22_downloaded_archive_manifest_validation_stream_complete"),
            "accepted_scope": l22.get("accepted_scope"),
            "real_downloaded_manifest_read": l22.get("real_downloaded_manifest_read"),
            "real_archive_manifest_read": l22.get("real_archive_manifest_read"),
            "archive_extracted": l22.get("archive_extracted"),
            "archive_member_bytes_read": l22.get("archive_member_bytes_read"),
            "browser_started": l22.get("browser_started"),
            "package_run": l22.get("package_run"),
        },
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "candidate_archive_path_recorded": candidate_archive_path is not None,
        "candidate_archive_path": candidate_archive_path,
        "real_archive_manifest_authorization_gate": True,
        "real_archive_manifest_authorization_readback_only": True,
        "real_archive_manifest_authorization_requested": authorization_requested,
        "real_archive_manifest_authorization_token_present": token_present,
        "real_archive_manifest_authorization_token_valid": token_valid,
        "real_archive_manifest_authorization_granted_for_future_patch": future_authorized,
        "future_real_archive_manifest_validation_requires_explicit_flag_and_token": True,
        "future_real_archive_manifest_validation_must_be_separately_gated_in_l23_2": True,
        "no_new_execution_permission_added_by_l23_1": True,
        "safety_boundary": "readback-only authorization gate; no real archive open/list/read, no manifest read from real archive, no browser, no pasteback, no package-run",
        "checks": checks,
        "next_patch": NEXT_PATCH,
        "notes": [
            "L23.1 starts a separate post-L22 stream.",
            "Authorization can be proven in readback, but real archive manifest validation execution remains blocked.",
            "No real archive path is statted, hashed, opened, listed, extracted, or read.",
        ],
    }
    for field in FALSE_FIELDS:
        payload[field] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Future Authorized             : {payload.get('real_archive_manifest_authorization_granted_for_future_patch')}",
        f"Execution Allowed             : {payload.get('real_archive_manifest_validation_execution_allowed')}",
        f"Real Archive Opened           : {payload.get('real_archive_opened')}",
        f"Real Archive Manifest Read    : {payload.get('real_archive_manifest_read')}",
        f"Archive Member Bytes Read     : {payload.get('archive_member_bytes_read')}",
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
    parser.add_argument("--allow-real-archive-manifest-validation-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--candidate-archive-path", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_real_archive_manifest_validation_authorization_gate(
        args.repo_root,
        allow_real_archive_manifest_validation_authorization=args.allow_real_archive_manifest_validation_authorization,
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
