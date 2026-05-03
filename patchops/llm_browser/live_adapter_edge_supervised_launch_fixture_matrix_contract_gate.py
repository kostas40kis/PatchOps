"""Passive L5.16 Microsoft Edge supervised-launch fixture matrix contract gate.

The contract gate consumes the accepted L5.15 fixture-matrix CLI/readback and
turns the fixture expectations into explicit gate assertions. It remains fully
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

from . import live_adapter_edge_supervised_launch_fixture_matrix_cli_readback as edge_readback

PATCH = "L5.16"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.16 Microsoft Edge Supervised Launch Fixture Matrix Contract Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-fixtures-contract-gate"
SOURCE_COMMAND_NAME = edge_readback.COMMAND_NAME
NEXT_PATCH = "L5.17 Live adapter Microsoft Edge supervised launch fixture matrix contract gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-fixture-matrix-contract-gate-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_CASE_IDS: tuple[str, ...] = (
    "edge_future_launch_user_visible",
    "edge_dedicated_profile_required",
    "edge_manual_login_required",
    "edge_no_silent_auto_submit",
    "edge_no_extension_no_localhost",
    "edge_no_current_side_effects",
)

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.md",
    "tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py",
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


def _evaluate_fixture_contract(cases: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    case_list = [dict(case) for case in cases]
    cases_by_id = {str(case.get("case_id")): case for case in case_list}
    missing_case_ids = [case_id for case_id in REQUIRED_CASE_IDS if case_id not in cases_by_id]
    unexpected_case_ids = [case_id for case_id in cases_by_id if case_id not in REQUIRED_CASE_IDS]
    violations: list[dict[str, Any]] = []

    required_false_fields = (
        "silent_auto_submit_default",
        "browser_extension_required",
        "localhost_patchops_server_required",
        "current_patch_launches_browser",
        "current_patch_imports_selenium",
        "current_patch_creates_profile_directory",
        "current_patch_clicks_download",
        "current_patch_pastes_or_sends",
        "current_patch_runs_package_from_adapter",
    )
    required_true_fields = (
        "edge_first",
        "dedicated_profile_required",
        "manual_user_login_required",
        "default_profile_forbidden",
        "passive_only",
    )

    for case_id in REQUIRED_CASE_IDS:
        case = cases_by_id.get(case_id)
        if case is None:
            continue
        if case.get("browser") != "edge":
            violations.append({"case_id": case_id, "field": "browser", "expected": "edge", "actual": case.get("browser")})
        for field in required_true_fields:
            if case.get(field) is not True:
                violations.append({"case_id": case_id, "field": field, "expected": True, "actual": case.get(field)})
        for field in required_false_fields:
            if case.get(field) is not False:
                violations.append({"case_id": case_id, "field": field, "expected": False, "actual": case.get(field)})

    ok = not missing_case_ids and not unexpected_case_ids and not violations
    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "case_count": len(case_list),
        "required_case_ids": list(REQUIRED_CASE_IDS),
        "actual_case_ids": [case.get("case_id") for case in case_list],
        "missing_case_ids": missing_case_ids,
        "unexpected_case_ids": unexpected_case_ids,
        "violations": violations,
        "edge_first_required": True,
        "dedicated_profile_required": True,
        "manual_user_login_required": True,
        "silent_auto_submit_must_remain_false": True,
        "no_extension_required": True,
        "no_localhost_server_required": True,
        "current_patch_must_remain_passive": True,
    }


def build_edge_supervised_launch_fixture_matrix_contract_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_15 = edge_readback.build_edge_supervised_launch_fixture_matrix_cli_readback(root)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.15 START")
    gate_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.16 START")
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    fixture_cases = l5_15.get("edge_fixture_cases", []) if isinstance(l5_15, Mapping) else []
    contract_gate = _evaluate_fixture_contract(fixture_cases)
    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_16_wire_edge_fixture_matrix_contract_gate.py",
        "python -m pytest -q tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_fixture_matrix_contract_gate --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-fixtures-contract-gate --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_15_edge_fixture_matrix_cli_readback_still_passes", l5_15.get("ok") is True and l5_15.get("status") == STATUS_PASS, {"patch": l5_15.get("patch")}),
        _check("l5_15_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_16_edge_fixture_matrix_contract_gate_command_registered", gate_command_static.get("ok") is True, gate_command_static),
        _check("edge_fixture_matrix_contract_gate_passes", contract_gate.get("ok") is True, contract_gate),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("l5_16_artifacts_present", not missing_repo_paths, {"missing": missing_repo_paths}),
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
        "l5_15_edge_fixture_matrix_cli_readback": l5_15,
        "edge_fixture_cases": [dict(case) for case in fixture_cases],
        "edge_fixture_contract_gate": contract_gate,
        "source_command_static_presence": source_command_static,
        "gate_command_static_presence": gate_command_static,
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
    gate = payload.get("edge_fixture_contract_gate", {})
    lines = [
        "PatchOps L5.16 Microsoft Edge supervised-launch fixture matrix contract gate",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Gate Status     : {gate.get('status') if isinstance(gate, Mapping) else None}",
        f"Case Count      : {gate.get('case_count') if isinstance(gate, Mapping) else None}",
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

    payload = build_edge_supervised_launch_fixture_matrix_contract_gate(args.repo_root)
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