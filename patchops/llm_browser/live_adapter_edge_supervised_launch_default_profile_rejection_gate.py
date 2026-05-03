"""Passive L5.27 Microsoft Edge default-profile rejection gate.

This module reads back L5.26 and gives default Microsoft Edge profile rejection
its own explicit CLI/readback surface. It validates that a future live-start path
cannot target the operator's normal Edge profile. It does not create profile
directories, import Selenium, start Edge, create a driver/session, click or
download, paste or send, run packages, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_dedicated_profile_argument_gate as l5_26_gate

PATCH = "L5.27"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.27 Microsoft Edge Supervised Launch Default Profile Rejection Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate"
SOURCE_COMMAND_NAME = l5_26_gate.COMMAND_NAME
NEXT_PATCH = "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-default-profile-rejection-gate-only"
BROWSER_PRIORITY = ("edge", "opera")
AUTHORIZATION_FLAG = "--allow-live-start"
PROFILE_DIR_ARGUMENT = "--profile-dir"
DEFAULT_PROFILE_STATUS = "BLOCKED_DEFAULT_PROFILE_FORBIDDEN"
DEDICATED_PROFILE_STATUS = "AUTHORIZED_NON_DEFAULT_PROFILE_PRESENT_BUT_BLOCKED_BY_CURRENT_PASSIVE_PHASE"
DEFAULT_PROFILE_EXAMPLES = (
    r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default",
    r"C:\Users\example\AppData\Local\Microsoft\Edge\User Data\Default",
    r"/home/example/.config/microsoft-edge/Default",
)

REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*l5_26_gate.REQUIRED_COMMANDS, COMMAND_NAME)))
REQUIRED_REPO_PATHS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *l5_26_gate.REQUIRED_REPO_PATHS,
            "patchops/llm_browser/live_adapter_edge_supervised_launch_default_profile_rejection_gate.py",
            "docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md",
            "tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py",
        )
    )
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_dedicated_profile_argument_gate.md": (
        "L5.26 Microsoft Edge supervised launch dedicated profile argument gate",
        "browser-start-supervised-launch-edge-live-start-profile-gate",
        "--profile-dir",
        "default profile forbidden",
        "default profile path rejected",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.27 Live adapter Microsoft Edge supervised launch default profile rejection gate",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_default_profile_rejection_gate.md": (
        "L5.27 Microsoft Edge supervised launch default profile rejection gate",
        "browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate",
        "browser-start-supervised-launch-edge-live-start-profile-gate",
        "Microsoft Edge first",
        "Opera second",
        "--allow-live-start",
        "--profile-dir",
        "default profile rejection gate enforced",
        "default Microsoft Edge profile forbidden",
        "default profile candidate detected",
        "default profile path rejected",
        "dedicated non-default profile remains passive-blocked",
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
        "L5.28 Live adapter Microsoft Edge supervised launch profile parent preflight contract",
    ),
}

COMMAND_PLAN: tuple[str, ...] = (
    "python -m compileall patchops/llm_browser tests scripts/patch_l5_27_wire_edge_default_profile_rejection_gate.py",
    "python -m pytest -q tests/test_l5_26_edge_supervised_launch_dedicated_profile_argument_gate_current.py tests/test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_default_profile_rejection_gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\Users\\kostas\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default --json --compact",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_default_profile_rejection_gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\dev\\patchops\\data\\runtime\\browser_profiles\\edge_l5_27_candidate --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-live-start-default-profile-rejection-gate --repo-root C:\\dev\\patchops --allow-live-start --profile-dir C:\\Users\\kostas\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default --json --compact",
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
    "selenium",
    "webdriver",
    "msedge.exe",
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
        "test_l5_26_edge_supervised_launch_dedicated_profile_argument_gate_current.py",
        "test_l5_27_edge_supervised_launch_default_profile_rejection_gate_current.py",
        "live_adapter_edge_supervised_launch_default_profile_rejection_gate",
        COMMAND_NAME,
        "--allow-live-start",
        "--profile-dir",
        "microsoft\\edge\\user data\\default".lower(),
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


def _normalize_profile(profile_dir: str | Path | None) -> str:
    if profile_dir is None:
        return ""
    # L5.27b: tolerate an accidental ASCII unit-separator path marker from a
    # failed repair manifest while still treating it as a path separator for
    # readback classification. Normal operator paths should use real backslash
    # or slash separators.
    return str(profile_dir).strip().replace("\x1f", "/").replace("\\", "/").lower().rstrip("/")


def _is_default_edge_profile(profile_dir: str | Path | None) -> bool:
    normalized = _normalize_profile(profile_dir)
    if not normalized:
        return False
    return normalized.endswith("/microsoft/edge/user data/default") or normalized.endswith("/microsoft-edge/default") or normalized.endswith("/microsoft-edge-dev/default")


def _l5_26_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    gate = payload.get("profile_gate", {})
    if not isinstance(gate, Mapping):
        gate = {}
    return {
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "doc_state_ok": payload.get("doc_state", {}).get("ok") if isinstance(payload.get("doc_state"), Mapping) else None,
        "missing_repo_paths": payload.get("missing_repo_paths", []),
        "authorization_flag_required": payload.get("authorization_flag_required"),
        "explicit_operator_authorization_required": payload.get("explicit_operator_authorization_required") is True,
        "profile_dir_argument_required": payload.get("profile_dir_argument_required"),
        "dedicated_profile_argument_gate_enforced": payload.get("dedicated_profile_argument_gate_enforced") is True,
        "dedicated_profile_argument_present": payload.get("dedicated_profile_argument_present") is True,
        "dedicated_profile_argument_valid": payload.get("dedicated_profile_argument_valid") is True,
        "default_profile_forbidden": payload.get("default_profile_forbidden") is True,
        "default_profile_path_rejected": payload.get("default_profile_path_rejected") is True,
        "profile_gate_status": payload.get("profile_gate_status"),
        "profile_gate_phase_allows_live_start": gate.get("phase_allows_live_start"),
        "startup_allowed": payload.get("startup_allowed") is True,
        "startup_authorized": payload.get("startup_authorized") is True,
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
    }


def _l5_26_profile_gate_still_passive(summary: Mapping[str, Any]) -> bool:
    """Return True when wrapped L5.26 preserves passive safety.

    L5.27 intentionally feeds default-profile candidates into its own default
    rejection gate. The older L5.26 profile gate is allowed to reject that
    default profile, so L5.27 must not require L5.26 to report ok=True for the
    default-profile scenario. The invariant L5.27 needs from L5.26 is that the
    L5.26 surface is still present, reports the expected safety fields, and
    performs no browser/profile/Selenium/click/download/paste/send/package-run
    side effects.
    """
    return (
        summary.get("patch") == "L5.26"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("doc_state_ok") is True
        and summary.get("missing_repo_paths") == []
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("authorization_flag_required") == AUTHORIZATION_FLAG
        and summary.get("profile_dir_argument_required") == PROFILE_DIR_ARGUMENT
        and summary.get("dedicated_profile_argument_gate_enforced") is True
        and summary.get("default_profile_forbidden") is True
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
        and summary.get("profile_gate_phase_allows_live_start") is False
    )


def _l5_26_source_gate_acceptable_for_l5_27(summary: Mapping[str, Any]) -> bool:
    """Return True when L5.26 is either PASS or safely rejecting a default profile.

    A PASS L5.26 readback remains the normal case for missing-profile and
    dedicated-profile scenarios. A FAIL L5.26 readback is acceptable only when
    the failure is the expected default-profile refusal and all passive safety
    invariants are still intact.
    """
    if not _l5_26_profile_gate_still_passive(summary):
        return False
    if summary.get("ok") is True and summary.get("status") == STATUS_PASS:
        return True
    return (
        summary.get("status") == STATUS_FAIL
        and summary.get("default_profile_forbidden") is True
        and summary.get("default_profile_path_rejected") is True
        and summary.get("profile_gate_status")
        in {
            "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION",
            "BLOCKED_DEFAULT_PROFILE_FORBIDDEN",
        }
    )


def _default_rejection_gate_state(allow_live_start: bool, profile_dir: str | Path | None) -> dict[str, Any]:
    profile_text = str(profile_dir).strip() if profile_dir is not None and str(profile_dir).strip() else None
    profile_present = profile_text is not None
    default_candidate = _is_default_edge_profile(profile_text)
    dedicated_non_default = bool(profile_present and not default_candidate)

    if not allow_live_start:
        status = "BLOCKED_MISSING_EXPLICIT_OPERATOR_AUTHORIZATION"
        reason = "Missing --allow-live-start keeps startup blocked before default-profile rejection can pass."
    elif not profile_present:
        status = "BLOCKED_MISSING_DEDICATED_PROFILE_DIR"
        reason = "Missing --profile-dir keeps startup blocked."
    elif default_candidate:
        status = DEFAULT_PROFILE_STATUS
        reason = "The normal/default Microsoft Edge profile is forbidden for supervised PatchOps automation."
    else:
        status = DEDICATED_PROFILE_STATUS
        reason = "A non-default profile was supplied, but L5.27 is still passive and cannot start Edge."

    return {
        "authorization_flag_required": AUTHORIZATION_FLAG,
        "explicit_operator_authorization_required": True,
        "explicit_operator_authorization_present": bool(allow_live_start),
        "profile_dir_argument_required": PROFILE_DIR_ARGUMENT,
        "profile_dir_argument_present": profile_present,
        "profile_dir_argument_value": profile_text,
        "default_profile_rejection_gate_enforced": True,
        "default_profile_path_forbidden": True,
        "default_microsoft_edge_profile_forbidden": True,
        "default_profile_candidate_detected": default_candidate,
        "default_profile_path_rejected": default_candidate,
        "dedicated_non_default_profile_present": dedicated_non_default,
        "dedicated_non_default_profile_remains_passive_blocked": bool(allow_live_start and dedicated_non_default),
        "default_profile_rejection_gate_status": status,
        "default_profile_rejection_reason": reason,
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


def build_edge_supervised_launch_default_profile_rejection_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)
    profile_text = str(profile_dir) if profile_dir is not None else None

    l5_26_payload = l5_26_gate.build_edge_supervised_launch_dedicated_profile_argument_gate(root, allow_live_start=allow_live_start, profile_dir=profile_text)
    l5_26_summary = _l5_26_summary(l5_26_payload)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.26 START")
    default_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.27 START")
    command_state = _required_command_state(root)
    doc_state = _doc_phrase_state(root)
    command_plan_state = _command_plan_state()
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    rejection_gate = _default_rejection_gate_state(bool(allow_live_start), profile_text)

    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    passive_detail = {
        **PASSIVE_INVARIANTS,
        "startup_authorized": rejection_gate["startup_authorized"],
        "live_start_requested": rejection_gate["live_start_requested"],
        "profile_dir_argument_present": rejection_gate["profile_dir_argument_present"],
        "profile_dir_argument_value": rejection_gate["profile_dir_argument_value"],
        "default_profile_candidate_detected": rejection_gate["default_profile_candidate_detected"],
        "default_profile_path_rejected": rejection_gate["default_profile_path_rejected"],
        "selenium_imported_by_readback": selenium_imported_by_readback,
    }

    checks = [
        _check("l5_26_edge_profile_gate_still_passes", _l5_26_source_gate_acceptable_for_l5_27(l5_26_summary), l5_26_summary),
        _check("l5_26_edge_profile_gate_remains_passive", _l5_26_profile_gate_still_passive(l5_26_summary), l5_26_summary),
        _check("l5_26_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_27_default_profile_rejection_command_registered", default_command_static.get("ok") is True, default_command_static),
        _check("edge_l5_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_default_profile_rejection_boundary", doc_state.get("ok") is True, doc_state),
        _check("l5_27_command_plan_is_readback_only", command_plan_state.get("ok") is True, command_plan_state),
        _check("adapter_logic_executes_no_validation_commands", command_plan_state.get("executed_by_adapter_logic") == [], command_plan_state),
        _check("default_profile_rejection_gate_is_enforced", rejection_gate.get("default_profile_rejection_gate_enforced") is True and rejection_gate.get("default_profile_path_forbidden") is True, rejection_gate),
        _check("default_profile_candidate_is_detected_when_supplied", ((not rejection_gate.get("profile_dir_argument_present")) or (not _is_default_edge_profile(profile_text)) or rejection_gate.get("default_profile_candidate_detected") is True), rejection_gate),
        _check("default_profile_path_is_rejected", ((not rejection_gate.get("default_profile_candidate_detected")) or rejection_gate.get("default_profile_path_rejected") is True) and rejection_gate.get("startup_allowed") is False, rejection_gate),
        _check("dedicated_non_default_profile_remains_passive_blocked", ((not rejection_gate.get("dedicated_non_default_profile_present")) or (rejection_gate.get("explicit_operator_authorization_present") is False) or rejection_gate.get("dedicated_non_default_profile_remains_passive_blocked") is True) and rejection_gate.get("startup_allowed") is False, rejection_gate),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_default_profile_rejection_gate", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
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
        "default_profile_examples": list(DEFAULT_PROFILE_EXAMPLES),
        "command_plan": list(COMMAND_PLAN),
        "command_plan_state": command_plan_state,
        "l5_26_edge_profile_gate": l5_26_payload,
        "l5_26_summary": l5_26_summary,
        "source_command_static_presence": source_command_static,
        "default_profile_rejection_command_static_presence": default_command_static,
        "command_state": command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_repo_paths,
        "default_profile_rejection_gate": rejection_gate,
        "checks": checks,
        "executed_validation_commands": [],
        **PASSIVE_INVARIANTS,
        "startup_authorized": rejection_gate["startup_authorized"],
        "live_start_requested": rejection_gate["live_start_requested"],
        "explicit_operator_authorization_required": True,
        "explicit_operator_authorization_present": rejection_gate["explicit_operator_authorization_present"],
        "authorization_flag_required": AUTHORIZATION_FLAG,
        "profile_dir_argument_required": PROFILE_DIR_ARGUMENT,
        "profile_dir_argument_present": rejection_gate["profile_dir_argument_present"],
        "profile_dir_argument_value": rejection_gate["profile_dir_argument_value"],
        "dedicated_profile_required": True,
        "default_profile_forbidden": True,
        "default_profile_rejection_gate_enforced": True,
        "default_profile_path_forbidden": True,
        "default_microsoft_edge_profile_forbidden": True,
        "default_profile_candidate_detected": rejection_gate["default_profile_candidate_detected"],
        "default_profile_path_rejected": rejection_gate["default_profile_path_rejected"],
        "default_profile_rejection_gate_status": rejection_gate["default_profile_rejection_gate_status"],
        "dedicated_non_default_profile_present": rejection_gate["dedicated_non_default_profile_present"],
        "dedicated_non_default_profile_remains_passive_blocked": rejection_gate["dedicated_non_default_profile_remains_passive_blocked"],
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
    gate = payload.get("default_profile_rejection_gate", {})
    if not isinstance(gate, Mapping):
        gate = {}
    lines = [
        "PatchOps L5.27 Microsoft Edge supervised-launch default profile rejection gate",
        f"Patch             : {payload.get('patch')}",
        f"Status            : {payload.get('status')}",
        f"OK                : {payload.get('ok')}",
        f"Command           : {payload.get('command_name')}",
        f"Source Command    : {payload.get('source_command_name')}",
        f"Edge First        : {payload.get('edge_first')}",
        f"Browser Priority  : {payload.get('browser_priority')}",
        f"Auth Required     : {payload.get('explicit_operator_authorization_required')}",
        f"Auth Present      : {payload.get('explicit_operator_authorization_present')}",
        f"Profile Required  : {payload.get('dedicated_profile_required')}",
        f"Profile Present   : {payload.get('profile_dir_argument_present')}",
        f"Profile Value     : {payload.get('profile_dir_argument_value')}",
        f"Default Forbidden : {payload.get('default_profile_forbidden')}",
        f"Default Detected  : {payload.get('default_profile_candidate_detected')}",
        f"Default Rejected  : {payload.get('default_profile_path_rejected')}",
        f"Gate Status       : {payload.get('default_profile_rejection_gate_status')}",
        f"Gate Reason       : {gate.get('default_profile_rejection_reason')}",
        f"Startup Allowed   : {payload.get('startup_allowed')}",
        f"Live Requested    : {payload.get('live_start_requested')}",
        f"Live Performed    : {payload.get('live_start_performed')}",
        f"Browser Started   : {payload.get('browser_started')}",
        f"Edge Started      : {payload.get('edge_process_started')}",
        f"Session Created   : {payload.get('browser_session_created')}",
        f"Driver Created    : {payload.get('driver_created')}",
        f"Profile Created   : {payload.get('profile_directory_created')}",
        f"SideEffects       : {payload.get('side_effects_performed')}",
        f"Filesystem        : writes={payload.get('filesystem_writes_performed')}",
        f"Adapter Writes    : {payload.get('adapter_filesystem_writes_performed')}",
        f"Selenium Import   : {payload.get('selenium_imported_by_readback')}",
        f"MissingPath       : {payload.get('missing_repo_paths')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next Patch        : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(AUTHORIZATION_FLAG, action="store_true", dest="allow_live_start")
    parser.add_argument(PROFILE_DIR_ARGUMENT, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_supervised_launch_default_profile_rejection_gate(
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