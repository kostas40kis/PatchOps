"""Passive L2 browser-profile preflight fixture-matrix contract gate.

This module validates the L2.3 browser-profile preflight fixture matrix as a
contract. It is intentionally passive: it imports no Selenium/browser optional
packages, starts no browser, creates no profile directory, writes no adapter
files, and performs no click/download/paste/send/package-run operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from patchops.llm_browser import live_adapter_browser_profile_preflight_fixtures as fixtures

PATCH = "L2.5"
PHASE = "L2"
NAME = "llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate"
NEXT_PATCH = "L2.6 Live adapter browser profile preflight fixture matrix contract gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "passive-only"
SIDE_EFFECT_OPERATIONS = [
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
]
FORBIDDEN_IMPORT_ROOTS = ("selenium", "playwright", "pyppeteer")
REQUIRED_CASES = [
    "default_edge_no_acknowledgements",
    "opera_acknowledged_start_and_profile_request",
    "edge_acknowledged_profile_only_request",
    "invalid_browser_send_request",
    "custom_profile_root_and_name",
    "opera_optional_dependency_flag",
]


def _check(name: str, ok: bool, details: Any | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"name": name, "ok": bool(ok), "status": "PASS" if ok else "FAIL"}
    if details is not None:
        item["details"] = details
    return item


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _loaded_forbidden_modules(before: set[str]) -> list[str]:
    after = set(sys.modules)
    loaded: list[str] = []
    for module_name in after - before:
        root = module_name.split(".", 1)[0]
        if root in FORBIDDEN_IMPORT_ROOTS:
            loaded.append(module_name)
    return sorted(loaded)


def build_contract_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build a passive contract-gate payload for the L2 profile fixture matrix."""
    before_modules = set(sys.modules)
    root = Path(repo_root).resolve() if repo_root else Path.cwd()
    matrix = fixtures.build_browser_profile_preflight_fixture_matrix(root)
    cases = list(matrix.get("cases", []))
    case_names = [str(case.get("name", "")) for case in cases]
    cases_by_name = {str(case.get("name", "")): case for case in cases}
    missing_cases = [name for name in REQUIRED_CASES if name not in cases_by_name]

    all_case_ok = all(case.get("ok") is True for case in cases)
    all_block_startup = all(case.get("startup_allowed") is False for case in cases)
    all_no_browser = all(
        case.get("browser_started") is False and case.get("browser_session_created") is False
        for case in cases
    )
    all_no_profile_or_writes = all(
        case.get("profile_directory_created") is False and not case.get("filesystem_writes_performed", [])
        for case in cases
    )
    all_no_side_effects = all(not case.get("side_effects_performed", []) for case in cases)
    requested_side_effect_cases = [
        str(case.get("name", "")) for case in cases if case.get("requested_side_effects", [])
    ]
    invalid_cases = [str(case.get("name", "")) for case in cases if case.get("invalid_fields", [])]
    invalid_without_side_effects = all(
        not cases_by_name[name].get("side_effects_performed", [])
        and cases_by_name[name].get("startup_allowed") is False
        and cases_by_name[name].get("browser_started") is False
        and cases_by_name[name].get("profile_directory_created") is False
        for name in invalid_cases
    )
    profile_paths_by_case = {
        str(case.get("name", "")): str(case.get("profile_path", ""))
        for case in cases
    }
    forbidden_import_roots_present = [
        root_name for root_name in FORBIDDEN_IMPORT_ROOTS if root_name in sys.modules
    ]
    newly_loaded_forbidden_modules = _loaded_forbidden_modules(before_modules)

    checks = [
        _check(
            "l2_profile_fixture_matrix_still_passes",
            matrix.get("ok") is True,
            {"patch": matrix.get("patch"), "status": matrix.get("status")},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_core_cases_present",
            not missing_cases,
            {"case_names": case_names, "missing_core_cases": missing_cases},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_all_cases_pass",
            all_case_ok,
            {"case_ok_by_case": {str(case.get("name", "")): case.get("ok") for case in cases}},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_blocks_startup",
            all_block_startup,
            {"startup_allowed_by_case": {str(case.get("name", "")): case.get("startup_allowed") for case in cases}},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_creates_no_browser_session",
            all_no_browser,
            {
                "browser_started_by_case": {str(case.get("name", "")): case.get("browser_started") for case in cases},
                "browser_session_created_by_case": {str(case.get("name", "")): case.get("browser_session_created") for case in cases},
            },
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_creates_no_profile_directory",
            all_no_profile_or_writes,
            {
                "profile_directory_created_by_case": {str(case.get("name", "")): case.get("profile_directory_created") for case in cases},
                "filesystem_writes_by_case": {str(case.get("name", "")): case.get("filesystem_writes_performed", []) for case in cases},
            },
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_requested_side_effects_modelled_not_executed",
            bool(requested_side_effect_cases) and all_no_side_effects,
            {
                "requested_side_effect_cases": requested_side_effect_cases,
                "side_effects_performed_by_case": {str(case.get("name", "")): case.get("side_effects_performed", []) for case in cases},
            },
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_invalid_browser_reported_without_side_effects",
            invalid_cases == ["invalid_browser_send_request"] and invalid_without_side_effects,
            {"invalid_cases": invalid_cases},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_profile_paths_modelled_only",
            bool(profile_paths_by_case) and all_no_profile_or_writes,
            {"profile_paths_by_case": profile_paths_by_case},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_payload_json_safe",
            _json_safe(matrix),
            {"case_count": len(cases)},
        ),
        _check(
            "no_optional_browser_dependency_imports",
            not forbidden_import_roots_present,
            {"forbidden_import_roots_present": forbidden_import_roots_present},
        ),
        _check(
            "l2_profile_fixture_matrix_contract_gate_did_not_load_browser_optional_modules",
            not newly_loaded_forbidden_modules,
            {"newly_loaded_forbidden_modules": newly_loaded_forbidden_modules},
        ),
    ]
    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": "PASS" if ok else "FAIL",
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "side_effect_operations": SIDE_EFFECT_OPERATIONS,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "case_count": len(cases),
        "case_names": case_names,
        "required_core_cases": REQUIRED_CASES,
        "missing_core_cases": missing_cases,
        "invalid_cases": invalid_cases,
        "requested_side_effect_cases": requested_side_effect_cases,
        "profile_paths_by_case": profile_paths_by_case,
        "fixture_matrix": matrix,
        "checks": checks,
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser profile preflight fixture matrix contract gate",
        "PatchOps LLM browser live adapter browser profile preflight fixture matrix contract gate",
        f"Name       : {payload['name']}",
        f"Phase      : {payload['phase']}",
        f"Patch      : {payload['patch']}",
        f"Status     : {payload['status']}",
        f"OK         : {payload['ok']}",
        f"Cases      : {payload['case_count']}",
        "Startup    : allowed=false",
        "BrowserRun : not started",
        "Profile    : created=false",
        "SideEffects: []",
        "Filesystem : writes=[]",
        "Case names : " + ", ".join(payload.get("case_names", [])),
        "Checks:",
    ]
    for check in payload.get("checks", []):
        lines.append(f"- {check['name']}: {check['status']}")
    lines.append(f"Next patch : {payload['next_patch']}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Passive L2 browser profile fixture-matrix contract gate")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_contract_gate(args.repo_root)
    if args.json:
        indent = None if args.compact else 2
        print(json.dumps(payload, indent=indent, sort_keys=True))
    else:
        print(render_text(payload))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
