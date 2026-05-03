"""Passive L5.18 Microsoft Edge supervised-launch L5 aggregate readiness gate.

This module aggregates the Microsoft Edge supervised-launch readiness stream
from L5.12 through L5.17. It remains fully passive: no Selenium import, no Edge
process start, no driver/session creation, no profile directory creation, no
click/download, no paste/send, no package run, and no automatic git operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback as l5_broad_readback
from . import live_adapter_edge_supervised_launch_readiness_contract as edge_readiness_contract
from . import live_adapter_edge_supervised_launch_readiness_cli_readback as edge_readiness_readback
from . import live_adapter_edge_supervised_launch_fixture_matrix as edge_fixture_matrix
from . import live_adapter_edge_supervised_launch_fixture_matrix_cli_readback as edge_fixture_readback
from . import live_adapter_edge_supervised_launch_fixture_matrix_contract_gate as edge_contract_gate
from . import live_adapter_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback as edge_contract_gate_readback

PATCH = "L5.18"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.18 Microsoft Edge Supervised Launch L5 Aggregate Readiness Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-l5-readiness"
NEXT_PATCH = "L5.19 Live adapter Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-l5-aggregate-readiness-gate-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_COMMANDS: tuple[str, ...] = (
    "browser-start-supervised-launch-handoff-l5-broad-validation",
    "browser-start-supervised-launch-edge-readiness",
    "browser-start-supervised-launch-edge-readiness-readback",
    "browser-start-supervised-launch-edge-fixtures",
    "browser-start-supervised-launch-edge-fixtures-readback",
    "browser-start-supervised-launch-edge-fixtures-contract-gate",
    "browser-start-supervised-launch-edge-fixtures-contract-gate-readback",
    COMMAND_NAME,
)

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_contract.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_contract.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md",
    "tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py",
    "tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py",
    "tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py",
    "tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py",
    "tests/test_l5_17_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback_current.py",
    "tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py",
)

REQUIRED_PATCH_STATUS_CHAIN: tuple[tuple[str, str], ...] = (
    ("L5.11", "l5_11_broad_validation_cli_readback"),
    ("L5.12", "edge_readiness_contract"),
    ("L5.13", "edge_readiness_cli_readback"),
    ("L5.14", "edge_fixture_matrix"),
    ("L5.15", "edge_fixture_matrix_cli_readback"),
    ("L5.16", "edge_fixture_matrix_contract_gate"),
    ("L5.17", "edge_fixture_matrix_contract_gate_cli_readback"),
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


def _registered_command_state(root: Path) -> dict[str, Any]:
    command_states = {command: _command_static_presence(root, command) for command in REQUIRED_COMMANDS}
    missing_commands = [command for command, state in command_states.items() if state.get("ok") is not True]
    return {"ok": not missing_commands, "missing_commands": missing_commands, "command_states": command_states}


def _payload_passive_state(payload: Mapping[str, Any]) -> dict[str, Any]:
    # L5.11 predates the Edge-specific edge_process_started readback field.
    # Missing legacy fields are treated as passive false only for that field;
    # explicit true would still fail the aggregate safety gate.
    return {
        "startup_authorized": payload.get("startup_authorized") is False,
        "startup_allowed": payload.get("startup_allowed") is False,
        "browser_started": payload.get("browser_started") is False,
        "edge_process_started": payload.get("edge_process_started", False) is False,
        "browser_session_created": payload.get("browser_session_created") is False,
        "driver_created": payload.get("driver_created") is False,
        "profile_directory_created": payload.get("profile_directory_created") is False,
        "adapter_filesystem_writes_performed": payload.get("adapter_filesystem_writes_performed") == [],
        "filesystem_writes_performed": payload.get("filesystem_writes_performed") == [],
        "side_effects_performed": payload.get("side_effects_performed") == [],
        "click_download_performed": payload.get("click_download_performed") is False,
        "download_performed": payload.get("download_performed") is False,
        "paste_performed": payload.get("paste_performed") is False,
        "send_or_submit_performed": payload.get("send_or_submit_performed") is False,
        "package_run_performed_by_adapter": payload.get("package_run_performed_by_adapter") is False,
        "git_commit_executed": payload.get("git_commit_executed") is False,
        "git_push_executed": payload.get("git_push_executed") is False,
        "optional_browser_dependencies_required": payload.get("optional_browser_dependencies_required") is False,
        "selenium_required": payload.get("selenium_required") is False,
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback") is False,
    }


def _patch_summary(name: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    passive_state = _payload_passive_state(payload)
    return {
        "label": name,
        "patch": payload.get("patch"),
        "name": payload.get("name"),
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "command_name": payload.get("command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "passive_state": passive_state,
        "passive_ok": all(passive_state.values()),
    }


def _edge_contract_state(l5_12: Mapping[str, Any]) -> dict[str, Any]:
    contract = l5_12.get("edge_readiness_contract", {}) if isinstance(l5_12, Mapping) else {}
    if not isinstance(contract, Mapping):
        contract = {}
    return {
        "browser": contract.get("browser"),
        "edge_is_first_supported_live_browser": contract.get("edge_is_first_supported_live_browser") is True,
        "opera_is_second_supported_live_browser": contract.get("opera_is_second_supported_live_browser") is True,
        "dedicated_profile_required_before_live_start": contract.get("dedicated_profile_required_before_live_start") is True,
        "default_browser_profile_forbidden": contract.get("default_browser_profile_forbidden") is True,
        "manual_user_login_required": contract.get("manual_user_login_required") is True,
        "silent_auto_submit_default": contract.get("silent_auto_submit_default") is False,
        "browser_extension_required": contract.get("browser_extension_required") is False,
        "localhost_patchops_server_required": contract.get("localhost_patchops_server_required") is False,
        "current_patch_launches_browser": contract.get("current_patch_launches_browser") is False,
        "current_patch_imports_selenium": contract.get("current_patch_imports_selenium") is False,
        "current_patch_creates_profile_directory": contract.get("current_patch_creates_profile_directory") is False,
        "download_click_allowed_in_this_patch": contract.get("download_click_allowed_in_this_patch") is False,
        "pasteback_insert_allowed_in_this_patch": contract.get("pasteback_insert_allowed_in_this_patch") is False,
        "package_run_allowed_from_adapter_in_this_patch": contract.get("package_run_allowed_from_adapter_in_this_patch") is False,
    }


def _gate_contract_state(l5_17: Mapping[str, Any]) -> dict[str, Any]:
    gate = l5_17.get("edge_fixture_contract_gate_summary", {}) if isinstance(l5_17, Mapping) else {}
    if not isinstance(gate, Mapping):
        gate = {}
    return {
        "ok": gate.get("ok") is True,
        "status": gate.get("status"),
        "case_count": gate.get("case_count"),
        "missing_case_ids": list(gate.get("missing_case_ids", [])),
        "unexpected_case_ids": list(gate.get("unexpected_case_ids", [])),
        "violations": list(gate.get("violations", [])),
        "edge_first_required": gate.get("edge_first_required") is True,
        "dedicated_profile_required": gate.get("dedicated_profile_required") is True,
        "manual_user_login_required": gate.get("manual_user_login_required") is True,
        "silent_auto_submit_must_remain_false": gate.get("silent_auto_submit_must_remain_false") is True,
        "no_extension_required": gate.get("no_extension_required") is True,
        "no_localhost_server_required": gate.get("no_localhost_server_required") is True,
        "current_patch_must_remain_passive": gate.get("current_patch_must_remain_passive") is True,
    }


def build_edge_supervised_launch_l5_aggregate_readiness_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    broad_l5_11 = l5_broad_readback.build_l5_broad_validation_cli_readback(root)
    l5_12 = edge_readiness_contract.build_edge_supervised_launch_readiness_contract(root)
    l5_13 = edge_readiness_readback.build_edge_supervised_launch_readiness_cli_readback(root)
    l5_14 = edge_fixture_matrix.build_edge_supervised_launch_fixture_matrix(root)
    l5_15 = edge_fixture_readback.build_edge_supervised_launch_fixture_matrix_cli_readback(root)
    l5_16 = edge_contract_gate.build_edge_supervised_launch_fixture_matrix_contract_gate(root)
    l5_17 = edge_contract_gate_readback.build_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback(root)

    payloads: dict[str, Mapping[str, Any]] = {
        "l5_11_broad_validation_cli_readback": broad_l5_11,
        "edge_readiness_contract": l5_12,
        "edge_readiness_cli_readback": l5_13,
        "edge_fixture_matrix": l5_14,
        "edge_fixture_matrix_cli_readback": l5_15,
        "edge_fixture_matrix_contract_gate": l5_16,
        "edge_fixture_matrix_contract_gate_cli_readback": l5_17,
    }

    patch_summaries = {label: _patch_summary(label, payload) for label, payload in payloads.items()}
    command_state = _registered_command_state(root)
    aggregate_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.18 START")
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    edge_contract = _edge_contract_state(l5_12)
    gate_contract = _gate_contract_state(l5_17)
    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    patch_status_chain = []
    for expected_patch, label in REQUIRED_PATCH_STATUS_CHAIN:
        summary = patch_summaries.get(label, {})
        patch_status_chain.append(
            {
                "expected_patch": expected_patch,
                "label": label,
                "actual_patch": summary.get("patch"),
                "ok": summary.get("ok") is True,
                "status": summary.get("status"),
                "passive_ok": summary.get("passive_ok") is True,
            }
        )

    aggregate_passive_ok = all(summary.get("passive_ok") is True for summary in patch_summaries.values())
    patch_chain_ok = all(
        item["ok"] is True
        and item["status"] == STATUS_PASS
        and item["actual_patch"] == item["expected_patch"]
        and item["passive_ok"] is True
        for item in patch_status_chain
    )
    edge_contract_ok = all(edge_contract.values()) if edge_contract else False
    gate_contract_ok = (
        gate_contract.get("ok") is True
        and gate_contract.get("status") == STATUS_PASS
        and gate_contract.get("case_count") == 6
        and gate_contract.get("missing_case_ids") == []
        and gate_contract.get("unexpected_case_ids") == []
        and gate_contract.get("violations") == []
        and gate_contract.get("edge_first_required") is True
        and gate_contract.get("dedicated_profile_required") is True
        and gate_contract.get("manual_user_login_required") is True
        and gate_contract.get("silent_auto_submit_must_remain_false") is True
        and gate_contract.get("no_extension_required") is True
        and gate_contract.get("no_localhost_server_required") is True
        and gate_contract.get("current_patch_must_remain_passive") is True
    )

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_18_wire_edge_l5_aggregate_readiness.py",
        "python -m pytest -q tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py tests/test_l5_17_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback_current.py tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-readiness --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_11_through_l5_17_edge_patch_chain_still_passes", patch_chain_ok, {"patch_status_chain": patch_status_chain}),
        _check("edge_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("l5_18_edge_aggregate_readiness_command_registered", aggregate_command_static.get("ok") is True, aggregate_command_static),
        _check("edge_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_readiness_contract_still_blocks_live_startup", edge_contract_ok, edge_contract),
        _check("edge_fixture_contract_gate_still_passes", gate_contract_ok, gate_contract),
        _check("edge_stream_payloads_all_remain_passive", aggregate_passive_ok, {"patch_summaries": patch_summaries}),
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
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "repo_root": str(root),
        "required_commands": list(REQUIRED_COMMANDS),
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "patch_status_chain": patch_status_chain,
        "patch_summaries": patch_summaries,
        "command_state": command_state,
        "aggregate_command_static_presence": aggregate_command_static,
        "missing_repo_paths": missing_repo_paths,
        "edge_readiness_contract_summary": edge_contract,
        "edge_fixture_contract_gate_summary": gate_contract,
        "l5_11_broad_validation_cli_readback": broad_l5_11,
        "l5_12_edge_readiness_contract": l5_12,
        "l5_13_edge_readiness_cli_readback": l5_13,
        "l5_14_edge_fixture_matrix": l5_14,
        "l5_15_edge_fixture_matrix_cli_readback": l5_15,
        "l5_16_edge_fixture_matrix_contract_gate": l5_16,
        "l5_17_edge_fixture_matrix_contract_gate_cli_readback": l5_17,
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
        "PatchOps L5.18 Microsoft Edge supervised-launch L5 aggregate readiness gate",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
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
        "Patch Chain:",
    ]
    for item in payload.get("patch_status_chain", []):
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

    payload = build_edge_supervised_launch_l5_aggregate_readiness_gate(args.repo_root)
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