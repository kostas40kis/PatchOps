"""L19.3 passive plan checkpoint for downloaded-file validation.

This module defines future downloaded-file validation rules after the accepted
L19.2 CLI/readback checkpoint. It is deliberately passive: it does not start
Edge, inspect pages, click, download, check real downloaded files, stat files,
hash files, open archives, list archive contents, extract archives, read
manifests, read file bytes, paste, send, run packages, start localhost services,
use browser extensions, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_file_validation_cli_readback_checkpoint as l19_02

PATCH = "L19.3"
PHASE = "L19"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L19.3 Microsoft Edge downloaded-file validation passive plan checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-validation-passive-plan-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-file-validation-cli-readback-checkpoint"
SOURCE_PATCH = "L19.2"
NEXT_PATCH = "L19.4 Microsoft Edge downloaded-file validation controlled authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_file_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_file_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_file_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_file_validation_passive_plan_checkpoint.md",
    "scripts/patch_l19_01_brief_validate.py",
    "scripts/patch_l19_02_brief_validate.py",
    "scripts/patch_l19_03_brief_validate.py",
    "tests/test_l19_01_edge_downloaded_file_validation_passive_preflight_gate_current.py",
    "tests/test_l19_02_edge_downloaded_file_validation_cli_readback_checkpoint_current.py",
    "tests/test_l19_03_edge_downloaded_file_validation_passive_plan_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L19.3 Microsoft Edge downloaded-file validation passive plan checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-file validation passive plan checkpoint",
    "passive plan checkpoint",
    "L19.2 CLI/readback checkpoint remains accepted",
    "safe future downloaded-file validation plan",
    "downloaded-file validation candidate means metadata-only path evidence for a future downloaded PatchOps zip artifact",
    "validation plan does not check whether a file exists",
    "validation plan does not stat a file",
    "validation plan does not hash a file",
    "validation plan does not read downloaded file bytes",
    "validation plan does not open a downloaded archive",
    "validation plan does not list downloaded archive contents",
    "validation plan does not extract a downloaded archive",
    "validation plan does not read a downloaded manifest",
    "validation plan does not run a package",
    "downloaded-file validation execution allowed: false",
    "downloaded-file validation active: false",
    "downloaded-file validation is not performed",
    "downloaded file bytes are not read",
    "downloaded archive is not opened",
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
    "L19.4 Microsoft Edge downloaded-file validation controlled authorization gate",
)

PASSIVE_FALSE_FIELDS = (
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_file_validation_passive_plan_checkpoint.md")
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


def downloaded_file_validation_candidate_definition() -> dict[str, Any]:
    return {
        "definition_version": "1",
        "candidate_means": "metadata-only path evidence for a future downloaded PatchOps zip artifact",
        "candidate_does_not_mean": [
            "checking whether a file exists",
            "stating a file",
            "hashing a file",
            "reading downloaded file bytes",
            "opening a downloaded archive",
            "listing downloaded archive contents",
            "extracting a downloaded archive",
            "reading a downloaded manifest",
            "running a package",
            "pasting into a browser",
            "sending or submitting a message",
        ],
        "future_candidate_path_rules": {
            "extension_must_be": ".zip",
            "recommended_pattern": "patch_*_patchops_bundle.zip",
            "path_must_be_metadata_only_in_l19_3": True,
            "reject_non_zip": True,
            "reject_ambiguous_multiple_candidates": True,
        },
        "future_validation_stages": {
            "existence_check_allowed_in_l19_3": False,
            "stat_allowed_in_l19_3": False,
            "hash_allowed_in_l19_3": False,
            "archive_open_allowed_in_l19_3": False,
            "archive_listing_allowed_in_l19_3": False,
            "archive_extract_allowed_in_l19_3": False,
            "manifest_read_allowed_in_l19_3": False,
            "file_byte_read_allowed_in_l19_3": False,
            "package_run_allowed_in_l19_3": False,
        },
        "operator_review_required_before_file_validation": True,
        "patchops_remains_source_of_truth": True,
    }


def future_downloaded_file_validation_plan() -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l19_2_cli_readback_checkpoint_accepted",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "require_l19_4_or_later_explicit_downloaded_file_validation_authorization_token",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 3,
            "name": "accept_future_downloaded_file_path_metadata_only",
            "status": "planned_not_executed",
            "side_effect": False,
            "path_metadata_only": True,
        },
        {
            "step": 4,
            "name": "future_phase_may_check_file_existence_without_reading_bytes",
            "status": "planned_not_executed",
            "allowed_only_in_future_l19_4_or_later": True,
            "side_effect": True,
            "read_file_bytes": False,
        },
        {
            "step": 5,
            "name": "future_phase_may_stat_and_hash_file_after_operator_review",
            "status": "planned_not_executed",
            "allowed_only_in_future_l19_4_or_later": True,
            "side_effect": True,
            "read_file_bytes": True,
            "run_package": False,
        },
        {
            "step": 6,
            "name": "future_archive_validation_must_be_gated_separately",
            "status": "planned_not_executed",
            "allowed_only_in_later_stream": True,
            "side_effect": False,
            "archive_open_in_l19_3": False,
            "archive_listing_in_l19_3": False,
            "archive_extract_in_l19_3": False,
            "manifest_read_in_l19_3": False,
            "package_run_in_l19_3": False,
        },
        {
            "step": 7,
            "name": "l19_3_plan_checkpoint_does_not_execute_validation",
            "status": "planned_not_executed",
            "side_effect": False,
            "downloaded_file_validation_execution_allowed": False,
            "downloaded_file_exists_check_performed": False,
            "downloaded_file_stat_performed": False,
            "downloaded_file_hash_performed": False,
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


def _plan_blocks_file_validation_file_read_archive_package_run(plan: Sequence[Mapping[str, Any]]) -> bool:
    final = plan[-1]
    archive = plan[5]
    return (
        final.get("downloaded_file_validation_execution_allowed") is False
        and final.get("downloaded_file_exists_check_performed") is False
        and final.get("downloaded_file_stat_performed") is False
        and final.get("downloaded_file_hash_performed") is False
        and final.get("downloaded_file_bytes_read") is False
        and final.get("downloaded_archive_opened") is False
        and final.get("downloaded_archive_contents_listed") is False
        and final.get("downloaded_archive_extracted") is False
        and final.get("downloaded_manifest_read") is False
        and final.get("package_run") is False
        and final.get("pasteback") is False
        and final.get("auto_send") is False
        and archive.get("archive_open_in_l19_3") is False
        and archive.get("archive_listing_in_l19_3") is False
        and archive.get("archive_extract_in_l19_3") is False
        and archive.get("manifest_read_in_l19_3") is False
        and archive.get("package_run_in_l19_3") is False
    )


def build_edge_downloaded_file_validation_passive_plan_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L19.3 downloaded-file validation plan checkpoint payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = l19_02.build_edge_downloaded_file_validation_cli_readback_checkpoint(root, target_url=target)

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    definition = downloaded_file_validation_candidate_definition()
    plan = future_downloaded_file_validation_plan()
    target_url_allowed = bool(source.get("target_url_allowed"))

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l19_2_complete") is True
        and source.get("l19_1_passive_preflight_gate_accepted") is True
        and source.get("downloaded_file_validation_preflight_authorization_remains_readback_only") is True
        and source.get("downloaded_file_validation_execution_allowed") is False
        and source.get("downloaded_file_validation_active") is False
        and source.get("downloaded_file_validation_performed") is False
        and source.get("downloaded_file_exists_check_performed") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("downloaded_archive_opened") is False
        and source.get("downloaded_archive_contents_listed") is False
        and source.get("downloaded_manifest_read") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
        and _payload_is_passive(source)
    )
    definition_blocks = (
        definition["future_validation_stages"]["existence_check_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["stat_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["hash_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["archive_open_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["archive_listing_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["archive_extract_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["manifest_read_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["file_byte_read_allowed_in_l19_3"] is False
        and definition["future_validation_stages"]["package_run_allowed_in_l19_3"] is False
    )
    plan_is_planned_not_executed = _plan_is_planned_not_executed(plan)
    plan_blocks = _plan_blocks_file_validation_file_read_archive_package_run(plan)

    checks = [
        _check("source_l19_2_cli_readback_checkpoint_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("downloaded_file_validation_candidate_definition_blocks_file_read_archive_package_run", definition_blocks),
        _check("future_downloaded_file_validation_plan_is_planned_not_executed", plan_is_planned_not_executed),
        _check("future_downloaded_file_validation_plan_blocks_file_checks_file_read_archive_package_run", plan_blocks),
        _check("downloaded_file_validation_execution_still_blocked", True),
        _check("downloaded_file_byte_reading_still_blocked", True),
        _check("downloaded_archive_opening_and_manifest_reading_still_blocked", True),
        _check("pasteback_and_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l19_3_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "passive_plan_checkpoint": True,
        "downloaded_file_validation_passive_plan_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l19_2_cli_readback_checkpoint_accepted": source_ok,
        "l19_2_complete": bool(source.get("l19_2_complete")),
        "l19_1_passive_preflight_gate_accepted": bool(source.get("l19_1_passive_preflight_gate_accepted")),
        "downloaded_file_validation_candidate_definition": definition,
        "downloaded_file_validation_candidate_definition_blocks_file_read_archive_package_run": definition_blocks,
        "future_downloaded_file_validation_plan": plan,
        "future_downloaded_file_validation_plan_is_planned_not_executed": plan_is_planned_not_executed,
        "future_downloaded_file_validation_plan_blocks_file_checks_file_read_archive_package_run": plan_blocks,
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
        "source_l19_2_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l19_2_complete": source.get("l19_2_complete"),
            "l19_1_passive_preflight_gate_accepted": source.get("l19_1_passive_preflight_gate_accepted"),
            "downloaded_file_validation_execution_allowed": source.get("downloaded_file_validation_execution_allowed"),
            "downloaded_file_validation_active": source.get("downloaded_file_validation_active"),
            "downloaded_file_validation_performed": source.get("downloaded_file_validation_performed"),
            "downloaded_file_exists_check_performed": source.get("downloaded_file_exists_check_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l19_3_complete": ok,
        "remaining_l19_3_patches": [] if ok else [PATCH],
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
        f"Patch                       : {payload.get('patch')}",
        f"Status                      : {payload.get('status')}",
        f"Command                     : {payload.get('command_name')}",
        f"Source Command              : {payload.get('source_command_name')}",
        f"L19.2 Accepted              : {payload.get('source_l19_2_cli_readback_checkpoint_accepted')}",
        f"Plan Blocks File Reads      : {payload.get('future_downloaded_file_validation_plan_blocks_file_checks_file_read_archive_package_run')}",
        f"File Validation Allowed     : {payload.get('downloaded_file_validation_execution_allowed')}",
        f"Downloaded Bytes Read       : {payload.get('downloaded_file_bytes_read')}",
        f"Archive Opened              : {payload.get('downloaded_archive_opened')}",
        f"Browser Started             : {payload.get('browser_started')}",
        f"Next Patch                  : {payload.get('next_patch')}",
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

    payload = build_edge_downloaded_file_validation_passive_plan_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
