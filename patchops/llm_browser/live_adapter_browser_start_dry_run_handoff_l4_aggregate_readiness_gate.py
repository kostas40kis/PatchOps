"""Passive L4 browser-start dry-run handoff aggregate readiness gate.

This module aggregates the already-accepted passive L4 dry-run handoff stack.
It is deliberately readback-only: no Selenium import, no browser start, no
browser session creation, no profile directory creation, no adapter filesystem
writes, and no click/download/paste/send/package-run side effect from adapter logic.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_contract import (
    BLOCKED_SIDE_EFFECTS,
    FORBIDDEN_OPTIONAL_ROOTS,
    STATUS_FAIL,
    STATUS_PASS,
    build_browser_start_dry_run_handoff_contract,
)
from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixtures import (
    build_browser_start_dry_run_handoff_fixture_matrix,
)
from patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate import (
    build_contract_gate,
)

PATCH = "L4.7"
PHASE = "L4"
NAME = "L4.7 Browser Start Dry-Run Handoff Aggregate Readiness Gate"
NEXT_PATCH = "L4.8 Live adapter browser-start dry-run handoff L4 aggregate readiness gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "dry-run-handoff-l4-aggregate-readiness-only"

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_contract.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate.md",
    "tests/test_l4_01_browser_start_dry_run_handoff_contract_current.py",
    "tests/test_l4_02_browser_start_dry_run_handoff_cli_readback_current.py",
    "tests/test_l4_03_browser_start_dry_run_handoff_fixture_matrix_current.py",
    "tests/test_l4_04_browser_start_dry_run_handoff_fixture_matrix_cli_readback_current.py",
    "tests/test_l4_05_browser_start_dry_run_handoff_fixture_matrix_contract_gate_current.py",
    "tests/test_l4_06_browser_start_dry_run_handoff_contract_gate_cli_readback_current.py",
    "tests/test_l4_07_browser_start_dry_run_handoff_l4_aggregate_readiness_gate_current.py",
)

REQUIRED_CLI_COMMANDS: tuple[str, ...] = (
    "browser-start-dry-run-handoff",
    "browser-start-dry-run-handoff-fixtures",
    "browser-start-dry-run-handoff-contract-gate",
)

REQUIRED_FIXTURE_CASE_IDS: tuple[str, ...] = (
    "edge_dry_run_handoff_passive",
    "opera_dry_run_handoff_passive",
    "mixed_case_edge_normalized",
    "unsupported_browser_rejected_without_startup",
)

READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-dry-run-handoff --repo-root C:\\dev\\patchops --browser edge --json --compact",
    "py -m patchops.cli llm-browser browser-start-dry-run-handoff --repo-root C:\\dev\\patchops --browser opera --json --compact",
    "py -m patchops.cli llm-browser browser-start-dry-run-handoff-fixtures --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-dry-run-handoff-contract-gate --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "open --browser",
    "run-once",
    "watch-downloads",
    "selenium",
    "webdriver",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_or_submit",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


def _missing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    return [path for path in paths if not (root / path).exists()]


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _json_safe(value: Mapping[str, Any]) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _optional_roots_present() -> list[str]:
    present: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            present.append(root)
    return sorted(set(present))


def _optional_roots_loaded_since(before_modules: set[str]) -> list[str]:
    newly_loaded = set(sys.modules) - before_modules
    loaded: list[str] = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            loaded.append(root)
    return sorted(set(loaded))


def _command_plan_is_readback_only(commands: Sequence[str]) -> bool:
    text = "\n".join(commands).lower()
    return not any(fragment.lower() in text for fragment in FORBIDDEN_COMMAND_FRAGMENTS)


def _safe_command_names() -> list[str]:
    try:
        from patchops.llm_browser import commands
    except Exception as exc:  # pragma: no cover - surfaced in payload for operator diagnosis
        return [f"IMPORT_ERROR:{type(exc).__name__}:{exc}"]
    try:
        names = commands.llm_browser_command_names()
    except Exception as exc:  # pragma: no cover - surfaced in payload for operator diagnosis
        return [f"COMMAND_NAMES_ERROR:{type(exc).__name__}:{exc}"]
    return sorted(str(name) for name in names)


def build_l4_browser_start_dry_run_handoff_aggregate_readiness_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L4 aggregate readiness gate payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    edge_contract = build_browser_start_dry_run_handoff_contract(root, browser="edge")
    opera_contract = build_browser_start_dry_run_handoff_contract(root, browser="opera")
    fixture_matrix = build_browser_start_dry_run_handoff_fixture_matrix(root)
    contract_gate = build_contract_gate(root)

    command_names = _safe_command_names()
    fixture_cases = list(fixture_matrix.get("cases", []))
    fixture_case_ids = [str(case.get("case_id", "")) for case in fixture_cases]
    missing_fixture_case_ids = [case_id for case_id in REQUIRED_FIXTURE_CASE_IDS if case_id not in fixture_case_ids]
    missing_cli_commands = [command for command in REQUIRED_CLI_COMMANDS if command not in command_names]
    repo_path_state = {path: (root / path).exists() for path in REQUIRED_REPO_PATHS}
    missing_repo_paths = [path for path, exists in repo_path_state.items() if not exists]

    optional_roots_present = _optional_roots_present()
    optional_roots_newly_loaded = _optional_roots_loaded_since(before_modules)

    all_passive_flags = (
        edge_contract.get("startup_authorized") is False
        and edge_contract.get("startup_allowed") is False
        and edge_contract.get("browser_started") is False
        and edge_contract.get("browser_session_created") is False
        and edge_contract.get("driver_created") is False
        and edge_contract.get("profile_directory_created") is False
        and edge_contract.get("side_effects_performed") == []
        and edge_contract.get("filesystem_writes_performed") == []
        and opera_contract.get("startup_authorized") is False
        and opera_contract.get("startup_allowed") is False
        and opera_contract.get("browser_started") is False
        and opera_contract.get("browser_session_created") is False
        and opera_contract.get("driver_created") is False
        and opera_contract.get("profile_directory_created") is False
        and opera_contract.get("side_effects_performed") == []
        and opera_contract.get("filesystem_writes_performed") == []
        and fixture_matrix.get("startup_authorized") is False
        and fixture_matrix.get("startup_allowed") is False
        and fixture_matrix.get("browser_started") is False
        and fixture_matrix.get("browser_session_created") is False
        and fixture_matrix.get("driver_created") is False
        and fixture_matrix.get("profile_directory_created") is False
        and fixture_matrix.get("side_effects_performed") == []
        and fixture_matrix.get("filesystem_writes_performed") == []
        and contract_gate.get("startup_authorized") is False
        and contract_gate.get("startup_allowed") is False
        and contract_gate.get("browser_started") is False
        and contract_gate.get("browser_session_created") is False
        and contract_gate.get("driver_created") is False
        and contract_gate.get("profile_directory_created") is False
        and contract_gate.get("side_effects_performed") == []
        and contract_gate.get("filesystem_writes_performed") == []
    )

    checks = [
        _check("l4_01_edge_dry_run_handoff_contract_still_passes", edge_contract.get("ok") is True and edge_contract.get("status") == STATUS_PASS, {"patch": edge_contract.get("patch")}),
        _check("l4_01_opera_dry_run_handoff_contract_still_passes", opera_contract.get("ok") is True and opera_contract.get("status") == STATUS_PASS, {"patch": opera_contract.get("patch")}),
        _check("l4_03_dry_run_handoff_fixture_matrix_still_passes", fixture_matrix.get("ok") is True and fixture_matrix.get("status") == STATUS_PASS, {"case_count": fixture_matrix.get("case_count"), "case_ids": fixture_case_ids}),
        _check("l4_03_required_fixture_cases_present", not missing_fixture_case_ids, {"missing_fixture_case_ids": missing_fixture_case_ids}),
        _check("l4_05_dry_run_handoff_contract_gate_still_passes", contract_gate.get("ok") is True and contract_gate.get("status") == STATUS_PASS, {"check_count": len(contract_gate.get("checks", []))}),
        _check("l4_cli_readback_commands_remain_registered", not missing_cli_commands, {"required_cli_commands": list(REQUIRED_CLI_COMMANDS), "missing_cli_commands": missing_cli_commands}),
        _check("l4_required_source_docs_tests_present", not missing_repo_paths, {"missing_repo_paths": missing_repo_paths}),
        _check("l4_command_plan_is_readback_only", _command_plan_is_readback_only(READBACK_COMMANDS), {"readback_commands": list(READBACK_COMMANDS)}),
        _check("l4_aggregate_keeps_all_live_side_effects_blocked", all_passive_flags, {"blocked_side_effects": list(BLOCKED_SIDE_EFFECTS)}),
        _check("l4_aggregate_no_optional_browser_dependency_imports_present", not optional_roots_present, {"present": optional_roots_present}),
        _check("l4_aggregate_did_not_load_optional_browser_dependencies", not optional_roots_newly_loaded, {"newly_loaded": optional_roots_newly_loaded}),
    ]

    payload: dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS,
        "ok": True,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "source_contract_patch": edge_contract.get("patch"),
        "source_fixture_matrix_patch": fixture_matrix.get("patch"),
        "source_contract_gate_patch": contract_gate.get("patch"),
        "source_contract_status": edge_contract.get("status"),
        "source_fixture_matrix_status": fixture_matrix.get("status"),
        "source_contract_gate_status": contract_gate.get("status"),
        "case_count": fixture_matrix.get("case_count"),
        "case_ids": fixture_case_ids,
        "missing_fixture_case_ids": missing_fixture_case_ids,
        "required_cli_commands": list(REQUIRED_CLI_COMMANDS),
        "missing_cli_commands": missing_cli_commands,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "repo_path_state": repo_path_state,
        "readback_commands": list(READBACK_COMMANDS),
        "executed_validation_commands": [],
        "dry_run_only": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "optional_browser_dependencies_imported": optional_roots_present,
        "forbidden_optional_imports_newly_loaded": optional_roots_newly_loaded,
        "selenium_imported": "selenium" in optional_roots_present,
        "git_commit_executed": False,
        "git_push_executed": False,
        "checks": checks,
    }
    checks.append(_check("l4_aggregate_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status          : {payload.get('status')}",
        f"Patch           : {payload.get('patch')}",
        f"Source Contract : {payload.get('source_contract_patch')} / {payload.get('source_contract_status')}",
        f"Source Matrix   : {payload.get('source_fixture_matrix_patch')} / {payload.get('source_fixture_matrix_status')}",
        f"Source Gate     : {payload.get('source_contract_gate_patch')} / {payload.get('source_contract_gate_status')}",
        f"Case Count      : {payload.get('case_count')}",
        f"Dry Run Only    : {payload.get('dry_run_only')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"Selenium Import : {payload.get('selenium_imported')}",
        f"Next Patch      : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    lines.extend(["", "Readback command plan:"])
    for command in payload.get("readback_commands", []):
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_l4_browser_start_dry_run_handoff_aggregate_readiness_gate(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
