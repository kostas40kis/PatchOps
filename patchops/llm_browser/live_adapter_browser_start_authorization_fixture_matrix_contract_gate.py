"""Passive L3 browser-start authorization fixture-matrix contract gate.

This module validates the L3.3 browser-start authorization fixture matrix as a
contract. It is intentionally passive: it imports no Selenium/browser optional
packages, starts no browser, creates no profile directory, writes no adapter
files, and performs no click/download/paste/send/package-run operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_browser_start_authorization_fixtures as fixtures
from patchops.llm_browser.live_adapter_browser_start_authorization import (
    FORBIDDEN_IMPORT_ROOTS,
    LIVE_SIDE_EFFECT_OPERATIONS,
    STATUS_FAIL,
    STATUS_PASS,
)

PATCH = "L3.5"
PHASE = "L3"
NAME = "llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate"
NEXT_PATCH = "L3.6 Live adapter browser-start authorization fixture matrix contract gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "passive-only"

REQUIRED_CASE_IDS = (
    "edge_default_missing_acknowledgements",
    "opera_ack_all_permission_flags_modelled_only",
    "unsupported_browser_rejected",
    "shared_profile_rejected",
    "download_paste_send_side_effects_blocked",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_browser_start_authorization.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixtures.py",
    "docs/llm_browser_live_adapter_browser_start_authorization.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_cli_readback.md",
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
    return {
        "name": name,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": bool(ok),
        "details": dict(details or {}),
    }


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _forbidden_imports_loaded_since(before_modules: set[str]) -> list[str]:
    after = set(sys.modules)
    loaded: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in after - before_modules):
            loaded.append(root)
    return sorted(set(loaded))


def _forbidden_imports_present() -> list[str]:
    present: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            present.append(root)
    return sorted(set(present))


def build_contract_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build a passive contract-gate payload for the L3 authorization fixture matrix."""
    root = resolve_repo_root(repo_root)
    before_modules = set(sys.modules)
    matrix = fixtures.build_l3_browser_start_authorization_fixture_matrix(root)
    cases = list(matrix.get("cases", []))
    case_ids = [str(case.get("case_id", "")) for case in cases]
    cases_by_id = {str(case.get("case_id", "")): case for case in cases}
    missing_case_ids = [case_id for case_id in REQUIRED_CASE_IDS if case_id not in cases_by_id]

    repo_path_state = {rel: (root / rel).exists() for rel in REQUIRED_REPO_PATHS}
    missing_repo_paths = [rel for rel, exists in repo_path_state.items() if not exists]

    all_expectations_met = all(bool(case.get("expectations_met")) for case in cases)
    all_startup_blocked = all(case.get("startup_authorized") is False for case in cases)
    all_no_browser = all(
        case.get("browser_started") is False and case.get("browser_session_created") is False
        for case in cases
    )
    all_no_profile_or_writes = all(
        case.get("profile_directory_created") is False and case.get("filesystem_writes_performed", []) == []
        for case in cases
    )
    all_no_side_effects = all(case.get("side_effects_performed", []) == [] for case in cases)
    all_optional_deps_not_required = all(
        case.get("optional_browser_dependencies_required") is False and case.get("selenium_imported") is False
        for case in cases
    )
    side_effect_request_cases = [
        case_id for case_id, case in cases_by_id.items() if case.get("side_effects_requested", [])
    ]
    invalid_cases = [case_id for case_id, case in cases_by_id.items() if case.get("invalid_fields", [])]
    blocked_reason_by_case = {case_id: cases_by_id[case_id].get("blocked_reasons", []) for case_id in case_ids}
    forbidden_imports_present = _forbidden_imports_present()
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    checks = [
        _check(
            "l3_browser_start_authorization_fixture_matrix_still_passes",
            matrix.get("ok") is True and matrix.get("status") == STATUS_PASS,
            {"patch": matrix.get("patch"), "status": matrix.get("status")},
        ),
        _check(
            "l3_browser_start_authorization_fixture_matrix_core_cases_present",
            missing_case_ids == [],
            {"case_ids": case_ids, "missing_case_ids": missing_case_ids},
        ),
        _check(
            "l3_browser_start_authorization_fixture_matrix_all_expectations_met",
            all_expectations_met,
            {"expectations_met_by_case": {case_id: cases_by_id[case_id].get("expectations_met") for case_id in case_ids}},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_blocks_startup",
            all_startup_blocked,
            {"startup_authorized_by_case": {case_id: cases_by_id[case_id].get("startup_authorized") for case_id in case_ids}},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_creates_no_browser_session",
            all_no_browser,
            {"browser_started_by_case": {case_id: cases_by_id[case_id].get("browser_started") for case_id in case_ids}},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_creates_no_profile_directory",
            all_no_profile_or_writes,
            {"profile_directory_created_by_case": {case_id: cases_by_id[case_id].get("profile_directory_created") for case_id in case_ids}},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_requested_side_effects_modelled_not_executed",
            bool(side_effect_request_cases) and all_no_side_effects,
            {"side_effect_request_cases": side_effect_request_cases},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_invalid_requests_blocked_without_side_effects",
            {"unsupported_browser_rejected", "shared_profile_rejected"}.issubset(set(invalid_cases)) and all_no_side_effects,
            {"invalid_cases": invalid_cases, "blocked_reason_by_case": blocked_reason_by_case},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_payload_json_safe",
            _json_safe(matrix),
            {"case_count": len(cases)},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_required_repo_paths_present",
            missing_repo_paths == [],
            {"repo_path_state": repo_path_state, "missing_repo_paths": missing_repo_paths},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_no_optional_browser_dependency_imports_present",
            forbidden_imports_present == [],
            {"forbidden_imports_present": forbidden_imports_present},
        ),
        _check(
            "l3_browser_start_authorization_contract_gate_did_not_load_optional_browser_dependencies",
            forbidden_imports_newly_loaded == [] and all_optional_deps_not_required,
            {"forbidden_imports_newly_loaded": forbidden_imports_newly_loaded},
        ),
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
        "startup_authorized": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": False,
        "case_count": len(cases),
        "case_ids": case_ids,
        "required_case_ids": list(REQUIRED_CASE_IDS),
        "missing_case_ids": missing_case_ids,
        "invalid_cases": invalid_cases,
        "side_effect_request_cases": side_effect_request_cases,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "fixture_matrix": matrix,
        "checks": checks,
        "command_plan": [
            "py -m patchops.llm_browser.live_adapter_browser_start_authorization_fixture_matrix_contract_gate --repo-root C:\\dev\\patchops --json --compact",
            "py -m pytest -q tests/test_l3_05_browser_start_authorization_fixture_matrix_contract_gate_current.py",
        ],
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "L3.5 Browser Start Authorization Fixture Matrix Contract Gate",
        "---------------------------------------------------------------",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
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
    parser = argparse.ArgumentParser(description="Read back the passive L3.5 browser-start authorization fixture-matrix contract gate.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to the current module's repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_contract_gate(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
