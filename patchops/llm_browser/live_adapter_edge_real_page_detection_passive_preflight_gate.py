"""L16.1 passive preflight gate for Microsoft Edge real-page detection.

This module starts the real-page-detection stream after the accepted L15.5
handoff marker. It is deliberately passive: it does not start Microsoft Edge,
inspect a page, import Selenium, touch ChatGPT, detect artifacts, download,
paste, send, run packages from the browser, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from patchops.llm_browser import live_adapter_edge_live_start_handoff_marker as l15_05

PATCH = "L16.1"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.1 Microsoft Edge real-page detection passive preflight gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-handoff-marker-before-real-page-detection"
L15_4_COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-open-proof-broad-checkpoint"
L15_3_COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-open-proof"
L15_2_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
L15_1_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
NEXT_PATCH = "L16.2 Microsoft Edge real-page detection CLI/readback checkpoint"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_PREFLIGHT_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ALLOWED_TARGET_HOSTS = ("chatgpt.com", "chat.openai.com")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_live_start_handoff_marker.py",
    "patchops/llm_browser/live_adapter_edge_real_page_detection_passive_preflight_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_live_start_handoff_marker.md",
    "docs/llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md",
    "scripts/patch_l16_01_brief_validate.py",
    "tests/test_l16_01_edge_real_page_detection_passive_preflight_gate_current.py",
)

SAFETY_PHRASES = (
    "L16.1 Microsoft Edge real-page detection passive preflight gate",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L15_4_COMMAND_NAME,
    L15_3_COMMAND_NAME,
    L15_2_COMMAND_NAME,
    L15_1_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "passive preflight gate",
    "real-page detection is not active yet",
    "target URL allowlist",
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


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _missing_doc_phrases(root: Path) -> list[str]:
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_real_page_detection_passive_preflight_gate.md")
    return [phrase for phrase in SAFETY_PHRASES if phrase not in text]


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _command_names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()


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


def _invoke_cli(root: Path, args: Sequence[str], timeout: int = 150) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "patchops.cli", "llm-browser", *args],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    payload = _json_from_stdout(completed.stdout)
    return {
        "ok": completed.returncode == 0 and bool(payload.get("ok")),
        "returncode": completed.returncode,
        "stdout_preview": completed.stdout[:500],
        "stderr_preview": completed.stderr[:500],
        "payload": payload,
    }


def _target_url_status(target_url: str | None) -> dict[str, Any]:
    value = target_url or DEFAULT_TARGET_URL
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    scheme = (parsed.scheme or "").lower()
    normalized = f"{scheme}://{host}{parsed.path or '/'}"
    allowed = scheme == "https" and host in ALLOWED_TARGET_HOSTS
    return {
        "ok": allowed,
        "target_url": value,
        "scheme": scheme,
        "host": host,
        "normalized_preview": normalized,
        "allowed_hosts": list(ALLOWED_TARGET_HOSTS),
    }


def build_edge_real_page_detection_passive_preflight_gate(
    repo_root: str | Path | None = None,
    *,
    allow_real_page_detection_preflight: bool = False,
    authorization_token: str | None = None,
    target_url: str | None = None,
) -> dict[str, Any]:
    """Build the passive L16.1 real-page detection preflight readback."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    source = l15_05.build_edge_live_start_handoff_marker(root)
    source_cli = _invoke_cli(
        root,
        [SOURCE_COMMAND_NAME, "--repo-root", str(root), "--json", "--compact"],
        timeout=150,
    )
    source_cli_payload = source_cli.get("payload", {})

    names = _command_names()
    missing_commands = [
        name
        for name in (L15_1_COMMAND_NAME, L15_2_COMMAND_NAME, L15_3_COMMAND_NAME, L15_4_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME)
        if name not in names
    ]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    target = _target_url_status(target_url)

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == "L15.5"
        and source.get("l15_live_start_stream_complete") is True
        and source.get("l15_1_through_l15_4_accepted") is True
        and source.get("real_page_detection_active") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("page_inspection_performed") is False
        and source.get("artifact_detection_performed") is False
    )
    source_cli_ok = (
        source_cli.get("ok") is True
        and source_cli_payload.get("patch") == "L15.5"
        and source_cli_payload.get("l15_5_complete") is True
        and source_cli_payload.get("l15_live_start_stream_complete") is True
        and source_cli_payload.get("real_page_detection_active") is False
        and source_cli_payload.get("browser_started") is False
        and source_cli_payload.get("edge_process_started") is False
    )
    explicit_preflight_authorized = bool(allow_real_page_detection_preflight) and authorization_token == REQUIRED_AUTHORIZATION_TOKEN

    checks = [
        _check("source_l15_5_handoff_marker_accepted", source_ok),
        _check("source_l15_5_cli_readback_accepted", source_cli_ok, {"returncode": source_cli.get("returncode")}),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlisted", target["ok"], {"host": target["host"], "scheme": target["scheme"]}),
        _check("real_page_detection_preflight_authorization_surface_present", True),
        _check("real_page_detection_still_inactive", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_1_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l15_4_command_name": L15_4_COMMAND_NAME,
        "l15_3_command_name": L15_3_COMMAND_NAME,
        "l15_2_command_name": L15_2_COMMAND_NAME,
        "l15_1_command_name": L15_1_COMMAND_NAME,
        "source_patch": "L15.5",
        "next_patch": NEXT_PATCH,
        "passive_preflight_gate": True,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "source_l15_5_handoff_marker_accepted": source_ok,
        "source_l15_5_cli_readback_accepted": source_cli_ok,
        "l15_live_start_stream_complete": bool(source.get("l15_live_start_stream_complete")),
        "l15_1_through_l15_4_accepted": bool(source.get("l15_1_through_l15_4_accepted")),
        "real_page_detection_preflight_flag_required": True,
        "real_page_detection_preflight_token_required": True,
        "real_page_detection_preflight_flag_present": bool(allow_real_page_detection_preflight),
        "real_page_detection_preflight_token_present": authorization_token == REQUIRED_AUTHORIZATION_TOKEN,
        "real_page_detection_preflight_authorized": explicit_preflight_authorized,
        "real_page_detection_active": False,
        "real_page_detection_allowed": False,
        "page_inspection_allowed": False,
        "page_inspection_performed": False,
        "target_url_allowlist_enforced": True,
        "target_url_status": target,
        "target_url": target["target_url"],
        "chatgpt_url_selected_for_future_detection": target["ok"],
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
        "operator_review_required_before_page_detection": True,
        "l16_1_complete": ok,
        "remaining_l16_1_patches": [] if ok else [PATCH],
        "source_l15_5_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "l15_live_start_stream_complete": source.get("l15_live_start_stream_complete"),
            "l15_1_through_l15_4_accepted": source.get("l15_1_through_l15_4_accepted"),
            "real_page_detection_active": source.get("real_page_detection_active"),
            "browser_started": source.get("browser_started"),
            "edge_process_started": source.get("edge_process_started"),
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
        f"Patch                       : {payload.get('patch')}",
        f"Status                      : {payload.get('status')}",
        f"Command                     : {payload.get('command_name')}",
        f"Source Command              : {payload.get('source_command_name')}",
        f"L15 Stream Complete         : {payload.get('l15_live_start_stream_complete')}",
        f"Preflight Authorized        : {payload.get('real_page_detection_preflight_authorized')}",
        f"Real Page Detection Active  : {payload.get('real_page_detection_active')}",
        f"Target URL                  : {payload.get('target_url')}",
        f"Target URL Allowlisted      : {(payload.get('target_url_status') or {}).get('ok')}",
        f"Browser Started             : {payload.get('browser_started')}",
        f"Page Inspection Performed   : {payload.get('page_inspection_performed')}",
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
    parser.add_argument("--allow-real-page-detection-preflight", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_real_page_detection_passive_preflight_gate(
        args.repo_root,
        allow_real_page_detection_preflight=args.allow_real_page_detection_preflight,
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
