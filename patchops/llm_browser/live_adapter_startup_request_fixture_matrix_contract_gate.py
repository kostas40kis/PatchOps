from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from patchops.llm_browser import live_adapter_startup_request_fixtures as fixtures

try:  # optional upstream gate check; passive import only
    from patchops.llm_browser import live_adapter_startup_request_contract_gate as startup_request_contract_gate
except Exception:  # pragma: no cover - defensive for partially applied trees
    startup_request_contract_gate = None  # type: ignore[assignment]

PATCH = "L1.11"
PHASE = "L1"
NAME = "llm_browser_live_adapter_startup_request_fixture_matrix_contract_gate"
NEXT_PATCH = "L1.12 Live adapter startup request fixture matrix contract gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "passive-only"

SIDE_EFFECT_OPERATIONS = (
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
)
FORBIDDEN_IMPORT_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil")
CORE_CASES = (
    "default_edge_no_acknowledgements",
    "edge_fully_acknowledged_start_only",
    "opera_all_side_effect_flags",
    "opera_optional_dependency_flag",
    "invalid_browser_send_request",
    "readback_only_operations",
)


def _json_safe(value: Any) -> bool:
    try:
        json.loads(json.dumps(value, sort_keys=True))
        return True
    except Exception:
        return False


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "name": name,
        "status": "PASS" if ok else "FAIL",
        "ok": bool(ok),
        "details": dict(details or {}),
    }


def _case_side_effects(case: Mapping[str, Any]) -> List[str]:
    effects = case.get("requested_side_effects", [])
    return [str(item) for item in effects]


def _case_performed(case: Mapping[str, Any]) -> List[str]:
    performed = case.get("side_effects_performed", [])
    return [str(item) for item in performed]


def _decision(case: Mapping[str, Any]) -> Mapping[str, Any]:
    value = case.get("decision")
    return value if isinstance(value, Mapping) else {}


def _bool_payload(value: Any) -> bool:
    return bool(value) is True


def _loaded_forbidden_modules(before: Iterable[str]) -> List[str]:
    before_roots = {name.split(".", 1)[0] for name in before}
    after_roots = {name.split(".", 1)[0] for name in sys.modules}
    return sorted(root for root in FORBIDDEN_IMPORT_ROOTS if root in after_roots and root not in before_roots)


def _upstream_gate_payload() -> Mapping[str, Any]:
    if startup_request_contract_gate is None:
        return {"ok": False, "status": "MISSING", "reason": "startup request contract gate module is unavailable"}
    builder = getattr(startup_request_contract_gate, "build_startup_request_contract_gate", None)
    if not callable(builder):
        return {"ok": False, "status": "MISSING", "reason": "build_startup_request_contract_gate is unavailable"}
    payload = builder()
    return payload if isinstance(payload, Mapping) else {"ok": False, "status": "INVALID"}


def build_startup_request_fixture_matrix_contract_gate() -> Dict[str, Any]:
    before_modules = set(sys.modules)
    matrix = fixtures.build_startup_request_fixture_matrix()
    if not isinstance(matrix, Mapping):
        matrix = {"ok": False, "status": "FAIL", "cases": []}

    cases_raw = matrix.get("cases", [])
    cases: List[Mapping[str, Any]] = [case for case in cases_raw if isinstance(case, Mapping)]
    case_names = [str(case.get("name", "")) for case in cases]
    case_name_set = set(case_names)
    missing_core_cases = [name for name in CORE_CASES if name not in case_name_set]

    startup_by_case = {str(case.get("name", "")): bool(case.get("startup_allowed")) for case in cases}
    browser_started_by_case = {str(case.get("name", "")): bool(case.get("browser_started")) for case in cases}
    browser_session_by_case = {str(case.get("name", "")): bool(case.get("browser_session_created")) for case in cases}
    performed_by_case = {str(case.get("name", "")): _case_performed(case) for case in cases}
    requested_by_case = {str(case.get("name", "")): _case_side_effects(case) for case in cases}

    all_blocked = all(value is False for value in startup_by_case.values()) and bool(cases)
    all_no_browser = all(value is False for value in browser_started_by_case.values()) and all(value is False for value in browser_session_by_case.values()) and bool(cases)
    all_no_performed = all(not performed for performed in performed_by_case.values()) and bool(cases)
    requested_cases = sorted(name for name, effects in requested_by_case.items() if effects)
    invalid_cases = sorted(
        str(case.get("name", ""))
        for case in cases
        if case.get("invalid_fields")
    )

    all_decisions_blocked = all(bool(_decision(case).get("startup_allowed")) is False for case in cases) and bool(cases)
    all_decisions_no_browser = all(bool(_decision(case).get("browser_started")) is False and bool(_decision(case).get("browser_session_created")) is False for case in cases) and bool(cases)
    all_decisions_no_performed = all(not _decision(case).get("side_effects_performed", []) for case in cases) and bool(cases)

    matrix_ok = bool(matrix.get("ok")) and matrix.get("status") == "PASS" and matrix.get("startup_allowed") is False
    upstream_gate = _upstream_gate_payload()
    forbidden_loaded = _loaded_forbidden_modules(before_modules)

    checks = [
        _check(
            "fixture_matrix_payload_contract",
            matrix_ok and int(matrix.get("case_count", len(cases))) == len(cases) and len(cases) >= len(CORE_CASES),
            {"matrix_status": matrix.get("status"), "case_count": len(cases)},
        ),
        _check(
            "fixture_matrix_core_cases",
            not missing_core_cases,
            {"case_names": case_names, "missing_core_cases": missing_core_cases},
        ),
        _check(
            "all_fixture_decisions_block_startup",
            all_blocked and all_decisions_blocked,
            {"startup_allowed_by_case": startup_by_case},
        ),
        _check(
            "all_fixture_decisions_create_no_browser_session",
            all_no_browser and all_decisions_no_browser,
            {"browser_started_by_case": browser_started_by_case, "browser_session_created_by_case": browser_session_by_case},
        ),
        _check(
            "requested_side_effects_modelled_not_executed",
            all_no_performed and all_decisions_no_performed and bool(requested_cases),
            {"requested_side_effect_cases": requested_cases, "side_effects_performed_by_case": performed_by_case},
        ),
        _check(
            "fixture_matrix_invalid_browser_reported_without_side_effects",
            "invalid_browser_send_request" in invalid_cases and not performed_by_case.get("invalid_browser_send_request", []),
            {"invalid_cases": invalid_cases},
        ),
        _check(
            "fixture_matrix_json_safe",
            _json_safe(matrix),
            {"case_count": len(cases)},
        ),
        _check(
            "startup_request_contract_gate_still_passes",
            bool(upstream_gate.get("ok")) and upstream_gate.get("status") == "PASS",
            {"upstream_status": upstream_gate.get("status"), "upstream_patch": upstream_gate.get("patch")},
        ),
        _check(
            "no_optional_browser_dependency_imports",
            not any(root in sys.modules for root in FORBIDDEN_IMPORT_ROOTS),
            {"forbidden_import_roots_present": sorted(root for root in FORBIDDEN_IMPORT_ROOTS if root in sys.modules)},
        ),
        _check(
            "fixture_matrix_contract_gate_did_not_load_browser_optional_modules",
            not forbidden_loaded,
            {"newly_loaded_forbidden_modules": forbidden_loaded},
        ),
    ]

    # Public check-name aliases intentionally preserve older/future naming while
    # pointing at the same passive facts. This prevents narrow readback changes
    # from breaking the operator contract again.
    alias_sources = {
        "fixture_matrix_has_core_cases": "fixture_matrix_core_cases",
        "fixture_matrix_readback_payload": "fixture_matrix_payload_contract",
        "fixture_matrix_payload_contract_json_safe": "fixture_matrix_json_safe",
        "fixture_matrix_cases_block_startup": "all_fixture_decisions_block_startup",
        "fixture_matrix_cases_create_no_browser_session": "all_fixture_decisions_create_no_browser_session",
        "fixture_matrix_requested_side_effects_modelled_not_executed": "requested_side_effects_modelled_not_executed",
        "invalid_browser_fixture_reported_without_side_effects": "fixture_matrix_invalid_browser_reported_without_side_effects",
        "fixture_gate_did_not_load_browser_optional_modules": "fixture_matrix_contract_gate_did_not_load_browser_optional_modules",
    }
    by_name = {check["name"]: check for check in checks}
    for alias, source in alias_sources.items():
        source_check = by_name[source]
        checks.append(_check(alias, bool(source_check["ok"]), source_check.get("details", {})))

    ok = all(bool(check.get("ok")) for check in checks)
    payload: Dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": "PASS" if ok else "FAIL",
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "matrix": matrix,
        "upstream_contract_gate": dict(upstream_gate),
        "case_names": case_names,
        "case_count": len(cases),
        "checks": checks,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
    }
    json.loads(json.dumps(payload, sort_keys=True))
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser startup request fixture matrix contract gate",
        "PatchOps LLM browser live adapter startup request fixture matrix contract gate",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        "Startup    : allowed=False",
        "Browser    : not started",
        "SideEffects: []",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive startup-request fixture matrix contract gate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON readback.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when used with --json.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    payload = build_startup_request_fixture_matrix_contract_gate()
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, sort_keys=True, indent=2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
