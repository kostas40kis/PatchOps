"""L17.1 passive preflight gate for Microsoft Edge artifact detection.

This module starts the artifact-detection stream after the accepted L16.7 final
metadata marker. It is intentionally passive: it does not start Edge, inspect
pages, import Selenium, use CDP, read ChatGPT conversations, detect artifacts,
download, paste, send, run packages from the browser, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from patchops.llm_browser import live_adapter_edge_real_page_metadata_detection_final_acceptance_marker as l16_07

PATCH = "L17.1"
PHASE = "L17"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L17.1 Microsoft Edge artifact detection passive preflight gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-artifact-detection-passive-preflight-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-metadata-detection-final-acceptance-marker"
L16_6_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint"
L16_5_COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
NEXT_PATCH = "L17.2 Microsoft Edge artifact detection CLI/readback checkpoint"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L17_EDGE_ARTIFACT_DETECTION_PREFLIGHT_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ALLOWED_TARGET_HOSTS = ("chatgpt.com", "chat.openai.com")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_metadata_detection_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_real_page_metadata_detection_broad_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_real_page_metadata_detection_proof.py",
    "patchops/llm_browser/live_adapter_edge_artifact_detection_passive_preflight_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_metadata_detection_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_artifact_detection_passive_preflight_gate.md",
    "scripts/patch_l16_07_brief_validate.py",
    "scripts/patch_l17_01_brief_validate.py",
    "tests/test_l16_07_edge_real_page_metadata_detection_final_acceptance_marker_current.py",
    "tests/test_l17_01_edge_artifact_detection_passive_preflight_gate_current.py",
)

SAFETY_PHRASES = (
    "L17.1 Microsoft Edge artifact detection passive preflight gate",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L16_6_COMMAND_NAME,
    L16_5_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "passive preflight gate",
    "L16 metadata detection stream complete",
    "artifact detection is not active yet",
    "artifact detection preflight authorization is readback-only",
    "artifact detection execution allowed: false",
    "download workflow is not active yet",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_artifact_detection_passive_preflight_gate.md")
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


def _future_artifact_detection_plan(target_url: str) -> list[dict[str, Any]]:
    return [
        {
            "step": 1,
            "name": "confirm_l16_metadata_detection_stream_complete",
            "status": "planned_not_executed",
            "requires_operator_authorization": False,
            "side_effect": False,
        },
        {
            "step": 2,
            "name": "confirm_explicit_artifact_detection_authorization",
            "status": "planned_not_executed",
            "requires_operator_authorization": True,
            "side_effect": False,
        },
        {
            "step": 3,
            "name": "open_allowlisted_chatgpt_page_with_dedicated_profile",
            "status": "planned_not_executed",
            "target_url": target_url,
            "requires_operator_authorization": True,
            "side_effect": True,
        },
        {
            "step": 4,
            "name": "detect_artifact_presence_from_safe_metadata_only",
            "status": "planned_not_executed",
            "allowed_future_observations": [
                "page_url",
                "page_title",
                "ready_state",
                "candidate_download_control_count",
                "candidate_artifact_label_metadata",
            ],
            "forbidden_observations": [
                "conversation_text",
                "prompt_text",
                "account_data",
                "artifact_content",
                "downloaded_file_bytes",
            ],
            "side_effect": False,
        },
        {
            "step": 5,
            "name": "emit_artifact_presence_readback_for_operator_review",
            "status": "planned_not_executed",
            "auto_click": False,
            "auto_download": False,
            "auto_send": False,
            "side_effect": False,
        },
    ]


def build_edge_artifact_detection_passive_preflight_gate(
    repo_root: str | Path | None = None,
    *,
    allow_artifact_detection_preflight: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L17.1 artifact detection preflight readback."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    source = l16_07.build_edge_real_page_metadata_detection_final_acceptance_marker(root)
    names = _command_names()
    missing_commands = [name for name in (L16_5_COMMAND_NAME, L16_6_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target = _target_url_status(target_url)
    explicit_preflight_authorized = bool(allow_artifact_detection_preflight) and authorization_token == REQUIRED_AUTHORIZATION_TOKEN
    plan = _future_artifact_detection_plan(str(target["target_url"]))

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == "L16.7"
        and source.get("l16_metadata_detection_stream_complete") is True
        and source.get("metadata_only_page_detection_accepted") is True
        and source.get("os_window_process_metadata_only_accepted") is True
        and source.get("artifact_detection_active") is False
        and source.get("download_workflow_active") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("artifact_detection_performed") is False
        and source.get("download_performed") is False
        and source.get("package_run_performed_by_adapter") is False
    )
    plan_is_passive = all(item.get("status") == "planned_not_executed" for item in plan)
    plan_blocks_download = plan[-1].get("auto_download") is False and plan[-1].get("auto_click") is False

    checks = [
        _check("source_l16_7_final_marker_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlisted", target["ok"], {"host": target["host"], "scheme": target["scheme"]}),
        _check("artifact_detection_preflight_authorization_surface_present", True),
        _check("artifact_detection_preflight_authorization_is_readback_only", True),
        _check("future_artifact_detection_plan_is_passive", plan_is_passive),
        _check("future_artifact_detection_plan_blocks_download", plan_blocks_download),
        _check("artifact_detection_still_inactive", True),
        _check("download_workflow_still_inactive", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l17_1_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l16_6_command_name": L16_6_COMMAND_NAME,
        "l16_5_command_name": L16_5_COMMAND_NAME,
        "source_patch": "L16.7",
        "next_patch": NEXT_PATCH,
        "passive_preflight_gate": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l16_7_final_marker_accepted": source_ok,
        "l16_metadata_detection_stream_complete": bool(source.get("l16_metadata_detection_stream_complete")),
        "metadata_only_page_detection_accepted": bool(source.get("metadata_only_page_detection_accepted")),
        "artifact_detection_preflight_flag_required": True,
        "artifact_detection_preflight_token_required": True,
        "artifact_detection_preflight_flag_present": bool(allow_artifact_detection_preflight),
        "artifact_detection_preflight_token_present": authorization_token == REQUIRED_AUTHORIZATION_TOKEN,
        "artifact_detection_preflight_authorized": explicit_preflight_authorized,
        "artifact_detection_preflight_is_readback_only_in_l17_1": True,
        "artifact_detection_execution_allowed": False,
        "artifact_detection_active": False,
        "artifact_detection_allowed": False,
        "artifact_detection_performed": False,
        "artifact_content_reading_performed": False,
        "future_artifact_detection_plan": plan,
        "future_artifact_detection_plan_is_passive": plan_is_passive,
        "future_artifact_detection_plan_blocks_download": plan_blocks_download,
        "target_url_allowlist_enforced": True,
        "target_url_status": target,
        "target_url": target["target_url"],
        "chatgpt_url_selected_for_future_detection": bool(target["ok"]),
        "chatgpt_url_opened": False,
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
        "operator_review_required_before_live_artifact_detection": True,
        "patchops_remains_source_of_truth": True,
        "l17_1_complete": ok,
        "remaining_l17_1_patches": [] if ok else [PATCH],
        "source_l16_7_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l16_metadata_detection_stream_complete": source.get("l16_metadata_detection_stream_complete"),
            "artifact_detection_active": source.get("artifact_detection_active"),
            "download_workflow_active": source.get("download_workflow_active"),
            "browser_started": source.get("browser_started"),
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
        f"L16 Metadata Complete         : {payload.get('l16_metadata_detection_stream_complete')}",
        f"Artifact Preflight Authorized : {payload.get('artifact_detection_preflight_authorized')}",
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
    parser.add_argument("--allow-artifact-detection-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_artifact_detection_passive_preflight_gate(
        args.repo_root,
        allow_artifact_detection_preflight=args.allow_artifact_detection_preflight,
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
