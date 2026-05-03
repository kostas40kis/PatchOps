"""L16.4 controlled live-plan authorization gate for Edge page detection.

This gate sits after the accepted L16.3 passive plan checkpoint. It adds the
explicit execution authorization surface required before any future live page
metadata detection proof. L16.4 is still passive: it does not start Edge, inspect
ChatGPT, import Selenium, detect artifacts, click, download, paste, send, run
packages from the browser, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from patchops.llm_browser import live_adapter_edge_real_page_detection_passive_plan_checkpoint as l16_03

PATCH = "L16.4"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.4 Microsoft Edge real-page detection controlled live plan authorization gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
L15_5_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"
NEXT_PATCH = "L16.5 Microsoft Edge first controlled real-page metadata detection proof"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ALLOWED_TARGET_HOSTS = ("chatgpt.com", "chat.openai.com")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.md",
    "scripts/patch_l16_03_brief_validate.py",
    "scripts/patch_l16_04_brief_validate.py",
    "tests/test_l16_03_edge_real_page_detection_passive_plan_checkpoint_current.py",
    "tests/test_l16_04_edge_real_page_detection_controlled_live_plan_authorization_gate_current.py",
)

SAFETY_PHRASES = (
    "L16.4 Microsoft Edge real-page detection controlled live plan authorization gate",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L16_2_COMMAND_NAME,
    L16_1_COMMAND_NAME,
    L15_5_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "controlled live plan authorization gate",
    "execution authorization is readback-only in L16.4",
    "real-page detection is still not active",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be authorized but not opened",
    "page detection execution allowed: false",
    "metadata-only detection contract",
    "current URL, page title, ready state, and window count only",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.md")
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


def build_edge_real_page_detection_controlled_live_plan_authorization_gate(
    repo_root: str | Path | None = None,
    *,
    allow_real_page_detection_execution: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L16.4 controlled live-plan authorization readback."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    source = l16_03.build_edge_real_page_detection_passive_plan_checkpoint(root, target_url=target_url or DEFAULT_TARGET_URL)
    names = _command_names()
    missing_commands = [name for name in (L15_5_COMMAND_NAME, L16_1_COMMAND_NAME, L16_2_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target = _target_url_status(target_url)

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == "L16.3"
        and source.get("source_l16_2_cli_readback_checkpoint_surface_present") is True
        and source.get("future_detection_plan_is_passive") is True
        and source.get("future_detection_plan_is_metadata_only") is True
        and source.get("real_page_detection_active") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("page_inspection_performed") is False
        and source.get("chatgpt_url_opened") is False
    )
    explicit_authorization_complete = bool(allow_real_page_detection_execution) and authorization_token == REQUIRED_AUTHORIZATION_TOKEN
    # L16.4 is authorization/readback only. It never allows execution.
    page_detection_execution_allowed = False

    metadata_only_contract = {
        "allowed_observations": ["current_url", "page_title", "ready_state", "window_count"],
        "forbidden_observations": ["conversation_text", "prompt_text", "account_data", "artifact_content", "downloaded_files", "dom_text"],
        "success_criteria": ["allowlisted_host", "chatgpt_title_or_url", "page_ready_metadata"],
    }

    checks = [
        _check("source_l16_3_passive_plan_checkpoint_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlisted", target["ok"], {"host": target["host"], "scheme": target["scheme"]}),
        _check("execution_authorization_surface_present", True),
        _check("execution_authorization_is_readback_only", page_detection_execution_allowed is False),
        _check("metadata_only_detection_contract_present", True),
        _check("real_page_detection_still_inactive", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_4_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l16_2_command_name": L16_2_COMMAND_NAME,
        "l16_1_command_name": L16_1_COMMAND_NAME,
        "l15_5_command_name": L15_5_COMMAND_NAME,
        "source_patch": "L16.3",
        "next_patch": NEXT_PATCH,
        "controlled_live_plan_authorization_gate": True,
        "source_l16_3_passive_plan_checkpoint_accepted": source_ok,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "real_page_detection_execution_flag_required": True,
        "real_page_detection_execution_token_required": True,
        "real_page_detection_execution_flag_present": bool(allow_real_page_detection_execution),
        "real_page_detection_execution_token_present": authorization_token == REQUIRED_AUTHORIZATION_TOKEN,
        "real_page_detection_execution_authorized": explicit_authorization_complete,
        "execution_authorization_is_readback_only_in_l16_4": True,
        "page_detection_execution_allowed": page_detection_execution_allowed,
        "real_page_detection_active": False,
        "real_page_detection_allowed": False,
        "page_inspection_allowed": False,
        "page_inspection_performed": False,
        "target_url_allowlist_enforced": True,
        "target_url_status": target,
        "target_url": target["target_url"],
        "chatgpt_url_selected_for_future_detection": bool(target["ok"]),
        "chatgpt_url_authorized_for_future_detection": explicit_authorization_complete and bool(target["ok"]),
        "chatgpt_url_opened": False,
        "metadata_only_detection_contract": metadata_only_contract,
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
        "l16_4_complete": ok,
        "remaining_l16_4_patches": [] if ok else [PATCH],
        "source_l16_3_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "future_detection_plan_is_passive": source.get("future_detection_plan_is_passive"),
            "future_detection_plan_is_metadata_only": source.get("future_detection_plan_is_metadata_only"),
            "real_page_detection_active": source.get("real_page_detection_active"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
            "page_inspection_performed": source.get("page_inspection_performed"),
        },
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
        f"Execution Authorized          : {payload.get('real_page_detection_execution_authorized')}",
        f"Execution Allowed             : {payload.get('page_detection_execution_allowed')}",
        f"Real Page Detection Active    : {payload.get('real_page_detection_active')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Page Inspection Performed     : {payload.get('page_inspection_performed')}",
        f"Target URL                    : {payload.get('target_url')}",
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
    parser.add_argument("--allow-real-page-detection-execution", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_real_page_detection_controlled_live_plan_authorization_gate(
        args.repo_root,
        allow_real_page_detection_execution=args.allow_real_page_detection_execution,
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
