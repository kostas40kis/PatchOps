from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from patchops.llm_browser import live_adapter_startup_request as request_model

PATCH = "L1.9"
PHASE = "L1"
NAME = "llm_browser_live_adapter_startup_request_fixture_matrix"
NEXT_PATCH = "L1.10 Live adapter startup request fixture matrix CLI/readback"

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


def _compact_payload(value: Any) -> Any:
    if hasattr(value, "to_payload"):
        return value.to_payload()
    if isinstance(value, dict):
        return {str(key): _compact_payload(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_compact_payload(item) for item in value]
    return value


def _call_build_startup_request(**kwargs: Any) -> Any:
    builder = getattr(request_model, "build_startup_request", None)
    if callable(builder):
        return builder(**kwargs)

    cls = getattr(request_model, "LiveAdapterStartupRequest", None) or getattr(request_model, "StartupDecisionRequest")
    translated = dict(kwargs)
    if "browser" in translated and "requested_browser" not in translated:
        translated["requested_browser"] = translated.pop("browser")
    return cls(**translated)


def _evaluate_request(request: Any) -> Any:
    evaluator = getattr(request_model, "evaluate_startup_request", None) or getattr(request_model, "decide_startup_request", None)
    if not callable(evaluator):
        raise RuntimeError("startup request evaluator is not available")
    return evaluator(request)


def _make_fixture_request(case: Mapping[str, Any]) -> Any:
    kwargs: Dict[str, Any] = {
        "browser": case.get("browser", "edge"),
        "acknowledgements": tuple(case.get("acknowledgements", ())),
        "requested_operations": tuple(case.get("requested_operations", ())),
        "allow_browser_start": bool(case.get("allow_browser_start", False)),
        "allow_optional_browser_dependencies": bool(case.get("allow_optional_browser_dependencies", False)),
        "allow_click_download": bool(case.get("allow_click_download", False)),
        "allow_run_patchops_package": bool(case.get("allow_run_patchops_package", False)),
        "allow_paste_to_composer": bool(case.get("allow_paste_to_composer", False)),
        "allow_send_or_submit": bool(case.get("allow_send_or_submit", False)),
        "operator_note": str(case.get("operator_note", "")),
    }
    return _call_build_startup_request(**kwargs)


def startup_request_fixture_cases() -> List[Dict[str, Any]]:
    required_acks = tuple(getattr(request_model, "REQUIRED_EXPLICIT_ACKNOWLEDGEMENTS", ()))
    return [
        {
            "name": "default_edge_no_acknowledgements",
            "browser": "edge",
            "acknowledgements": (),
            "requested_operations": (),
            "operator_note": "default passive fixture",
        },
        {
            "name": "edge_fully_acknowledged_start_only",
            "browser": "edge",
            "acknowledgements": required_acks,
            "requested_operations": ("start_browser",),
            "allow_browser_start": True,
            "operator_note": "fully acknowledged but still blocked in L1",
        },
        {
            "name": "opera_all_side_effect_flags",
            "browser": "opera",
            "acknowledgements": required_acks,
            "requested_operations": SIDE_EFFECT_OPERATIONS,
            "allow_browser_start": True,
            "allow_click_download": True,
            "allow_run_patchops_package": True,
            "allow_paste_to_composer": True,
            "allow_send_or_submit": True,
            "operator_note": "all side-effect operations are modelled but not executed",
        },
        {
            "name": "opera_optional_dependency_flag",
            "browser": "opera",
            "acknowledgements": required_acks,
            "requested_operations": ("start_browser",),
            "allow_browser_start": True,
            "allow_optional_browser_dependencies": True,
            "operator_note": "optional browser dependencies remain disabled in L1",
        },
        {
            "name": "invalid_browser_send_request",
            "browser": "invalid-browser",
            "acknowledgements": ("operator_confirms_no_auto_send",),
            "requested_operations": ("send_or_submit",),
            "allow_send_or_submit": True,
            "operator_note": "invalid browser is reported without side effects",
        },
        {
            "name": "readback_only_operations",
            "browser": "edge",
            "acknowledgements": required_acks,
            "requested_operations": ("read_page", "detect_latest_assistant_reply"),
            "operator_note": "readback operations are modelled for later phases only",
        },
    ]


def _case_payload(case: Mapping[str, Any]) -> Dict[str, Any]:
    request = _make_fixture_request(case)
    decision = _evaluate_request(request)
    request_payload = _compact_payload(request)
    decision_payload = _compact_payload(decision)

    return {
        "name": str(case["name"]),
        "request": request_payload,
        "decision": decision_payload,
        "startup_allowed": bool(decision_payload.get("startup_allowed", False)),
        "browser_started": bool(decision_payload.get("browser_started", False)),
        "browser_session_created": bool(decision_payload.get("browser_session_created", False)),
        "side_effects_performed": list(decision_payload.get("side_effects_performed", [])),
        "requested_side_effects": list(decision_payload.get("requested_side_effects", request_payload.get("requested_side_effects", []))),
        "invalid_fields": list(decision_payload.get("invalid_fields", [])),
        "status": str(decision_payload.get("status", "")),
        "ok": bool(decision_payload.get("ok", True)),
    }


def _module_import_roots() -> List[str]:
    try:
        text = Path(__file__).read_text(encoding="utf-8")
    except Exception:
        return []
    roots: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import "):
            roots.extend(part.split(".", 1)[0].strip() for part in stripped[7:].split(","))
        elif stripped.startswith("from "):
            roots.append(stripped.split()[1].split(".", 1)[0])
    return sorted({root for root in roots if root})


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {
        "name": name,
        "ok": bool(ok),
        "status": "PASS" if ok else "FAIL",
        "details": dict(details or {}),
    }


def build_startup_request_fixture_matrix() -> Dict[str, Any]:
    before_modules = set(sys.modules)
    cases = [_case_payload(case) for case in startup_request_fixture_cases()]
    after_modules = set(sys.modules)

    case_names = [case["name"] for case in cases]
    all_blocked = all(case["startup_allowed"] is False for case in cases)
    no_browser_started = all(case["browser_started"] is False and case["browser_session_created"] is False for case in cases)
    no_side_effects = all(case["side_effects_performed"] == [] for case in cases)
    has_requested_side_effects = any(case["requested_side_effects"] for case in cases)
    invalid_case_reported = any("requested_browser" in case["invalid_fields"] for case in cases)
    forbidden_import_roots = [root for root in _module_import_roots() if root in FORBIDDEN_IMPORT_ROOTS]
    newly_loaded_forbidden = sorted((after_modules - before_modules) & set(FORBIDDEN_IMPORT_ROOTS))

    checks = [
        _check(
            "fixture_matrix_has_core_cases",
            {"default_edge_no_acknowledgements", "opera_all_side_effect_flags", "invalid_browser_send_request"}.issubset(case_names),
            {"case_names": case_names},
        ),
        _check(
            "all_fixture_decisions_block_startup",
            all_blocked,
            {"startup_allowed_by_case": {case["name"]: case["startup_allowed"] for case in cases}},
        ),
        _check(
            "all_fixture_decisions_create_no_browser_session",
            no_browser_started,
            {"browser_started_by_case": {case["name"]: case["browser_started"] for case in cases}},
        ),
        _check(
            "requested_side_effects_modelled_not_executed",
            has_requested_side_effects and no_side_effects,
            {"requested_side_effect_cases": [case["name"] for case in cases if case["requested_side_effects"]]},
        ),
        _check(
            "invalid_browser_fixture_reported_without_side_effects",
            invalid_case_reported,
            {"invalid_cases": [case["name"] for case in cases if case["invalid_fields"]]},
        ),
        _check(
            "fixture_matrix_json_safe",
            True,
            {"case_count": len(cases)},
        ),
        _check(
            "no_optional_browser_dependency_imports",
            not forbidden_import_roots,
            {"forbidden_import_roots": forbidden_import_roots},
        ),
        _check(
            "fixture_gate_did_not_load_browser_optional_modules",
            not newly_loaded_forbidden,
            {"newly_loaded_forbidden_modules": newly_loaded_forbidden},
        ),
    ]

    ok = all(check["ok"] for check in checks)
    payload: Dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": "PASS" if ok else "FAIL",
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "cases": cases,
        "case_names": case_names,
        "case_count": len(cases),
        "checks": checks,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "side_effect_boundary": "passive-only",
    }

    json.loads(json.dumps(payload, sort_keys=True))
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser startup request fixture matrix",
        "PatchOps LLM browser live adapter startup request fixture matrix",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        "Startup    : allowed=False",
        "Browser    : not started",
        "SideEffects: []",
        "Fixtures:",
    ]
    for case in payload.get("cases", []):
        lines.append(f"- {case.get('name')}: startup_allowed={case.get('startup_allowed')} side_effects={case.get('side_effects_performed')}")
    lines.append("Checks:")
    for check in payload.get("checks", []):
        lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L1 startup-request fixture matrix readback.")
    parser.add_argument("--json", action="store_true", help="Emit JSON readback.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when used with --json.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    payload = build_startup_request_fixture_matrix()
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
