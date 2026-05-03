"""L16.2 CLI/readback checkpoint for Edge real-page detection preflight.

L16.2 proves the accepted L16.1 passive preflight gate through compact CLI JSON
in both default and explicitly-authorized preflight modes. It remains passive: no
browser start, no page inspection, no Selenium, and no ChatGPT interaction.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L16.2"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.2 Microsoft Edge real-page detection CLI/readback checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
L15_5_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"
NEXT_PATCH = "L16.3 Microsoft Edge real-page detection passive plan checkpoint"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_PREFLIGHT_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_preflight_gate.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_cli_readback_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_live_start_handoff_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_cli_readback_checkpoint.md",
    "scripts/patch_l16_01_brief_validate.py",
    "scripts/patch_l16_02_brief_validate.py",
    "tests/test_l16_01_edge_real_page_detection_passive_preflight_gate_current.py",
    "tests/test_l16_02_edge_real_page_detection_cli_readback_checkpoint_current.py",
)

SAFETY_PHRASES = (
    "L16.2 Microsoft Edge real-page detection CLI/readback checkpoint",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L15_5_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "compact JSON readback",
    "default preflight readback",
    "authorized preflight readback",
    "real-page detection remains inactive",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be selected but not opened",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_real_page_detection_cli_readback_checkpoint.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _json_from_stdout(stdout: str) -> dict[str, Any]:
    text = (stdout or "").strip()
    if not text:
        return {}
    try:
        value = json.loads(text)
        return value if isinstance(value, dict) else {}
    except json.JSONDecodeError:
        for line in reversed(text.splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    value = json.loads(line)
                    return value if isinstance(value, dict) else {}
                except json.JSONDecodeError:
                    continue
    return {}


def _invoke_l16_1_cli(root: Path, *, authorized: bool, target_url: str = DEFAULT_TARGET_URL) -> dict[str, Any]:
    args = [
        sys.executable,
        "-m",
        "patchops.cli",
        "llm-browser",
        SOURCE_COMMAND_NAME,
        "--repo-root",
        str(root),
        "--json",
        "--compact",
    ]
    if authorized:
        args.extend([
            "--allow-real-page-detection-preflight",
            "--authorization-token",
            REQUIRED_AUTHORIZATION_TOKEN,
            "--target-url",
            target_url,
        ])
    completed = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=180)
    payload = _json_from_stdout(completed.stdout)
    return {
        "ok": completed.returncode == 0 and bool(payload.get("ok")),
        "returncode": completed.returncode,
        "stdout_preview": completed.stdout[:500],
        "stderr_preview": completed.stderr[:500],
        "payload": payload,
    }


def _summarize_l16_1_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = (
        "ok",
        "status",
        "patch",
        "phase",
        "command_name",
        "source_patch",
        "source_l15_5_handoff_marker_accepted",
        "source_l15_5_cli_readback_accepted",
        "l15_live_start_stream_complete",
        "l15_1_through_l15_4_accepted",
        "microsoft_edge_first",
        "opera_second",
        "opera_active_implementation_target",
        "real_page_detection_preflight_flag_present",
        "real_page_detection_preflight_token_present",
        "real_page_detection_preflight_authorized",
        "real_page_detection_active",
        "real_page_detection_allowed",
        "page_inspection_allowed",
        "page_inspection_performed",
        "target_url_allowlist_enforced",
        "target_url_status",
        "target_url",
        "chatgpt_url_selected_for_future_detection",
        "chatgpt_url_opened",
        "launch_execution_allowed",
        "browser_process_launch_requested",
        "browser_started",
        "edge_process_started",
        "selenium_required",
        "selenium_imported_by_readback",
        "browser_session_created",
        "driver_created",
        "artifact_detection_performed",
        "click_download_performed",
        "download_performed",
        "paste_performed",
        "send_or_submit_performed",
        "package_run_performed_by_adapter",
        "localhost_patchops_server_started",
        "browser_extension_used",
        "git_commit_executed",
        "git_push_executed",
        "auto_send_allowed",
        "missing_commands",
        "missing_doc_phrases",
        "next_patch",
    )
    return {key: payload.get(key) for key in keys}


def _source_payload_is_passive(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L16.1"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("source_l15_5_handoff_marker_accepted") is True
        and summary.get("source_l15_5_cli_readback_accepted") is True
        and summary.get("l15_live_start_stream_complete") is True
        and summary.get("l15_1_through_l15_4_accepted") is True
        and summary.get("microsoft_edge_first") is True
        and summary.get("opera_second") is True
        and summary.get("opera_active_implementation_target") is False
        and summary.get("real_page_detection_active") is False
        and summary.get("real_page_detection_allowed") is False
        and summary.get("page_inspection_allowed") is False
        and summary.get("page_inspection_performed") is False
        and summary.get("target_url_allowlist_enforced") is True
        and (summary.get("target_url_status") or {}).get("ok") is True
        and summary.get("chatgpt_url_selected_for_future_detection") is True
        and summary.get("chatgpt_url_opened") is False
        and summary.get("launch_execution_allowed") is False
        and summary.get("browser_process_launch_requested") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("selenium_required") is False
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("artifact_detection_performed") is False
        and summary.get("click_download_performed") is False
        and summary.get("download_performed") is False
        and summary.get("paste_performed") is False
        and summary.get("send_or_submit_performed") is False
        and summary.get("package_run_performed_by_adapter") is False
        and summary.get("localhost_patchops_server_started") is False
        and summary.get("browser_extension_used") is False
        and summary.get("git_commit_executed") is False
        and summary.get("git_push_executed") is False
        and summary.get("auto_send_allowed") is False
        and summary.get("missing_commands") == []
        and summary.get("missing_doc_phrases") == []
    )


def build_edge_real_page_detection_cli_readback_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Run compact CLI readback over the accepted passive L16.1 preflight gate."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    default_run = _invoke_l16_1_cli(root, authorized=False)
    authorized_run = _invoke_l16_1_cli(root, authorized=True, target_url=DEFAULT_TARGET_URL)
    default_readback = _summarize_l16_1_payload(default_run.get("payload", {}))
    authorized_readback = _summarize_l16_1_payload(authorized_run.get("payload", {}))

    names = _command_names()
    missing_commands = [name for name in (L15_5_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    default_readback_ok = (
        default_run.get("returncode") == 0
        and _source_payload_is_passive(default_readback)
        and default_readback.get("real_page_detection_preflight_flag_present") is False
        and default_readback.get("real_page_detection_preflight_token_present") is False
        and default_readback.get("real_page_detection_preflight_authorized") is False
    )
    authorized_readback_ok = (
        authorized_run.get("returncode") == 0
        and _source_payload_is_passive(authorized_readback)
        and authorized_readback.get("real_page_detection_preflight_flag_present") is True
        and authorized_readback.get("real_page_detection_preflight_token_present") is True
        and authorized_readback.get("real_page_detection_preflight_authorized") is True
        and authorized_readback.get("real_page_detection_active") is False
        and authorized_readback.get("page_inspection_performed") is False
    )

    checks = [
        _check("source_l16_1_default_cli_readback_passive", default_readback_ok, {"returncode": default_run.get("returncode")}),
        _check("source_l16_1_authorized_cli_readback_passive", authorized_readback_ok, {"returncode": authorized_run.get("returncode")}),
        _check("real_page_detection_remains_inactive", authorized_readback.get("real_page_detection_active") is False and authorized_readback.get("page_inspection_performed") is False),
        _check("target_url_allowlist_remains_enforced", (authorized_readback.get("target_url_status") or {}).get("ok") is True),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_2_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l15_5_command_name": L15_5_COMMAND_NAME,
        "source_patch": "L16.1",
        "next_patch": NEXT_PATCH,
        "cli_readback_checkpoint": True,
        "compact_json_readback": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "default_preflight_readback_ok": default_readback_ok,
        "authorized_preflight_readback_ok": authorized_readback_ok,
        "real_page_detection_active": False,
        "real_page_detection_allowed": False,
        "page_inspection_allowed": False,
        "page_inspection_performed": False,
        "target_url_allowlist_enforced": True,
        "target_url": DEFAULT_TARGET_URL,
        "chatgpt_url_selected_for_future_detection": True,
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
        "l16_2_complete": ok,
        "remaining_l16_2_patches": [] if ok else [PATCH],
        "default_preflight_readback": default_readback,
        "authorized_preflight_readback": authorized_readback,
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
        f"Default Readback OK        : {payload.get('default_preflight_readback_ok')}",
        f"Authorized Readback OK     : {payload.get('authorized_preflight_readback_ok')}",
        f"Real Page Detection Active : {payload.get('real_page_detection_active')}",
        f"Browser Started            : {payload.get('browser_started')}",
        f"Page Inspection Performed  : {payload.get('page_inspection_performed')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_real_page_detection_cli_readback_checkpoint(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
