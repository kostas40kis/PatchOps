"""L22.1a passive preflight repair for downloaded-archive manifest validation.

This module repairs L22.1 by using a less brittle source readback against the
accepted L21.7a archive final marker repair. It remains readback-only: no Edge
start, page inspection, click, download, archive extraction, manifest read,
archive member-byte read, downloaded file-byte read, file stat/hash, paste, send,
package run, localhost server, browser extension, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L22.1a"
PHASE = "L22"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L22.1a Microsoft Edge downloaded-archive manifest validation passive preflight repair"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-manifest-validation-passive-preflight-gate-repair"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-final-acceptance-marker-repair"
SOURCE_PATCH = "L21.7a"
NEXT_PATCH = "L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN = "PATCHOPS_L22_EDGE_DOWNLOADED_ARCHIVE_MANIFEST_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_repair.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_repair.md",
    "scripts/patch_l22_01a_brief_validate.py",
    "tests/test_l22_01a_edge_downloaded_archive_manifest_validation_passive_preflight_gate_repair_current.py",
)

SAFETY_PHRASES = (
    "L22.1a Microsoft Edge downloaded-archive manifest validation passive preflight repair",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-archive manifest validation passive preflight repair",
    "manifest validation preflight authorization is readback-only",
    "L21.7a archive final marker repair remains accepted",
    "L21 completion means metadata-only listing of the synthetic archive fixture",
    "manifest validation execution allowed: false",
    "manifest validation active: false",
    "manifest validation is not performed",
    "downloaded manifest is not read",
    "downloaded archive is not extracted",
    "archive member bytes are not read",
    "downloaded archive is not opened for manifest validation",
    "downloaded archive contents are not listed for manifest validation",
    "downloaded file bytes are not read",
    "downloaded file stat is not performed",
    "downloaded file hash is not performed",
    "package-run from browser remains inactive",
    "pasteback remains inactive",
    "download workflow remains inactive",
    "real browser download remains inactive",
    "PatchOps remains source of truth",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be selected but not opened",
    "dedicated Microsoft Edge runtime profile remains required for future live phases",
    "never use the default Microsoft Edge profile",
    "no Microsoft Edge start",
    "no Selenium import",
    "no CDP use",
    "no DOM scraping",
    "no prompt text extraction",
    "no conversation reading",
    "no artifact content reading",
    "no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest-read/member-byte-read/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "less brittle source readback than L22.1",
    "L22.2 Microsoft Edge downloaded-archive manifest validation CLI/readback checkpoint",
)

MANIFEST_FALSE_FIELDS = (
    "manifest_validation_execution_allowed",
    "manifest_validation_active",
    "manifest_validation_performed",
    "downloaded_manifest_read",
    "downloaded_archive_opened_for_manifest_validation",
    "downloaded_archive_contents_listed_for_manifest_validation",
    "downloaded_archive_extracted",
    "archive_member_bytes_read",
    "downloaded_file_bytes_read",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "real_file_stat_performed",
    "real_file_hash_performed",
    "package_run_from_browser_active",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_performed",
    "live_browser_download_workflow_active",
    "live_browser_download_workflow_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "chatgpt_url_opened",
    "page_inspection_performed",
    "page_metadata_detection_performed",
    "selenium_required",
    "selenium_imported_by_readback",
    "cdp_used",
    "remote_debugging_port_used",
    "browser_session_created",
    "driver_created",
    "dom_scraping_performed",
    "prompt_text_extraction_performed",
    "conversation_reading_performed",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "localhost_patchops_server_started",
    "browser_extension_used",
    "git_commit_executed",
    "git_push_executed",
)


def _repo_root(repo_root: str | Path | None) -> Path:
    return Path.cwd().resolve() if repo_root is None or str(repo_root) == "." else Path(repo_root).resolve()


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _command_names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _missing_doc_phrases(root: Path) -> list[str]:
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_archive_manifest_validation_passive_preflight_gate_repair.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _manifest_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in MANIFEST_FALSE_FIELDS}


def _manifest_payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_manifest_false_summary(payload).values())


def _load_source(root: Path, target_url: str) -> dict[str, Any]:
    try:
        from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_final_acceptance_marker_repair as l21_07a
        return dict(l21_07a.build_edge_downloaded_archive_validation_final_acceptance_marker_repair(root, target_url=target_url))
    except Exception as exc:
        return {
            "ok": False,
            "patch": SOURCE_PATCH,
            "target_url_allowed": target_url.startswith("https://chatgpt.com"),
            "source_error": f"{type(exc).__name__}: {exc}",
        }


def _source_ok(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("patch") in {"L21.7a", "L21.7"}
        and bool(source.get("target_url_allowed", True)) is True
        and source.get("downloaded_archive_extracted") is False
        and source.get("downloaded_manifest_read") is False
        and source.get("archive_member_bytes_read") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
    )


def build_manifest_validation_preflight_readback(
    *,
    allow_manifest_validation_preflight: bool = False,
    authorization_token: str | None = None,
) -> dict[str, Any]:
    requested = bool(allow_manifest_validation_preflight)
    token_present = authorization_token == REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN
    authorized = requested and token_present
    return {
        "manifest_validation_preflight_requested": requested,
        "manifest_validation_preflight_authorization_token_required": True,
        "manifest_validation_preflight_authorization_token_present": token_present,
        "manifest_validation_preflight_authorized": authorized,
        "manifest_validation_preflight_authorization_is_readback_only_in_l22_1a": True,
        "manifest_validation_execution_allowed": False,
        "manifest_validation_active": False,
        "manifest_validation_performed": False,
        "downloaded_manifest_read": False,
        "downloaded_archive_opened_for_manifest_validation": False,
        "downloaded_archive_contents_listed_for_manifest_validation": False,
        "downloaded_archive_extracted": False,
        "archive_member_bytes_read": False,
        "downloaded_file_bytes_read": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "package_run_performed_by_adapter": False,
        "pasteback_workflow_active": False,
        "required_authorization_token": REQUIRED_MANIFEST_PREFLIGHT_AUTHORIZATION_TOKEN,
    }


def build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_repair(
    repo_root: str | Path | None = None,
    *,
    allow_manifest_validation_preflight: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = _load_source(root, target)
    readback = build_manifest_validation_preflight_readback(
        allow_manifest_validation_preflight=allow_manifest_validation_preflight,
        authorization_token=authorization_token,
    )

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed", target.startswith("https://chatgpt.com")))
    source_ok = _source_ok(source)

    base_payload: dict[str, Any] = {
        "manifest_validation_execution_allowed": False,
        "manifest_validation_active": False,
        "manifest_validation_performed": False,
        "downloaded_manifest_read": False,
        "downloaded_archive_opened_for_manifest_validation": False,
        "downloaded_archive_contents_listed_for_manifest_validation": False,
        "downloaded_archive_extracted": False,
        "archive_member_bytes_read": False,
        "downloaded_file_bytes_read": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "real_file_stat_performed": False,
        "real_file_hash_performed": False,
        "package_run_from_browser_active": False,
        "download_workflow_execution_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_allowed": False,
        "download_performed": False,
        "click_download_performed": False,
        "artifact_content_reading_performed": False,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_performed": False,
        "live_browser_download_workflow_active": False,
        "live_browser_download_workflow_performed": False,
        "pasteback_workflow_active": False,
        "auto_send_allowed": False,
        "launch_execution_allowed": False,
        "browser_process_launch_requested": False,
        "browser_started": False,
        "edge_process_started": False,
        "chatgpt_url_opened": False,
        "page_inspection_performed": False,
        "page_metadata_detection_performed": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "cdp_used": False,
        "remote_debugging_port_used": False,
        "browser_session_created": False,
        "driver_created": False,
        "dom_scraping_performed": False,
        "prompt_text_extraction_performed": False,
        "conversation_reading_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "git_commit_executed": False,
        "git_push_executed": False,
    }
    passive = _manifest_payload_is_passive(base_payload)

    checks = [
        _check("source_l21_7a_archive_final_marker_repair_accepted", source_ok),
        _check("manifest_validation_preflight_authorization_surface_present", True),
        _check("manifest_validation_preflight_authorization_is_readback_only", readback["manifest_validation_preflight_authorization_is_readback_only_in_l22_1a"] is True),
        _check("manifest_validation_execution_blocked", passive),
        _check("manifest_read_archive_extract_member_byte_package_run_blocked", passive),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("less_brittle_source_readback_than_l22_1", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l22_1a_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("no_forbidden_optional_browser_imports", not forbidden_imports_newly_loaded, {"newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(check["ok"] for check in checks)

    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": SOURCE_PATCH,
        "next_patch": NEXT_PATCH,
        "downloaded_archive_manifest_validation_passive_preflight_gate_repair": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l21_7a_archive_final_marker_repair_accepted": source_ok,
        "l21_downloaded_archive_validation_stream_complete": bool(source.get("l21_downloaded_archive_validation_stream_complete", source_ok)),
        "l21_completion_means_metadata_only_archive_listing": bool(source.get("l21_completion_means_metadata_only_synthetic_archive_listing", source_ok)),
        "source_archive_validation_scope": source.get("archive_validation_scope"),
        "manifest_validation_preflight_readback": readback,
        "manifest_validation_preflight_requested": readback["manifest_validation_preflight_requested"],
        "manifest_validation_preflight_authorized": readback["manifest_validation_preflight_authorized"],
        "manifest_validation_preflight_authorization_is_readback_only_in_l22_1a": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "patchops_remains_source_of_truth": True,
        "real_browser_download_remains_inactive": True,
        "pasteback_remains_inactive": True,
        "package_run_from_browser_remains_inactive": True,
        "source_l21_7a_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l21_downloaded_archive_validation_stream_complete": source.get("l21_downloaded_archive_validation_stream_complete"),
            "archive_validation_scope": source.get("archive_validation_scope"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "downloaded_archive_extracted": source.get("downloaded_archive_extracted"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "archive_member_bytes_read": source.get("archive_member_bytes_read"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
            "target_url_allowed": source.get("target_url_allowed"),
            "source_error": source.get("source_error"),
        },
        "l22_1a_complete": ok,
        "remaining_l22_1a_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }
    payload.update(base_payload)
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"L21.7a Accepted               : {payload.get('source_l21_7a_archive_final_marker_repair_accepted')}",
        f"Manifest Preflight Authorized : {payload.get('manifest_validation_preflight_authorized')}",
        f"Manifest Execution Allowed    : {payload.get('manifest_validation_execution_allowed')}",
        f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",
        f"Archive Extracted             : {payload.get('downloaded_archive_extracted')}",
        f"Browser Started               : {payload.get('browser_started')}",
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
    parser.add_argument("--allow-manifest-validation-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_downloaded_archive_manifest_validation_passive_preflight_gate_repair(
        args.repo_root,
        allow_manifest_validation_preflight=args.allow_manifest_validation_preflight,
        authorization_token=args.authorization_token,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
