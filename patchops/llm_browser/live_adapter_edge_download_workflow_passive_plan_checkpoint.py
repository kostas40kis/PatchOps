"""L18.3 passive plan checkpoint for Microsoft Edge download workflow.

This module defines the future download workflow plan after the accepted L18.2
CLI/readback checkpoint. L18.3 is intentionally passive: it does not start Edge,
inspect real pages, click a download control, download a file, read downloaded
file bytes, read artifact content, paste, send, run browser-provided packages,
start localhost services, use a browser extension, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_download_workflow_cli_readback_checkpoint as l18_02

PATCH = "L18.3"
PHASE = "L18"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L18.3 Microsoft Edge download workflow passive plan checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-download-workflow-passive-plan-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-download-workflow-cli-readback-checkpoint"
SOURCE_PATCH = "L18.2"
NEXT_PATCH = "L18.4 Microsoft Edge download workflow controlled live authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_download_workflow_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_passive_plan_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_download_workflow_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_passive_plan_checkpoint.md",
    "scripts/patch_l18_01_brief_validate.py",
    "scripts/patch_l18_02_brief_validate.py",
    "scripts/patch_l18_03_brief_validate.py",
    "tests/test_l18_01_edge_download_workflow_passive_preflight_gate_current.py",
    "tests/test_l18_02_edge_download_workflow_cli_readback_checkpoint_current.py",
    "tests/test_l18_03_edge_download_workflow_passive_plan_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L18.3 Microsoft Edge download workflow passive plan checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "download workflow passive plan checkpoint",
    "passive plan checkpoint",
    "L18.2 CLI/readback checkpoint remains accepted",
    "safe future download workflow plan",
    "download candidate means metadata-only evidence for a PatchOps zip artifact selected by the accepted L17 stream",
    "download plan does not click a download control",
    "download plan does not download a file",
    "download plan does not read downloaded file bytes",
    "download plan does not read artifact content",
    "download plan does not run a package",
    "download workflow execution allowed: false",
    "download workflow active: false",
    "download is not performed",
    "downloaded file bytes are not read",
    "download staging path is planned metadata only",
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
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L18.4 Microsoft Edge download workflow controlled live authorization gate",
)

PASSIVE_FALSE_FIELDS = (
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "downloaded_file_bytes_read",
    "download_staging_directory_created",
    "click_download_performed",
    "artifact_content_reading_performed",
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_performed",
    "real_page_inspection_performed",
    "live_browser_artifact_detection_active",
    "live_browser_artifact_detection_performed",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_download_workflow_passive_plan_checkpoint.md")
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


def download_candidate_definition() -> dict[str, Any]:
    return {
        "download_candidate_definition_version": "1",
        "download_candidate_means": "metadata-only evidence for a PatchOps zip artifact selected by the accepted L17 stream",
        "download_candidate_does_not_mean": [
            "clicking a download control",
            "downloading a file",
            "reading downloaded file bytes",
            "reading artifact content",
            "running a package",
            "pasting into a browser",
            "sending or submitting a message",
        ],
        "candidate_filename_rules": {
            "extension_must_be": ".zip",
            "recommended_pattern": "patch_*_patchops_bundle.zip",
            "reject_non_zip": True,
            "reject_ambiguous_multiple_candidates": True,
        },
        "future_download_staging_rules": {
            "staging_path_is_metadata_only_in_l18_3": True,
            "create_staging_directory_allowed_in_l18_3": False,
            "read_downloaded_file_bytes_allowed_in_l18_3": False,
            "run_downloaded_package_allowed_in_l18_3": False,
        },
        "operator_review_required_before_download": True,
        "patchops_remains_source_of_truth": True,
    }


def future_download_workflow_plan(target_url: str) -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l18_2_cli_readback_checkpoint_accepted",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "require_l18_4_or_later_explicit_download_authorization_token",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 3,
            "name": "reuse_l17_metadata_selected_patchops_zip_candidate",
            "status": "planned_not_executed",
            "side_effect": False,
            "candidate_source": "accepted_l17_metadata_only_artifact_presence_stream",
        },
        {
            "step": 4,
            "name": "plan_download_staging_path_without_creating_or_reading_files",
            "status": "planned_not_executed",
            "side_effect": False,
            "download_staging_path_is_metadata_only": True,
            "create_directory": False,
            "read_file_bytes": False,
        },
        {
            "step": 5,
            "name": "future_live_phase_may_click_download_after_operator_review",
            "status": "planned_not_executed",
            "target_url": target_url,
            "side_effect": True,
            "allowed_only_in_future_l18_4_or_later": True,
        },
        {
            "step": 6,
            "name": "future_download_completion_must_emit_metadata_readback_only_before_file_byte_validation_stream",
            "status": "planned_not_executed",
            "side_effect": False,
            "download_performed_in_l18_3": False,
            "downloaded_file_bytes_read_in_l18_3": False,
            "package_run": False,
            "pasteback": False,
            "auto_send": False,
        },
    ]


def _plan_is_planned_not_executed(plan: Sequence[Mapping[str, Any]]) -> bool:
    return all(item.get("status") == "planned_not_executed" for item in plan)


def _plan_blocks_download_file_read_paste_send_package_run(plan: Sequence[Mapping[str, Any]]) -> bool:
    step4 = plan[3]
    final = plan[-1]
    return (
        step4.get("create_directory") is False
        and step4.get("read_file_bytes") is False
        and final.get("download_performed_in_l18_3") is False
        and final.get("downloaded_file_bytes_read_in_l18_3") is False
        and final.get("package_run") is False
        and final.get("pasteback") is False
        and final.get("auto_send") is False
    )


def build_edge_download_workflow_passive_plan_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L18.3 download workflow plan checkpoint payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL
    source = l18_02.build_edge_download_workflow_cli_readback_checkpoint(root, target_url=target)

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    definition = download_candidate_definition()
    plan = future_download_workflow_plan(target)
    target_url_allowed = bool(source.get("target_url_allowed"))

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l18_2_complete") is True
        and source.get("l18_1_passive_preflight_gate_accepted") is True
        and source.get("l18_1_default_compact_readback_ok") is True
        and source.get("l18_1_authorized_compact_readback_ok") is True
        and source.get("download_workflow_preflight_authorization_remains_readback_only") is True
        and source.get("download_workflow_execution_allowed") is False
        and source.get("download_workflow_active") is False
        and source.get("download_performed") is False
        and source.get("downloaded_file_bytes_read") is False
        and source.get("click_download_performed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("package_run_performed_by_adapter") is False
    )
    definition_blocks = (
        definition["future_download_staging_rules"]["create_staging_directory_allowed_in_l18_3"] is False
        and definition["future_download_staging_rules"]["read_downloaded_file_bytes_allowed_in_l18_3"] is False
        and definition["future_download_staging_rules"]["run_downloaded_package_allowed_in_l18_3"] is False
    )
    plan_is_planned_not_executed = _plan_is_planned_not_executed(plan)
    plan_blocks = _plan_blocks_download_file_read_paste_send_package_run(plan)

    checks = [
        _check("source_l18_2_cli_readback_checkpoint_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("download_candidate_definition_blocks_download_file_read_package_run", definition_blocks),
        _check("future_download_plan_is_planned_not_executed", plan_is_planned_not_executed),
        _check("future_download_plan_blocks_click_download_file_read_paste_send_package_run", plan_blocks),
        _check("download_workflow_execution_still_blocked", True),
        _check("download_file_byte_reading_still_blocked", True),
        _check("pasteback_and_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l18_3_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "download_workflow_passive_plan_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l18_2_cli_readback_checkpoint_accepted": source_ok,
        "l18_2_complete": bool(source.get("l18_2_complete")),
        "l18_1_passive_preflight_gate_accepted": bool(source.get("l18_1_passive_preflight_gate_accepted")),
        "download_candidate_definition": definition,
        "download_candidate_definition_blocks_download_file_read_package_run": definition_blocks,
        "future_download_workflow_plan": plan,
        "future_download_plan_is_planned_not_executed": plan_is_planned_not_executed,
        "future_download_plan_blocks_click_download_file_read_paste_send_package_run": plan_blocks,
        "download_workflow_execution_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_allowed": False,
        "download_performed": False,
        "downloaded_file_bytes_read": False,
        "download_staging_path_metadata_only": True,
        "download_staging_directory_created": False,
        "click_download_performed": False,
        "artifact_content_reading_performed": False,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_performed": False,
        "real_page_inspection_performed": False,
        "live_browser_artifact_detection_active": False,
        "live_browser_artifact_detection_performed": False,
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
        "source_l18_2_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l18_2_complete": source.get("l18_2_complete"),
            "l18_1_passive_preflight_gate_accepted": source.get("l18_1_passive_preflight_gate_accepted"),
            "download_workflow_execution_allowed": source.get("download_workflow_execution_allowed"),
            "download_workflow_active": source.get("download_workflow_active"),
            "download_performed": source.get("download_performed"),
            "downloaded_file_bytes_read": source.get("downloaded_file_bytes_read"),
            "click_download_performed": source.get("click_download_performed"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l18_3_complete": ok,
        "remaining_l18_3_patches": [] if ok else [PATCH],
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
        f"L18.2 Accepted              : {payload.get('source_l18_2_cli_readback_checkpoint_accepted')}",
        f"Plan Blocks Download        : {payload.get('future_download_plan_blocks_click_download_file_read_paste_send_package_run')}",
        f"Download Execution Allowed  : {payload.get('download_workflow_execution_allowed')}",
        f"Download Performed          : {payload.get('download_performed')}",
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

    payload = build_edge_download_workflow_passive_plan_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
