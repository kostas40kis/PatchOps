"""Passive L5 supervised-launch handoff fixture-matrix contract gate.

This module validates the L5 supervised-launch handoff fixture matrix as a
modelled/readback-only contract. It imports no Selenium/browser optional
packages, starts no browser, creates no browser session, creates no profile
directory, writes no adapter files, and performs no click/download/paste/send
or package-run operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_fixtures as fixtures
from patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract import (
    FORBIDDEN_OPTIONAL_ROOTS,
    STATUS_FAIL,
    STATUS_PASS,
)

PATCH = "L5.5"
PHASE = "L5"
NAME = "L5.5 Browser Start Supervised Launch Handoff Fixture Matrix Contract Gate"
NEXT_PATCH = "L5.6 Live adapter browser-start supervised launch handoff fixture matrix contract gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-fixture-matrix-contract-gate-only"
L5_04_COMMAND = "browser-start-supervised-launch-handoff-fixtures"

REQUIRED_CASE_IDS: tuple[str, ...] = (
    "edge_review_only_passive",
    "opera_prepare_only_passive",
    "mixed_case_browser_and_decision_normalized",
    "unsupported_browser_rejected_without_startup",
    "invalid_operator_decision_rejected_without_startup",
)

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_contract.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_fixtures.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_contract.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate.md",
    "tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py",
    "tests/test_l5_02_browser_start_supervised_launch_handoff_cli_readback_current.py",
    "tests/test_l5_03_browser_start_supervised_launch_handoff_fixture_matrix_current.py",
    "tests/test_l5_04_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_05_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_current.py",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L5.5 Live adapter browser-start supervised launch handoff fixture matrix contract gate",
    "supervised-launch handoff",
    "fixture matrix contract gate",
    "modelled/readback-only",
    "no Selenium import",
    "no browser start",
    "no browser session creation",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "L5.6 Live adapter browser-start supervised launch handoff fixture matrix contract gate CLI/readback",
)

READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-fixtures --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "llm-browser open",
    "open --browser",
    "run-once",
    "watch-downloads",
    "selenium",
    "webdriver",
    "start_browser",
    "browser_factory",
    "click_download",
    "paste_to_composer",
    "send_message",
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


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


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


def _json_safe(value: Mapping[str, Any]) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _llm_browser_command_names() -> list[str]:
    try:
        from patchops.llm_browser import commands
    except Exception as exc:  # pragma: no cover - surfaced in payload for diagnosis
        return [f"IMPORT_ERROR:{type(exc).__name__}:{exc}"]
    try:
        names = commands.llm_browser_command_names()
    except Exception as exc:  # pragma: no cover - surfaced in payload for diagnosis
        return [f"COMMAND_NAMES_ERROR:{type(exc).__name__}:{exc}"]
    return sorted(str(name) for name in names)


def build_contract_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L5.5 supervised-launch handoff contract gate payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    matrix = fixtures.build_supervised_launch_handoff_fixture_matrix(root)
    cases = list(matrix.get("cases", []))
    case_ids = [str(case.get("case_id", "")) for case in cases]
    cases_by_id = {str(case.get("case_id", "")): case for case in cases}
    missing_case_ids = [case_id for case_id in REQUIRED_CASE_IDS if case_id not in cases_by_id]

    repo_path_state = {rel: (root / rel).exists() for rel in REQUIRED_REPO_PATHS}
    missing_repo_paths = [rel for rel, exists in repo_path_state.items() if not exists]

    doc_path = root / "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate.md"
    doc_text = _read_text(doc_path)
    missing_doc_phrases = [phrase for phrase in DOC_REQUIRED_PHRASES if phrase not in doc_text]

    command_names = _llm_browser_command_names()
    command_registered = L5_04_COMMAND in command_names

    all_cases_ok = all(bool(case.get("case_ok")) for case in cases)
    all_startup_blocked = (
        matrix.get("startup_authorized") is False
        and matrix.get("startup_allowed") is False
        and matrix.get("live_driver_session_allowed") is False
    )
    all_no_browser = (
        matrix.get("browser_started") is False
        and matrix.get("browser_session_created") is False
        and matrix.get("driver_created") is False
    )
    all_no_profile_or_writes = (
        matrix.get("profile_directory_created") is False
        and matrix.get("filesystem_writes_performed") == []
    )
    all_no_side_effects = matrix.get("side_effects_performed") == []
    all_optional_deps_not_required = (
        matrix.get("optional_browser_dependencies_required") is False
        and matrix.get("selenium_imported") is False
    )

    optional_roots_present = _optional_roots_present()
    optional_roots_newly_loaded = _optional_roots_loaded_since(before_modules)

    checks = [
        _check("l5_supervised_launch_handoff_fixture_matrix_still_passes", matrix.get("ok") is True and matrix.get("status") == STATUS_PASS, {"patch": matrix.get("patch"), "status": matrix.get("status")}),
        _check("l5_supervised_launch_handoff_fixture_matrix_core_cases_present", not missing_case_ids, {"case_ids": case_ids, "missing_case_ids": missing_case_ids}),
        _check("l5_supervised_launch_handoff_fixture_matrix_all_cases_match_expectations", all_cases_ok),
        _check("l5_supervised_launch_handoff_contract_gate_keeps_startup_blocked", all_startup_blocked),
        _check("l5_supervised_launch_handoff_contract_gate_creates_no_browser_or_driver", all_no_browser),
        _check("l5_supervised_launch_handoff_contract_gate_creates_no_profile_or_adapter_writes", all_no_profile_or_writes),
        _check("l5_supervised_launch_handoff_contract_gate_executes_no_side_effects", all_no_side_effects),
        _check("l5_supervised_launch_handoff_contract_gate_requires_no_optional_browser_dependencies", all_optional_deps_not_required),
        _check("l5_supervised_launch_handoff_contract_gate_required_repo_paths_present", not missing_repo_paths, {"missing_repo_paths": missing_repo_paths}),
        _check("l5_supervised_launch_handoff_contract_gate_doc_contains_boundary", not missing_doc_phrases, {"missing_doc_phrases": missing_doc_phrases}),
        _check("l5_supervised_launch_handoff_fixture_cli_command_registered", command_registered, {"command": L5_04_COMMAND}),
        _check("l5_supervised_launch_handoff_contract_gate_command_plan_is_readback_only", _command_plan_is_readback_only(READBACK_COMMANDS)),
        _check("l5_supervised_launch_handoff_contract_gate_no_optional_browser_imports_present", not optional_roots_present, {"present": optional_roots_present}),
        _check("l5_supervised_launch_handoff_contract_gate_did_not_load_optional_browser_dependencies", not optional_roots_newly_loaded, {"newly_loaded": optional_roots_newly_loaded}),
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
        "source_matrix_patch": matrix.get("patch"),
        "source_matrix_status": matrix.get("status"),
        "case_count": len(cases),
        "case_ids": case_ids,
        "missing_case_ids": missing_case_ids,
        "missing_repo_paths": missing_repo_paths,
        "missing_doc_phrases": missing_doc_phrases,
        "l5_04_command_registered": command_registered,
        "llm_browser_command_names_checked": command_names,
        "readback_commands": list(READBACK_COMMANDS),
        "executed_validation_commands": [],
        "modelled_only": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "live_driver_session_allowed": False,
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
    checks.append(_check("l5_supervised_launch_handoff_contract_gate_payload_json_safe", _json_safe(payload)))
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
        f"Source Matrix   : {payload.get('source_matrix_patch')} / {payload.get('source_matrix_status')}",
        f"Cases           : {payload.get('case_count')}",
        f"Modelled Only   : {payload.get('modelled_only')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Session Created : {payload.get('browser_session_created')}",
        f"Driver Created  : {payload.get('driver_created')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"Selenium Import : {payload.get('selenium_imported')}",
        f"L5.4 CLI Present: {payload.get('l5_04_command_registered')}",
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

    payload = build_contract_gate(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
