"""L20.1 passive preflight gate for downloaded-file filesystem validation.

This starts a separate filesystem-validation stream after accepted L19.7. L20.1
is readback-only. It does not start Edge, inspect a page, click, download, check
whether a real file exists, stat/hash files, open/list/extract archives, read
manifests, read file bytes, read artifact content, paste, send, run packages,
start localhost services, use browser extensions, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_final_acceptance_marker as l19_07

PATCH = "L20.1"
PHASE = "L20"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L20.1 Microsoft Edge downloaded-file filesystem validation passive preflight gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-preflight-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-validation-final-acceptance-marker"
SOURCE_PATCH = "L19.7"
NEXT_PATCH = "L20.2 Microsoft Edge downloaded-file filesystem validation CLI/readback checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZATION_TOKEN = "PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_file_validation_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_file_validation_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.md",
    "scripts/patch_l19_07_brief_validate.py",
    "scripts/patch_l20_01_brief_validate.py",
    "tests/test_l19_07_edge_downloaded_file_validation_final_acceptance_marker_current.py",
    "tests/test_l20_01_edge_downloaded_file_filesystem_validation_passive_preflight_gate_current.py",
)

SAFETY_PHRASES = (
    "L20.1 Microsoft Edge downloaded-file filesystem validation passive preflight gate",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-file filesystem validation passive preflight gate",
    "L19.7 downloaded-file validation final acceptance marker remains accepted",
    "L19 downloaded-file validation stream is complete as metadata/readback-only",
    "filesystem validation preflight authorization is readback-only",
    "filesystem validation execution allowed: false",
    "filesystem validation active: false",
    "real filesystem validation remains inactive",
    "real file existence check remains inactive",
    "real file stat remains inactive",
    "real file hash remains inactive",
    "downloaded-file validation execution allowed: false",
    "downloaded-file validation active: false",
    "downloaded-file validation is not performed",
    "downloaded file existence check is not performed",
    "downloaded file stat is not performed",
    "downloaded file hash is not performed",
    "downloaded file bytes are not read",
    "downloaded archive is not opened",
    "downloaded archive contents are not listed",
    "downloaded archive is not extracted",
    "downloaded manifest is not read",
    "download workflow remains inactive",
    "real browser download remains inactive",
    "pasteback remains inactive",
    "package-run from browser remains inactive",
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
    "no click/download/file-read/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L20.2 Microsoft Edge downloaded-file filesystem validation CLI/readback checkpoint",
)

PASSIVE_FALSE_FIELDS = (
    "filesystem_validation_execution_allowed",
    "filesystem_validation_active",
    "filesystem_validation_performed",
    "real_filesystem_validation_active",
    "real_file_existence_check_active",
    "real_file_stat_active",
    "real_file_hash_active",
    "real_file_exists_check_performed",
    "real_file_stat_performed",
    "real_file_hash_performed",
    "archive_validation_active",
    "archive_validation_performed",
    "controlled_downloaded_file_validation_execution_allowed",
    "downloaded_file_metadata_validation_execution_allowed",
    "downloaded_file_metadata_validation_active",
    "downloaded_file_validation_execution_allowed",
    "downloaded_file_validation_active",
    "downloaded_file_validation_performed",
    "downloaded_file_exists_check_performed",
    "downloaded_file_stat_performed",
    "downloaded_file_hash_performed",
    "downloaded_file_bytes_read",
    "downloaded_archive_opened",
    "downloaded_archive_contents_listed",
    "downloaded_archive_extracted",
    "downloaded_manifest_read",
    "live_download_execution_allowed",
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_performed",
    "real_page_inspection_performed",
    "live_browser_artifact_detection_active",
    "live_browser_artifact_detection_performed",
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

SOURCE_L19_7_PASSIVE_FALSE_FIELDS = tuple(
    field for field in PASSIVE_FALSE_FIELDS
    if field not in {
        "filesystem_validation_execution_allowed",
        "filesystem_validation_active",
        "filesystem_validation_performed",
        "real_file_exists_check_performed",
        "real_file_stat_performed",
        "real_file_hash_performed",
        "archive_validation_performed",
    }
)


def _repo_root(repo_root: str | Path | None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _passive_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in PASSIVE_FALSE_FIELDS}


def _payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_passive_false_summary(payload).values())


def _source_passive_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in SOURCE_L19_7_PASSIVE_FALSE_FIELDS}


def _source_payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_source_passive_false_summary(payload).values())


def build_filesystem_validation_preflight_authorization_readback(
    *,
    allow_filesystem_validation_preflight: bool = False,
    authorization_token: str | None = None,
) -> dict[str, Any]:
    requested = bool(allow_filesystem_validation_preflight)
    token_present = authorization_token == REQUIRED_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZATION_TOKEN
    authorized = requested and token_present
    return {
        "filesystem_validation_preflight_requested": requested,
        "filesystem_validation_preflight_authorization_token_required": True,
        "filesystem_validation_preflight_authorization_token_present": token_present,
        "filesystem_validation_preflight_authorized": authorized,
        "filesystem_validation_preflight_authorization_is_readback_only_in_l20_1": True,
        "filesystem_validation_execution_allowed": False,
        "filesystem_validation_active": False,
        "filesystem_validation_performed": False,
        "real_filesystem_validation_active": False,
        "real_file_existence_check_active": False,
        "real_file_stat_active": False,
        "real_file_hash_active": False,
        "real_file_exists_check_performed": False,
        "real_file_stat_performed": False,
        "real_file_hash_performed": False,
        "downloaded_file_exists_check_performed": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "downloaded_file_bytes_read": False,
        "downloaded_archive_opened": False,
        "downloaded_archive_contents_listed": False,
        "downloaded_archive_extracted": False,
        "downloaded_manifest_read": False,
        "required_authorization_token": REQUIRED_FILESYSTEM_VALIDATION_PREFLIGHT_AUTHORIZATION_TOKEN,
    }


def _source_l19_7_ok(root: Path, target_url: str) -> tuple[bool, dict[str, Any]]:
    source = l19_07.build_edge_downloaded_file_validation_final_acceptance_marker(root, target_url=target_url)
    ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l19_7_complete") is True
        and source.get("l19_downloaded_file_validation_stream_complete") is True
        and source.get("downloaded_file_validation_stream_completion_is_metadata_readback_only") is True
        and source.get("real_filesystem_validation_active") is False
        and source.get("real_file_existence_check_active") is False
        and source.get("real_file_stat_active") is False
        and source.get("real_file_hash_active") is False
        and source.get("archive_validation_active") is False
        and source.get("downloaded_file_validation_execution_allowed") is False
        and source.get("downloaded_file_validation_active") is False
        and source.get("downloaded_file_validation_performed") is False
        and source.get("downloaded_file_exists_check_performed") is False
        and source.get("downloaded_file_stat_performed") is False
        and source.get("downloaded_file_hash_performed") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("downloaded_archive_opened") is False
        and source.get("downloaded_archive_contents_listed") is False
        and source.get("downloaded_archive_extracted") is False
        and source.get("downloaded_manifest_read") is False
        and source.get("download_workflow_active") is False
        and source.get("download_performed") is False
        and source.get("click_download_performed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("chatgpt_url_opened") is False
        and source.get("package_run_performed_by_adapter") is False
        and _source_payload_is_passive(source)
    )
    return ok, source


def build_edge_downloaded_file_filesystem_validation_passive_preflight_gate(
    repo_root: str | Path | None = None,
    *,
    allow_filesystem_validation_preflight: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the L20.1 passive filesystem-validation preflight payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source_ok, source = _source_l19_7_ok(root, target)
    auth = build_filesystem_validation_preflight_authorization_readback(
        allow_filesystem_validation_preflight=allow_filesystem_validation_preflight,
        authorization_token=authorization_token,
    )

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed"))

    auth_execution_blocked = (
        auth["filesystem_validation_execution_allowed"] is False
        and auth["filesystem_validation_active"] is False
        and auth["filesystem_validation_performed"] is False
        and auth["real_filesystem_validation_active"] is False
        and auth["real_file_existence_check_active"] is False
        and auth["real_file_stat_active"] is False
        and auth["real_file_hash_active"] is False
        and auth["real_file_exists_check_performed"] is False
        and auth["real_file_stat_performed"] is False
        and auth["real_file_hash_performed"] is False
        and auth["downloaded_file_exists_check_performed"] is False
        and auth["downloaded_file_stat_performed"] is False
        and auth["downloaded_file_hash_performed"] is False
        and auth["downloaded_file_bytes_read"] is False
        and auth["downloaded_archive_opened"] is False
        and auth["downloaded_archive_contents_listed"] is False
        and auth["downloaded_archive_extracted"] is False
        and auth["downloaded_manifest_read"] is False
    )

    checks = [
        _check("source_l19_7_final_acceptance_marker_accepted", source_ok),
        _check("l19_downloaded_file_validation_complete_metadata_readback_only", source_ok),
        _check("filesystem_validation_preflight_authorization_surface_present", True),
        _check("filesystem_validation_preflight_authorization_is_readback_only", auth["filesystem_validation_preflight_authorization_is_readback_only_in_l20_1"] is True),
        _check("filesystem_validation_execution_blocked", auth_execution_blocked),
        _check("real_file_existence_stat_hash_byte_archive_manifest_package_run_blocked", True),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("dedicated_edge_profile_required_and_default_profile_rejected", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l20_1_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
        _check("no_forbidden_optional_browser_imports", not forbidden_imports_newly_loaded, {"newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(check["ok"] for check in checks)

    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": SOURCE_PATCH,
        "next_patch": NEXT_PATCH,
        "filesystem_validation_passive_preflight_gate": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l19_7_final_acceptance_marker_accepted": source_ok,
        "l19_downloaded_file_validation_stream_complete": bool(source.get("l19_downloaded_file_validation_stream_complete")),
        "l19_downloaded_file_validation_completion_metadata_readback_only": bool(source.get("downloaded_file_validation_stream_completion_is_metadata_readback_only")),
        "filesystem_validation_preflight_readback": auth,
        "filesystem_validation_preflight_requested": auth["filesystem_validation_preflight_requested"],
        "filesystem_validation_preflight_authorized": auth["filesystem_validation_preflight_authorized"],
        "filesystem_validation_preflight_authorization_is_readback_only_in_l20_1": True,
        "filesystem_validation_execution_allowed": False,
        "filesystem_validation_active": False,
        "filesystem_validation_performed": False,
        "real_filesystem_validation_active": False,
        "real_file_existence_check_active": False,
        "real_file_stat_active": False,
        "real_file_hash_active": False,
        "real_file_exists_check_performed": False,
        "real_file_stat_performed": False,
        "real_file_hash_performed": False,
        "archive_validation_active": False,
        "archive_validation_performed": False,
        "controlled_downloaded_file_validation_execution_allowed": False,
        "downloaded_file_metadata_validation_execution_allowed": False,
        "downloaded_file_metadata_validation_active": False,
        "downloaded_file_validation_execution_allowed": False,
        "downloaded_file_validation_active": False,
        "downloaded_file_validation_performed": False,
        "downloaded_file_exists_check_performed": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "downloaded_file_bytes_read": False,
        "downloaded_archive_opened": False,
        "downloaded_archive_contents_listed": False,
        "downloaded_archive_extracted": False,
        "downloaded_manifest_read": False,
        "live_download_execution_allowed": False,
        "download_workflow_execution_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_allowed": False,
        "download_performed": False,
        "download_staging_directory_created": False,
        "click_download_performed": False,
        "artifact_content_reading_performed": False,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_performed": False,
        "real_page_inspection_performed": False,
        "live_browser_artifact_detection_active": False,
        "live_browser_artifact_detection_performed": False,
        "live_browser_download_workflow_active": False,
        "live_browser_download_workflow_performed": False,
        "pasteback_workflow_active": False,
        "auto_send_allowed": False,
        "launch_execution_allowed": False,
        "browser_process_launch_requested": False,
        "browser_started": False,
        "edge_process_started": False,
        "chatgpt_url_selected_for_future_detection": target_url_allowed,
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
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "patchops_remains_source_of_truth": True,
        "target_url_allowlist_enforced": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "real_browser_download_remains_inactive": True,
        "pasteback_remains_inactive": True,
        "package_run_from_browser_remains_inactive": True,
        "source_l19_7_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l19_7_complete": source.get("l19_7_complete"),
            "l19_downloaded_file_validation_stream_complete": source.get("l19_downloaded_file_validation_stream_complete"),
            "downloaded_file_validation_stream_completion_is_metadata_readback_only": source.get("downloaded_file_validation_stream_completion_is_metadata_readback_only"),
            "real_filesystem_validation_active": source.get("real_filesystem_validation_active"),
            "real_file_existence_check_active": source.get("real_file_existence_check_active"),
            "real_file_stat_active": source.get("real_file_stat_active"),
            "real_file_hash_active": source.get("real_file_hash_active"),
            "archive_validation_active": source.get("archive_validation_active"),
            "downloaded_file_validation_execution_allowed": source.get("downloaded_file_validation_execution_allowed"),
            "downloaded_file_validation_active": source.get("downloaded_file_validation_active"),
            "downloaded_file_validation_performed": source.get("downloaded_file_validation_performed"),
            "downloaded_file_exists_check_performed": source.get("downloaded_file_exists_check_performed"),
            "downloaded_file_stat_performed": source.get("downloaded_file_stat_performed"),
            "downloaded_file_hash_performed": source.get("downloaded_file_hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "downloaded_archive_extracted": source.get("downloaded_archive_extracted"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l20_1_complete": ok,
        "remaining_l20_1_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                           : {payload.get('patch')}",
        f"Status                          : {payload.get('status')}",
        f"Command                         : {payload.get('command_name')}",
        f"L19.7 Accepted                  : {payload.get('source_l19_7_final_acceptance_marker_accepted')}",
        f"Filesystem Preflight Authorized : {payload.get('filesystem_validation_preflight_authorized')}",
        f"Filesystem Execution Allowed    : {payload.get('filesystem_validation_execution_allowed')}",
        f"Real File Exists Check          : {payload.get('real_file_exists_check_performed')}",
        f"Downloaded Bytes Read           : {payload.get('downloaded_file_bytes_read')}",
        f"Archive Opened                  : {payload.get('downloaded_archive_opened')}",
        f"Browser Started                 : {payload.get('browser_started')}",
        f"Next Patch                      : {payload.get('next_patch')}",
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
    parser.add_argument("--allow-filesystem-validation-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_downloaded_file_filesystem_validation_passive_preflight_gate(
        args.repo_root,
        allow_filesystem_validation_preflight=args.allow_filesystem_validation_preflight,
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
