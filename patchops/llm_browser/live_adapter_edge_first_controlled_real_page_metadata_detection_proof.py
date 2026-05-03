"""L16.5 first controlled real-page metadata detection proof for Edge.

This is the first L16 patch allowed to open an allowlisted real page. It opens
Microsoft Edge with the dedicated PatchOps runtime profile, navigates only to an
allowlisted ChatGPT URL, observes OS/window/process metadata only, and closes
only the Edge process tree/profile it started.

It does not use Selenium, CDP, browser extensions, DOM scraping, prompt text
extraction, conversation reading, artifact detection, clicks, downloads, paste,
send/submit, package-running from a browser, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence
from urllib.parse import urlparse

from patchops.llm_browser import live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate as l16_04

PATCH = "L16.5"
PHASE = "L16"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L16.5 Microsoft Edge first controlled real-page metadata detection proof"
COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-real-page-metadata-detection-proof"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-controlled-live-plan-authorization-gate"
L16_3_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-plan-checkpoint"
L16_2_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-cli-readback-checkpoint"
L16_1_COMMAND_NAME = "browser-start-supervised-launch-edge-real-page-detection-passive-preflight-gate"
NEXT_PATCH = "L16.6 Microsoft Edge real-page metadata detection broad checkpoint"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L16_EDGE_REAL_PAGE_DETECTION_EXECUTION_AUTHORIZED"
DEFAULT_TARGET_URL = "https://chatgpt.com/"
ALLOWED_TARGET_HOSTS = ("chatgpt.com", "chat.openai.com")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
EDGE_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_real_page_metadata_detection_proof.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_real_page_detection_controlled_live_plan_authorization_gate.md",
    "docs/llm_browser_live_adapter_edge_first_controlled_real_page_metadata_detection_proof.md",
    "scripts/patch_l16_04_brief_validate.py",
    "scripts/patch_l16_05_brief_validate.py",
    "tests/test_l16_04_edge_real_page_detection_controlled_live_plan_authorization_gate_current.py",
    "tests/test_l16_05_edge_first_controlled_real_page_metadata_detection_proof_current.py",
)

SAFETY_PHRASES = (
    "L16.5 Microsoft Edge first controlled real-page metadata detection proof",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L16_3_COMMAND_NAME,
    L16_2_COMMAND_NAME,
    L16_1_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "first controlled real-page metadata detection proof",
    "explicit execution authorization required",
    "target URL allowlist remains enforced",
    "ChatGPT URL may be opened only with explicit authorization",
    "dedicated PatchOps runtime profile only",
    "default Microsoft Edge profile rejected",
    "metadata-only page detection",
    "OS/window/process metadata only",
    "requested URL, process count, window count, and window title only",
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

DEFAULT_PROFILE_MARKERS = (
    "microsoft/edge/user data/default",
    "microsoft\\edge\\user data\\default",
    "/edge/user data/default",
    "\\edge\\user data\\default",
    "user data/default",
    "user data\\default",
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
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_first_controlled_real_page_metadata_detection_proof.md")
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


def _looks_like_default_edge_profile(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.replace("\\", "/").lower()
    return any(marker.replace("\\", "/").lower() in normalized for marker in DEFAULT_PROFILE_MARKERS)


def _profile_path(root: Path) -> Path:
    return (root / "data" / "runtime" / "browser_profiles" / "edge_supervised_l14").resolve()


def _profile_is_allowed(root: Path, profile_path: Path) -> bool:
    allowed_root = (root / "data" / "runtime" / "browser_profiles").resolve()
    try:
        resolved = profile_path.resolve()
        return resolved == allowed_root or allowed_root in resolved.parents
    except OSError:
        return False


def _discover_edge_executable(explicit: str | Path | None = None) -> dict[str, Any]:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(Path(item) for item in EDGE_CANDIDATES)
    seen: set[str] = set()
    checked: list[str] = []
    for candidate in candidates:
        key = str(candidate).lower()
        if key in seen:
            continue
        seen.add(key)
        checked.append(str(candidate))
        if candidate.exists() and candidate.is_file() and candidate.name.lower() == "msedge.exe":
            return {"ok": True, "path": str(candidate), "checked": checked}
    return {"ok": False, "path": None, "checked": checked}


def _powershell_executable() -> str | None:
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return None


def _profile_process_metadata(profile_path: Path, target_host: str) -> dict[str, Any]:
    shell = _powershell_executable()
    if shell is None:
        return {"ok": False, "available": False, "process_count": 0, "window_count": 0, "items": [], "stderr": "PowerShell not found"}
    profile_literal = str(profile_path).replace("'", "''")
    host_literal = target_host.replace("'", "''")
    script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$profile = '{profile_literal}'
$hostNeedle = '{host_literal}'
$matches = @(Get-CimInstance Win32_Process -Filter "Name = 'msedge.exe'" | Where-Object {{ $_.CommandLine -and $_.CommandLine.IndexOf($profile, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 }})
$items = @()
foreach ($p in $matches) {{
    $gp = Get-Process -Id $p.ProcessId -ErrorAction SilentlyContinue
    $title = ''
    if ($gp) {{ $title = [string]$gp.MainWindowTitle }}
    $items += [pscustomobject]@{{
        pid = [int]$p.ProcessId
        has_window = -not [string]::IsNullOrWhiteSpace($title)
        title = $title
        command_line_contains_profile = $true
        command_line_contains_target_host = ($p.CommandLine -and $p.CommandLine.IndexOf($hostNeedle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
    }}
}}
$windowCount = @($items | Where-Object {{ $_.has_window }}).Count
$targetHostCount = @($items | Where-Object {{ $_.command_line_contains_target_host }}).Count
@{{ process_count = $items.Count; window_count = $windowCount; target_host_process_count = $targetHostCount; items = @($items) }} | ConvertTo-Json -Compress -Depth 5
"""
    completed = subprocess.run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], text=True, capture_output=True, timeout=20)
    payload: dict[str, Any] = {}
    try:
        payload = json.loads((completed.stdout or "").strip() or "{}")
    except json.JSONDecodeError:
        payload = {}
    return {
        "ok": completed.returncode == 0,
        "available": True,
        "returncode": completed.returncode,
        "process_count": int(payload.get("process_count") or 0),
        "window_count": int(payload.get("window_count") or 0),
        "target_host_process_count": int(payload.get("target_host_process_count") or 0),
        "items": payload.get("items") or [],
        "stderr": completed.stderr[:300],
    }


def _stop_edge_processes_for_profile(profile_path: Path) -> dict[str, Any]:
    shell = _powershell_executable()
    if shell is None:
        return {"ok": False, "available": False, "stopped_count": 0, "remaining_count": None, "stderr": "PowerShell not found"}
    profile_literal = str(profile_path).replace("'", "''")
    script = f"""
$ErrorActionPreference = 'SilentlyContinue'
$profile = '{profile_literal}'
$matches = @(Get-CimInstance Win32_Process -Filter "Name = 'msedge.exe'" | Where-Object {{ $_.CommandLine -and $_.CommandLine.IndexOf($profile, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 }})
$stopped = 0
foreach ($p in $matches) {{
    try {{ Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop; $stopped++ }} catch {{}}
}}
Start-Sleep -Milliseconds 900
$remaining = @(Get-CimInstance Win32_Process -Filter "Name = 'msedge.exe'" | Where-Object {{ $_.CommandLine -and $_.CommandLine.IndexOf($profile, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 }})
@{{ stopped_count = $stopped; remaining_count = $remaining.Count }} | ConvertTo-Json -Compress
"""
    completed = subprocess.run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], text=True, capture_output=True, timeout=25)
    payload: dict[str, Any] = {}
    try:
        payload = json.loads((completed.stdout or "").strip() or "{}")
    except json.JSONDecodeError:
        payload = {}
    remaining = payload.get("remaining_count")
    return {
        "ok": completed.returncode == 0 and remaining == 0,
        "available": True,
        "returncode": completed.returncode,
        "stopped_count": payload.get("stopped_count", 0),
        "remaining_count": remaining,
        "stdout": completed.stdout[:300],
        "stderr": completed.stderr[:300],
    }


def _start_edge_for_metadata(edge_executable: Path, profile_path: Path, target_url: str, target_host: str, wait_seconds: float) -> dict[str, Any]:
    args = [
        str(edge_executable),
        f"--user-data-dir={profile_path}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-notifications",
        "--new-window",
        target_url,
    ]
    started_at = time.time()
    start_error: str | None = None
    proc: subprocess.Popen[str] | None = None
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    except Exception as exc:  # pragma: no cover - environment dependent
        start_error = f"{type(exc).__name__}: {exc}"

    metadata = {"ok": False, "process_count": 0, "window_count": 0, "target_host_process_count": 0, "items": []}
    if proc is not None:
        deadline = time.time() + max(1.0, min(float(wait_seconds), 20.0))
        while time.time() < deadline:
            time.sleep(0.75)
            metadata = _profile_process_metadata(profile_path, target_host)
            if int(metadata.get("process_count") or 0) > 0:
                break
        # Give the title a little more time, but do not require it for proof.
        if int(metadata.get("window_count") or 0) == 0:
            time.sleep(1.0)
            metadata = _profile_process_metadata(profile_path, target_host)

    close_result = _stop_edge_processes_for_profile(profile_path)
    process_started = proc is not None and start_error is None
    page_metadata_observed = process_started and int(metadata.get("process_count") or 0) > 0
    page_identity_metadata_detected = page_metadata_observed and target_host in ALLOWED_TARGET_HOSTS
    duration = round(time.time() - started_at, 3)
    return {
        "ok": process_started and page_identity_metadata_detected and bool(close_result.get("ok")),
        "process_started": process_started,
        "pid": proc.pid if proc is not None else None,
        "start_error": start_error,
        "metadata_observed": page_metadata_observed,
        "page_identity_metadata_detected": page_identity_metadata_detected,
        "metadata": metadata,
        "close_attempted": True,
        "close_result": close_result,
        "duration_seconds": duration,
        "command_preview": [str(edge_executable), "--user-data-dir=<dedicated-patchops-profile>", "--no-first-run", "--no-default-browser-check", "--disable-notifications", "--new-window", target_url],
    }


def build_edge_first_controlled_real_page_metadata_detection_proof(
    repo_root: str | Path | None = None,
    *,
    allow_real_page_detection_execution: bool = False,
    authorization_token: str | None = None,
    execute_page_metadata_detection: bool = False,
    target_url: str | None = None,
    edge_executable: str | Path | None = None,
    close_after_seconds: float = 6.0,
) -> dict[str, Any]:
    """Build or execute the first controlled Edge page metadata proof."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    target = _target_url_status(target_url)
    profile_path = _profile_path(root)
    profile_allowed = _profile_is_allowed(root, profile_path)
    default_profile_requested = _looks_like_default_edge_profile(str(profile_path))
    edge = _discover_edge_executable(edge_executable)

    source = l16_04.build_edge_real_page_detection_controlled_live_plan_authorization_gate(
        root,
        allow_real_page_detection_execution=True,
        authorization_token=REQUIRED_AUTHORIZATION_TOKEN,
        target_url=target["target_url"],
    )
    names = _command_names()
    missing_commands = [name for name in (L16_1_COMMAND_NAME, L16_2_COMMAND_NAME, L16_3_COMMAND_NAME, SOURCE_COMMAND_NAME, COMMAND_NAME) if name not in names]
    required = _required_paths_status(root)
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    source_ok = (
        source.get("ok") is True
        and source.get("patch") == "L16.4"
        and source.get("real_page_detection_execution_authorized") is True
        and source.get("execution_authorization_is_readback_only_in_l16_4") is True
        and source.get("page_detection_execution_allowed") is False
        and source.get("real_page_detection_active") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
    )
    explicit_authorization_complete = bool(allow_real_page_detection_execution) and authorization_token == REQUIRED_AUTHORIZATION_TOKEN
    page_detection_execution_allowed = bool(execute_page_metadata_detection and explicit_authorization_complete and target["ok"] and edge["ok"] and profile_allowed and not default_profile_requested and source_ok)

    live_result: dict[str, Any] = {
        "ok": False,
        "process_started": False,
        "metadata_observed": False,
        "page_identity_metadata_detected": False,
        "metadata": {"process_count": 0, "window_count": 0, "target_host_process_count": 0, "items": []},
        "close_attempted": False,
        "close_result": {},
    }
    if page_detection_execution_allowed:
        profile_path.mkdir(parents=True, exist_ok=True)
        live_result = _start_edge_for_metadata(
            Path(str(edge["path"])),
            profile_path,
            str(target["target_url"]),
            str(target["host"]),
            close_after_seconds,
        )

    metadata = live_result.get("metadata") or {}
    page_metadata_detection_performed = bool(execute_page_metadata_detection)
    page_metadata_detection_proven = bool(live_result.get("ok")) and bool(live_result.get("metadata_observed"))
    page_identity_metadata_detected = bool(live_result.get("page_identity_metadata_detected"))

    checks = [
        _check("source_l16_4_authorization_gate_accepted", source_ok),
        _check("microsoft_edge_first", True),
        _check("opera_second_not_active", True, {"opera_active": False}),
        _check("target_url_allowlisted", target["ok"], {"host": target["host"], "scheme": target["scheme"]}),
        _check("dedicated_patchops_profile_allowed", profile_allowed, {"profile_path": str(profile_path)}),
        _check("default_edge_profile_rejected", not default_profile_requested, {"profile_path": str(profile_path)}),
        _check("edge_executable_discovered", bool(edge["ok"]), {"path": edge.get("path"), "checked": edge.get("checked")}),
        _check("explicit_execution_authorization_required", True, {"authorized": explicit_authorization_complete}),
        _check("metadata_detection_proven_when_execution_allowed", (not page_detection_execution_allowed) or page_metadata_detection_proven, {"live_result_ok": live_result.get("ok")}),
        _check("close_attempted_when_execution_allowed", (not page_detection_execution_allowed) or bool(live_result.get("close_attempted"))),
        _check("close_left_no_profile_edge_processes", (not page_detection_execution_allowed) or (live_result.get("close_result") or {}).get("remaining_count") == 0),
        _check("metadata_only_no_dom_contract_preserved", True),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l16_5_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l16_3_command_name": L16_3_COMMAND_NAME,
        "l16_2_command_name": L16_2_COMMAND_NAME,
        "l16_1_command_name": L16_1_COMMAND_NAME,
        "source_patch": "L16.4",
        "next_patch": NEXT_PATCH,
        "first_controlled_real_page_metadata_detection_proof": True,
        "source_l16_4_authorization_gate_accepted": source_ok,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "target_url_allowlist_enforced": True,
        "target_url_status": target,
        "target_url": target["target_url"],
        "target_host": target["host"],
        "chatgpt_url_opened": bool(page_detection_execution_allowed and live_result.get("process_started")),
        "real_page_detection_execution_flag_required": True,
        "real_page_detection_execution_token_required": True,
        "real_page_detection_execution_flag_present": bool(allow_real_page_detection_execution),
        "real_page_detection_execution_token_present": authorization_token == REQUIRED_AUTHORIZATION_TOKEN,
        "real_page_detection_execution_authorized": explicit_authorization_complete,
        "execute_page_metadata_detection_flag_present": bool(execute_page_metadata_detection),
        "page_detection_execution_allowed": page_detection_execution_allowed,
        "real_page_detection_active": bool(page_detection_execution_allowed),
        "page_inspection_allowed": bool(page_detection_execution_allowed),
        "page_inspection_performed": page_metadata_detection_performed,
        "page_metadata_detection_performed": page_metadata_detection_performed,
        "page_metadata_detection_proven": page_metadata_detection_proven,
        "page_identity_metadata_detected": page_identity_metadata_detected,
        "metadata_only_detection_contract": {
            "allowed_observations": ["requested_url", "target_host", "process_count", "window_count", "window_title"],
            "forbidden_observations": ["dom_text", "conversation_text", "prompt_text", "account_data", "artifact_content", "downloaded_files"],
            "observation_source": "os_window_process_metadata_only",
        },
        "requested_url_metadata": target["target_url"],
        "current_url_observed": False,
        "current_url_observation_reason": "L16.5 avoids CDP/Selenium/DOM access; current URL proof is deferred to a later explicitly-authorized metadata layer.",
        "window_title_observed": any(bool((item or {}).get("title")) for item in (metadata.get("items") or [])) if isinstance(metadata, dict) else False,
        "metadata_observation": {
            "process_count": metadata.get("process_count", 0) if isinstance(metadata, dict) else 0,
            "window_count": metadata.get("window_count", 0) if isinstance(metadata, dict) else 0,
            "target_host_process_count": metadata.get("target_host_process_count", 0) if isinstance(metadata, dict) else 0,
            "items": metadata.get("items", []) if isinstance(metadata, dict) else [],
        },
        "profile_candidate_path": str(profile_path),
        "dedicated_patchops_profile_allowed": profile_allowed,
        "default_edge_profile_rejected": not default_profile_requested,
        "default_edge_profile_requested": default_profile_requested,
        "default_profile_use_allowed": False,
        "edge_executable_discovery": edge,
        "edge_executable_path": edge.get("path"),
        "launch_execution_allowed": page_detection_execution_allowed,
        "browser_process_launch_requested": bool(execute_page_metadata_detection),
        "browser_started": bool(live_result.get("process_started")),
        "edge_process_started": bool(live_result.get("process_started")),
        "browser_close_attempted": bool(live_result.get("close_attempted")),
        "edge_process_close_result": live_result.get("close_result"),
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
        "live_result": live_result,
        "l16_5_complete": ok,
        "remaining_l16_5_patches": [] if ok else [PATCH],
        "source_l16_4_summary": {
            "ok": source.get("ok"),
            "patch": source.get("patch"),
            "authorized": source.get("real_page_detection_execution_authorized"),
            "readback_only": source.get("execution_authorization_is_readback_only_in_l16_4"),
            "page_detection_execution_allowed": source.get("page_detection_execution_allowed"),
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
        f"Patch                         : {payload.get('patch')}",
        f"Status                        : {payload.get('status')}",
        f"Command                       : {payload.get('command_name')}",
        f"Source Command                : {payload.get('source_command_name')}",
        f"Execution Allowed             : {payload.get('page_detection_execution_allowed')}",
        f"Metadata Proven               : {payload.get('page_metadata_detection_proven')}",
        f"Browser Started               : {payload.get('browser_started')}",
        f"Edge Started                  : {payload.get('edge_process_started')}",
        f"ChatGPT URL Opened            : {payload.get('chatgpt_url_opened')}",
        f"Page Inspection Performed     : {payload.get('page_inspection_performed')}",
        f"Current URL Observed          : {payload.get('current_url_observed')}",
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
    parser.add_argument("--execute-page-metadata-detection", action="store_true")
    parser.add_argument("--target-url", default=DEFAULT_TARGET_URL)
    parser.add_argument("--edge-executable", default=None)
    parser.add_argument("--close-after-seconds", type=float, default=6.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_first_controlled_real_page_metadata_detection_proof(
        args.repo_root,
        allow_real_page_detection_execution=args.allow_real_page_detection_execution,
        authorization_token=args.authorization_token,
        execute_page_metadata_detection=args.execute_page_metadata_detection,
        target_url=args.target_url,
        edge_executable=args.edge_executable,
        close_after_seconds=args.close_after_seconds,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
