"""Passive L5.23 Microsoft Edge live-start preflight contract.

This module reads back the accepted L5.22 Microsoft Edge L5 broad-validation
CLI/readback checkpoint and defines the explicit preflight contract that must be
satisfied before a future patch may perform a real, user-visible Edge launch.

It remains fully passive: no Selenium import, no Edge process start, no browser
session, no driver, no profile directory creation, no click/download, no
paste/send, no package run, and no automatic git operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback as l5_22_readback

PATCH = "L5.23"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.23 Microsoft Edge Supervised Launch Live Start Preflight Contract"
COMMAND_NAME = "browser-start-supervised-launch-edge-live-start-preflight"
SOURCE_COMMAND_NAME = l5_22_readback.COMMAND_NAME
NEXT_PATCH = "L5.24 Live adapter Microsoft Edge supervised launch live-start preflight CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-live-start-preflight-contract-only"
BROWSER_PRIORITY = ("edge", "opera")

EDGE_EXECUTABLE_CANDIDATES: tuple[str, ...] = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)

REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*l5_22_readback.REQUIRED_COMMANDS, COMMAND_NAME)))

REQUIRED_REPO_PATHS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *l5_22_readback.REQUIRED_REPO_PATHS,
            "patchops/llm_browser/live_adapter_edge_supervised_launch_live_start_preflight_contract.py",
            "docs/llm_browser_live_adapter_edge_supervised_launch_live_start_preflight_contract.md",
            "tests/test_l5_23_edge_supervised_launch_live_start_preflight_contract_current.py",
        )
    )
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback.md": (
        "L5.22 Microsoft Edge supervised launch L5 broad validation checkpoint CLI/readback",
        "browser-start-supervised-launch-edge-l5-broad-validation-readback",
        "Microsoft Edge first",
        "Opera second",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.23 Live adapter Microsoft Edge supervised launch live-start preflight contract",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_live_start_preflight_contract.md": (
        "L5.23 Microsoft Edge supervised launch live-start preflight contract",
        "browser-start-supervised-launch-edge-live-start-preflight",
        "browser-start-supervised-launch-edge-l5-broad-validation-readback",
        "Microsoft Edge first",
        "Opera second",
        "explicit operator authorization required",
        "dedicated profile required",
        "default profile forbidden",
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
        "L5.24 Live adapter Microsoft Edge supervised launch live-start preflight CLI/readback",
    ),
}

LIVE_START_PREFLIGHT_CONTRACT: Mapping[str, Any] = {
    "browser": "edge",
    "browser_priority": list(BROWSER_PRIORITY),
    "edge_first": True,
    "opera_second": True,
    "launch_mode": "future_user_visible_supervised_edge_launch",
    "current_patch_launches_browser": False,
    "current_patch_imports_selenium": False,
    "current_patch_creates_profile_directory": False,
    "current_patch_creates_driver": False,
    "current_patch_creates_browser_session": False,
    "explicit_operator_authorization_required": True,
    "authorization_flag_required": "--allow-live-start",
    "profile_dir_argument_required": "--profile-dir",
    "dedicated_profile_required": True,
    "default_profile_forbidden": True,
    "manual_user_login_required": True,
    "silent_auto_submit_default": False,
    "silent_auto_submit_must_remain_false": True,
    "download_click_allowed_in_this_patch": False,
    "pasteback_insert_allowed_in_this_patch": False,
    "send_or_submit_allowed_in_this_patch": False,
    "package_run_allowed_from_adapter_in_this_patch": False,
    "browser_extension_required": False,
    "localhost_patchops_server_required": False,
    "edge_executable_candidates": list(EDGE_EXECUTABLE_CANDIDATES),
    "preflight_checks_modelled_only": True,
    "filesystem_probe_required_in_this_patch": False,
}

PASSIVE_INVARIANTS: Mapping[str, Any] = {
    "startup_authorized": False,
    "startup_allowed": False,
    "live_start_requested": False,
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


def _l5_22_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    l5_21_summary = payload.get("l5_21_summary", {})
    return {
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "source_command_name": payload.get("source_command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "l5_21_patch": l5_21_summary.get("patch") if isinstance(l5_21_summary, Mapping) else None,
        "l5_21_status": l5_21_summary.get("status") if isinstance(l5_21_summary, Mapping) else None,
        "l5_20_patch": l5_21_summary.get("l5_20_patch") if isinstance(l5_21_summary, Mapping) else None,
        "l5_20_status": l5_21_summary.get("l5_20_status") if isinstance(l5_21_summary, Mapping) else None,
        "l5_19_chain_length": l5_21_summary.get("l5_19_chain_length") if isinstance(l5_21_summary, Mapping) else None,
        "doc_state_ok": payload.get("doc_state", {}).get("ok") if isinstance(payload.get("doc_state"), Mapping) else None,
        "missing_repo_paths": payload.get("missing_repo_paths", []),
        "startup_authorized": payload.get("startup_authorized") is True,
        "startup_allowed": payload.get("startup_allowed") is True,
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


def _l5_22_passive_ok(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.22"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l5_21_patch") == "L5.21"
        and summary.get("l5_21_status") == STATUS_PASS
        and summary.get("l5_20_patch") == "L5.20"
        and summary.get("l5_20_status") == STATUS_PASS
        and summary.get("l5_19_chain_length") == 7
        and summary.get("doc_state_ok") is True
        and summary.get("missing_repo_paths") == []
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("startup_authorized") is False
        and summary.get("startup_allowed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
    )


def _preflight_contract_ok(contract: Mapping[str, Any]) -> bool:
    return (
        contract.get("browser") == "edge"
        and contract.get("browser_priority") == list(BROWSER_PRIORITY)
        and contract.get("edge_first") is True
        and contract.get("opera_second") is True
        and contract.get("explicit_operator_authorization_required") is True
        and contract.get("authorization_flag_required") == "--allow-live-start"
        and contract.get("profile_dir_argument_required") == "--profile-dir"
        and contract.get("dedicated_profile_required") is True
        and contract.get("default_profile_forbidden") is True
        and contract.get("manual_user_login_required") is True
        and contract.get("silent_auto_submit_default") is False
        and contract.get("silent_auto_submit_must_remain_false") is True
        and contract.get("browser_extension_required") is False
        and contract.get("localhost_patchops_server_required") is False
        and contract.get("current_patch_launches_browser") is False
        and contract.get("current_patch_imports_selenium") is False
        and contract.get("current_patch_creates_profile_directory") is False
        and contract.get("current_patch_creates_driver") is False
        and contract.get("current_patch_creates_browser_session") is False
        and contract.get("download_click_allowed_in_this_patch") is False
        and contract.get("pasteback_insert_allowed_in_this_patch") is False
        and contract.get("send_or_submit_allowed_in_this_patch") is False
        and contract.get("package_run_allowed_from_adapter_in_this_patch") is False
        and contract.get("edge_executable_candidates") == list(EDGE_EXECUTABLE_CANDIDATES)
        and contract.get("preflight_checks_modelled_only") is True
        and contract.get("filesystem_probe_required_in_this_patch") is False
    )


def build_edge_supervised_launch_live_start_preflight_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_22_payload = l5_22_readback.build_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback(root)
    l5_22_summary = _l5_22_summary(l5_22_payload)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.22 START")
    preflight_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.23 START")
    command_state = _required_command_state(root)
    doc_state = _doc_phrase_state(root)
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)

    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    checks = [
        _check("l5_22_edge_l5_broad_validation_readback_still_passes", l5_22_summary.get("ok") is True and l5_22_summary.get("status") == STATUS_PASS, l5_22_summary),
        _check("l5_22_edge_l5_broad_validation_readback_remains_passive", _l5_22_passive_ok(l5_22_summary), l5_22_summary),
        _check("l5_22_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_23_live_start_preflight_command_registered", preflight_command_static.get("ok") is True, preflight_command_static),
        _check("edge_l5_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_preflight_boundary", doc_state.get("ok") is True, doc_state),
        _check("edge_live_start_preflight_contract_is_explicit", _preflight_contract_ok(LIVE_START_PREFLIGHT_CONTRACT), LIVE_START_PREFLIGHT_CONTRACT),
        _check("edge_live_start_requires_explicit_operator_authorization", LIVE_START_PREFLIGHT_CONTRACT["explicit_operator_authorization_required"] is True, LIVE_START_PREFLIGHT_CONTRACT),
        _check("edge_live_start_requires_dedicated_profile", LIVE_START_PREFLIGHT_CONTRACT["dedicated_profile_required"] is True, LIVE_START_PREFLIGHT_CONTRACT),
        _check("edge_live_start_keeps_default_profile_forbidden", LIVE_START_PREFLIGHT_CONTRACT["default_profile_forbidden"] is True, LIVE_START_PREFLIGHT_CONTRACT),
        _check("edge_live_start_keeps_manual_login_required", LIVE_START_PREFLIGHT_CONTRACT["manual_user_login_required"] is True, LIVE_START_PREFLIGHT_CONTRACT),
        _check("edge_live_start_keeps_silent_auto_submit_false", LIVE_START_PREFLIGHT_CONTRACT["silent_auto_submit_default"] is False and LIVE_START_PREFLIGHT_CONTRACT["silent_auto_submit_must_remain_false"] is True, LIVE_START_PREFLIGHT_CONTRACT),
        _check("edge_live_start_requires_no_localhost_or_extension", LIVE_START_PREFLIGHT_CONTRACT["localhost_patchops_server_required"] is False and LIVE_START_PREFLIGHT_CONTRACT["browser_extension_required"] is False, LIVE_START_PREFLIGHT_CONTRACT),
        _check("selenium_not_imported_by_preflight_readback", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
        _check("no_browser_or_adapter_side_effects", PASSIVE_INVARIANTS["browser_started"] is False and PASSIVE_INVARIANTS["side_effects_performed"] == [], dict(PASSIVE_INVARIANTS)),
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
        "live_start_preflight_contract": dict(LIVE_START_PREFLIGHT_CONTRACT),
        "edge_executable_candidates": list(EDGE_EXECUTABLE_CANDIDATES),
        "l5_22_edge_l5_broad_validation_readback": l5_22_payload,
        "l5_22_summary": l5_22_summary,
        "source_command_static_presence": source_command_static,
        "preflight_command_static_presence": preflight_command_static,
        "command_state": command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_repo_paths,
        "checks": checks,
        "executed_validation_commands": [],
        **PASSIVE_INVARIANTS,
        "selenium_imported_by_readback": selenium_imported_by_readback,
    }
    payload["payload_json_safe"] = _json_safe(payload)
    if not payload["payload_json_safe"]:
        payload["ok"] = False
        payload["status"] = STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    contract = payload.get("live_start_preflight_contract", {})
    if not isinstance(contract, Mapping):
        contract = {}
    lines = [
        "PatchOps L5.23 Microsoft Edge supervised-launch live-start preflight contract",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Browser Priority: {payload.get('browser_priority')}",
        f"Authorization   : required={contract.get('explicit_operator_authorization_required')} flag={contract.get('authorization_flag_required')}",
        f"Profile         : dedicated={contract.get('dedicated_profile_required')} default_forbidden={contract.get('default_profile_forbidden')}",
        f"Manual Login    : {contract.get('manual_user_login_required')}",
        f"Silent Submit   : {contract.get('silent_auto_submit_default')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_supervised_launch_live_start_preflight_contract(args.repo_root)
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