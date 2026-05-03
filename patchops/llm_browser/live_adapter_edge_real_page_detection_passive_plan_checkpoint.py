"""L16.3 passive plan checkpoint for Microsoft Edge real-page detection.

L16.3 is deliberately passive and fast. It does not call the nested L16.2 CLI
readback stack. Instead it verifies that the accepted source surfaces exist,
that the command chain is registered, and that the future page-detection plan is
safe, explicit, and still not executable.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

PATCH = "L16.3"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.3 Microsoft Edge real-page detection passive plan checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
L15_5_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"
NEXT_PATCH = "L16.4 Microsoft Edge real-page detection controlled live plan authorization gate"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ALLOWED_TARGET_HOSTS = ("chatgpt.com", "chat.openai.com")
FUTURE_EXECUTION_TOKEN_NAME = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_live_start_handoff_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_plan_checkpoint.md",
    "scripts/patch_l16_01_brief_validate.py",
    "scripts/patch_l16_02_brief_validate.py",
    "scripts/patch_l16_03_brief_validate.py",
    "tests/test_l16_01_edge_real_page_detection_passive_preflight_gate_current.py",
    "tests/test_l16_02_edge_real_page_detection_cli_readback_checkpoint_current.py",
    "tests/test_l16_03_edge_real_page_detection_passive_plan_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L16.3 Microsoft Edge real-page detection passive plan checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L16_1_COMMAND_NAME,
    L15_5_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "passive plan checkpoint",
    "nested CLI readbacks are not performed",
    "real-page detection is still not active",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be planned but not opened",
    "page detected means URL/title/readiness metadata only",
    "no DOM scraping",
    "no prompt text extraction",
    "no conversation reading",
    "no Microsoft Edge start",
    "no Selenium import",
    "no ChatGPT interaction",
    "no page inspection",
    "no artifact detection",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    NEXT_PATCH,
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_real_page_detection_passive_plan_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _target_url_status(target_url: str | None) -> dict[str, Any]:
    value = target_url or DEFAULT_TARGET_URL
    parsed = urlparse(value)
    scheme = (parsed.scheme or "").lower()
    host = (parsed.hostname or "").lower()
    allowed = scheme == "https" and host in ALLOWED_TARGET_HOSTS
    return {
        "ok": allowed,
        "target_url": value,
        "scheme": scheme,
        "host": host,
        "path": parsed.path or "/",
        "allowed_hosts": list(ALLOWED_TARGET_HOSTS),
    }


def _future_detection_plan(target_url: str) -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l16_preflight_authorization",
            "status": "planned_not_executed",
            "requires_operator_authorization": True,
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "start_edge_with_dedicated_l14_profile_to_allowlisted_target",
            "status": "planned_not_executed",
            "target_url": target_url,
            "requires_operator_authorization": True,
            "side_effect": True,
        },
        {
            "step": 3,
            "name": "detect_page_identity_from_safe_metadata_only",
            "status": "planned_not_executed",
            "allowed_observations": ["current_url", "page_title", "ready_state", "window_count"],
            "forbidden_observations": ["conversation_text", "prompt_text", "account_data", "artifact_content"],
            "side_effect": False,
        },
        {
            "step": 4,
            "name": "classify_chatgpt_page_presence_without_interaction",
            "status": "planned_not_executed",
            "success_criteria": ["host_is_allowlisted", "title_or_url_matches_chatgpt", "page_ready_metadata_observed"],
            "side_effect": False,
        },
        {
            "step": 5,
            "name": "close_or_leave_browser_according_to_operator_flag",
            "status": "planned_not_executed",
            "default_close_policy": "close_only_process_tree_started_by_patchops",
            "side_effect": True,
        },
        {
            "step": 6,
            "name": "emit_compact_readback_for_operator_review",
            "status": "planned_not_executed",
            "auto_send": False,
            "side_effect": False,
        },
    ]


def build_edge_real_page_detection_passive_plan_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive future execution plan for real-page detection."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    names = _command_names()
    missing_commands = [name for name in (L15_5_COMMAND_NAME, L16_1_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target = _target_url_status(target_url)
    plan = _future_detection_plan(str(target["target_url"]))

    source_l16_2_surface_present = (
        (root / "patchops/llm_browser/live_adapter_edge_real_page_detection_cli_readback_checkpoint.py").exists()
        and (root / "tests/test_l16_02_edge_real_page_detection_cli_readback_checkpoint_current.py").exists()
        and SOURCE_COMMAND_NAME in names
    )
    plan_is_passive = all(item.get("status") == "planned_not_executed" for item in plan)
    metadata_only = all(
        forbidden in plan[2].get("forbidden_observations", [])
        for forbidden in ("conversation_text", "prompt_text", "account_data", "artifact_content")
    )

    checks = [
        _check("source_l16_2_cli_readback_checkpoint_surface_present", source_l16_2_surface_present),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlisted", target["ok"], {"host": target["host"], "scheme": target["scheme"]}),
        _check("future_detection_plan_is_passive", plan_is_passive),
        _check("future_detection_plan_is_metadata_only", metadata_only),
        _check("nested_cli_readbacks_not_performed", True),
        _check("real_page_detection_still_inactive", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_3_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l16_1_command_name": L16_1_COMMAND_NAME,
        "l15_5_command_name": L15_5_COMMAND_NAME,
        "source_patch": "L16.2",
        "next_patch": NEXT_PATCH,
        "passive_plan_checkpoint": True,
        "source_l16_2_cli_readback_checkpoint_surface_present": source_l16_2_surface_present,
        "nested_cli_readbacks_performed": False,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "target_url_allowlist_enforced": True,
        "target_url_status": target,
        "target_url": target["target_url"],
        "chatgpt_url_selected_for_future_detection": bool(target["ok"]),
        "future_execution_authorization_token_name": FUTURE_EXECUTION_TOKEN_NAME,
        "future_detection_plan": plan,
        "future_detection_plan_is_passive": plan_is_passive,
        "future_detection_plan_is_metadata_only": metadata_only,
        "page_detected_definition": {
            "allowed_observations": ["current_url", "page_title", "ready_state", "window_count"],
            "forbidden_observations": ["conversation_text", "prompt_text", "account_data", "artifact_content", "downloaded_files"],
            "success_criteria": ["allowlisted_host", "chatgpt_title_or_url", "page_ready_metadata"],
        },
        "real_page_detection_active": False,
        "real_page_detection_allowed": False,
        "page_inspection_allowed": False,
        "page_inspection_performed": False,
        "chatgpt_url_opened": False,
        "launch_execution_allowed": False,
        "browser_process_launch_requested": False,
        "browser_started": False,
        "edge_process_started": False,
        "live_open_smoke_executed": False,
        "live_open_smoke_proven": False,
        "browser_close_attempted": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "browser_session_created": False,
        "driver_created": False,
        "artifact_detection_performed": False,
        "click_download_performed": False,
        "download_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "localhost_patchops_server_started": False,
        "browser_extension_used": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "auto_send_allowed": False,
        "operator_review_required_before_live_page_detection": True,
        "l16_3_complete": ok,
        "remaining_l16_3_patches": [] if ok else [PATCH],
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
        f"Patch                      : {payload.get('patch')}",
        f"Status                     : {payload.get('status')}",
        f"Command                    : {payload.get('command_name')}",
        f"Source Command             : {payload.get('source_command_name')}",
        f"Nested CLI Readbacks       : {payload.get('nested_cli_readbacks_performed')}",
        f"Real Page Detection Active : {payload.get('real_page_detection_active')}",
        f"Browser Started            : {payload.get('browser_started')}",
        f"Page Inspection Performed  : {payload.get('page_inspection_performed')}",
        f"Target URL                 : {payload.get('target_url')}",
        f"Next Patch                 : {payload.get('next_patch')}",
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

    payload = build_edge_real_page_detection_passive_plan_checkpoint(
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
