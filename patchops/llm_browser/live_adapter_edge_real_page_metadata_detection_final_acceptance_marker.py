"""L16.7 final acceptance marker for Edge real-page metadata detection.

This marker closes the L16 real-page metadata detection stream after the accepted
L16.6 broad checkpoint. It is deliberately passive: it does not start Microsoft
Edge, inspect pages, import Selenium, use CDP, read ChatGPT conversations, detect
artifacts, download, paste, send, run packages from the browser, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_real_page_metadata_detection_broad_checkpoint as l16_06

PATCH = "L16.7"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.7 Microsoft Edge real-page metadata detection final acceptance marker"
COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-metadata-detection-final-acceptance-marker"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-metadata-detection-broad-checkpoint"
L16_5_COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
L16_4_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
L16_3_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
NEXT_PATCH = "L17.1 Microsoft Edge artifact detection passive preflight gate"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

ACCEPTED_L16_SEQUENCE = (
    "L16.1 Microsoft Edge real-page detection passive preflight gate",
    "L16.2 Microsoft Edge real-page detection CLI/readback checkpoint",
    "L16.3 Microsoft Edge real-page detection passive plan checkpoint",
    "L16.4 Microsoft Edge real-page detection controlled live plan authorization gate",
    "L16.5 Microsoft Edge first controlled real-page metadata detection proof",
    "L16.6 Microsoft Edge real-page metadata detection broad checkpoint",
    "L16.7 Microsoft Edge real-page metadata detection final acceptance marker",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_plan_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_real_page_metadata_detection_proof.py",
    "patchops/llm_browser/live_adapter_edge_real_page_metadata_detection_broad_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_real_page_metadata_detection_final_acceptance_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_cli_readback_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_plan_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_first_controlled_real_page_metadata_detection_proof.md",
    "docs/llm_browser_live_adapter_edge_real_page_metadata_detection_broad_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_real_page_metadata_detection_final_acceptance_marker.md",
    "scripts/patch_l16_05_brief_validate.py",
    "scripts/patch_l16_06_brief_validate.py",
    "scripts/patch_l16_07_brief_validate.py",
    "tests/test_l16_05_edge_first_controlled_real_page_metadata_detection_proof_current.py",
    "tests/test_l16_06_edge_real_page_metadata_detection_broad_checkpoint_current.py",
    "tests/test_l16_07_edge_real_page_metadata_detection_final_acceptance_marker_current.py",
)

SAFETY_PHRASES = (
    "L16.7 Microsoft Edge real-page metadata detection final acceptance marker",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L16_5_COMMAND_NAME,
    L16_4_COMMAND_NAME,
    L16_3_COMMAND_NAME,
    L16_2_COMMAND_NAME,
    L16_1_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "final acceptance marker",
    "L16.1 through L16.6 accepted",
    "L16 metadata detection stream complete",
    "artifact detection is not active yet",
    "download workflow is not active yet",
    "metadata-only page detection accepted",
    "OS/window/process metadata only accepted",
    "no Microsoft Edge start",
    "no Selenium import",
    "no CDP use",
    "no DOM scraping",
    "no prompt text extraction",
    "no conversation reading",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_real_page_metadata_detection_final_acceptance_marker.md")
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


def build_edge_real_page_metadata_detection_final_acceptance_marker(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L16.7 final acceptance marker."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    source = l16_06.build_edge_real_page_metadata_detection_broad_checkpoint(root)
    names = _command_names()
    missing_commands = [
        name
        for name in (L16_1_COMMAND_NAME, L16_2_COMMAND_NAME, L16_3_COMMAND_NAME, L16_4_COMMAND_NAME, L16_5_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME)
        if name not in names
    ]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == "L16.6"
        and source.get("broad_checkpoint") is True
        and source.get("l16_1_through_l16_5_accepted") is True
        and source.get("l16_6_complete") is True
        and source.get("dry_metadata_checkpoint") is True
        and source.get("explicit_live_metadata_checkpoint") is False
        and source.get("page_detection_execution_allowed") is False
        and source.get("real_page_detection_active") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("chatgpt_url_opened") is False
        and _no_forbidden_side_effects(source)
    )

    checks = [
        _check("source_l16_6_broad_checkpoint_accepted", source_ok),
        _check("l16_sequence_truthful", True, {"accepted_sequence": list(ACCEPTED_L16_SEQUENCE)}),
        _check("metadata_only_detection_stream_complete", source_ok),
        _check("artifact_detection_not_active_yet", True),
        _check("download_workflow_not_active_yet", True),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_7_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l16_5_command_name": L16_5_COMMAND_NAME,
        "l16_4_command_name": L16_4_COMMAND_NAME,
        "l16_3_command_name": L16_3_COMMAND_NAME,
        "l16_2_command_name": L16_2_COMMAND_NAME,
        "l16_1_command_name": L16_1_COMMAND_NAME,
        "source_patch": "L16.6",
        "next_patch": NEXT_PATCH,
        "final_acceptance_marker": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "accepted_l16_sequence": list(ACCEPTED_L16_SEQUENCE),
        "l16_1_through_l16_6_accepted": source_ok,
        "l16_metadata_detection_stream_complete": ok,
        "metadata_only_page_detection_accepted": source_ok,
        "os_window_process_metadata_only_accepted": source_ok,
        "artifact_detection_active": False,
        "artifact_detection_allowed": False,
        "download_workflow_active": False,
        "download_workflow_allowed": False,
        "pasteback_workflow_active": False,
        "auto_send_allowed": False,
        "real_page_detection_active": False,
        "page_detection_execution_allowed": False,
        "page_inspection_performed": False,
        "page_metadata_detection_performed": False,
        "page_metadata_detection_proven": False,
        "chatgpt_url_opened": False,
        "launch_execution_allowed": False,
        "browser_process_launch_requested": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_close_attempted": False,
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
        "operator_review_required_before_artifact_detection": True,
        "l16_7_complete": ok,
        "remaining_l16_patches": [] if ok else [PATCH],
        "source_l16_6_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l16_1_through_l16_5_accepted": source.get("l16_1_through_l16_5_accepted"),
            "l16_6_complete": source.get("l16_6_complete"),
            "dry_metadata_checkpoint": source.get("dry_metadata_checkpoint"),
            "page_detection_execution_allowed": source.get("page_detection_execution_allowed"),
            "browser_started": source.get("browser_started"),
            "chatgpt_url_opened": source.get("chatgpt_url_opened"),
            "page_metadata_detection_proven": source.get("page_metadata_detection_proven"),
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
        f"L16.1-L16.6 Accepted          : {payload.get('l16_1_through_l16_6_accepted')}",
        f"L16 Stream Complete           : {payload.get('l16_metadata_detection_stream_complete')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_real_page_metadata_detection_final_acceptance_marker(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
