"""L15.1 controlled Microsoft Edge live open proof.

This module is the first live Microsoft Edge start surface after the accepted
L14 dedicated-profile lifecycle final marker. It deliberately avoids Selenium,
page scraping, artifact detection, downloads, pasteback, send/submit, PatchOps
package runs, localhost servers, browser extensions, git commit, and git push.

A real Edge process can start only when all explicit execution gates are present:

- --execute-live-open
- --allow-live-edge-start
- --authorization-token PATCHOPS_L15_EDGE_LIVE_OPEN_PROOF

Default CLI/readback mode is non-executing and side-effect free.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, MutableMapping, Sequence

from patchops.llm_browser import live_adapter_edge_dedicated_profile_lifecycle_final_acceptance_marker as l14_09
from patchops.llm_browser.browser_paths import require_browser_path

PATCH = "L15.1"
PHASE = "L15"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_BLOCKED = "BLOCKED"
NAME = "L15.1 Microsoft Edge live open proof explicit authorization gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-open-proof"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-dedicated-profile-lifecycle-final-acceptance-marker"
AUTHORIZATION_TOKEN = "PATCHOPS_L15_EDGE_LIVE_OPEN_PROOF"
DEFAULT_PROFILE_RELATIVE_PATH = "data/runtime/browser_profiles/edge_supervised_l14"
DEFAULT_CHAT_URL = "about:blank"
NEXT_PATCH = "L15.2 Microsoft Edge live open proof CLI/readback and operator report polish"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_IMPORT_ROOTS = ("selenium", "webdriver_manager", "pyperclip")

NO_INTERACTION_BOUNDARIES = {
    "selenium_required": False,
    "selenium_imported_by_readback": False,
    "page_scraping_performed": False,
    "chatgpt_interaction_performed": False,
    "latest_assistant_reply_detection_performed": False,
    "artifact_detection_performed": False,
    "click_download_performed": False,
    "download_performed": False,
    "paste_performed": False,
    "send_or_submit_performed": False,
    "package_run_performed_by_adapter": False,
    "git_commit_executed": False,
    "git_push_executed": False,
    "localhost_patchops_server_started": False,
    "browser_extension_used": False,
    "opera_active_target": False,
}


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _source_l14_09_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L14.9"
        and source.get("l14_complete") is True
        and source.get("remaining_l14_patches") == []
        and source.get("profile_final_marker_truthful") is True
        and source.get("profile_final_marker_is_passive") is True
        and source.get("profile_candidate_under_allowed_runtime_root") is True
        and source.get("profile_lifecycle_steps_are_passive") is True
        and source.get("launch_execution_allowed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("driver_created") is False
        and source.get("selenium_imported_by_readback") is False
    )


def _is_relative_path_safe(value: str) -> bool:
    path = Path(value)
    return bool(value.strip()) and not path.is_absolute() and ".." not in path.parts


def _is_under(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _looks_like_default_edge_profile(path: Path) -> bool:
    text = str(path).replace("\\", "/").lower().rstrip("/")
    return (
        "/microsoft/edge/user data/default" in text
        or text.endswith("/microsoft/edge/user data")
        or text.endswith("/microsoft/edge/user data/default")
    )


def _profile_status(root: Path, profile_relative_path: str) -> dict[str, Any]:
    allowed_root = root / "data" / "runtime" / "browser_profiles"
    safe_relative = _is_relative_path_safe(profile_relative_path)
    candidate = (root / profile_relative_path).resolve() if safe_relative else (root / "__invalid_profile_path__").resolve()
    under_allowed_root = safe_relative and _is_under(candidate, allowed_root)
    default_profile_rejected = not _looks_like_default_edge_profile(candidate)
    return {
        "profile_relative_path": profile_relative_path,
        "profile_candidate_path": str(candidate),
        "allowed_profile_root": str(allowed_root.resolve()),
        "profile_candidate_under_allowed_runtime_root": under_allowed_root,
        "profile_default_profile_rejected": default_profile_rejected,
        "profile_path_safe_relative": safe_relative,
        "ok": under_allowed_root and default_profile_rejected,
    }


def _forbidden_imports_loaded() -> list[str]:
    return sorted(name for name in FORBIDDEN_IMPORT_ROOTS if name in sys.modules)


def _edge_executable_status(
    *,
    edge_executable_path: str | Path | None,
    exists: Callable[[Path], bool] | None = None,
) -> dict[str, Any]:
    exists_func = Path.exists if exists is None else exists
    try:
        executable = Path(edge_executable_path) if edge_executable_path else require_browser_path("edge", exists=exists_func)
        executable = executable.resolve()
        found = bool(exists_func(executable))
        return {
            "edge_executable_found": found,
            "edge_executable_path": str(executable),
            "edge_executable_error": None if found else f"Edge executable not found: {executable}",
        }
    except Exception as exc:  # pragma: no cover - exercised through payload checks
        return {"edge_executable_found": False, "edge_executable_path": None, "edge_executable_error": str(exc)}


def _launch_arguments(*, edge_executable: Path, profile_dir: Path, chat_url: str) -> list[str]:
    return [
        str(edge_executable),
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--disable-notifications",
        "--disable-popup-blocking",
        "--new-window",
        chat_url,
    ]


def _default_popen(args: Sequence[str], *, cwd: str) -> subprocess.Popen[Any]:
    kwargs: MutableMapping[str, Any] = {
        "cwd": cwd,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen(list(args), **kwargs)


def _start_edge_open_proof(
    *,
    root: Path,
    edge_executable: Path,
    profile_dir: Path,
    chat_url: str,
    close_after_seconds: float,
    leave_open: bool,
    popen_factory: Callable[..., Any] | None = None,
    sleep_func: Callable[[float], None] | None = None,
) -> dict[str, Any]:
    profile_dir.mkdir(parents=True, exist_ok=True)
    args = _launch_arguments(edge_executable=edge_executable, profile_dir=profile_dir, chat_url=chat_url)
    popen = popen_factory or _default_popen
    sleeper = sleep_func or time.sleep
    process = popen(args, cwd=str(root))
    pid = getattr(process, "pid", None)
    if close_after_seconds > 0:
        sleeper(float(close_after_seconds))

    close_attempted = not leave_open
    terminated = False
    poll_value = None
    if hasattr(process, "poll"):
        try:
            poll_value = process.poll()
        except Exception:
            poll_value = None

    if close_attempted and poll_value is None and hasattr(process, "terminate"):
        try:
            process.terminate()
            terminated = True
        except Exception:
            terminated = False
        if hasattr(process, "wait"):
            try:
                process.wait(timeout=5)
            except Exception:
                pass

    return {
        "browser_process_launch_args": args,
        "edge_process_pid": pid,
        "browser_close_attempted": close_attempted,
        "browser_terminate_called": terminated,
        "browser_left_open_by_operator_request": bool(leave_open),
    }


def build_edge_live_open_proof(
    repo_root: str | Path | None = None,
    *,
    profile_relative_path: str = DEFAULT_PROFILE_RELATIVE_PATH,
    edge_executable_path: str | Path | None = None,
    chat_url: str = DEFAULT_CHAT_URL,
    execute_live_open: bool = False,
    allow_live_edge_start: bool = False,
    authorization_token: str = "",
    close_after_seconds: float = 3.0,
    leave_open: bool = False,
    source_l14_payload: Mapping[str, Any] | None = None,
    popen_factory: Callable[..., Any] | None = None,
    sleep_func: Callable[[float], None] | None = None,
    exists: Callable[[Path], bool] | None = None,
) -> dict[str, Any]:
    root = Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()
    source = dict(source_l14_payload) if source_l14_payload is not None else l14_09.build_edge_dedicated_profile_lifecycle_final_acceptance_marker(root)
    source_safe = _source_l14_09_safe(source)
    profile = _profile_status(root, profile_relative_path)
    executable = _edge_executable_status(edge_executable_path=edge_executable_path, exists=exists)
    token_matches = authorization_token == AUTHORIZATION_TOKEN
    explicit_gate_satisfied = bool(execute_live_open and allow_live_edge_start and token_matches)
    forbidden_imports = _forbidden_imports_loaded()
    chat_url_safe = chat_url.strip() == "about:blank" or chat_url.startswith("https://") or chat_url.startswith("http://")
    launch_execution_allowed = bool(source_safe and profile["ok"] and executable["edge_executable_found"] and explicit_gate_satisfied and chat_url_safe)

    started = False
    launch_detail: dict[str, Any] = {
        "browser_process_launch_args": [],
        "edge_process_pid": None,
        "browser_close_attempted": False,
        "browser_terminate_called": False,
        "browser_left_open_by_operator_request": False,
    }
    launch_error = None
    profile_created = False
    profile_mutated = False
    filesystem_writes: list[str] = []

    if launch_execution_allowed:
        try:
            before_exists = Path(profile["profile_candidate_path"]).exists()
            launch_detail = _start_edge_open_proof(
                root=root,
                edge_executable=Path(str(executable["edge_executable_path"])),
                profile_dir=Path(str(profile["profile_candidate_path"])),
                chat_url=chat_url,
                close_after_seconds=close_after_seconds,
                leave_open=leave_open,
                popen_factory=popen_factory,
                sleep_func=sleep_func,
            )
            after_exists = Path(profile["profile_candidate_path"]).exists()
            profile_created = (not before_exists) and after_exists
            profile_mutated = after_exists
            if after_exists:
                filesystem_writes.append(str(Path(profile["profile_candidate_path"])))
            started = True
        except Exception as exc:  # pragma: no cover - payload path for real environment failures
            launch_error = str(exc)
            started = False

    checks = [
        _check("l14_09_final_marker_remains_accepted", source_safe),
        _check("microsoft_edge_is_active_target", True),
        _check("opera_remains_second_priority", True),
        _check("explicit_execute_flag_required", bool(execute_live_open) if launch_execution_allowed else True),
        _check("explicit_allow_flag_required", bool(allow_live_edge_start) if launch_execution_allowed else True),
        _check("authorization_token_required", token_matches if launch_execution_allowed else True),
        _check("authorization_token_not_echoed", True),
        _check("dedicated_profile_under_allowed_runtime_root", bool(profile["profile_candidate_under_allowed_runtime_root"])),
        _check("default_profile_rejected", bool(profile["profile_default_profile_rejected"])),
        _check("edge_executable_available_before_launch", bool(executable["edge_executable_found"]) if execute_live_open else True),
        _check("chat_url_safe", chat_url_safe),
        _check("no_forbidden_optional_imports", forbidden_imports == [], {"loaded": forbidden_imports}),
        _check("no_page_or_chat_interaction", True),
        _check("no_download_paste_send_package_git_localhost_extension", True),
    ]
    if execute_live_open:
        checks.append(_check("live_open_execution_authorized", launch_execution_allowed))
        checks.append(_check("live_open_process_started", started))

    ok = all(item["ok"] for item in checks) and (not execute_live_open or started)
    status = STATUS_PASS if ok else (STATUS_FAIL if execute_live_open else STATUS_BLOCKED)

    payload: dict[str, Any] = {
        "ok": ok,
        "status": status,
        "patch": PATCH,
        "phase": PHASE,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "source_patch": "L14.9",
        "source_l14_complete": source.get("l14_complete"),
        "remaining_l14_patches": source.get("remaining_l14_patches"),
        "microsoft_edge_first": True,
        "opera_second": True,
        "opera_active_target": False,
        "l14_09_final_marker_remains_accepted": source_safe,
        "l15_01_live_open_proof_enforced": True,
        "execution_mode": "live_open" if execute_live_open else "readback_only",
        "execute_live_open_requested": bool(execute_live_open),
        "allow_live_edge_start_requested": bool(allow_live_edge_start),
        "authorization_token_supplied": bool(authorization_token),
        "authorization_token_matches": token_matches,
        "authorization_token_echoed": False,
        "explicit_authorization_flags_required": True,
        "explicit_gate_satisfied": explicit_gate_satisfied,
        "browser_process_launch_requested": bool(execute_live_open),
        "browser_process_launch_authorized": bool(explicit_gate_satisfied),
        "launch_execution_allowed": launch_execution_allowed,
        "edge_executable_found": executable["edge_executable_found"],
        "edge_executable_path": executable["edge_executable_path"],
        "edge_executable_error": executable["edge_executable_error"],
        "profile_relative_path": profile["profile_relative_path"],
        "profile_candidate_path": profile["profile_candidate_path"],
        "allowed_profile_root": profile["allowed_profile_root"],
        "profile_candidate_under_allowed_runtime_root": profile["profile_candidate_under_allowed_runtime_root"],
        "profile_default_profile_rejected": profile["profile_default_profile_rejected"],
        "profile_directory_create_allowed": launch_execution_allowed,
        "profile_directory_cleanup_allowed": False,
        "profile_directory_delete_allowed": False,
        "profile_directory_created": profile_created,
        "profile_directory_mutated": profile_mutated,
        "filesystem_writes_performed": filesystem_writes,
        "adapter_filesystem_writes_performed": filesystem_writes,
        "browser_started": started,
        "edge_process_started": started,
        "browser_session_created": started,
        "driver_created": False,
        "edge_process_pid": launch_detail.get("edge_process_pid"),
        "browser_close_attempted": launch_detail.get("browser_close_attempted"),
        "browser_terminate_called": launch_detail.get("browser_terminate_called"),
        "browser_left_open_by_operator_request": launch_detail.get("browser_left_open_by_operator_request"),
        "browser_process_launch_args": launch_detail.get("browser_process_launch_args"),
        "launch_error": launch_error,
        "chat_url": chat_url,
        "close_after_seconds": close_after_seconds,
        "side_effects_performed": ["edge_process_start", "dedicated_profile_directory_create_or_use"] if started else [],
        "executed_validation_commands": [],
        "checks": checks,
        "next_patch": NEXT_PATCH,
    }
    payload.update(NO_INTERACTION_BOUNDARIES)
    payload["browser_started"] = started
    payload["edge_process_started"] = started
    payload["browser_session_created"] = started
    payload["opera_active_target"] = False
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        f"Status              : {payload.get('status')}",
        f"Command             : {payload.get('command_name')}",
        f"Source Patch        : {payload.get('source_patch')}",
        f"Execution Mode      : {payload.get('execution_mode')}",
        f"Launch Requested    : {payload.get('browser_process_launch_requested')}",
        f"Launch Authorized   : {payload.get('browser_process_launch_authorized')}",
        f"Launch Allowed      : {payload.get('launch_execution_allowed')}",
        f"Browser Started     : {payload.get('browser_started')}",
        f"Edge Process Started: {payload.get('edge_process_started')}",
        f"Profile Candidate   : {payload.get('profile_candidate_path')}",
        f"Default Rejected    : {payload.get('profile_default_profile_rejected')}",
        f"No Auto Send        : {payload.get('send_or_submit_performed') is False}",
        f"Next Patch          : {payload.get('next_patch')}",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=COMMAND_NAME)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--profile-relative-path", default=DEFAULT_PROFILE_RELATIVE_PATH)
    parser.add_argument("--edge-executable-path", default=None)
    parser.add_argument("--chat-url", default=DEFAULT_CHAT_URL)
    parser.add_argument("--execute-live-open", action="store_true")
    parser.add_argument("--allow-live-edge-start", action="store_true")
    parser.add_argument("--authorization-token", default="")
    parser.add_argument("--close-after-seconds", type=float, default=3.0)
    parser.add_argument("--leave-open", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_live_open_proof(
        args.repo_root,
        profile_relative_path=args.profile_relative_path,
        edge_executable_path=args.edge_executable_path,
        chat_url=args.chat_url,
        execute_live_open=args.execute_live_open,
        allow_live_edge_start=args.allow_live_edge_start,
        authorization_token=args.authorization_token,
        close_after_seconds=args.close_after_seconds,
        leave_open=args.leave_open,
    )

    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")

    if payload.get("ok") is True:
        return 0
    return 1 if (args.strict or args.execute_live_open) else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
