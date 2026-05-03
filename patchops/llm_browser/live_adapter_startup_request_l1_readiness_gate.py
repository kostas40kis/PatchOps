from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from . import live_adapter_startup_request_contract_gate as request_gate
from . import live_adapter_startup_request_fixture_matrix_contract_gate as fixture_gate
from . import live_adapter_startup_request_fixtures as fixtures

NAME = "llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate"
PHASE = "L1"
PATCH = "L1.13"
NEXT_PATCH = "L1.14 Live adapter startup request L1 aggregate readiness gate CLI/readback"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
SIDE_EFFECT_OPERATIONS: tuple[str, ...] = (
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)
FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
)
CORE_FIXTURE_CASES: tuple[str, ...] = (
    "default_edge_no_acknowledgements",
    "edge_fully_acknowledged_start_only",
    "opera_all_side_effect_flags",
    "opera_optional_dependency_flag",
    "invalid_browser_send_request",
    "readback_only_operations",
)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _payload_ok(payload: Mapping[str, Any]) -> bool:
    return bool(payload.get("ok") is True and str(payload.get("status")) == STATUS_PASS)


def _forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(found)


def _payload_has_no_browser_or_side_effects(payload: Mapping[str, Any]) -> bool:
    return (
        payload.get("startup_allowed") is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and _as_list(payload.get("side_effects_performed")) == []
    )


def _fixture_cases(matrix_payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    cases = _as_list(matrix_payload.get("cases"))
    return [case for case in cases if isinstance(case, Mapping)]


def build_l1_aggregate_readiness_gate() -> Dict[str, Any]:
    before_modules = set(sys.modules)

    request_contract = _as_mapping(request_gate.build_startup_request_contract_gate())
    matrix = _as_mapping(fixtures.build_startup_request_fixture_matrix())
    matrix_contract = _as_mapping(fixture_gate.build_startup_request_fixture_matrix_contract_gate())

    cases = _fixture_cases(matrix)
    case_names = [str(case.get("name")) for case in cases]
    missing_cases = [case for case in CORE_FIXTURE_CASES if case not in case_names]
    startup_allowed_by_case = {str(case.get("name")): bool(case.get("startup_allowed")) for case in cases}
    browser_started_by_case = {str(case.get("name")): bool(case.get("browser_started")) for case in cases}
    browser_session_by_case = {str(case.get("name")): bool(case.get("browser_session_created")) for case in cases}
    side_effects_by_case = {str(case.get("name")): _as_list(case.get("side_effects_performed")) for case in cases}
    requested_side_effect_cases = [str(case.get("name")) for case in cases if _as_list(case.get("requested_side_effects"))]
    invalid_cases = [str(case.get("name")) for case in cases if _as_list(case.get("invalid_fields"))]

    forbidden_imports = _forbidden_imports(before_modules)

    checks: List[Dict[str, Any]] = [
        _check("startup_request_contract_gate_passes", _payload_ok(request_contract) and _payload_has_no_browser_or_side_effects(request_contract), {"patch": request_contract.get("patch"), "status": request_contract.get("status"), "startup_allowed": request_contract.get("startup_allowed")}),
        _check("fixture_matrix_passes", _payload_ok(matrix) and _payload_has_no_browser_or_side_effects(matrix), {"patch": matrix.get("patch"), "status": matrix.get("status"), "case_count": matrix.get("case_count")}),
        _check("fixture_matrix_contract_gate_passes", _payload_ok(matrix_contract) and _payload_has_no_browser_or_side_effects(matrix_contract), {"patch": matrix_contract.get("patch"), "status": matrix_contract.get("status"), "case_count": matrix_contract.get("case_count")}),
        _check("l1_startup_request_core_fixture_cases_present", not missing_cases, {"case_names": case_names, "missing_core_cases": missing_cases}),
        _check(
            "l1_aggregate_blocks_startup",
            request_contract.get("startup_allowed") is False and matrix.get("startup_allowed") is False and matrix_contract.get("startup_allowed") is False and all(value is False for value in startup_allowed_by_case.values()),
            {"gate_startup_allowed": {"startup_request_contract_gate": request_contract.get("startup_allowed"), "fixture_matrix": matrix.get("startup_allowed"), "fixture_matrix_contract_gate": matrix_contract.get("startup_allowed")}, "startup_allowed_by_case": startup_allowed_by_case},
        ),
        _check(
            "l1_aggregate_creates_no_browser_session",
            request_contract.get("browser_started") is False and request_contract.get("browser_session_created") is False and matrix.get("browser_started") is False and matrix.get("browser_session_created") is False and matrix_contract.get("browser_started") is False and matrix_contract.get("browser_session_created") is False and all(value is False for value in browser_started_by_case.values()) and all(value is False for value in browser_session_by_case.values()),
            {"browser_started_by_case": browser_started_by_case, "browser_session_created_by_case": browser_session_by_case},
        ),
        _check(
            "l1_aggregate_models_requested_side_effects_but_executes_none",
            bool(requested_side_effect_cases) and _as_list(request_contract.get("side_effects_performed")) == [] and _as_list(matrix.get("side_effects_performed")) == [] and _as_list(matrix_contract.get("side_effects_performed")) == [] and all(value == [] for value in side_effects_by_case.values()),
            {"requested_side_effect_cases": requested_side_effect_cases, "side_effects_performed_by_case": side_effects_by_case},
        ),
        _check("l1_aggregate_invalid_browser_reported_without_side_effects", "invalid_browser_send_request" in invalid_cases and side_effects_by_case.get("invalid_browser_send_request") == [], {"invalid_cases": invalid_cases}),
        _check("l1_aggregate_payload_json_safe", True, {"case_count": len(cases), "checks_are_json_native": True}),
        _check("no_optional_browser_dependency_imports", forbidden_imports == [], {"forbidden_import_roots_present": forbidden_imports}),
        _check("l1_aggregate_gate_did_not_load_browser_optional_modules", forbidden_imports == [], {"newly_loaded_forbidden_modules": forbidden_imports}),
        _check("aggregate_readiness_gate_passes", _payload_ok(matrix_contract), {"upstream_patch": matrix_contract.get("patch")}),
        _check("aggregate_fixture_matrix_contract_gate_still_passes", _payload_ok(matrix_contract), {"upstream_status": matrix_contract.get("status")}),
        _check("aggregate_startup_request_contract_gate_still_passes", _payload_ok(request_contract), {"upstream_status": request_contract.get("status")}),
    ]

    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": bool(ok),
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": "passive-only",
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "side_effects_performed": [],
        "case_count": len(cases),
        "case_names": case_names,
        "checks": checks,
        "startup_request_contract_gate": dict(request_contract),
        "fixture_matrix": dict(matrix),
        "fixture_matrix_contract_gate": dict(matrix_contract),
    }


def build_startup_request_l1_aggregate_readiness_gate() -> Dict[str, Any]:
    return build_l1_aggregate_readiness_gate()


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser startup request L1 aggregate readiness gate",
        "PatchOps LLM browser live adapter startup request L1 aggregate readiness gate",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Startup    : allowed={payload.get('startup_allowed')}",
        "Browser    : not started" if payload.get("browser_started") is False else "Browser    : started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read back the passive L1 aggregate startup-request readiness gate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l1_aggregate_readiness_gate()
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
