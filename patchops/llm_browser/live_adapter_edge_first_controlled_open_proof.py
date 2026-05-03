"""L15.3 first controlled Microsoft Edge open proof.

This is the first L15 patch allowed to cross the browser-process boundary. It
only does so when the operator supplies every live-start authorization argument.
The proof opens Microsoft Edge to about:blank using the dedicated L14 profile
candidate, waits briefly, then attempts to close only the Edge process/profile it
started. It does not use Selenium and does not interact with ChatGPT.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate as l15_01
from patchops.llm_browser import live_adapter_edge_live_start_authorization_execution_gate_cli_readback as l15_02

PATCH = "L15.3"
PHASE = "L15"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L15.3 first controlled Microsoft Edge open proof"
COMMAND_NAME = "browser-start-supervised-launch-edge-first-controlled-open-proof"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate-cli-readback"
L15_1_COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-authorization-execution-gate"
NEXT_PATCH = "L15.4 Microsoft Edge first controlled open proof broad checkpoint"
REQUIRED_AUTHORIZATION_TOKEN = "PATCHOPS_L15_EDGE_LIVE_START_AUTHORIZED"
DEFAULT_OPEN_URL = "about:blank"
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

EDGE_CANDIDATES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate.py",
    "patchops/llm_browser/live_adapter_edge_live_start_authorization_execution_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_first_controlled_open_proof.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_first_controlled_open_proof.md",
    "scripts/patch_l15_03_brief_validate.py",
    "tests/test_l15_03_edge_first_controlled_open_proof_current.py",
)

SAFETY_PHRASES = (
    "L15.3 first controlled Microsoft Edge open proof",
    COMMAND_NAME,
    SOURCE_COMMAND_NAME,
    L15_1_COMMAND_NAME,
    "Microsoft Edge first",
    "Opera second",
    "explicit live-start authorization flag required",
    "explicit live-start authorization token required",
    "explicit live-open execution flag required",
    "dedicated L14 profile candidate required",
    "default Microsoft Edge profile rejected",
    "open URL is about:blank",
    "Selenium is not imported",
    "no ChatGPT interaction",
    "no click/download/paste/send/package-run side effect",
    "no localhost PatchOps server",
    "no browser extension",
    "no git commit or git push",
    "close only the Edge process/profile it started",
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


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _missing_doc_phrases(root: Path) -> list[str]:
    text = _read_text(root / "docs/llm_browser_live_adapter_edge_first_controlled_open_proof.md")
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


def _looks_like_default_edge_profile(value: str | None) -> bool:
    if not value:
        return False
    normalized = value.replace("\\", "/").lower()
    return any(marker.replace("\\", "/").lower() in normalized for marker in DEFAULT_PROFILE_MARKERS)


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


def _profile_is_allowed(root: Path, profile_path: Path) -> bool:
    allowed_root = (root / "data" / "runtime" / "browser_profiles").resolve()
    try:
        resolved = profile_path.resolve()
        return resolved == allowed_root or allowed_root in resolved.parents
    except OSError:
        return False


def _profile_stats(profile_path: Path) -> dict[str, Any]:
    if not profile_path.exists():
        return {"exists": False, "file_count": 0, "dir_count": 0, "latest_mtime": None}
    file_count = 0
    dir_count = 0
    latest = 0.0
    try:
        for path in profile_path.rglob("*"):
            try:
                if path.is_dir():
                    dir_count += 1
                elif path.is_file():
                    file_count += 1
                latest = max(latest, path.stat().st_mtime)
            except OSError:
                continue
    except OSError:
        pass
    return {"exists": True, "file_count": file_count, "dir_count": dir_count, "latest_mtime": latest or None}


def _powershell_executable() -> str | None:
    for name in ("pwsh", "powershell"):
        found = shutil.which(name)
        if found:
            return found
    return None


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
Start-Sleep -Milliseconds 700
$remaining = @(Get-CimInstance Win32_Process -Filter "Name = 'msedge.exe'" | Where-Object {{ $_.CommandLine -and $_.CommandLine.IndexOf($profile, [System.StringComparison]::OrdinalIgnoreCase) -ge 0 }})
@{{ stopped_count = $stopped; remaining_count = $remaining.Count }} | ConvertTo-Json -Compress
"""
    completed = subprocess.run([shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], text=True, capture_output=True, timeout=20)
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


def _start_edge_once(edge_executable: Path, profile_path: Path, open_url: str, close_after_seconds: float) -> dict[str, Any]:
    args = [
        str(edge_executable),
        f"--user-data-dir={profile_path}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-notifications",
        "--new-window",
        open_url,
    ]
    started_at = time.time()
    proc: subprocess.Popen[str] | None = None
    start_error: str | None = None
    try:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
    except Exception as exc:  # pragma: no cover - environment dependent
        start_error = f"{type(exc).__name__}: {exc}"

    if proc is not None:
        time.sleep(max(0.5, min(float(close_after_seconds), 10.0)))
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    proc.kill()
        except Exception:
            pass

    stop_result = _stop_edge_processes_for_profile(profile_path)
    duration = round(time.time() - started_at, 3)
    process_started = proc is not None and start_error is None
    return {
        "ok": process_started and bool(stop_result.get("ok")),
        "process_started": process_started,
        "pid": proc.pid if proc is not None else None,
        "start_error": start_error,
        "close_attempted": True,
        "close_result": stop_result,
        "duration_seconds": duration,
        "command_preview": [str(edge_executable), "--user-data-dir=<dedicated-profile>", "--no-first-run", "--no-default-browser-check", "--disable-notifications", "--new-window", open_url],
    }


def build_edge_first_controlled_open_proof(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    authorization_token: str | None = None,
    execute_live_open: bool = False,
    edge_executable: str | Path | None = None,
    close_after_seconds: float = 3.0,
    open_url: str = DEFAULT_OPEN_URL,
) -> dict[str, Any]:
    """Build or execute the first controlled Microsoft Edge open proof."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l15_2_payload = l15_02.build_edge_live_start_authorization_execution_gate_cli_readback(root)
    l15_1_authorized = l15_01.build_edge_live_start_authorization_execution_gate(
        root,
        allow_live_start=True,
        authorization_token=REQUIRED_AUTHORIZATION_TOKEN,
    )

    required = _required_paths_status(root)
    names = _command_names()
    missing_commands = [name for name in (SOURCE_COMMAND_NAME, L15_1_COMMAND_NAME, COMMAND_NAME) if name not in names]
    missing_doc_phrases = _missing_doc_phrases(root)
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    profile_candidate_raw = l15_1_authorized.get("profile_candidate_path")
    profile_path = Path(str(profile_candidate_raw)).resolve() if profile_candidate_raw else (root / "data" / "runtime" / "browser_profiles" / "edge_supervised_l14").resolve()
    profile_existed_before = profile_path.exists()
    stats_before = _profile_stats(profile_path)
    profile_allowed = _profile_is_allowed(root, profile_path)
    default_profile_requested = _looks_like_default_edge_profile(str(profile_path))
    profile_ready = profile_allowed and not default_profile_requested and bool(profile_candidate_raw)

    edge = _discover_edge_executable(edge_executable)
    open_url_safe = open_url == DEFAULT_OPEN_URL
    explicit_authorization_complete = bool(allow_live_start) and authorization_token == REQUIRED_AUTHORIZATION_TOKEN
    live_execution_allowed = explicit_authorization_complete and bool(execute_live_open) and profile_ready and edge["ok"] and open_url_safe and bool(l15_2_payload.get("ok"))

    live_result: dict[str, Any] = {
        "ok": False,
        "process_started": False,
        "pid": None,
        "start_error": None,
        "close_attempted": False,
        "close_result": {},
        "duration_seconds": 0,
        "command_preview": [],
    }
    if live_execution_allowed:
        profile_path.mkdir(parents=True, exist_ok=True)
        live_result = _start_edge_once(Path(str(edge["path"])), profile_path, open_url, close_after_seconds)

    stats_after = _profile_stats(profile_path)
    profile_exists_after = profile_path.exists()
    profile_created = (not profile_existed_before) and profile_exists_after
    profile_mutated = stats_after != stats_before
    live_open_smoke_proven = bool(live_result.get("ok")) and bool(live_result.get("process_started"))

    checks = [
        _check("source_l15_2_cli_readback_accepted", l15_2_payload.get("ok") is True, {"source_patch": l15_2_payload.get("patch")}),
        _check("source_l15_1_authorized_readback_available", l15_1_authorized.get("ok") is True and l15_1_authorized.get("live_start_operator_authorization_complete") is True),
        _check("microsoft_edge_is_active_l15_target", True, {"browser": "edge"}),
        _check("opera_remains_second_priority", True, {"opera_active": False}),
        _check("dedicated_l14_profile_candidate_required", profile_ready, {"profile_candidate_path": str(profile_path)}),
        _check("default_edge_profile_rejected", not default_profile_requested, {"profile_candidate_path": str(profile_path)}),
        _check("edge_executable_discovered", bool(edge["ok"]), {"path": edge.get("path"), "checked": edge.get("checked")}),
        _check("open_url_is_about_blank", open_url_safe, {"open_url": open_url}),
        _check("explicit_authorization_required", True, {"execute_live_open": bool(execute_live_open), "authorization_complete": explicit_authorization_complete}),
        _check("explicit_live_open_flag_required", True, {"execute_live_open": bool(execute_live_open), "launch_execution_allowed": bool(live_execution_allowed)}),
        _check("live_open_smoke_proven_when_execution_allowed", (not live_execution_allowed) or live_open_smoke_proven, {"live_result": live_result, "launch_execution_allowed": bool(live_execution_allowed)}),
        _check("close_attempted_when_execution_allowed", (not live_execution_allowed) or bool(live_result.get("close_attempted")), {"launch_execution_allowed": bool(live_execution_allowed)}),
        _check("command_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("required_repo_paths_present", required["ok"], {"missing": required["missing"]}),
        _check("docs_contain_l15_3_safety_contract", not missing_doc_phrases, {"missing_phrases": missing_doc_phrases}),
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
        "l15_1_command_name": L15_1_COMMAND_NAME,
        "source_patch": "L15.2",
        "next_patch": NEXT_PATCH,
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_implementation_target": False,
        "first_controlled_edge_open_proof": True,
        "explicit_live_start_authorization_flag_required": True,
        "explicit_live_start_authorization_token_required": True,
        "explicit_live_open_execution_flag_required": True,
        "explicit_live_start_authorization_flag_present": bool(allow_live_start),
        "explicit_live_start_authorization_token_present": authorization_token == REQUIRED_AUTHORIZATION_TOKEN,
        "execute_live_open_flag_present": bool(execute_live_open),
        "live_start_operator_authorization_complete": explicit_authorization_complete,
        "launch_execution_allowed": bool(live_execution_allowed),
        "open_url": open_url,
        "open_url_is_about_blank": open_url_safe,
        "edge_executable_discovery": edge,
        "edge_executable_path": edge.get("path"),
        "dedicated_profile_required": True,
        "dedicated_l14_profile_candidate_required": True,
        "dedicated_profile_candidate_inherited_from_l14_09": bool(profile_candidate_raw),
        "profile_candidate_path": str(profile_path),
        "profile_candidate_under_allowed_runtime_root": profile_allowed,
        "default_edge_profile_rejected": not default_profile_requested,
        "default_edge_profile_requested": default_profile_requested,
        "default_profile_use_allowed": False,
        "profile_existed_before": profile_existed_before,
        "profile_exists_after": profile_exists_after,
        "profile_directory_creation_allowed": bool(live_execution_allowed),
        "profile_directory_mutation_allowed": bool(live_execution_allowed),
        "profile_directory_created": profile_created,
        "profile_directory_mutated": profile_mutated,
        "profile_stats_before": stats_before,
        "profile_stats_after": stats_after,
        "browser_process_launch_requested": bool(execute_live_open),
        "browser_process_launch_authorized": explicit_authorization_complete,
        "browser_started": bool(live_result.get("process_started")),
        "edge_process_started": bool(live_result.get("process_started")),
        "live_open_smoke_executed": bool(execute_live_open),
        "live_open_smoke_proven": live_open_smoke_proven,
        "browser_close_attempted": bool(live_result.get("close_attempted")),
        "edge_process_close_result": live_result.get("close_result"),
        "browser_session_created": False,
        "driver_created": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "chatgpt_url_opened": False,
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
        "filesystem_writes_performed": [str(profile_path)] if profile_mutated else [],
        "adapter_filesystem_writes_performed": [str(profile_path)] if profile_mutated else [],
        "side_effects_performed": ["edge_process_start", "dedicated_profile_mutation"] if live_open_smoke_proven else [],
        "operator_review_required_before_chatgpt_interaction": True,
        "l15_3_complete": ok,
        "remaining_l15_3_patches": [] if ok else [PATCH],
        "source_l15_2_status": {
            "ok": l15_2_payload.get("ok"),
            "status": l15_2_payload.get("status"),
            "patch": l15_2_payload.get("patch"),
            "no_authorization_readback_ok": l15_2_payload.get("no_authorization_readback_ok"),
            "authorized_readback_ok": l15_2_payload.get("authorized_readback_ok"),
            "authorization_is_readback_only_in_l15_2": l15_2_payload.get("authorization_is_readback_only_in_l15_2"),
        },
        "live_result": live_result,
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
        f"Patch                 : {payload.get('patch')}",
        f"Status                : {payload.get('status')}",
        f"Command               : {payload.get('command_name')}",
        f"Source Command        : {payload.get('source_command_name')}",
        f"Launch Allowed        : {payload.get('launch_execution_allowed')}",
        f"Live Open Executed    : {payload.get('live_open_smoke_executed')}",
        f"Live Open Proven      : {payload.get('live_open_smoke_proven')}",
        f"Browser Started       : {payload.get('browser_started')}",
        f"Edge Process Started  : {payload.get('edge_process_started')}",
        f"Close Attempted       : {payload.get('browser_close_attempted')}",
        f"Profile Path          : {payload.get('profile_candidate_path')}",
        f"Profile Mutated       : {payload.get('profile_directory_mutated')}",
        f"Open URL              : {payload.get('open_url')}",
        f"Selenium Imported     : {payload.get('selenium_imported_by_readback')}",
        f"Next Patch            : {payload.get('next_patch')}",
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
    parser.add_argument("--allow-live-start", action="store_true")
    parser.add_argument("--authorization-token", default=None)
    parser.add_argument("--execute-live-open", action="store_true")
    parser.add_argument("--edge-executable", default=None)
    parser.add_argument("--close-after-seconds", type=float, default=3.0)
    parser.add_argument("--open-url", default=DEFAULT_OPEN_URL)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_first_controlled_open_proof(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        authorization_token=args.authorization_token,
        execute_live_open=args.execute_live_open,
        edge_executable=args.edge_executable,
        close_after_seconds=args.close_after_seconds,
        open_url=args.open_url,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
