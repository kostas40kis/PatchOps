"""Passive L5.26 Microsoft Edge dedicated profile argument gate.

This module reads back L5.25 and adds the dedicated ``--profile-dir`` argument
gate that future live-start code must satisfy before Microsoft Edge can be
started. It validates argument semantics only. It does not create the profile
directory, import Selenium, start Edge, create a driver/session, click/download,
paste/send, run packages, or perform git operations.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_explicit_authorization_argument_gate as l5_25_gate

PATCH = "L5.26"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.26 Microsoft Edge Supervised Launch Dedicated Profile Argument Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-profile-gate"
SOURCE_COMMAND_NAME = l5_25_gate.COMMAND_NAME
NEXT_PATCH = "L5.27 Live adapter Microsoft Edge supervised launch default profile rejection gate"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-dedicated-profile-argument-gate-only"
BROWSER_PRIORITY = ("edge", "opera")
AUTHORIZATION_FLAG = "--allow-live-start"
PROFILE_DIR_ARGUMENT = "--profile-dir"
DEFAULT_PROFILE_MARKERS = (
    "microsoft/edge/user data/default",
    "microsoft\\edge\\user data\\default",
    "/edge/user data/default",
    "\\edge\\user data\\default",
)

REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*l5_25_gate.REQUIRED_COMMANDS, COMMAND_NAME)))

REQUIRED_REPO_PATHS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *l5_25_gate.REQUIRED_REPO_PATHS,
            "patchops/llm_browser/live_adapter_edge_supervised_launch_dedicated_profile_argument_gate.py",
            "docs/llm_browser_live_adapter_edge_supervised_launch_dedicated_profile_argument_gate.md",
            "tests/test_l5_26_edge_supervised_launch_dedicated_profile_argument_gate_current.py",
        )
    )
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_explicit_authorization_argument_gate.md": (
        "L5.25 Microsoft Edge supervised launch explicit authorization argument gate",
        "browser-start-supervised-launch-edge-live-start-authorization-gate",
        "--allow-live-start",
        "explicit operator authorization required",
        "authorization missing keeps startup blocked",
        "authorization present is still blocked by the current passive phase",
        "dedicated profile required",
        "default profile forbidden",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.26 Live adapter Microsoft Edge supervised launch dedicated profile argument gate",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_dedicated_profile_argument_gate.md": (
        "L5.26 Microsoft Edge supervised launch dedicated profile argument gate",
        "browser-start-supervised-launch-edge-live-start-profile-gate",
        "browser-start-supervised-launch-edge-live-start-authorization-gate",
        "Microsoft Edge first",
        "Opera second",
        "--allow-live-start",
        "--profile-dir",
        "dedicated profile argument required",
        "dedicated profile argument present",
        "missing profile keeps startup blocked",
        "default profile forbidden",
        "default profile path rejected",
        "dedicated profile present is still blocked by the current passive phase",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.27 Live adapter Microsoft Edge supervised launch default profile rejection gate",
    ),
}

COMMAND_PLAN: tuple[str, ...] = (
    "python -m compileall patchops/llm_browser tests scripts/patch_l5_26_wire_edge_profile_gate.py",
    "python -m pytest -q tests/test_l5_25_edge_supervised_launch_explicit_authorization_argument_gate_current.py tests/test_l5_26_edge_supervised_launch_dedicated_profile_argument_gate_current.py",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_dedicated_profile_argument_gate --repo-root C:\\dev\\patchops --json --compact",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_dedicated_profile_argument_gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_26_candidate --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-profile-gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_26_candidate --json --compact",
    "git status --short --branch",
)

PASSIVE_INVARIANTS: Mapping[str, Any] = {
    "startup_allowed": False,
    "live_start_performed": False,
    "browser_started": False,
    "edge_process_started": False,
    "browser_session_created": False,
    "driver_created": False,
    "profile_directory_created": False,
    "adapter_filesystem_writes_performed": [],
    "filesystem_writes_performed": [],
    "side_effects_performed": [],
    "click_download_performed": False,
    "download_performed": False,
    "paste_performed": False,
    "send_or_submit_performed": False,
    "package_run_performed_by_adapter": False,
    "git_commit_executed": False,
    "git_push_executed": False,
    "optional_browser_dependencies_required": False,
    "selenium_required": False,
    "selenium_imported_by_readback": False,
}

FORBIDDEN_PLAN_TOKENS: tuple[str, ...] = (
    "msedge.exe",
    "selenium",
    "webdriver",
    "click-download",
    "paste-to-composer",
    "send-message",
    "run-package-from-adapter",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()


def _missing_paths(root: Path, rel_paths: Iterable[str]) -> list[str]:
    return [rel for rel in rel_paths if not (root / rel).exists()]


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _json_safe(value: object) -> bool:
    try:
        json.dumps(value, sort_keys=True)
        return True
    except TypeError:
        return False


def _command_static_presence(root: Path, command_name: str, sentinel: str | None = None) -> dict[str, Any]:
    commands_path = root / "patchops" / "llm_browser" / "commands.py"
    if not commands_path.exists():
        return {"ok": False, "commands_path": str(commands_path), "reason": "commands.py missing", "command_name": command_name}
    text = commands_path.read_text(encoding="utf-8", errors="replace")
    payload: dict[str, Any] = {"ok": command_name in text, "commands_path": str(commands_path), "command_name": command_name}
    if sentinel is not None:
        payload["sentinel_present"] = sentinel in text
        payload["ok"] = bool(payload["ok"] and payload["sentinel_present"])
    return payload


def _required_command_state(root: Path) -> dict[str, Any]:
    command_states = {command: _command_static_presence(root, command) for command in REQUIRED_COMMANDS}
    missing_commands = [command for command, state in command_states.items() if state.get("ok") is not True]
    return {"ok": not missing_commands, "missing_commands": missing_commands, "command_states": command_states}


def _doc_phrase_state(root: Path) -> dict[str, Any]:
    state: dict[str, Any] = {}
    missing_docs: list[str] = []
    missing_phrases: dict[str, list[str]] = {}
    for rel, phrases in DOC_REQUIREMENTS.items():
        path = root / rel
        if not path.exists():
            missing_docs.append(rel)
            state[rel] = {"exists": False, "missing_phrases": list(phrases)}
            missing_phrases[rel] = list(phrases)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [phrase for phrase in phrases if phrase not in text]
        state[rel] = {"exists": True, "missing_phrases": missing}
        if missing:
            missing_phrases[rel] = missing
    return {"ok": not missing_docs and not missing_phrases, "missing_docs": missing_docs, "missing_phrases": missing_phrases, "doc_state": state}


def _command_plan_state() -> dict[str, Any]:
    plan = list(COMMAND_PLAN)
    joined = "\n".join(plan).lower()
    forbidden_present = [token for token in FORBIDDEN_PLAN_TOKENS if token.lower() in joined]
    expected_fragments = [
        "compileall patchops/llm_browser tests",
        "pytest -q",
        "test_l5_25_edge_supervised_launch_explicit_authorization_argument_gate_current.py",
        "test_l5_26_edge_supervised_launch_dedicated_profile_argument_gate_current.py",
        "live_adapter_edge_supervised_launch_dedicated_profile_argument_gate",
        COMMAND_NAME,
        "--allow-live-start",
        "--profile-dir",
        "git status --short --branch",
    ]
    missing_fragments = [fragment for fragment in expected_fragments if fragment not in joined]
    return {
        "ok": not forbidden_present and not missing_fragments and len(plan) == 6,
        "planned_commands": plan,
        "forbidden_present": forbidden_present,
        "missing_fragments": missing_fragments,
        "executed_by_adapter_logic": [],
    }


def _l5_25_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    gate = payload.get("authorization_gate", {})
    if not isinstance(gate, Mapping):
        gate = {}
    return {
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "source_command_name": payload.get("source_command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "doc_state_ok": payload.get("doc_state", {}).get("ok") if isinstance(payload.get("doc_state"), Mapping) else None,
        "missing_repo_paths": payload.get("missing_repo_paths", []),
        "explicit_operator_authorization_required": payload.get("explicit_operator_authorization_required") is True,
        "explicit_operator_authorization_present": payload.get("explicit_operator_authorization_present") is True,
        "authorization_flag_required": payload.get("authorization_flag_required"),
        "authorization_gate_status": payload.get("authorization_gate_status"),
        "profile_dir_argument_required": payload.get("profile_dir_argument_required"),
        "profile_dir_argument_present": payload.get("profile_dir_argument_present") is True,
        "dedicated_profile_required": payload.get("dedicated_profile_required") is True,
        "default_profile_forbidden": payload.get("default_profile_forbidden") is True,
        "manual_user_login_required": payload.get("manual_user_login_required") is True,
        "silent_auto_submit_default": payload.get("silent_auto_submit_default"),
        "localhost_patchops_server_required": payload.get("localhost_patchops_server_required"),
        "browser_extension_required": payload.get("browser_extension_required"),
        "startup_authorized": payload.get("startup_authorized") is True,
        "startup_allowed": payload.get("startup_allowed") is True,
        "live_start_requested": payload.get("live_start_requested") is True,
        "live_start_performed": payload.get("live_start_performed") is True,
        "browser_started": payload.get("browser_started") is True,
        "edge_process_started": payload.get("edge_process_started") is True,
        "browser_session_created": payload.get("browser_session_created") is True,
        "driver_created": payload.get("driver_created") is True,
        "profile_directory_created": payload.get("profile_directory_created") is True,
        "filesystem_writes_performed": payload.get("filesystem_writes_performed"),
        "adapter_filesystem_writes_performed": payload.get("adapter_filesystem_writes_performed"),
        "side_effects_performed": payload.get("side_effects_performed"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback") is True,
        "authorization_gate_phase_allows_live_start": gate.get("phase_allows_live_start"),
    }


def _l5_25_passive_ok(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.25"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("doc_state_ok") is True
        and summary.get("missing_repo_paths") == []
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("explicit_operator_authorization_required") is True
        and summary.get("authorization_flag_required") == AUTHORIZATION_FLAG
        and summary.get("profile_dir_argument_required") == PROFILE_DIR_ARGUMENT
        and summary.get("dedicated_profile_required") is True
        and summary.get("default_profile_forbidden") is True
        and summary.get("manual_user_login_required") is True
        and summary.get("silent_auto_submit_default") is False
        and summary.get("localhost_patchops_server_required") is False
        and summary.get("browser_extension_required") is False
        and summary.get("startup_allowed") is False
        and summary.get("live_start_performed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("authorization_gate_phase_allows_live_start") is False
    )


def _looks_like_default_profile(profile_dir: str | None) -> bool:
    if not profile_dir:
        return False
    normalized = profile_dir.strip().lower().replace("\\", "/")
    if normalized.endswith("/default") and "/microsoft/edge/user data/default" in normalized:
        return True
    return any(marker.replace("\\", "/") in normalized for marker in DEFAULT_PROFILE_MARKERS)


def _profile_gate_state(allow_live_start: bool, profile_dir: str | None) -> dict[str, Any]:
    present = bool(profile_dir and str(profile_dir).strip())
    default_profile = _looks_like_default_profile(profile_dir)
    dedicated_valid = present and not default_profile

    if not allow_live_start:
        gate_status = "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
        reason = "Missing --allow-live-start keeps startup blocked before the profile gate can pass."
    elif not present:
        gate_status = "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
        reason = "Missing --profile-dir keeps startup blocked."
    elif default_profile:
        gate_status = "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
        reason = "The default Microsoft Edge profile path is forbidden for supervised PatchOps automation."
    else:
        gate_status = "AUTHORIZED_PROFILE_PRESENT_BUT_BLOCKED_BY_CURRENT_PASSIVE_PHASE"
        reason = "Authorization and a dedicated profile argument were supplied, but L5.26 is still passive and cannot start Edge."

    return {
        "authorization_flag_required": AUTHORIZATION_FLAG,
        "explicit_operator_authorization_required": True,
        "explicit_operator_authorization_present": bool(allow_live_start),
        "profile_dir_argument_required": PROFILE_DIR_ARGUMENT,
        "dedicated_profile_argument_gate_enforced": True,
        "dedicated_profile_argument_required": True,
        "dedicated_profile_argument_present": present,
        "dedicated_profile_argument_value": str(profile_dir) if present else None,
        "dedicated_profile_argument_valid": dedicated_valid,
        "missing_profile_keeps_startup_blocked": bool(allow_live_start and not present),
        "default_profile_forbidden": True,
        "default_profile_path_rejected": bool(present and default_profile),
        "dedicated_profile_present_is_still_blocked_by_current_passive_phase": bool(allow_live_start and dedicated_valid),
        "profile_gate_status": gate_status,
        "profile_gate_refusal_reason": reason,
        "phase_allows_live_start": False,
        "startup_authorized": bool(allow_live_start),
        "startup_allowed": False,
        "live_start_requested": bool(allow_live_start),
        "live_start_performed": False,
        "profile_directory_created": False,
        "manual_user_login_required": True,
        "silent_auto_submit_default": False,
        "silent_auto_submit_must_remain_false": True,
        "localhost_patchops_server_required": False,
        "browser_extension_required": False,
    }


def build_edge_supervised_launch_dedicated_profile_argument_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    profile_dir_text = str(profile_dir) if profile_dir is not None else None

    l5_25_payload = l5_25_gate.build_edge_supervised_launch_explicit_authorization_argument_gate(root, allow_live_start=allow_live_start, profile_dir=profile_dir_text)
    l5_25_summary = _l5_25_summary(l5_25_payload)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.25 START")
    profile_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.26 START")
    command_state = _required_command_state(root)
    doc_state = _doc_phrase_state(root)
    command_plan_state = _command_plan_state()
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    profile_gate = _profile_gate_state(bool(allow_live_start), profile_dir_text)

    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    passive_detail = {
        **PASSIVE_INVARIANTS,
        "startup_authorized": profile_gate["startup_authorized"],
        "live_start_requested": profile_gate["live_start_requested"],
        "profile_dir_argument_present": profile_gate["dedicated_profile_argument_present"],
        "profile_dir_argument_value": profile_gate["dedicated_profile_argument_value"],
        "selenium_imported_by_readback": selenium_imported_by_readback,
    }

    checks = [
        _check("l5_25_edge_authorization_gate_still_passes", l5_25_summary.get("ok") is True and l5_25_summary.get("status") == STATUS_PASS, l5_25_summary),
        _check("l5_25_edge_authorization_gate_remains_passive", _l5_25_passive_ok(l5_25_summary), l5_25_summary),
        _check("l5_25_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_26_profile_gate_command_registered", profile_command_static.get("ok") is True, profile_command_static),
        _check("edge_l5_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_profile_gate_boundary", doc_state.get("ok") is True, doc_state),
        _check("l5_26_command_plan_is_readback_only", command_plan_state.get("ok") is True, command_plan_state),
        _check("adapter_logic_executes_no_validation_commands", command_plan_state.get("executed_by_adapter_logic") == [], command_plan_state),
        _check("dedicated_profile_argument_gate_is_enforced", profile_gate.get("dedicated_profile_argument_gate_enforced") is True and profile_gate.get("profile_dir_argument_required") == PROFILE_DIR_ARGUMENT, profile_gate),
        _check("missing_profile_blocks_startup_when_authorized", ((not allow_live_start) or profile_gate.get("dedicated_profile_argument_present") is True or profile_gate.get("missing_profile_keeps_startup_blocked") is True) and profile_gate.get("startup_allowed") is False, profile_gate),
        _check("default_profile_path_is_rejected", ((not profile_gate.get("default_profile_path_rejected")) or profile_gate.get("profile_gate_status") == "BLOCKED_DEFAULT_PROFILE_FORBIDDEN") and profile_gate.get("startup_allowed") is False, profile_gate),
        _check("dedicated_profile_present_still_cannot_start_edge_in_l5_26", ((not (allow_live_start and profile_gate.get("dedicated_profile_argument_valid"))) or profile_gate.get("dedicated_profile_present_is_still_blocked_by_current_passive_phase") is True) and profile_gate.get("startup_allowed") is False, profile_gate),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_profile_gate", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
        _check("no_browser_profile_or_adapter_side_effects", PASSIVE_INVARIANTS["browser_started"] is False and PASSIVE_INVARIANTS["profile_directory_created"] is False and PASSIVE_INVARIANTS["side_effects_performed"] == [], passive_detail),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "phase": PHASE,
        "patch": PATCH,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "repo_root": str(root),
        "required_commands": list(REQUIRED_COMMANDS),
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "doc_requirements": {key: list(value) for key, value in DOC_REQUIREMENTS.items()},
        "command_plan": list(COMMAND_PLAN),
        "command_plan_state": command_plan_state,
        "l5_25_edge_authorization_gate": l5_25_payload,
        "l5_25_summary": l5_25_summary,
        "source_command_static_presence": source_command_static,
        "profile_gate_command_static_presence": profile_command_static,
        "command_state": command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_repo_paths,
        "profile_gate": profile_gate,
        "checks": checks,
        "executed_validation_commands": [],
        **PASSIVE_INVARIANTS,
        "startup_authorized": profile_gate["startup_authorized"],
        "live_start_requested": profile_gate["live_start_requested"],
        "explicit_operator_authorization_required": True,
        "explicit_operator_authorization_present": profile_gate["explicit_operator_authorization_present"],
        "authorization_flag_required": AUTHORIZATION_FLAG,
        "profile_dir_argument_required": PROFILE_DIR_ARGUMENT,
        "profile_dir_argument_present": profile_gate["dedicated_profile_argument_present"],
        "profile_dir_argument_value": profile_gate["dedicated_profile_argument_value"],
        "dedicated_profile_argument_gate_enforced": True,
        "dedicated_profile_argument_required": True,
        "dedicated_profile_argument_present": profile_gate["dedicated_profile_argument_present"],
        "dedicated_profile_argument_valid": profile_gate["dedicated_profile_argument_valid"],
        "dedicated_profile_required": True,
        "default_profile_forbidden": True,
        "default_profile_path_rejected": profile_gate["default_profile_path_rejected"],
        "profile_gate_status": profile_gate["profile_gate_status"],
        "manual_user_login_required": True,
        "silent_auto_submit_default": False,
        "localhost_patchops_server_required": False,
        "browser_extension_required": False,
        "selenium_imported_by_readback": selenium_imported_by_readback,
    }
    payload["payload_json_safe"] = _json_safe(payload)
    if not payload["payload_json_safe"]:
        payload["ok"] = False
        payload["status"] = STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    gate = payload.get("profile_gate", {})
    if not isinstance(gate, Mapping):
        gate = {}
    lines = [
        "PatchOps L5.26 Microsoft Edge supervised-launch dedicated profile argument gate",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Browser Priority: {payload.get('browser_priority')}",
        f"Auth Required   : {payload.get('explicit_operator_authorization_required')}",
        f"Auth Present    : {payload.get('explicit_operator_authorization_present')}",
        f"Profile Required: {payload.get('dedicated_profile_argument_required')}",
        f"Profile Present : {payload.get('dedicated_profile_argument_present')}",
        f"Profile Valid   : {payload.get('dedicated_profile_argument_valid')}",
        f"Profile Value   : {payload.get('dedicated_profile_argument_present') and payload.get('profile_dir_argument_value')}",
        f"Default Rejected: {payload.get('default_profile_path_rejected')}",
        f"Gate Status     : {payload.get('profile_gate_status')}",
        f"Gate Reason     : {gate.get('profile_gate_refusal_reason')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Live Requested  : {payload.get('live_start_requested')}",
        f"Live Performed  : {payload.get('live_start_performed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Edge Started    : {payload.get('edge_process_started')}",
        f"Session Created : {payload.get('browser_session_created')}",
        f"Driver Created  : {payload.get('driver_created')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"SideEffects     : {payload.get('side_effects_performed')}",
        f"Filesystem      : writes={payload.get('filesystem_writes_performed')}",
        f"Adapter Writes  : {payload.get('adapter_filesystem_writes_performed')}",
        f"Selenium Import : {payload.get('selenium_imported_by_readback')}",
        f"MissingPath     : {payload.get('missing_repo_paths')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next Patch      : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(AUTHORIZATION_FLAG, action="store_true", dest="allow_live_start")
    parser.add_argument(PROFILE_DIR_ARGUMENT, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_supervised_launch_dedicated_profile_argument_gate(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
    )
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())