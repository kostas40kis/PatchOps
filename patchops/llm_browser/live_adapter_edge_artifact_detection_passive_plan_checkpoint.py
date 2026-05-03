"""L17.3 passive artifact-presence plan checkpoint for Microsoft Edge.

This module defines the safe future artifact-presence detection plan after the
accepted L17.2 CLI/readback checkpoint. It is intentionally passive: it does not
start Edge, inspect pages, use Selenium/CDP/DOM scraping, read conversation text,
read artifact content, detect artifacts, click, download, paste, send, run a
browser-provided package, start a localhost server, use a browser extension,
commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_artifact_detection_cli_readback_checkpoint as l17_02

PATCH = "L17.3"
PHASE = "L17"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L17.3 Microsoft Edge artifact detection passive plan checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-detection-cli-readback-checkpoint"
SOURCE_PATCH = "L17.2"
NEXT_PATCH = "L17.4 Microsoft Edge artifact detection controlled live authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_plan_checkpoint.md",
    "scripts/patch_l17_01_brief_validate.py",
    "scripts/patch_l17_02_brief_validate.py",
    "scripts/patch_l17_03_brief_validate.py",
    "tests/test_l17_01_edge_artifact_detection_passive_preflight_gate_current.py",
    "tests/test_l17_02_edge_artifact_detection_cli_readback_checkpoint_current.py",
    "tests/test_l17_03_edge_artifact_detection_passive_plan_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L17.3 Microsoft Edge artifact detection passive plan checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "passive plan checkpoint",
    "L17.2 CLI/readback checkpoint remains accepted",
    "safe future artifact-presence detection plan",
    "artifact presence means metadata-only evidence that a downloadable PatchOps zip candidate exists",
    "artifact presence does not mean reading artifact content",
    "artifact presence does not mean clicking a download control",
    "artifact presence does not mean downloading a file",
    "artifact presence does not mean running a package",
    "download workflow remains inactive",
    "artifact detection execution allowed: false",
    "artifact detection is not performed",
    "download workflow active: false",
    "PatchOps remains source of truth",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be selected but not opened",
    "no Microsoft Edge start",
    "no Selenium import",
    "no CDP use",
    "no DOM scraping",
    "no prompt text extraction",
    "no conversation reading",
    "no artifact detection",
    "no artifact content reading",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L17.4 Microsoft Edge artifact detection controlled live authorization gate",
)

PASSIVE_FALSE_FIELDS = (
    "artifact_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_allowed",
    "artifact_detection_performed",
    "artifact_content_reading_performed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_performed",
    "click_download_performed",
    "pasteback_workflow_active",
    "auto_send_allowed",
    "launch_execution_allowed",
    "browser_process_launch_requested",
    "browser_started",
    "edge_process_started",
    "page_inspection_performed",
    "page_metadata_detection_performed",
    "page_metadata_detection_proven",
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
    "chatgpt_url_opened",
)

ALLOWED_FUTURE_ARTIFACT_PRESENCE_SIGNALS = (
    "latest_assistant_reply_container_identity",
    "visible_filename_metadata_ending_dot_zip",
    "filename_pattern_metadata_patchops_bundle_zip",
    "download_control_accessible_name_metadata",
    "download_control_visible_enabled_state",
    "artifact_card_role_or_label_metadata",
    "candidate_belongs_to_latest_assistant_reply",
    "candidate_not_already_processed_by_metadata_key",
)

FORBIDDEN_FUTURE_ARTIFACT_PRESENCE_SIGNALS = (
    "conversation_text",
    "prompt_text",
    "account_data",
    "artifact_content",
    "artifact_source_code",
    "downloaded_file_bytes",
    "cookies",
    "tokens",
    "local_storage",
    "older_conversation_messages",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_artifact_detection_passive_plan_checkpoint.md")
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


def artifact_presence_definition() -> dict[str, Any]:
    """Return the L17.3 definition of artifact presence without content access."""
    return {
        "artifact_presence_definition_version": "1",
        "artifact_presence_means": "metadata-only evidence that a downloadable PatchOps zip candidate exists in the latest assistant reply",
        "artifact_presence_does_not_mean": [
            "reading artifact content",
            "reading downloaded file bytes",
            "clicking a download control",
            "downloading a file",
            "running a package",
            "reading conversation text",
            "reading prompt text",
            "reading account data",
        ],
        "candidate_filename_rules": {
            "extension_must_be": ".zip",
            "recommended_pattern": "patch_*_patchops_bundle.zip",
            "reject_non_zip": True,
            "reject_ambiguous_multiple_candidates": True,
        },
        "allowed_future_metadata_signals": list(ALLOWED_FUTURE_ARTIFACT_PRESENCE_SIGNALS),
        "forbidden_future_observations": list(FORBIDDEN_FUTURE_ARTIFACT_PRESENCE_SIGNALS),
        "content_reading_allowed": False,
        "download_allowed": False,
        "package_run_allowed": False,
        "operator_review_required_before_live_detection": True,
    }


def future_artifact_presence_plan(target_url: str) -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l17_2_cli_readback_checkpoint_accepted",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "require_l17_4_or_later_explicit_live_authorization_token",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 3,
            "name": "open_allowlisted_chatgpt_url_only_with_dedicated_edge_profile",
            "status": "planned_not_executed",
            "target_url": target_url,
            "side_effect": True,
            "allowed_only_in_future_live_phase": True,
        },
        {
            "step": 4,
            "name": "observe_latest_assistant_reply_metadata_without_text_extraction",
            "status": "planned_not_executed",
            "side_effect": False,
            "allowed_future_metadata_signals": list(ALLOWED_FUTURE_ARTIFACT_PRESENCE_SIGNALS),
            "forbidden_future_observations": list(FORBIDDEN_FUTURE_ARTIFACT_PRESENCE_SIGNALS),
        },
        {
            "step": 5,
            "name": "classify_artifact_presence_candidate_from_metadata_only",
            "status": "planned_not_executed",
            "side_effect": False,
            "positive_presence_requires": [
                "latest assistant reply scope",
                "visible zip filename metadata",
                "PatchOps bundle filename pattern metadata",
                "nearby visible download control metadata",
                "candidate not already processed by metadata key",
            ],
            "negative_presence_when": [
                "no visible zip filename metadata",
                "candidate is not in latest assistant reply scope",
                "candidate is non-zip",
                "candidate filename is ambiguous",
                "candidate has already been processed",
            ],
        },
        {
            "step": 6,
            "name": "emit_operator_review_readback_without_download",
            "status": "planned_not_executed",
            "side_effect": False,
            "auto_click": False,
            "auto_download": False,
            "auto_paste": False,
            "auto_send": False,
            "package_run": False,
        },
    ]


def _plan_is_passive_for_l17_3(plan: Sequence[Mapping[str, Any]]) -> bool:
    # Step 3 is a future live-phase side effect by design, but it is explicitly
    # planned_not_executed in L17.3. Everything remains non-executed here.
    return all(item.get("status") == "planned_not_executed" for item in plan)


def _plan_blocks_download(plan: Sequence[Mapping[str, Any]]) -> bool:
    final = plan[-1]
    return (
        final.get("auto_click") is False
        and final.get("auto_download") is False
        and final.get("auto_paste") is False
        and final.get("auto_send") is False
        and final.get("package_run") is False
    )


def build_edge_artifact_detection_passive_plan_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L17.3 artifact-presence plan checkpoint payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL

    source = l17_02.build_edge_artifact_detection_cli_readback_checkpoint(root, target_url=target)
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    definition = artifact_presence_definition()
    plan = future_artifact_presence_plan(target)

    source_passive = _payload_is_passive(source)
    source_ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l17_2_complete") is True
        and source.get("l17_1_passive_preflight_gate_accepted") is True
        and source.get("l17_1_default_compact_readback_ok") is True
        and source.get("l17_1_authorized_compact_readback_ok") is True
        and source.get("artifact_detection_execution_allowed") is False
        and source.get("artifact_detection_active") is False
        and source.get("artifact_detection_performed") is False
        and source.get("download_workflow_active") is False
        and source.get("download_performed") is False
        and source_passive
    )
    target_url_allowed = bool(source.get("target_url_allowed"))
    plan_is_passive = _plan_is_passive_for_l17_3(plan)
    plan_blocks_download = _plan_blocks_download(plan)
    definition_blocks_content = definition["content_reading_allowed"] is False and definition["download_allowed"] is False
    definition_forbids_sensitive = all(item in definition["forbidden_future_observations"] for item in ("conversation_text", "prompt_text", "account_data", "artifact_content", "downloaded_file_bytes"))

    checks = [
        _check("source_l17_2_cli_readback_checkpoint_accepted", source_ok),
        _check("source_l17_2_readback_remains_passive", source_passive, _passive_false_summary(source)),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("artifact_presence_definition_blocks_content_and_download", definition_blocks_content),
        _check("artifact_presence_definition_forbids_sensitive_observations", definition_forbids_sensitive),
        _check("future_artifact_presence_plan_is_planned_not_executed", plan_is_passive),
        _check("future_artifact_presence_plan_blocks_download_paste_send_package_run", plan_blocks_download),
        _check("artifact_detection_execution_still_blocked", True),
        _check("download_workflow_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l17_3_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l17_2_cli_readback_checkpoint_accepted": source_ok,
        "l17_2_complete": bool(source.get("l17_2_complete")),
        "l17_1_passive_preflight_gate_accepted": bool(source.get("l17_1_passive_preflight_gate_accepted")),
        "artifact_presence_definition": definition,
        "artifact_presence_definition_blocks_content_and_download": definition_blocks_content,
        "artifact_presence_definition_forbids_sensitive_observations": definition_forbids_sensitive,
        "future_artifact_presence_plan": plan,
        "future_artifact_presence_plan_is_planned_not_executed": plan_is_passive,
        "future_artifact_presence_plan_blocks_download_paste_send_package_run": plan_blocks_download,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_allowed": False,
        "artifact_detection_performed": False,
        "artifact_content_reading_performed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_performed": False,
        "click_download_performed": False,
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
        "page_metadata_detection_proven": False,
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
        "download_workflow_remains_separate_future_stream": True,
        "operator_review_required_before_live_artifact_detection": True,
        "patchops_remains_source_of_truth": True,
        "target_url_allowlist_enforced": True,
        "target_url": target,
        "target_url_allowed": target_url_allowed,
        "source_l17_2_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l17_2_complete": source.get("l17_2_complete"),
            "l17_1_passive_preflight_gate_accepted": source.get("l17_1_passive_preflight_gate_accepted"),
            "artifact_detection_active": source.get("artifact_detection_active"),
            "artifact_detection_performed": source.get("artifact_detection_performed"),
            "download_workflow_active": source.get("download_workflow_active"),
            "download_performed": source.get("download_performed"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "chatgpt_url_opened": source.get("chatgpt_url_opened"),
            "missing_commands": source.get("missing_commands"),
            "missing_doc_phrases": source.get("missing_doc_phrases"),
        },
        "l17_3_complete": ok,
        "remaining_l17_3_patches": [] if ok else [PATCH],
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
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"Source Command                : {payload.get('source_command_name')}",
        f"L17.2 Accepted                : {payload.get('source_l17_2_cli_readback_checkpoint_accepted')}",
        f"Artifact Definition Blocks    : {payload.get('artifact_presence_definition_blocks_content_and_download')}",
        f"Plan Blocks Download/Run      : {payload.get('future_artifact_presence_plan_blocks_download_paste_send_package_run')}",
        f"Artifact Detection Active     : {payload.get('artifact_detection_active')}",
        f"Download Workflow Active      : {payload.get('download_workflow_active')}",
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

    payload = build_edge_artifact_detection_passive_plan_checkpoint(
        args.repo_root,
        target_url=args.target_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
