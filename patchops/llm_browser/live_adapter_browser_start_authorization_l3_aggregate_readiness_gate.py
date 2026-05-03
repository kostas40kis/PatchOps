"""Passive L3 browser-start authorization aggregate readiness gate.

This module aggregates the already-accepted passive L3 browser-start authorization stack.
It intentionally performs no live browser operation: no Selenium import, no browser start, no
browser session creation, no profile directory creation, no adapter filesystem writes, and no
click/download/paste/send/package-run side effect from adapter logic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser.live_adapter_browser_start_authorization import (
    FORBIDDEN_IMPORT_ROOTS,
    LIVE_SIDE_EFFECT_OPERATIONS,
    STATUS_FAIL,
    STATUS_PASS,
    build_browser_start_authorization_request,
    evaluate_browser_start_authorization,
)
from patchops.llm_browser.live_adapter_browser_start_authorization_fixtures import (
    build_l3_browser_start_authorization_fixture_matrix,
)
from patchops.llm_browser.live_adapter_browser_start_authorization_fixture_matrix_contract_gate import (
    build_contract_gate,
)

PATCH = "L3.7"
PHASE = "L3"
NAME = "llm_browser_live_adapter_browser_start_authorization_l3_aggregate_readiness_gate"
NEXT_PATCH = "L3.8 Live adapter browser-start authorization L3 aggregate readiness gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "passive-only"

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_browser_start_authorization.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.py",
    "docs/llm_browser_live_adapter_browser_start_authorization.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.md",
    "tests/test_l3_07_browser_start_authorization_l3_aggregate_readiness_gate_current.py",
)

REQUIRED_CLI_COMMANDS = (
    "browser-start-authorization",
    "browser-start-authorization-fixtures",
    "browser-start-authorization-contract-gate",
)

REQUIRED_FIXTURE_CASE_IDS = (
    "edge_default_missing_acknowledgements",
    "opera_ack_all_permission_flags_modelled_only",
    "unsupported_browser_rejected",
    "shared_profile_rejected",
    "download_paste_send_side_effects_blocked",
)


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        candidate = Path(repo_root)
        if str(candidate) == ".":
            return Path.cwd().resolve()
        return candidate.resolve()
    return _repo_root_from_here()


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _forbidden_imports_present() -> list[str]:
    present: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            present.append(root)
    return sorted(set(present))


def _forbidden_imports_loaded_since(before_modules: set[str]) -> list[str]:
    newly_loaded = set(sys.modules) - before_modules
    loaded: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            loaded.append(root)
    return sorted(set(loaded))


def _safe_command_names() -> list[str]:
    from patchops.llm_browser import commands
    return sorted(str(name) for name in commands.llm_browser_command_names())


def build_l3_browser_start_authorization_aggregate_readiness_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = resolve_repo_root(repo_root)
    before_modules = set(sys.modules)
    baseline_decision = evaluate_browser_start_authorization(
        build_browser_start_authorization_request(browser="edge", ack_all=True), repo_root=root
    )
    fixture_matrix = build_l3_browser_start_authorization_fixture_matrix(root)
    contract_gate = build_contract_gate(root)
    command_names = _safe_command_names()
    fixture_cases = list(fixture_matrix.get("cases", []))
    fixture_case_ids = [str(case.get("case_id", "")) for case in fixture_cases]
    missing_fixture_case_ids = [case_id for case_id in REQUIRED_FIXTURE_CASE_IDS if case_id not in fixture_case_ids]
    repo_path_state = {rel: (root / rel).exists() for rel in REQUIRED_REPO_PATHS}
    missing_repo_paths = [rel for rel, exists in repo_path_state.items() if not exists]
    missing_cli_commands = [command for command in REQUIRED_CLI_COMMANDS if command not in command_names]
    forbidden_imports_present = _forbidden_imports_present()
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)
    payload_json_safe = _json_safe({
        "baseline_decision": baseline_decision.to_payload(),
        "fixture_matrix": fixture_matrix,
        "contract_gate": contract_gate,
    })
    all_passive_flags = (
        baseline_decision.startup_authorized is False
        and baseline_decision.browser_started is False
        and baseline_decision.browser_session_created is False
        and baseline_decision.profile_directory_created is False
        and baseline_decision.side_effects_performed == ()
        and baseline_decision.filesystem_writes_performed == ()
        and fixture_matrix.get("browser_started") is False
        and fixture_matrix.get("browser_session_created") is False
        and fixture_matrix.get("profile_directory_created") is False
        and fixture_matrix.get("side_effects_performed") == []
        and fixture_matrix.get("filesystem_writes_performed") == []
        and contract_gate.get("startup_authorized") is False
        and contract_gate.get("browser_started") is False
        and contract_gate.get("browser_session_created") is False
        and contract_gate.get("profile_directory_created") is False
        and contract_gate.get("side_effects_performed") == []
        and contract_gate.get("filesystem_writes_performed") == []
    )
    checks = [
        _check("l3_01_browser_start_authorization_contract_still_blocks_startup", baseline_decision.ok is True and baseline_decision.startup_authorized is False, {"status": baseline_decision.status, "blocked_reasons": list(baseline_decision.blocked_reasons)}),
        _check("l3_03_browser_start_authorization_fixture_matrix_still_passes", fixture_matrix.get("ok") is True and fixture_matrix.get("status") == STATUS_PASS, {"case_count": fixture_matrix.get("case_count"), "case_ids": fixture_case_ids}),
        _check("l3_03_browser_start_authorization_fixture_matrix_required_cases_present", missing_fixture_case_ids == [], {"missing_fixture_case_ids": missing_fixture_case_ids}),
        _check("l3_05_browser_start_authorization_contract_gate_still_passes", contract_gate.get("ok") is True and contract_gate.get("status") == STATUS_PASS, {"check_count": len(contract_gate.get("checks", []))}),
        _check("l3_cli_readback_commands_remain_registered", missing_cli_commands == [], {"required_cli_commands": list(REQUIRED_CLI_COMMANDS), "missing_cli_commands": missing_cli_commands}),
        _check("l3_required_source_docs_tests_present", missing_repo_paths == [], {"missing_repo_paths": missing_repo_paths, "repo_path_state": repo_path_state}),
        _check("l3_aggregate_payload_json_safe", payload_json_safe, {"payload_json_safe": payload_json_safe}),
        _check("l3_aggregate_keeps_all_live_side_effects_blocked", all_passive_flags, {"side_effect_operations": list(LIVE_SIDE_EFFECT_OPERATIONS)}),
        _check("l3_aggregate_no_optional_browser_dependency_imports_present", forbidden_imports_present == [], {"forbidden_imports_present": forbidden_imports_present}),
        _check("l3_aggregate_did_not_load_optional_browser_dependencies", forbidden_imports_newly_loaded == [], {"forbidden_imports_newly_loaded": forbidden_imports_newly_loaded}),
    ]
    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "side_effect_operations": list(LIVE_SIDE_EFFECT_OPERATIONS),
        "repo_root": str(root),
        "startup_authorized": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": False,
        "required_fixture_case_ids": list(REQUIRED_FIXTURE_CASE_IDS),
        "missing_fixture_case_ids": missing_fixture_case_ids,
        "required_cli_commands": list(REQUIRED_CLI_COMMANDS),
        "missing_cli_commands": missing_cli_commands,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "baseline_decision": baseline_decision.to_payload(),
        "fixture_matrix": fixture_matrix,
        "contract_gate": contract_gate,
        "checks": checks,
        "command_plan": [
            r"py -m patchops.llm_browser.live_adapter_browser_start_authorization_l3_aggregate_readiness_gate --repo-root C:\dev\patchops --json --compact",
            r"py -m pytest -q tests/test_l3_07_browser_start_authorization_l3_aggregate_readiness_gate_current.py",
            r"py -m patchops.cli llm-browser browser-start-authorization --repo-root C:\dev\patchops --json --compact",
            r"py -m patchops.cli llm-browser browser-start-authorization-fixtures --repo-root C:\dev\patchops --json --compact",
            r"py -m patchops.cli llm-browser browser-start-authorization-contract-gate --repo-root C:\dev\patchops --json --compact",
        ],
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "L3.7 Browser Start Authorization Aggregate Readiness Gate",
        "-----------------------------------------------------------",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        "Startup    : authorized=false",
        f"Browser    : started={payload.get('browser_started')}",
        f"Session    : created={payload.get('browser_session_created')}",
        f"ProfileDir : created={payload.get('profile_directory_created')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"Next patch : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read back the passive L3 browser-start authorization aggregate readiness gate.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to the current module's repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l3_browser_start_authorization_aggregate_readiness_gate(args.repo_root)
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")) if args.compact else json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
