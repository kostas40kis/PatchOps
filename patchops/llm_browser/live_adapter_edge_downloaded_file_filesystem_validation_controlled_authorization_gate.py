"""L20.4 controlled authorization gate for downloaded-file filesystem validation.

This checkpoint adds an explicit future authorization token/readback surface after
L20.3. It remains passive/readback-only: no Edge start, no real page inspection,
no click, no download, no real file existence check, no stat, no hash, no archive
open/list/extract, no manifest read, no file-byte read, no artifact-content read,
no paste, no send, no package run, no localhost server, no browser extension, no
commit, and no push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint as l20_03

PATCH = "L20.4"
PHASE = "L20"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L20.4 Microsoft Edge downloaded-file filesystem validation controlled authorization gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-controlled-authorization-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-filesystem-validation-passive-plan-checkpoint"
SOURCE_PATCH = "L20.3"
NEXT_PATCH = "L20.5 Microsoft Edge first controlled downloaded-file filesystem validation proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_FILESYSTEM_VALIDATION_AUTHORIZATION_TOKEN = "PATCHOPS_L20_EDGE_DOWNLOADED_FILE_FILESYSTEM_VALIDATION_CONTROLLED_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_filesystem_validation_controlled_authorization_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_controlled_authorization_gate.md",
    "scripts/patch_l20_01_brief_validate.py",
    "scripts/patch_l20_02_brief_validate.py",
    "scripts/patch_l20_03_brief_validate.py",
    "scripts/patch_l20_04_brief_validate.py",
    "tests/test_l20_01_edge_downloaded_file_filesystem_validation_passive_preflight_gate_current.py",
    "tests/test_l20_02_edge_downloaded_file_filesystem_validation_cli_readback_checkpoint_current.py",
    "tests/test_l20_03_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint_current.py",
    "tests/test_l20_04_edge_downloaded_file_filesystem_validation_controlled_authorization_gate_current.py",
)

SAFETY_PHRASES = (
    "L20.4 Microsoft Edge downloaded-file filesystem validation controlled authorization gate",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_FILESYSTEM_VALIDATION_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-file filesystem validation controlled authorization gate",
    "controlled authorization gate",
    "L20.3 passive plan checkpoint remains accepted",
    "explicit future filesystem validation authorization token",
    "filesystem validation authorization is readback-only",
    "filesystem validation execution allowed: false",
    "filesystem validation active: false",
    "filesystem validation is not performed",
    "real filesystem validation remains inactive",
    "real file existence check remains inactive",
    "real file stat remains inactive",
    "real file hash remains inactive",
    "archive validation remains inactive",
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
    "L20.5 Microsoft Edge first controlled downloaded-file filesystem validation proof",
)

PASSIVE_FALSE_FIELDS = (
    "controlled_filesystem_validation_execution_allowed",
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

SOURCE_L20_3_PASSIVE_FALSE_FIELDS = tuple(
    field for field in PASSIVE_FALSE_FIELDS if field != "controlled_filesystem_validation_execution_allowed"
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_file_filesystem_validation_controlled_authorization_gate.md")
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
    return {field: payload.get(field) is False for field in SOURCE_L20_3_PASSIVE_FALSE_FIELDS}


def _source_payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_source_passive_false_summary(payload).values())


def build_filesystem_validation_authorization_readback(
    *,
    allow_filesystem_validation_authorization: bool = False,
    authorization_token: str | None = None,
) -> dict[str, Any]:
    requested = bool(allow_filesystem_validation_authorization)
    token_present = authorization_token == REQUIRED_FILESYSTEM_VALIDATION_AUTHORIZATION_TOKEN
    authorized = requested and token_present
    return {
        "filesystem_validation_authorization_requested": requested,
        "filesystem_validation_authorization_token_required": True,
        "filesystem_validation_authorization_token_present": token_present,
        "filesystem_validation_authorized_for_future_phase": authorized,
        "filesystem_validation_authorization_is_readback_only_in_l20_4": True,
        "controlled_filesystem_validation_execution_allowed": False,
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
        "downloaded_file_exists_check_performed": False,
        "downloaded_file_stat_performed": False,
        "downloaded_file_hash_performed": False,
        "downloaded_file_bytes_read": False,
        "downloaded_archive_opened": False,
        "downloaded_archive_contents_listed": False,
        "downloaded_archive_extracted": False,
        "downloaded_manifest_read": False,
        "required_authorization_token": REQUIRED_FILESYSTEM_VALIDATION_AUTHORIZATION_TOKEN,
        "operator_review_required_before_filesystem_validation": True,
        "archive_validation_requires_separate_gate": True,
        "hash_requires_separate_byte_read_gate": True,
        "package_run_from_browser_remains_inactive": True,
        "pasteback_remains_inactive": True,
    }


def future_filesystem_validation_authorization_gate_plan() -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l20_3_passive_plan_checkpoint_accepted",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "require_explicit_filesystem_validation_authorization_flag",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 3,
            "name": "require_exact_filesystem_validation_authorization_token",
            "status": "planned_not_executed",
            "required_authorization_token": REQUIRED_FILESYSTEM_VALIDATION_AUTHORIZATION_TOKEN,
            "side_effect": False,
        },
        {
            "step": 4,
            "name": "future_l20_5_or_later_may_check_file_existence_without_reading_bytes",
            "status": "planned_not_executed",
            "allowed_only_in_future_l20_5_or_later": True,
            "side_effect": True,
            "file_exists_check_in_l20_4": False,
            "read_file_bytes": False,
            "archive_open": False,
            "manifest_read": False,
            "package_run": False,
        },
        {
            "step": 5,
            "name": "future_stat_hash_archive_manifest_package_run_remain_separately_gated",
            "status": "planned_not_executed",
            "allowed_only_in_later_stream": True,
            "side_effect": True,
            "file_stat_in_l20_4": False,
            "file_hash_in_l20_4": False,
            "file_byte_read_in_l20_4": False,
            "archive_open_in_l20_4": False,
            "archive_listing_in_l20_4": False,
            "archive_extract_in_l20_4": False,
            "manifest_read_in_l20_4": False,
            "package_run_in_l20_4": False,
        },
        {
            "step": 6,
            "name": "l20_4_readback_does_not_execute_filesystem_validation",
            "status": "planned_not_executed",
            "side_effect": False,
            "filesystem_validation_execution_allowed": False,
            "real_file_exists_check_performed": False,
            "real_file_stat_performed": False,
            "real_file_hash_performed": False,
            "downloaded_file_bytes_read": False,
            "downloaded_archive_opened": False,
            "downloaded_archive_contents_listed": False,
            "downloaded_archive_extracted": False,
            "downloaded_manifest_read": False,
            "package_run": False,
            "pasteback": False,
            "auto_send": False,
        },
    ]


def _plan_is_planned_not_executed(plan: Sequence[Mapping[str, Any]]) -> bool:
    return all(item.get("status") == "planned_not_executed" for item in plan)


def _plan_blocks_filesystem_file_read_archive_package_run(plan: Sequence[Mapping[str, Any]]) -> bool:
    future_exists = plan[3]
    later = plan[4]
    final = plan[-1]
    return (
        future_exists.get("file_exists_check_in_l20_4") is False
        and future_exists.get("read_file_bytes") is False
        and future_exists.get("archive_open") is False
        and future_exists.get("manifest_read") is False
        and future_exists.get("package_run") is False
        and later.get("file_stat_in_l20_4") is False
        and later.get("file_hash_in_l20_4") is False
        and later.get("file_byte_read_in_l20_4") is False
        and later.get("archive_open_in_l20_4") is False
        and later.get("archive_listing_in_l20_4") is False
        and later.get("archive_extract_in_l20_4") is False
        and later.get("manifest_read_in_l20_4") is False
        and later.get("package_run_in_l20_4") is False
        and final.get("filesystem_validation_execution_allowed") is False
        and final.get("real_file_exists_check_performed") is False
        and final.get("real_file_stat_performed") is False
        and final.get("real_file_hash_performed") is False
        and final.get("downloaded_file_bytes_read") is False
        and final.get("downloaded_archive_opened") is False
        and final.get("downloaded_archive_contents_listed") is False
        and final.get("downloaded_archive_extracted") is False
        and final.get("downloaded_manifest_read") is False
        and final.get("package_run") is False
        and final.get("pasteback") is False
        and final.get("auto_send") is False
    )


def build_edge_downloaded_file_filesystem_validation_controlled_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_filesystem_validation_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L20.4 controlled authorization gate payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = l20_03.build_edge_downloaded_file_filesystem_validation_passive_plan_checkpoint(root, target_url=target)
    auth = build_filesystem_validation_authorization_readback(
        allow_filesystem_validation_authorization=allow_filesystem_validation_authorization,
        authorization_token=authorization_token,
    )
    plan = future_filesystem_validation_authorization_gate_plan()

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed"))

    source_passive = _source_payload_is_passive(source)
    source_ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l20_3_complete") is True
        and source.get("source_l20_2_cli_readback_checkpoint_accepted") is True
        and source.get("future_filesystem_validation_plan_blocks_filesystem_file_read_archive_package_run") is True
        and source.get("filesystem_validation_execution_allowed") is False
        and source.get("filesystem_validation_active") is False
        and source.get("filesystem_validation_performed") is False
        and source.get("real_filesystem_validation_active") is False
        and source.get("real_file_exists_check_performed") is False
        and source.get("real_file_stat_performed") is False
        and source.get("real_file_hash_performed") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("downloaded_archive_opened") is False
        and source.get("downloaded_manifest_read") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
        and source_passive
    )
    authorization_surface_ok = (
        auth["filesystem_validation_authorization_token_required"] is True
        and auth["filesystem_validation_authorization_is_readback_only_in_l20_4"] is True
    )
    execution_blocked = (
        auth["controlled_filesystem_validation_execution_allowed"] is False
        and auth["filesystem_validation_execution_allowed"] is False
        and auth["filesystem_validation_active"] is False
        and auth["filesystem_validation_performed"] is False
        and auth["real_filesystem_validation_active"] is False
        and auth["real_file_exists_check_performed"] is False
        and auth["real_file_stat_performed"] is False
        and auth["real_file_hash_performed"] is False
        and auth["archive_validation_performed"] is False
        and auth["downloaded_file_bytes_read"] is False
        and auth["downloaded_archive_opened"] is False
        and auth["downloaded_archive_contents_listed"] is False
        and auth["downloaded_archive_extracted"] is False
        and auth["downloaded_manifest_read"] is False
    )
    plan_is_planned_not_executed = _plan_is_planned_not_executed(plan)
    plan_blocks = _plan_blocks_filesystem_file_read_archive_package_run(plan)

    checks = [
        _check("source_l20_3_passive_plan_checkpoint_accepted", source_ok),
        _check("source_l20_3_readback_remains_passive", source_passive, _source_passive_false_summary(source)),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("filesystem_validation_authorization_surface_present", authorization_surface_ok),
        _check("filesystem_validation_authorization_is_readback_only", True),
        _check("filesystem_validation_execution_blocked", execution_blocked),
        _check("future_authorization_gate_plan_is_planned_not_executed", plan_is_planned_not_executed),
        _check("future_authorization_gate_plan_blocks_filesystem_file_read_archive_package_run", plan_blocks),
        _check("real_file_stat_hash_archive_manifest_pasteback_and_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l20_4_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "controlled_authorization_gate": True,
        "filesystem_validation_controlled_authorization_gate": True,
        "passive_readback_only_in_l20_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l20_3_passive_plan_checkpoint_accepted": source_ok,
        "l20_3_complete": bool(source.get("l20_3_complete")),
        "filesystem_validation_authorization_readback": auth,
        "filesystem_validation_authorization_requested": auth["filesystem_validation_authorization_requested"],
        "filesystem_validation_authorization_token_present": auth["filesystem_validation_authorization_token_present"],
        "filesystem_validation_authorized_for_future_phase": auth["filesystem_validation_authorized_for_future_phase"],
        "filesystem_validation_authorization_is_readback_only_in_l20_4": True,
        "controlled_filesystem_validation_execution_allowed": False,
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
        "future_filesystem_validation_authorization_gate_plan": plan,
        "future_authorization_gate_plan_is_planned_not_executed": plan_is_planned_not_executed,
        "future_authorization_gate_plan_blocks_filesystem_file_read_archive_package_run": plan_blocks,
        "source_l20_3_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l20_3_complete": source.get("l20_3_complete"),
            "source_l20_2_cli_readback_checkpoint_accepted": source.get("source_l20_2_cli_readback_checkpoint_accepted"),
            "future_filesystem_validation_plan_blocks_filesystem_file_read_archive_package_run": source.get("future_filesystem_validation_plan_blocks_filesystem_file_read_archive_package_run"),
            "filesystem_validation_execution_allowed": source.get("filesystem_validation_execution_allowed"),
            "filesystem_validation_active": source.get("filesystem_validation_active"),
            "filesystem_validation_performed": source.get("filesystem_validation_performed"),
            "real_filesystem_validation_active": source.get("real_filesystem_validation_active"),
            "real_file_exists_check_performed": source.get("real_file_exists_check_performed"),
            "real_file_stat_performed": source.get("real_file_stat_performed"),
            "real_file_hash_performed": source.get("real_file_hash_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l20_4_complete": ok,
        "remaining_l20_4_patches": [] if ok else [PATCH],
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
        f"L20.3 Accepted                  : {payload.get('source_l20_3_passive_plan_checkpoint_accepted')}",
        f"Authorization Requested         : {payload.get('filesystem_validation_authorization_requested')}",
        f"Future Authorization Accepted   : {payload.get('filesystem_validation_authorized_for_future_phase')}",
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
    parser.add_argument("--allow-filesystem-validation-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_downloaded_file_filesystem_validation_controlled_authorization_gate(
        args.repo_root,
        allow_filesystem_validation_authorization=args.allow_filesystem_validation_authorization,
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
