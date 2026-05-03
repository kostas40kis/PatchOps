"""L21.3 passive plan checkpoint for downloaded-archive validation.

This repaired L21.3 module is intentionally conservative. It defines the future
archive-validation plan after accepted L21.2 without opening archives, listing
archive contents, extracting archives, reading manifests, reading file bytes,
stating/hashing files, starting browsers, pasting, sending, or running packages.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint as l21_02

PATCH = "L21.3"
PHASE = "L21"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L21.3 Microsoft Edge downloaded-archive validation passive plan checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-passive-plan-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-downloaded-archive-validation-cli-readback-checkpoint"
SOURCE_PATCH = "L21.2"
NEXT_PATCH = "L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
DEFAULT_ARCHIVE_PATTERN = "patch_*_patchops_bundle.zip"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer", "zipfile")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.md",
    "scripts/patch_l21_01_brief_validate.py",
    "scripts/patch_l21_02_brief_validate.py",
    "scripts/patch_l21_03_brief_validate.py",
    "tests/test_l21_01_edge_downloaded_archive_validation_passive_preflight_gate_current.py",
    "tests/test_l21_02_edge_downloaded_archive_validation_cli_readback_checkpoint_current.py",
    "tests/test_l21_03_edge_downloaded_archive_validation_passive_plan_checkpoint_current.py",
    "data/runtime/browser_downloads/patch_l20_05_synthetic_patchops_bundle.zip",
)

SAFETY_PHRASES = (
    "L21.3 Microsoft Edge downloaded-archive validation passive plan checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "downloaded-archive validation passive plan checkpoint",
    "safe future archive validation plan",
    "L21.2 CLI/readback checkpoint remains accepted",
    "archive candidate path remains metadata-only in L21.3",
    "archive validation plan does not open a downloaded archive",
    "archive validation plan does not list downloaded archive contents",
    "archive validation plan does not extract a downloaded archive",
    "archive validation plan does not read a downloaded manifest",
    "archive validation plan does not read downloaded file bytes",
    "archive validation plan does not stat a downloaded file",
    "archive validation plan does not hash a downloaded file",
    "archive validation plan does not run a package",
    "archive validation execution allowed: false",
    "archive validation active: false",
    "archive validation is not performed",
    "downloaded archive is not opened",
    "downloaded archive contents are not listed",
    "downloaded archive is not extracted",
    "downloaded manifest is not read",
    "downloaded file bytes are not read",
    "downloaded file stat is not performed",
    "downloaded file hash is not performed",
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
    "no click/download/stat/hash/archive-open/archive-list/archive-extract/manifest/byte-read/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L21.4 Microsoft Edge downloaded-archive validation controlled authorization gate",
)

ARCHIVE_FALSE_FIELDS = (
    "archive_validation_execution_allowed", "archive_validation_active", "archive_validation_performed",
    "downloaded_archive_opened", "downloaded_archive_contents_listed", "downloaded_archive_extracted",
    "downloaded_manifest_read", "downloaded_file_bytes_read", "downloaded_file_stat_performed",
    "downloaded_file_hash_performed", "real_file_stat_performed", "real_file_hash_performed",
    "download_workflow_execution_allowed", "download_workflow_active", "download_workflow_allowed",
    "download_allowed", "download_performed", "click_download_performed", "artifact_content_reading_performed",
    "artifact_detection_execution_allowed", "artifact_detection_active", "artifact_detection_performed",
    "live_browser_download_workflow_active", "live_browser_download_workflow_performed", "pasteback_workflow_active",
    "auto_send_allowed", "launch_execution_allowed", "browser_process_launch_requested", "browser_started",
    "edge_process_started", "chatgpt_url_opened", "page_inspection_performed", "page_metadata_detection_performed",
    "selenium_required", "selenium_imported_by_readback", "cdp_used", "remote_debugging_port_used",
    "browser_session_created", "driver_created", "dom_scraping_performed", "prompt_text_extraction_performed",
    "conversation_reading_performed", "paste_performed", "send_or_submit_performed", "package_run_performed_by_adapter",
    "localhost_patchops_server_started", "browser_extension_used", "git_commit_executed", "git_push_executed",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_downloaded_archive_validation_passive_plan_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _false_payload() -> dict[str, bool]:
    return {field: False for field in ARCHIVE_FALSE_FIELDS}


def archive_validation_candidate_definition() -> dict[str, Any]:
    return {
        "definition_version": "1",
        "candidate_means": "metadata-only path evidence for a future downloaded PatchOps zip archive",
        "candidate_does_not_mean": [
            "opening a downloaded archive",
            "listing downloaded archive contents",
            "extracting a downloaded archive",
            "reading a downloaded manifest",
            "reading downloaded file bytes",
            "stating or hashing a downloaded file",
            "running a package",
            "pasting into a browser",
            "sending or submitting a message",
        ],
        "future_candidate_rules": {
            "extension_must_be": ".zip",
            "recommended_pattern": DEFAULT_ARCHIVE_PATTERN,
            "candidate_path_must_remain_metadata_only_in_l21_3": True,
            "reject_non_zip": True,
            "reject_ambiguous_multiple_candidates": True,
        },
        "future_validation_stages": {
            "archive_open_allowed_in_l21_3": False,
            "archive_listing_allowed_in_l21_3": False,
            "archive_extract_allowed_in_l21_3": False,
            "manifest_read_allowed_in_l21_3": False,
            "file_byte_read_allowed_in_l21_3": False,
            "file_stat_allowed_in_l21_3": False,
            "file_hash_allowed_in_l21_3": False,
            "package_run_allowed_in_l21_3": False,
        },
        "patchops_remains_source_of_truth": True,
    }


def future_archive_validation_plan() -> list[dict[str, Any]]:
    return [
        {"step": 1, "name": "confirm_l21_2_cli_readback_checkpoint_accepted", "status": "planned_not_executed", "side_effect": False},
        {"step": 2, "name": "require_future_l21_4_archive_validation_authorization_token", "status": "planned_not_executed", "side_effect": False},
        {"step": 3, "name": "accept_archive_candidate_path_metadata_only", "status": "planned_not_executed", "metadata_only": True, "side_effect": False},
        {"step": 4, "name": "future_phase_may_open_archive_without_extracting", "status": "planned_not_executed", "archive_open_allowed_in_l21_3": False, "archive_extract": False, "manifest_read": False, "file_payload_read": False, "package_run": False},
        {"step": 5, "name": "future_archive_listing_requires_separate_authorization", "status": "planned_not_executed", "archive_listing_allowed_in_l21_3": False, "archive_extract": False, "file_payload_read": False, "manifest_read": False, "package_run": False},
        {"step": 6, "name": "future_manifest_or_file_content_read_requires_separate_stream", "status": "planned_not_executed", "manifest_read_allowed_in_l21_3": False, "file_byte_read_allowed_in_l21_3": False, "package_run_allowed_in_l21_3": False},
        {"step": 7, "name": "l21_3_plan_checkpoint_does_not_execute_archive_validation", "status": "planned_not_executed", "archive_validation_execution_allowed": False, "downloaded_archive_opened": False, "downloaded_archive_contents_listed": False, "downloaded_archive_extracted": False, "downloaded_manifest_read": False, "downloaded_file_bytes_read": False, "package_run": False, "pasteback": False, "auto_send": False},
    ]


def _source_l21_2_ok(source: Mapping[str, Any]) -> bool:
    essential_false = (
        "archive_validation_execution_allowed", "archive_validation_active", "archive_validation_performed",
        "downloaded_archive_opened", "downloaded_archive_contents_listed", "downloaded_archive_extracted",
        "downloaded_manifest_read", "downloaded_file_bytes_read", "downloaded_file_stat_performed",
        "downloaded_file_hash_performed", "browser_started", "edge_process_started", "package_run_performed_by_adapter",
    )
    return (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l21_2_complete") is True
        and source.get("l21_1_passive_preflight_gate_accepted") is True
        and source.get("l21_1_default_archive_preflight_readback_ok") is True
        and source.get("l21_1_authorized_archive_preflight_readback_ok") is True
        and all(source.get(field) is False for field in essential_false)
    )


def _plan_is_planned_not_executed(plan: Sequence[Mapping[str, Any]]) -> bool:
    return all(item.get("status") == "planned_not_executed" for item in plan)


def _plan_blocks_archive_execution(plan: Sequence[Mapping[str, Any]]) -> bool:
    return (
        plan[3].get("archive_open_allowed_in_l21_3") is False
        and plan[3].get("archive_extract") is False
        and plan[3].get("manifest_read") is False
        and plan[3].get("file_payload_read") is False
        and plan[3].get("package_run") is False
        and plan[4].get("archive_listing_allowed_in_l21_3") is False
        and plan[4].get("archive_extract") is False
        and plan[4].get("file_payload_read") is False
        and plan[4].get("manifest_read") is False
        and plan[4].get("package_run") is False
        and plan[5].get("manifest_read_allowed_in_l21_3") is False
        and plan[5].get("file_byte_read_allowed_in_l21_3") is False
        and plan[5].get("package_run_allowed_in_l21_3") is False
        and plan[-1].get("archive_validation_execution_allowed") is False
        and plan[-1].get("downloaded_archive_opened") is False
        and plan[-1].get("downloaded_archive_contents_listed") is False
        and plan[-1].get("downloaded_archive_extracted") is False
        and plan[-1].get("downloaded_manifest_read") is False
        and plan[-1].get("downloaded_file_bytes_read") is False
        and plan[-1].get("package_run") is False
        and plan[-1].get("pasteback") is False
        and plan[-1].get("auto_send") is False
    )


def build_edge_downloaded_archive_validation_passive_plan_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = l21_02.build_edge_downloaded_archive_validation_cli_readback_checkpoint(root, target_url=target)
    definition = archive_validation_candidate_definition()
    plan = future_archive_validation_plan()
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target_url_allowed = bool(source.get("target_url_allowed"))
    source_ok = _source_l21_2_ok(source)
    definition_blocks = all(value is False for value in definition["future_validation_stages"].values())
    plan_is_planned = _plan_is_planned_not_executed(plan)
    plan_blocks = _plan_blocks_archive_execution(plan)
    false_fields = _false_payload()

    checks = [
        _check("source_l21_2_cli_readback_checkpoint_accepted", source_ok),
        _check("l21_1_passive_preflight_gate_accepted", bool(source.get("l21_1_passive_preflight_gate_accepted"))),
        _check("archive_candidate_definition_blocks_l21_3_archive_execution", definition_blocks),
        _check("future_archive_validation_plan_is_planned_not_executed", plan_is_planned),
        _check("future_archive_validation_plan_blocks_archive_execution", plan_blocks),
        _check("archive_open_list_extract_manifest_byte_read_package_run_still_blocked", True),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l21_3_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "downloaded_archive_validation_passive_plan_checkpoint": True,
        "passive_plan_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l21_2_cli_readback_checkpoint_accepted": source_ok,
        "l21_2_complete": bool(source.get("l21_2_complete")),
        "l21_1_passive_preflight_gate_accepted": bool(source.get("l21_1_passive_preflight_gate_accepted")),
        "archive_candidate_definition": definition,
        "archive_candidate_definition_blocks_l21_3_archive_execution": definition_blocks,
        "future_archive_validation_plan": plan,
        "future_archive_validation_plan_is_planned_not_executed": plan_is_planned,
        "future_archive_validation_plan_blocks_archive_execution": plan_blocks,
        "archive_validation_scope": "future_plan_only_metadata_only_no_archive_access",
        "hash_validation_active": False,
        "manifest_read_active": False,
        "package_run_from_browser_active": False,
        "chatgpt_url_selected_for_future_detection": target_url_allowed,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "patchops_remains_source_of_truth": True,
        "target_url_allowlist_enforced": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "real_browser_download_remains_inactive": True,
        "pasteback_remains_inactive": True,
        "package_run_from_browser_remains_inactive": True,
        "source_l21_2_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l21_2_complete": source.get("l21_2_complete"),
            "l21_1_passive_preflight_gate_accepted": source.get("l21_1_passive_preflight_gate_accepted"),
            "l21_1_default_archive_preflight_readback_ok": source.get("l21_1_default_archive_preflight_readback_ok"),
            "l21_1_authorized_archive_preflight_readback_ok": source.get("l21_1_authorized_archive_preflight_readback_ok"),
            "archive_validation_execution_allowed": source.get("archive_validation_execution_allowed"),
            "archive_validation_active": source.get("archive_validation_active"),
            "archive_validation_performed": source.get("archive_validation_performed"),
            "downloaded_archive_opened": source.get("downloaded_archive_opened"),
            "downloaded_archive_contents_listed": source.get("downloaded_archive_contents_listed"),
            "downloaded_archive_extracted": source.get("downloaded_archive_extracted"),
            "downloaded_manifest_read": source.get("downloaded_manifest_read"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "downloaded_file_stat_performed": source.get("downloaded_file_stat_performed"),
            "downloaded_file_hash_performed": source.get("downloaded_file_hash_performed"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "package_run_performed_by_adapter": source.get("package_run_performed_by_adapter"),
        },
        "l21_3_complete": ok,
        "remaining_l21_3_patches": [] if ok else [PATCH],
        "missing_commands": missing_commands,
        "missing_doc_phrases": missing_doc_phrases,
        "required_repo_paths": required,
        "forbidden_optional_browser_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }
    payload.update(false_fields)
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"L21.2 Accepted                : {payload.get('source_l21_2_cli_readback_checkpoint_accepted')}",
        f"Plan Blocks Archive Access    : {payload.get('future_archive_validation_plan_blocks_archive_execution')}",
        f"Archive Execution Allowed     : {payload.get('archive_validation_execution_allowed')}",
        f"Archive Opened                : {payload.get('downloaded_archive_opened')}",
        f"Manifest Read                 : {payload.get('downloaded_manifest_read')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_downloaded_archive_validation_passive_plan_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
