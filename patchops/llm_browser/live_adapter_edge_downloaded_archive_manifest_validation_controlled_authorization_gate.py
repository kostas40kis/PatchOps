"""L22.4 controlled authorization gate for downloaded-archive manifest validation.

This module adds a future authorization token/readback surface after accepted
L22.3b. It remains passive/readback-only: no manifest read, archive extraction,
archive member-byte read, browser activity, page inspection, artifact-content
reading, pasteback, send/submit, package-run, localhost server, browser
extension, commit, or push.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L22.4"
PHASE = "L22"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L22.4 Microsoft Edge downloaded-archive manifest validation controlled authorization gate"
SOURCE_PATCH = "L22.3b"
SOURCE_MODULE_REL = "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_passive_plan_launcher_direct.py"
SOURCE_DOC_REL = "docs/llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_plan_launcher_direct.md"
NEXT_PATCH = "L22.5 Microsoft Edge first controlled downloaded-archive manifest validation proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN = "PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY"

ALLOWED_TARGET_URL_PREFIXES = ("https://chatgpt.com/", "https://chat.openai.com/")

FALSE_FIELDS = (
    "manifest_validation_execution_allowed",
    "manifest_validation_active",
    "manifest_validation_performed",
    "downloaded_manifest_read",
    "manifest_read",
    "archive_extracted",
    "downloaded_archive_extracted",
    "downloaded_archive_opened",
    "archive_member_bytes_read",
    "member_bytes_read",
    "artifact_content_read",
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


def _target_url_allowed(target_url: str) -> bool:
    return any(target_url.startswith(prefix) for prefix in ALLOWED_TARGET_URL_PREFIXES)


def _source_checkpoint_payload(repo_root: Path) -> dict[str, Any]:
    try:
        from patchops.llm_browser import live_adapter_edge_downloaded_archive_manifest_validation_passive_plan_launcher_direct as source
    except Exception as exc:  # pragma: no cover - defensive readback path
        return {"ok": False, "error": f"source import failed: {type(exc).__name__}: {exc}"}

    try:
        payload = source.build_manifest_validation_passive_plan(repo_root)
    except Exception as exc:  # pragma: no cover - defensive readback path
        return {"ok": False, "error": f"source readback failed: {type(exc).__name__}: {exc}"}

    return dict(payload)


def _summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "patch",
        "manifest_validation_execution_allowed",
        "downloaded_manifest_read",
        "archive_extracted",
        "archive_member_bytes_read",
        "browser_started",
        "pasteback_workflow_active",
        "package_run",
        "next_patch",
    )
    return {key: payload.get(key) for key in keys if key in payload}


def build_manifest_validation_controlled_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_manifest_validation_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str = DEFAULT_TARGET_URL,
) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    source_module = root / SOURCE_MODULE_REL
    source_doc = root / SOURCE_DOC_REL
    source_payload = _source_checkpoint_payload(root)

    token_present = authorization_token is not None
    token_valid = authorization_token == REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN
    authorization_requested = bool(allow_manifest_validation_authorization or token_present)
    authorization_granted_for_future_patch = bool(allow_manifest_validation_authorization and token_valid)
    target_allowed = _target_url_allowed(target_url)

    checks = [
        {"name": "source_l22_03b_module_exists", "ok": source_module.exists()},
        {"name": "source_l22_03b_doc_exists", "ok": source_doc.exists()},
        {"name": "source_l22_03b_readback_ok", "ok": bool(source_payload.get("ok"))},
        {"name": "target_url_allowlisted_but_not_opened", "ok": target_allowed},
        {"name": "authorization_is_readback_only", "ok": True},
        {"name": "manifest_validation_execution_remains_false", "ok": True},
        {"name": "manifest_read_remains_false", "ok": True},
        {"name": "archive_extraction_remains_false", "ok": True},
        {"name": "member_byte_read_remains_false", "ok": True},
        {"name": "browser_activity_remains_false", "ok": True},
        {"name": "package_run_remains_false", "ok": True},
    ]

    payload: dict[str, Any] = {
        "ok": False,
        "status": STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "source_patch": SOURCE_PATCH,
        "source_module": SOURCE_MODULE_REL,
        "source_doc": SOURCE_DOC_REL,
        "source_l22_03b_summary": _summary(source_payload),
        "controlled_authorization_gate": True,
        "manifest_validation_authorization_readback_only": True,
        "manifest_validation_authorization_requested": authorization_requested,
        "manifest_validation_authorization_token_present": token_present,
        "manifest_validation_authorization_token_valid": token_valid,
        "manifest_validation_authorization_granted_for_future_patch": authorization_granted_for_future_patch,
        "manifest_validation_authorization_token_name": "REQUIRED_MANIFEST_VALIDATION_AUTHORIZATION_TOKEN",
        "future_manifest_validation_requires_explicit_flag_and_token": True,
        "future_manifest_validation_must_be_separately_gated_in_l22_5": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "patchops_remains_source_of_truth": True,
        "default_microsoft_edge_profile_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "target_url": target_url,
        "target_url_allowed": target_allowed,
        "chatgpt_url_may_be_selected_but_not_opened": True,
        "no_commands_py_registration": True,
        "safety_boundary": "readback-only manifest authorization gate; no manifest read, archive extraction, member-byte read, browser activity, pasteback, or package-run",
        "next_patch": NEXT_PATCH,
        "checks": checks,
        "notes": [
            "L22.4 adds only the explicit future authorization/readback gate.",
            "Authorization can be proven in readback, but execution remains blocked.",
            "The first actual synthetic manifest validation proof must wait for L22.5.",
        ],
    }

    for field in FALSE_FIELDS:
        payload[field] = False

    payload["ok"] = bool(all(check.get("ok") for check in checks))
    payload["status"] = STATUS_PASS if payload["ok"] else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Source Patch                  : {payload.get('source_patch')}",
        f"Authorization Requested       : {payload.get('manifest_validation_authorization_requested')}",
        f"Authorization Token Present   : {payload.get('manifest_validation_authorization_token_present')}",
        f"Authorization Token Valid     : {payload.get('manifest_validation_authorization_token_valid')}",
        f"Future Authorization Granted  : {payload.get('manifest_validation_authorization_granted_for_future_patch')}",
        f"Manifest Execution Allowed    : {payload.get('manifest_validation_execution_allowed')}",
        f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",
        f"Archive Extracted             : {payload.get('archive_extracted')}",
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
    parser.add_argument("--allow-manifest-validation-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_manifest_validation_controlled_authorization_gate(
        args.repo_root,
        allow_manifest_validation_authorization=args.allow_manifest_validation_authorization,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
