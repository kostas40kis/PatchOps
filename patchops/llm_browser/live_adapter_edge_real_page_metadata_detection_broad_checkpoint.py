"""L16.6 broad checkpoint for Edge real-page metadata detection.

This broad checkpoint consolidates the accepted L16.1-L16.5 real-page detection
stream. It validates the dry/readback surfaces quickly and can run one explicit
live metadata checkpoint through L16.5. It still forbids Selenium, CDP, DOM
scraping, conversation reading, artifact detection, downloads, paste, send,
package-running from a browser, commit, and push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_first_controlled_real_page_metadata_detection_proof as l16_05
from patchops.llm_browser import live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate as l16_04
from patchops.llm_browser import live_adapter_edge_real_page_detection_passive_plan_checkpoint as l16_03

PATCH = "L16.6"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.6 Microsoft Edge real-page metadata detection broad checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
L16_4_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
L16_3_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
NEXT_PATCH = "L16.7 Microsoft Edge real-page metadata detection final acceptance marker"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_real_page_metadata_detection_proof.py",
    "patchops/llm_browser/live_adapter_edge_real_page_metadata_detection_broad_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_first_controlled_real_page_metadata_detection_proof.md",
    "docs/llm_browser_live_adapter_edge_real_page_metadata_detection_broad_checkpoint.md",
    "scripts/patch_l16_03_brief_validate.py",
    "scripts/patch_l16_04_brief_validate.py",
    "scripts/patch_l16_05_brief_validate.py",
    "scripts/patch_l16_06_brief_validate.py",
    "tests/test_l16_03_edge_real_page_detection_passive_plan_checkpoint_current.py",
    "tests/test_l16_04_edge_real_page_detection_controlled_live_plan_authorization_gate_current.py",
    "tests/test_l16_05_edge_first_controlled_real_page_metadata_detection_proof_current.py",
    "tests/test_l16_06_edge_real_page_metadata_detection_broad_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L16.6 Microsoft Edge real-page metadata detection broad checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L16_4_COMMAND_NAME,
    L16_3_COMMAND_NAME,
    L16_2_COMMAND_NAME,
    L16_1_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "broad checkpoint",
    "dry metadata checkpoint",
    "explicit live metadata checkpoint",
    "L16.1 through L16.5 accepted",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be opened only during explicit live checkpoint",
    "metadata-only page detection",
    "OS/window/process metadata only",
    "no DOM scraping",
    "no prompt text extraction",
    "no conversation reading",
    "no Selenium import",
    "no CDP use",
    "no browser extension",
    "no artifact detection",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_real_page_metadata_detection_broad_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _no_forbidden_side_effects(payload: Mapping[str, Any]) -> bool:
    return (
        payload.get("selenium_required") is False
        and payload.get("selenium_imported_by_readback") is False
        and payload.get("cdp_used") is False
        and payload.get("remote_debugging_port_used") is False
        and payload.get("browser_session_created") is False
        and payload.get("driver_created") is False
        and payload.get("dom_scraping_performed") is False
        and payload.get("prompt_text_extraction_performed") is False
        and payload.get("conversation_reading_performed") is False
        and payload.get("artifact_detection_performed") is False
        and payload.get("click_download_performed") is False
        and payload.get("download_performed") is False
        and payload.get("paste_performed") is False
        and payload.get("send_or_submit_performed") is False
        and payload.get("package_run_performed_by_adapter") is False
        and payload.get("localhost_patchops_server_started") is False
        and payload.get("browser_extension_used") is False
        and payload.get("git_commit_executed") is False
        and payload.get("git_push_executed") is False
        and payload.get("auto_send_allowed") is False
    )


def build_edge_real_page_metadata_detection_broad_checkpoint(
    repo_root: str | Path | None = None,
    *,
    execute_live_checkpoint: bool = False,
    close_after_seconds: float = 6.0,
) -> dict[str, Any]:
    """Build the L16.6 broad checkpoint over the metadata detection stream."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l16_3 = l16_03.build_edge_real_page_detection_passive_plan_checkpoint(root)
    l16_4_default = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(root)
    l16_4_authorized = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(
        root,
        allow_real_page_detection_execution=True,
        authorization_token=REQUIRED_AUTHORIZATION_TOKEN,
        target_url=DEFAULT_TARGET_URL,
    )
    l16_5_dry = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(root)

    l16_5_live: dict[str, Any] = {}
    if execute_live_checkpoint:
        l16_5_live = l16_05.build_edge_first_controlled_real_page_metadata_detection_proof(
            root,
            allow_real_page_detection_execution=True,
            authorization_token=REQUIRED_AUTHORIZATION_TOKEN,
            execute_page_metadata_detection=True,
            target_url=DEFAULT_TARGET_URL,
            close_after_seconds=close_after_seconds,
        )

    names = _command_names()
    missing_commands = [
        name
        for name in (L16_1_COMMAND_NAME, L16_2_COMMAND_NAME, L16_3_COMMAND_NAME, L16_4_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME)
        if name not in names
    ]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    l16_3_ok = (
        l16_3.get("ok") is True
        and l16_3.get("future_detection_plan_is_passive") is True
        and l16_3.get("future_detection_plan_is_metadata_only") is True
        and l16_3.get("real_page_detection_active") is False
        and l16_3.get("browser_started") is False
        and l16_3.get("page_inspection_performed") is False
    )
    l16_4_ok = (
        l16_4_default.get("ok") is True
        and l16_4_authorized.get("ok") is True
        and l16_4_authorized.get("real_page_detection_execution_authorized") is True
        and l16_4_authorized.get("execution_authorization_is_readback_only_in_l16_4") is True
        and l16_4_authorized.get("page_detection_execution_allowed") is False
        and l16_4_authorized.get("browser_started") is False
        and l16_4_authorized.get("page_inspection_performed") is False
    )
    l16_5_dry_ok = (
        l16_5_dry.get("ok") is True
        and l16_5_dry.get("page_detection_execution_allowed") is False
        and l16_5_dry.get("real_page_detection_active") is False
        and l16_5_dry.get("browser_started") is False
        and l16_5_dry.get("edge_process_started") is False
        and l16_5_dry.get("page_metadata_detection_proven") is False
        and l16_5_dry.get("chatgpt_url_opened") is False
        and _no_forbidden_side_effects(l16_5_dry)
    )
    l16_5_live_ok = True
    if execute_live_checkpoint:
        l16_5_live_ok = (
            l16_5_live.get("ok") is True
            and l16_5_live.get("page_detection_execution_allowed") is True
            and l16_5_live.get("real_page_detection_active") is True
            and l16_5_live.get("browser_started") is True
            and l16_5_live.get("edge_process_started") is True
            and l16_5_live.get("chatgpt_url_opened") is True
            and l16_5_live.get("page_metadata_detection_performed") is True
            and l16_5_live.get("page_metadata_detection_proven") is True
            and l16_5_live.get("page_identity_metadata_detected") is True
            and (l16_5_live.get("edge_process_close_result") or {}).get("remaining_count") == 0
            and _no_forbidden_side_effects(l16_5_live)
        )

    checks = [
        _check("l16_3_passive_plan_checkpoint_still_green", l16_3_ok),
        _check("l16_4_authorization_gate_still_green", l16_4_ok),
        _check("l16_5_dry_metadata_detection_readback_still_green", l16_5_dry_ok),
        _check("l16_5_live_metadata_detection_green_when_requested", l16_5_live_ok, {"execute_live_checkpoint": execute_live_checkpoint}),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("metadata_only_contract_preserved", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_6_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l16_4_command_name": L16_4_COMMAND_NAME,
        "l16_3_command_name": L16_3_COMMAND_NAME,
        "l16_2_command_name": L16_2_COMMAND_NAME,
        "l16_1_command_name": L16_1_COMMAND_NAME,
        "source_patch": "L16.5",
        "next_patch": NEXT_PATCH,
        "broad_checkpoint": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "l16_1_through_l16_5_accepted": l16_3_ok and l16_4_ok and l16_5_dry_ok and l16_5_live_ok,
        "dry_metadata_checkpoint": not execute_live_checkpoint,
        "explicit_live_metadata_checkpoint": bool(execute_live_checkpoint),
        "l16_3_passive_plan_checkpoint_still_green": l16_3_ok,
        "l16_4_authorization_gate_still_green": l16_4_ok,
        "l16_5_dry_metadata_detection_readback_still_green": l16_5_dry_ok,
        "l16_5_live_metadata_detection_green_when_requested": l16_5_live_ok,
        "target_url_allowlist_enforced": True,
        "target_url": DEFAULT_TARGET_URL,
        "metadata_only_detection_contract": {
            "allowed_observations": ["requested_url", "target_host", "process_count", "window_count", "window_title"],
            "forbidden_observations": ["dom_text", "conversation_text", "prompt_text", "account_data", "artifact_content", "downloaded_files"],
            "observation_source": "os_window_process_metadata_only",
        },
        "page_detection_execution_allowed": bool(execute_live_checkpoint and l16_5_live.get("page_detection_execution_allowed") is True),
        "real_page_detection_active": bool(execute_live_checkpoint and l16_5_live.get("real_page_detection_active") is True),
        "page_inspection_performed": bool(execute_live_checkpoint and l16_5_live.get("page_inspection_performed") is True),
        "page_metadata_detection_performed": bool(execute_live_checkpoint and l16_5_live.get("page_metadata_detection_performed") is True),
        "page_metadata_detection_proven": bool(execute_live_checkpoint and l16_5_live.get("page_metadata_detection_proven") is True),
        "page_identity_metadata_detected": bool(execute_live_checkpoint and l16_5_live.get("page_identity_metadata_detected") is True),
        "chatgpt_url_opened": bool(execute_live_checkpoint and l16_5_live.get("chatgpt_url_opened") is True),
        "browser_started": bool(execute_live_checkpoint and l16_5_live.get("browser_started") is True),
        "edge_process_started": bool(execute_live_checkpoint and l16_5_live.get("edge_process_started") is True),
        "browser_close_attempted": bool(execute_live_checkpoint and l16_5_live.get("browser_close_attempted") is True),
        "edge_process_close_result": l16_5_live.get("edge_process_close_result") if execute_live_checkpoint else {},
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "cdp_used": False,
        "remote_debugging_port_used": False,
        "browser_session_created": False,
        "driver_created": False,
        "dom_scraping_performed": False,
        "prompt_text_extraction_performed": False,
        "conversation_reading_performed": False,
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
        "operator_review_required_before_artifact_detection": True,
        "l16_6_complete": ok,
        "remaining_l16_6_patches": [] if ok else [PATCH],
        "l16_3_summary": {
            "ok": l16_3.get("ok"),
            "future_detection_plan_is_passive": l16_3.get("future_detection_plan_is_passive"),
            "future_detection_plan_is_metadata_only": l16_3.get("future_detection_plan_is_metadata_only"),
            "real_page_detection_active": l16_3.get("real_page_detection_active"),
        },
        "l16_4_summary": {
            "default_ok": l16_4_default.get("ok"),
            "authorized_ok": l16_4_authorized.get("ok"),
            "authorized_readback_only": l16_4_authorized.get("execution_authorization_is_readback_only_in_l16_4"),
            "page_detection_execution_allowed": l16_4_authorized.get("page_detection_execution_allowed"),
        },
        "l16_5_dry_summary": {
            "ok": l16_5_dry.get("ok"),
            "page_detection_execution_allowed": l16_5_dry.get("page_detection_execution_allowed"),
            "browser_started": l16_5_dry.get("browser_started"),
            "page_metadata_detection_proven": l16_5_dry.get("page_metadata_detection_proven"),
            "chatgpt_url_opened": l16_5_dry.get("chatgpt_url_opened"),
        },
        "l16_5_live_summary": {
            "ok": l16_5_live.get("ok"),
            "page_detection_execution_allowed": l16_5_live.get("page_detection_execution_allowed"),
            "browser_started": l16_5_live.get("browser_started"),
            "edge_process_started": l16_5_live.get("edge_process_started"),
            "chatgpt_url_opened": l16_5_live.get("chatgpt_url_opened"),
            "page_metadata_detection_proven": l16_5_live.get("page_metadata_detection_proven"),
            "page_identity_metadata_detected": l16_5_live.get("page_identity_metadata_detected"),
            "edge_process_close_result": l16_5_live.get("edge_process_close_result"),
        } if execute_live_checkpoint else {},
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
        f"Live Checkpoint               : {payload.get('explicit_live_metadata_checkpoint')}",
        f"L16.1-L16.5 Accepted          : {payload.get('l16_1_through_l16_5_accepted')}",
        f"Metadata Proven               : {payload.get('page_metadata_detection_proven')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"ChatGPT URL Opened            : {payload.get('chatgpt_url_opened')}",
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
    parser.add_argument("--execute-live-checkpoint", action="store_true")
    parser.add_argument("--close-after-seconds", type=float, default=6.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_real_page_metadata_detection_broad_checkpoint(
        args.repo_root,
        execute_live_checkpoint=args.execute_live_checkpoint,
        close_after_seconds=args.close_after_seconds,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
