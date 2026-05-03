"""Passive L5.19 Microsoft Edge L5 aggregate readiness gate CLI/readback.

This module exposes a dedicated readback/checkpoint around the accepted L5.18
Microsoft Edge supervised-launch L5 aggregate readiness gate. It remains fully
passive: no Selenium import, no Edge process start, no driver/session creation,
no profile directory creation, no click/download, no paste/send, no package run,
and no automatic git operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate as aggregate_gate

PATCH = "L5.19"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.19 Microsoft Edge Supervised Launch L5 Aggregate Readiness Gate CLI Readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-l5-readiness-readback"
SOURCE_COMMAND_NAME = aggregate_gate.COMMAND_NAME
NEXT_PATCH = "L5.20 Live adapter Microsoft Edge supervised launch L5 documentation checkpoint"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-l5-aggregate-readiness-gate-cli-readback-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_PATCH_STATUS_CHAIN: tuple[tuple[str, str], ...] = aggregate_gate.REQUIRED_PATCH_STATUS_CHAIN
REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*aggregate_gate.REQUIRED_COMMANDS, COMMAND_NAME)))

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback.md",
    "tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py",
    "tests/test_l5_19_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback_current.py",
)

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
    if repo_root is None:
        return Path.cwd().resolve()
    return Path(repo_root).resolve()


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
    payload: dict[str, Any] = {
        "ok": command_name in text,
        "commands_path": str(commands_path),
        "command_name": command_name,
    }
    if sentinel is not None:
        payload["sentinel_present"] = sentinel in text
        payload["ok"] = bool(payload["ok"] and payload["sentinel_present"])
    return payload


def _required_command_state(root: Path) -> dict[str, Any]:
    command_states = {command: _command_static_presence(root, command) for command in REQUIRED_COMMANDS}
    missing_commands = [command for command, state in command_states.items() if state.get("ok") is not True]
    return {"ok": not missing_commands, "missing_commands": missing_commands, "command_states": command_states}


def _aggregate_summary(aggregate_payload: Mapping[str, Any]) -> dict[str, Any]:
    chain = aggregate_payload.get("patch_status_chain", [])
    if not isinstance(chain, list):
        chain = []
    checks = aggregate_payload.get("checks", [])
    if not isinstance(checks, list):
        checks = []
    chain_by_patch = {
        str(item.get("expected_patch")): item
        for item in chain
        if isinstance(item, Mapping)
    }
    check_by_name = {
        str(item.get("name")): item
        for item in checks
        if isinstance(item, Mapping)
    }
    return {
        "ok": aggregate_payload.get("ok") is True,
        "status": aggregate_payload.get("status"),
        "patch": aggregate_payload.get("patch"),
        "command_name": aggregate_payload.get("command_name"),
        "edge_first": aggregate_payload.get("edge_first") is True,
        "browser_priority": aggregate_payload.get("browser_priority"),
        "patch_status_chain": chain,
        "chain_length": len(chain),
        "chain_by_patch": chain_by_patch,
        "check_by_name": check_by_name,
        "missing_repo_paths": aggregate_payload.get("missing_repo_paths", []),
        "selenium_imported_by_readback": aggregate_payload.get("selenium_imported_by_readback") is True,
        "startup_authorized": aggregate_payload.get("startup_authorized") is True,
        "startup_allowed": aggregate_payload.get("startup_allowed") is True,
        "browser_started": aggregate_payload.get("browser_started") is True,
        "edge_process_started": aggregate_payload.get("edge_process_started") is True,
        "browser_session_created": aggregate_payload.get("browser_session_created") is True,
        "driver_created": aggregate_payload.get("driver_created") is True,
        "profile_directory_created": aggregate_payload.get("profile_directory_created") is True,
        "side_effects_performed": aggregate_payload.get("side_effects_performed"),
        "adapter_filesystem_writes_performed": aggregate_payload.get("adapter_filesystem_writes_performed"),
        "filesystem_writes_performed": aggregate_payload.get("filesystem_writes_performed"),
    }


def _aggregate_passive_ok(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.18"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("chain_length") == len(REQUIRED_PATCH_STATUS_CHAIN)
        and summary.get("missing_repo_paths") == []
        and summary.get("selenium_imported_by_readback") is False
        and summary.get("startup_authorized") is False
        and summary.get("startup_allowed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("side_effects_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("filesystem_writes_performed") == []
    )


def _patch_chain_ok(summary: Mapping[str, Any]) -> bool:
    chain = summary.get("patch_status_chain", [])
    if not isinstance(chain, list):
        return False
    expected = list(REQUIRED_PATCH_STATUS_CHAIN)
    if len(chain) != len(expected):
        return False
    for item, (expected_patch, expected_label) in zip(chain, expected):
        if not isinstance(item, Mapping):
            return False
        if item.get("expected_patch") != expected_patch:
            return False
        if item.get("actual_patch") != expected_patch:
            return False
        if item.get("label") != expected_label:
            return False
        if item.get("ok") is not True:
            return False
        if item.get("status") != STATUS_PASS:
            return False
        if item.get("passive_ok") is not True:
            return False
    return True


def build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_18 = aggregate_gate.build_edge_supervised_launch_l5_aggregate_readiness_gate(root)
    aggregate = _aggregate_summary(l5_18)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.18 START")
    readback_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.19 START")
    command_state = _required_command_state(root)
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_19_wire_edge_l5_aggregate_readiness_readback.py",
        "python -m pytest -q tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py tests/test_l5_19_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-readiness-readback --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_18_edge_l5_aggregate_readiness_gate_still_passes", aggregate.get("ok") is True and aggregate.get("status") == STATUS_PASS, {"patch": aggregate.get("patch"), "command_name": aggregate.get("command_name")}),
        _check("l5_18_patch_chain_l5_11_through_l5_17_still_passes", _patch_chain_ok(aggregate), {"patch_status_chain": aggregate.get("patch_status_chain")}),
        _check("l5_18_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_19_edge_l5_aggregate_readback_command_registered", readback_command_static.get("ok") is True, readback_command_static),
        _check("edge_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("l5_19_artifacts_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_aggregate_readiness_remains_passive", _aggregate_passive_ok(aggregate), aggregate),
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
        "l5_18_edge_l5_aggregate_readiness_gate": l5_18,
        "edge_l5_aggregate_readiness_summary": aggregate,
        "source_command_static_presence": source_command_static,
        "readback_command_static_presence": readback_command_static,
        "command_state": command_state,
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
    summary = payload.get("edge_l5_aggregate_readiness_summary", {})
    chain = summary.get("patch_status_chain", []) if isinstance(summary, Mapping) else []
    lines = [
        "PatchOps L5.19 Microsoft Edge supervised-launch L5 aggregate readiness gate CLI/readback",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Browser Priority: {payload.get('browser_priority')}",
        f"Aggregate Patch : {summary.get('patch') if isinstance(summary, Mapping) else None}",
        f"Aggregate Status: {summary.get('status') if isinstance(summary, Mapping) else None}",
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
        "Patch Chain:",
    ]
    if isinstance(chain, list):
        for item in chain:
            if isinstance(item, Mapping):
                lines.append(f"- {item.get('expected_patch')}: ok={item.get('ok')} status={item.get('status')} passive={item.get('passive_ok')}")
    lines.append("Checks:")
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

    payload = build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(args.repo_root)
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