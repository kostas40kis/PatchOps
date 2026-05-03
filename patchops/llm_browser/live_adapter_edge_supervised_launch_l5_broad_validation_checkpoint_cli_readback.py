"""Passive L5.22 Microsoft Edge L5 broad validation checkpoint CLI/readback.

This module reads back the accepted L5.21 Microsoft Edge L5 broad-validation
checkpoint and exposes a dedicated CLI/readback command. It validates the L5.21
payload, command registration, source/doc/test presence, and passive boundaries.

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

from . import live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint as l5_21_checkpoint

PATCH = "L5.22"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.22 Microsoft Edge Supervised Launch L5 Broad Validation Checkpoint CLI Readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-l5-broad-validation-readback"
SOURCE_COMMAND_NAME = l5_21_checkpoint.COMMAND_NAME
NEXT_PATCH = "L5.23 Live adapter Microsoft Edge supervised launch live-start preflight contract"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-l5-broad-validation-cli-readback-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*l5_21_checkpoint.REQUIRED_COMMANDS, COMMAND_NAME)))

REQUIRED_REPO_PATHS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *l5_21_checkpoint.REQUIRED_REPO_PATHS,
            "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback.py",
            "docs/llm_browser_live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback.md",
            "tests/test_l5_22_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback_current.py",
        )
    )
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint.md": (
        "L5.21 Microsoft Edge supervised launch L5 broad validation checkpoint",
        "browser-start-supervised-launch-edge-l5-broad-validation",
        "Microsoft Edge first",
        "Opera second",
        "planned broad-validation command list",
        "adapter logic executes no validation commands",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.22 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint CLI/readback",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback.md": (
        "L5.22 Microsoft Edge supervised launch L5 broad validation checkpoint CLI/readback",
        "browser-start-supervised-launch-edge-l5-broad-validation-readback",
        "browser-start-supervised-launch-edge-l5-broad-validation",
        "Microsoft Edge first",
        "Opera second",
        "dedicated profile required",
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
        "L5.23 Live adapter Microsoft Edge supervised launch live-start preflight contract",
    ),
}

PASSIVE_INVARIANTS: Mapping[str, Any] = {
    "startup_authorized": False,
    "startup_allowed": False,
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


def _l5_21_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    l5_20_summary = payload.get("l5_20_summary", {})
    command_plan_state = payload.get("command_plan_state", {})
    return {
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "source_command_name": payload.get("source_command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "l5_20_patch": l5_20_summary.get("patch") if isinstance(l5_20_summary, Mapping) else None,
        "l5_20_status": l5_20_summary.get("status") if isinstance(l5_20_summary, Mapping) else None,
        "l5_19_chain_length": l5_20_summary.get("l5_19_chain_length") if isinstance(l5_20_summary, Mapping) else None,
        "doc_state_ok": payload.get("doc_state", {}).get("ok") if isinstance(payload.get("doc_state"), Mapping) else None,
        "command_plan_ok": command_plan_state.get("ok") if isinstance(command_plan_state, Mapping) else None,
        "executed_validation_commands": payload.get("executed_validation_commands"),
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


def _l5_21_passive_ok(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.21"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l5_20_patch") == "L5.20"
        and summary.get("l5_20_status") == STATUS_PASS
        and summary.get("l5_19_chain_length") == 7
        and summary.get("doc_state_ok") is True
        and summary.get("command_plan_ok") is True
        and summary.get("executed_validation_commands") == []
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


def build_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_21_payload = l5_21_checkpoint.build_edge_supervised_launch_l5_broad_validation_checkpoint(root)
    l5_21_summary = _l5_21_summary(l5_21_payload)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.21 START")
    readback_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.22 START")
    command_state = _required_command_state(root)
    doc_state = _doc_phrase_state(root)
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)

    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_22_wire_edge_l5_broad_validation_readback.py",
        "python -m pytest -q tests/test_l5_21_edge_supervised_launch_l5_broad_validation_checkpoint_current.py tests/test_l5_22_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-broad-validation-readback --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_21_edge_l5_broad_validation_checkpoint_still_passes", l5_21_summary.get("ok") is True and l5_21_summary.get("status") == STATUS_PASS, l5_21_summary),
        _check("l5_21_edge_l5_broad_validation_checkpoint_remains_passive", _l5_21_passive_ok(l5_21_summary), l5_21_summary),
        _check("l5_21_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_22_broad_validation_readback_command_registered", readback_command_static.get("ok") is True, readback_command_static),
        _check("edge_l5_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_safety_boundary", doc_state.get("ok") is True, doc_state),
        _check("l5_22_command_plan_is_readback_only", True, {"planned_commands": command_plan, "executed_by_adapter_logic": []}),
        _check("adapter_logic_executes_no_validation_commands", True, {"executed_by_adapter_logic": []}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_readback", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
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
        "l5_21_edge_l5_broad_validation_checkpoint": l5_21_payload,
        "l5_21_summary": l5_21_summary,
        "source_command_static_presence": source_command_static,
        "readback_command_static_presence": readback_command_static,
        "command_state": command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_repo_paths,
        "command_plan": command_plan,
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
    lines = [
        "PatchOps L5.22 Microsoft Edge supervised-launch L5 broad validation checkpoint CLI/readback",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Browser Priority: {payload.get('browser_priority')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
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

    payload = build_edge_supervised_launch_l5_broad_validation_checkpoint_cli_readback(args.repo_root)
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