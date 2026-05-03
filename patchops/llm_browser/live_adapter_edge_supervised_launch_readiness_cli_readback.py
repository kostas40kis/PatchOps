"""Passive L5.13 Microsoft Edge supervised-launch readiness CLI/readback.

This module exposes a dedicated readback/checkpoint around the accepted L5.12
Microsoft Edge readiness contract. It is still passive: no Selenium import, no
Edge process start, no driver/session creation, no profile directory creation,
no click/download/paste/send/package-run side effect, and no automatic git
operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_readiness_contract as edge_contract

PATCH = "L5.13"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.13 Microsoft Edge Supervised Launch Readiness CLI Readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-readiness-readback"
SOURCE_COMMAND_NAME = edge_contract.COMMAND_NAME
NEXT_PATCH = "L5.14 Live adapter Microsoft Edge supervised launch fixture matrix"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-readiness-cli-readback-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_contract.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_cli_readback.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_contract.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_cli_readback.md",
    "tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py",
    "tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py",
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


def build_edge_supervised_launch_readiness_cli_readback(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_12 = edge_contract.build_edge_supervised_launch_readiness_contract(root)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.12 START")
    readback_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.13 START")
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    source_contract = l5_12.get("edge_readiness_contract", {}) if isinstance(l5_12, Mapping) else {}
    edge_contract_still_blocks_live_start = (
        l5_12.get("ok") is True
        and source_contract.get("browser") == "edge"
        and source_contract.get("current_patch_launches_browser") is False
        and source_contract.get("current_patch_imports_selenium") is False
        and source_contract.get("download_click_allowed_in_this_patch") is False
        and source_contract.get("pasteback_insert_allowed_in_this_patch") is False
        and source_contract.get("package_run_allowed_from_adapter_in_this_patch") is False
    )

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_13_wire_edge_readiness_readback.py",
        "python -m pytest -q tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_readiness_cli_readback --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-readiness-readback --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_12_edge_readiness_contract_still_passes", l5_12.get("ok") is True and l5_12.get("status") == STATUS_PASS, {"patch": l5_12.get("patch")}),
        _check("l5_12_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_13_edge_readiness_readback_command_registered", readback_command_static.get("ok") is True, readback_command_static),
        _check("edge_readiness_contract_still_blocks_live_startup", edge_contract_still_blocks_live_start, dict(source_contract)),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("l5_13_artifacts_present", not missing_repo_paths, {"missing": missing_repo_paths}),
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
        "l5_12_edge_readiness_contract": l5_12,
        "source_command_static_presence": source_command_static,
        "readback_command_static_presence": readback_command_static,
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
        "PatchOps L5.13 Microsoft Edge supervised-launch readiness CLI/readback",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
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

    payload = build_edge_supervised_launch_readiness_cli_readback(args.repo_root)
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