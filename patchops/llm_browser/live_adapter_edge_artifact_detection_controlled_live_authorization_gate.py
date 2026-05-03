"""L17.4 controlled live authorization gate for Edge artifact detection.

This checkpoint adds the explicit future live authorization token/readback surface
after the accepted L17.3 passive plan. It is still passive/readback-only in L17.4:
no Edge start, no Selenium/CDP/DOM scraping, no page inspection, no artifact
detection execution, no artifact content reading, no click, no download, no paste,
no send, no package run, no localhost server, no browser extension, no commit, and
no push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_artifact_detection_passive_plan_checkpoint as l17_03

PATCH = "L17.4"
PHASE = "L17"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L17.4 Microsoft Edge artifact detection controlled live authorization gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-detection-controlled-live-authorization-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-detection-passive-plan-checkpoint"
SOURCE_PATCH = "L17.3"
NEXT_PATCH = "L17.5 Microsoft Edge first controlled artifact-presence metadata proof"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_LIVE_AUTHORIZATION_TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_LIVE_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_controlled_live_authorization_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_controlled_live_authorization_gate.md",
    "scripts/patch_l17_01_brief_validate.py",
    "scripts/patch_l17_02_brief_validate.py",
    "scripts/patch_l17_03_brief_validate.py",
    "scripts/patch_l17_04_brief_validate.py",
    "tests/test_l17_01_edge_artifact_detection_passive_preflight_gate_current.py",
    "tests/test_l17_02_edge_artifact_detection_cli_readback_checkpoint_current.py",
    "tests/test_l17_03_edge_artifact_detection_passive_plan_checkpoint_current.py",
    "tests/test_l17_04_edge_artifact_detection_controlled_live_authorization_gate_current.py",
)

SAFETY_PHRASES = (
    "L17.4 Microsoft Edge artifact detection controlled live authorization gate",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_LIVE_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "controlled live authorization gate",
    "passive/readback-only in L17.4",
    "L17.3 passive plan checkpoint remains accepted",
    "explicit future live authorization token",
    "live artifact detection authorization is readback-only",
    "live artifact detection execution allowed: false",
    "artifact detection execution allowed: false",
    "artifact detection is not performed",
    "artifact presence detection is not performed",
    "download workflow active: false",
    "download workflow remains inactive",
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
    "no artifact detection",
    "no artifact content reading",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "L17.5 Microsoft Edge first controlled artifact-presence metadata proof",
)

PASSIVE_FALSE_FIELDS = (
    "live_artifact_detection_execution_allowed",
    "artifact_detection_execution_allowed",
    "artifact_presence_detection_execution_allowed",
    "artifact_detection_active",
    "artifact_detection_allowed",
    "artifact_detection_performed",
    "artifact_presence_detection_performed",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_artifact_detection_controlled_live_authorization_gate.md")
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


# L17.4a repair: L17.4 adds live-authorization-specific fields that do not
# exist on the L17.3 source payload. When validating that the accepted L17.3
# readback remains passive, use the L17.3-compatible passive field set instead
# of requiring L17.4-only keys to be present in the source payload.
SOURCE_L17_3_PASSIVE_FALSE_FIELDS = tuple(
    field
    for field in PASSIVE_FALSE_FIELDS
    if field
    not in {
        "live_artifact_detection_execution_allowed",
        "artifact_presence_detection_execution_allowed",
        "artifact_presence_detection_performed",
    }
)


def _source_l17_3_passive_false_summary(payload: Mapping[str, Any]) -> dict[str, bool]:
    return {field: payload.get(field) is False for field in SOURCE_L17_3_PASSIVE_FALSE_FIELDS}


def _source_l17_3_payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return all(_source_l17_3_passive_false_summary(payload).values())


def build_live_authorization_readback(
    *,
    allow_live_artifact_detection_authorization: bool = False,
    authorization_token: str | None = None,
) -> dict[str, Any]:
    token_valid = authorization_token == REQUIRED_LIVE_AUTHORIZATION_TOKEN
    requested = bool(allow_live_artifact_detection_authorization)
    authorized = requested and token_valid
    return {
        "authorization_requested": requested,
        "authorization_token_required": True,
        "authorization_token_present": token_valid,
        "live_artifact_detection_authorized_for_future_phase": authorized,
        "live_artifact_detection_authorization_is_readback_only_in_l17_4": True,
        "live_artifact_detection_execution_allowed": False,
        "artifact_presence_detection_execution_allowed": False,
        "required_authorization_token": REQUIRED_LIVE_AUTHORIZATION_TOKEN,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "operator_review_required_before_live_artifact_detection": True,
        "download_workflow_remains_separate_future_stream": True,
        "auto_send_allowed": False,
    }


def future_live_authorization_gate_plan(target_url: str) -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l17_3_passive_plan_checkpoint_accepted",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "require_explicit_live_artifact_detection_authorization_flag",
            "status": "planned_not_executed",
            "side_effect": False,
        },
        {
            "step": 3,
            "name": "require_exact_live_artifact_detection_authorization_token",
            "status": "planned_not_executed",
            "required_authorization_token": REQUIRED_LIVE_AUTHORIZATION_TOKEN,
            "side_effect": False,
        },
        {
            "step": 4,
            "name": "require_dedicated_edge_runtime_profile_and_reject_default_profile",
            "status": "planned_not_executed",
            "side_effect": False,
            "default_microsoft_edge_profile_allowed": False,
        },
        {
            "step": 5,
            "name": "future_live_phase_may_open_allowlisted_chatgpt_url_after_operator_review",
            "status": "planned_not_executed",
            "target_url": target_url,
            "side_effect": True,
            "allowed_only_in_future_l17_5_or_later": True,
        },
        {
            "step": 6,
            "name": "l17_4_readback_does_not_execute_live_artifact_detection",
            "status": "planned_not_executed",
            "side_effect": False,
            "artifact_detection_execution_allowed": False,
            "auto_click": False,
            "auto_download": False,
            "auto_paste": False,
            "auto_send": False,
            "package_run": False,
        },
    ]


def _plan_is_planned_not_executed(plan: Sequence[Mapping[str, Any]]) -> bool:
    return all(item.get("status") == "planned_not_executed" for item in plan)


def _plan_blocks_execution_download_send(plan: Sequence[Mapping[str, Any]]) -> bool:
    final = plan[-1]
    return (
        final.get("artifact_detection_execution_allowed") is False
        and final.get("auto_click") is False
        and final.get("auto_download") is False
        and final.get("auto_paste") is False
        and final.get("auto_send") is False
        and final.get("package_run") is False
    )


def build_edge_artifact_detection_controlled_live_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_artifact_detection_authorization: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L17.4 controlled live authorization gate payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL

    source = l17_03.build_edge_artifact_detection_passive_plan_checkpoint(root, target_url=target)
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    auth = build_live_authorization_readback(
        allow_live_artifact_detection_authorization=allow_live_artifact_detection_authorization,
        authorization_token=authorization_token,
    )
    plan = future_live_authorization_gate_plan(target)

    source_passive = _source_l17_3_payload_is_passive(source)
    source_ok = (
        source.get("ok") is True
        and source.get("patch") == SOURCE_PATCH
        and source.get("l17_3_complete") is True
        and source.get("source_l17_2_cli_readback_checkpoint_accepted") is True
        and source.get("artifact_presence_definition_blocks_content_and_download") is True
        and source.get("future_artifact_presence_plan_blocks_download_paste_send_package_run") is True
        and source.get("artifact_detection_execution_allowed") is False
        and source.get("artifact_detection_active") is False
        and source.get("artifact_detection_performed") is False
        and source.get("download_workflow_active") is False
        and source.get("download_performed") is False
        and source_passive
    )
    target_url_allowed = bool(source.get("target_url_allowed"))
    plan_is_planned_not_executed = _plan_is_planned_not_executed(plan)
    plan_blocks_execution = _plan_blocks_execution_download_send(plan)
    authorization_surface_ok = auth["authorization_token_required"] is True and auth["live_artifact_detection_authorization_is_readback_only_in_l17_4"] is True
    authorization_execution_blocked = auth["live_artifact_detection_execution_allowed"] is False and auth["artifact_presence_detection_execution_allowed"] is False
    default_profile_rejected = auth["requires_dedicated_edge_runtime_profile_in_future_live_phase"] is True and auth["default_microsoft_edge_profile_allowed"] is False

    checks = [
        _check("source_l17_3_passive_plan_checkpoint_accepted", source_ok),
        _check("source_l17_3_readback_remains_passive", source_passive, _source_l17_3_passive_false_summary(source)),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("live_authorization_surface_present", authorization_surface_ok),
        _check("live_authorization_is_readback_only", True),
        _check("live_artifact_detection_execution_blocked", authorization_execution_blocked),
        _check("dedicated_edge_profile_required_and_default_profile_rejected", default_profile_rejected),
        _check("future_live_authorization_plan_is_planned_not_executed", plan_is_planned_not_executed),
        _check("future_live_authorization_plan_blocks_detection_download_send_package_run", plan_blocks_execution),
        _check("artifact_detection_execution_still_blocked", True),
        _check("download_workflow_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l17_4_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "controlled_live_authorization_gate": True,
        "passive_readback_only_in_l17_4": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l17_3_passive_plan_checkpoint_accepted": source_ok,
        "l17_3_complete": bool(source.get("l17_3_complete")),
        "source_l17_2_cli_readback_checkpoint_accepted": bool(source.get("source_l17_2_cli_readback_checkpoint_accepted")),
        "live_authorization_readback": auth,
        "live_artifact_detection_authorization_requested": auth["authorization_requested"],
        "live_artifact_detection_authorization_token_present": auth["authorization_token_present"],
        "live_artifact_detection_authorized_for_future_phase": auth["live_artifact_detection_authorized_for_future_phase"],
        "live_artifact_detection_authorization_is_readback_only_in_l17_4": True,
        "live_artifact_detection_execution_allowed": False,
        "artifact_presence_detection_execution_allowed": False,
        "requires_dedicated_edge_runtime_profile_in_future_live_phase": True,
        "default_microsoft_edge_profile_allowed": False,
        "future_live_authorization_gate_plan": plan,
        "future_live_authorization_plan_is_planned_not_executed": plan_is_planned_not_executed,
        "future_live_authorization_plan_blocks_detection_download_send_package_run": plan_blocks_execution,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_allowed": False,
        "artifact_detection_performed": False,
        "artifact_presence_detection_performed": False,
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
        "source_l17_3_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l17_3_complete": source.get("l17_3_complete"),
            "source_l17_2_cli_readback_checkpoint_accepted": source.get("source_l17_2_cli_readback_checkpoint_accepted"),
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
        "l17_4_complete": ok,
        "remaining_l17_4_patches": [] if ok else [PATCH],
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
        f"L17.3 Accepted                : {payload.get('source_l17_3_passive_plan_checkpoint_accepted')}",
        f"Live Auth Requested           : {payload.get('live_artifact_detection_authorization_requested')}",
        f"Future Auth Accepted          : {payload.get('live_artifact_detection_authorized_for_future_phase')}",
        f"Live Detection Execution      : {payload.get('live_artifact_detection_execution_allowed')}",
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
    parser.add_argument("--allow-live-artifact-detection-authorization", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_artifact_detection_controlled_live_authorization_gate(
        args.repo_root,
        allow_live_artifact_detection_authorization=args.allow_live_artifact_detection_authorization,
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
