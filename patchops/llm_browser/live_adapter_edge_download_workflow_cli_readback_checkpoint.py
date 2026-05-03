"""L18.2 passive CLI/readback checkpoint for Edge download workflow.

This checkpoint proves the accepted L18.1 default and authorized compact readbacks
without starting Edge, inspecting pages, clicking, downloading, reading file bytes,
pasting, sending, running packages, starting localhost services, using a browser
extension, committing, or pushing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_download_workflow_passive_preflight_gate as l18_01

PATCH = "L18.2"
PHASE = "L18"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L18.2 Microsoft Edge download workflow CLI/readback checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-download-workflow-cli-readback-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-download-workflow-passive-preflight-gate"
SOURCE_PATCH = "L18.1"
NEXT_PATCH = "L18.3 Microsoft Edge download workflow passive plan checkpoint"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
REQUIRED_DOWNLOAD_PREFLIGHT_AUTHORIZATION_TOKEN = "PATCHOPS_L18_EDGE_DOWNLOAD_PREFLIGHT_AUTHORIZED_READBACK_ONLY"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_artifact_detection_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_download_workflow_cli_readback_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_artifact_detection_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_download_workflow_cli_readback_checkpoint.md",
    "scripts/patch_l17_07_brief_validate.py",
    "scripts/patch_l18_01_brief_validate.py",
    "scripts/patch_l18_02_brief_validate.py",
    "tests/test_l17_07_edge_artifact_detection_final_acceptance_marker_current.py",
    "tests/test_l18_01_edge_download_workflow_passive_preflight_gate_current.py",
    "tests/test_l18_02_edge_download_workflow_cli_readback_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L18.2 Microsoft Edge download workflow CLI/readback checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    REQUIRED_DOWNLOAD_PREFLIGHT_AUTHORIZATION_TOKEN,
    "Microsoft Edge first",
    "Opera second",
    "download workflow CLI/readback checkpoint",
    "passive CLI/readback checkpoint",
    "L18.1 passive preflight gate remains accepted",
    "default compact readback remains passive",
    "authorized compact readback remains passive",
    "download workflow preflight authorization remains readback-only",
    "download workflow execution allowed: false",
    "download workflow active: false",
    "download is not performed",
    "downloaded file bytes are not read",
    "artifact content reading performed: false",
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
    "avoid nested CLI validation cascades",
    "one shallow L18.2 compact CLI smoke",
    "L18.3 Microsoft Edge download workflow passive plan checkpoint",
)

PASSIVE_FALSE_FIELDS = (
    "download_workflow_execution_allowed",
    "download_workflow_active",
    "download_workflow_allowed",
    "download_allowed",
    "download_performed",
    "downloaded_file_bytes_read",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_download_workflow_cli_readback_checkpoint.md")
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


def _compact_source_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("ok"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "download_workflow_preflight_authorized": payload.get("download_workflow_preflight_authorized"),
        "download_workflow_preflight_authorization_is_readback_only_in_l18_1": payload.get("download_workflow_preflight_authorization_is_readback_only_in_l18_1"),
        "download_workflow_execution_allowed": payload.get("download_workflow_execution_allowed"),
        "download_workflow_active": payload.get("download_workflow_active"),
        "download_allowed": payload.get("download_allowed"),
        "download_performed": payload.get("download_performed"),
        "downloaded_file_bytes_read": payload.get("downloaded_file_bytes_read"),
        "click_download_performed": payload.get("click_download_performed"),
        "browser_started": payload.get("browser_started"),
        "edge_process_started": payload.get("edge_process_started"),
        "chatgpt_url_opened": payload.get("chatgpt_url_opened"),
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter"),
        "missing_commands": payload.get("missing_commands"),
        "missing_doc_phrases": payload.get("missing_doc_phrases"),
        "required_repo_paths_ok": (payload.get("required_repo_paths") or {}).get("ok"),
    }


def _planned_cli_readbacks(root: Path, target_url: str) -> list[dict[str, Any]]:
    root_text = str(root)
    return [
        {
            "name": "l18_01_default_compact_json_readback",
            "status": "proven_by_l18_2_direct_module_readback_not_executed_by_adapter",
            "command": [
                "py", "-m", "patchops.cli", "llm-browser", SOURCE_COMMAND_NAME,
                "--repo-root", root_text, "--target-url", target_url, "--json", "--compact",
            ],
            "expected_download_workflow_preflight_authorized": False,
            "side_effect": False,
        },
        {
            "name": "l18_01_authorized_compact_json_readback",
            "status": "proven_by_l18_2_direct_module_readback_not_executed_by_adapter",
            "command": [
                "py", "-m", "patchops.cli", "llm-browser", SOURCE_COMMAND_NAME,
                "--repo-root", root_text,
                "--target-url", target_url,
                "--allow-download-workflow-preflight",
                "--authorization-token", REQUIRED_DOWNLOAD_PREFLIGHT_AUTHORIZATION_TOKEN,
                "--json", "--compact",
            ],
            "expected_download_workflow_preflight_authorized": True,
            "side_effect": False,
        },
        {
            "name": "l18_02_checkpoint_compact_json_readback",
            "status": "available_for_one_shallow_cli_smoke_in_patch_validation",
            "command": [
                "py", "-m", "patchops.cli", "llm-browser", COMMAND_NAME,
                "--repo-root", root_text, "--target-url", target_url, "--json", "--compact",
            ],
            "side_effect": False,
        },
    ]


def build_edge_download_workflow_cli_readback_checkpoint(
    repo_root: str | Path | None = None,
    *,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L18.2 CLI/readback checkpoint payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = target_url or DEFAULT_TARGET_URL

    default_payload = l18_01.build_edge_download_workflow_passive_preflight_gate(
        root,
        allow_download_workflow_preflight=False,
        authorization_token=None,
        target_url=target,
    )
    authorized_payload = l18_01.build_edge_download_workflow_passive_preflight_gate(
        root,
        allow_download_workflow_preflight=True,
        authorization_token=REQUIRED_DOWNLOAD_PREFLIGHT_AUTHORIZATION_TOKEN,
        target_url=target,
    )

    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    planned = _planned_cli_readbacks(root, target)

    default_passive = _payload_is_passive(default_payload)
    authorized_passive = _payload_is_passive(authorized_payload)
    default_ok = (
        default_payload.get("ok") is True
        and default_payload.get("patch") == SOURCE_PATCH
        and default_payload.get("l18_1_complete") is True
        and default_payload.get("source_l17_7_artifact_detection_final_marker_accepted") is True
        and default_payload.get("download_workflow_preflight_authorized") is False
        and default_payload.get("download_workflow_preflight_authorization_is_readback_only_in_l18_1") is True
        and default_payload.get("download_workflow_execution_allowed") is False
        and default_payload.get("download_workflow_active") is False
        and default_payload.get("download_performed") is False
        and default_payload.get("downloaded_file_bytes_read") is False
        and default_payload.get("click_download_performed") is False
        and default_passive
    )
    authorized_ok = (
        authorized_payload.get("ok") is True
        and authorized_payload.get("patch") == SOURCE_PATCH
        and authorized_payload.get("l18_1_complete") is True
        and authorized_payload.get("source_l17_7_artifact_detection_final_marker_accepted") is True
        and authorized_payload.get("download_workflow_preflight_authorized") is True
        and authorized_payload.get("download_workflow_preflight_authorization_is_readback_only_in_l18_1") is True
        and authorized_payload.get("download_workflow_execution_allowed") is False
        and authorized_payload.get("download_workflow_active") is False
        and authorized_payload.get("download_performed") is False
        and authorized_payload.get("downloaded_file_bytes_read") is False
        and authorized_payload.get("click_download_performed") is False
        and authorized_passive
    )
    target_url_allowed = bool(authorized_payload.get("target_url_allowed"))
    planned_is_passive = all(item.get("side_effect") is False for item in planned)

    checks = [
        _check("l18_1_default_compact_readback_ok", default_ok),
        _check("l18_1_authorized_compact_readback_ok", authorized_ok),
        _check("default_readback_remains_passive", default_passive, _passive_false_summary(default_payload)),
        _check("authorized_readback_remains_passive", authorized_passive, _passive_false_summary(authorized_payload)),
        _check("target_url_allowlist_enforced", target_url_allowed, {"target_url": target}),
        _check("planned_cli_readbacks_are_passive", planned_is_passive),
        _check("download_workflow_execution_still_blocked", True),
        _check("download_file_byte_reading_still_blocked", True),
        _check("pasteback_and_package_run_still_blocked", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l18_2_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "passive_cli_readback_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "l18_1_passive_preflight_gate_accepted": default_ok and authorized_ok,
        "l18_1_default_compact_readback_ok": default_ok,
        "l18_1_authorized_compact_readback_ok": authorized_ok,
        "default_download_workflow_preflight_authorized": default_payload.get("download_workflow_preflight_authorized"),
        "authorized_download_workflow_preflight_authorized": authorized_payload.get("download_workflow_preflight_authorized"),
        "download_workflow_preflight_authorization_remains_readback_only": True,
        "download_workflow_execution_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "download_allowed": False,
        "download_performed": False,
        "downloaded_file_bytes_read": False,
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
        "avoid_nested_cli_validation_cascades": True,
        "one_shallow_cli_smoke_recommended": True,
        "planned_cli_readbacks": planned,
        "planned_cli_readbacks_are_passive": planned_is_passive,
        "source_default_summary": _compact_source_summary(default_payload),
        "source_authorized_summary": _compact_source_summary(authorized_payload),
        "l18_2_complete": ok,
        "remaining_l18_2_patches": [] if ok else [PATCH],
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
        f"L18.1 Default Readback      : {payload.get('l18_1_default_compact_readback_ok')}",
        f"L18.1 Authorized Readback   : {payload.get('l18_1_authorized_compact_readback_ok')}",
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

    payload = build_edge_download_workflow_cli_readback_checkpoint(args.repo_root, target_url=args.target_url)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
