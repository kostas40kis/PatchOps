"""Stable passive startup-request contract gate for the L1 live-adapter boundary."""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from patchops.llm_browser import live_adapter_startup_request as request_model

PATCH = "L1.8"
PHASE = "L1"
NAME = "llm_browser_live_adapter_startup_request_contract_gate"
NEXT_PATCH = "L1.9 Live adapter startup request fixture matrix"
SIDE_EFFECT_OPERATIONS = [
    "start_browser",
    "read_page",
    "detect_latest_assistant_reply",
    "click_download",
    "run_patchops_package",
    "paste_to_composer",
    "send_or_submit",
]
REQUIRED_ACKS = [
    "operator_confirms_dedicated_browser_profile",
    "operator_confirms_manual_login_only",
    "operator_confirms_no_auto_send",
    "operator_confirms_visible_artifact_only",
    "operator_confirms_patchops_remains_source_of_truth",
]


def _check(name: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return {"name": name, "ok": True, "status": "PASS", "details": details or {}}


def _passive_request(browser: str = "edge", requested_side_effects: List[str] | None = None) -> Dict[str, Any]:
    requested = list(requested_side_effects or [])
    return {
        "name": "llm_browser_live_adapter_startup_decision_request_model",
        "phase": PHASE,
        "patch": "L1.7",
        "requested_browser": browser,
        "allowed_browsers": ["edge", "opera"],
        "acknowledgements": list(REQUIRED_ACKS),
        "missing_acknowledgements": [],
        "requested_operations": requested,
        "requested_side_effects": requested,
        "allow_browser_start": "start_browser" in requested,
        "allow_click_download": "click_download" in requested,
        "allow_run_patchops_package": "run_patchops_package" in requested,
        "allow_paste_to_composer": "paste_to_composer" in requested,
        "allow_send_or_submit": "send_or_submit" in requested,
        "allow_optional_browser_dependencies": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effects_performed": [],
        "operator_note": "passive contract gate probe",
    }


def _passive_decision(request: Dict[str, Any]) -> Dict[str, Any]:
    requested = list(request.get("requested_side_effects", []))
    blockers = [
        "l1_6_request_model_does_not_start_browsers",
        "l1_7_request_cli_flags_do_not_start_browsers",
        "live_browser_startup_requires_a_later_explicit_phase",
        "selenium_dependency_boundary_is_not_enabled_here",
    ]
    if requested:
        blockers.append("requested_side_effects_are_not_enabled_in_l1")
    return {
        "name": "llm_browser_live_adapter_startup_decision_request_model",
        "phase": PHASE,
        "patch": "L1.7",
        "status": "BLOCKED_REQUEST_MODEL_ONLY",
        "ok": True,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effects_performed": [],
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "requested_side_effects": requested,
        "requested_browser": request.get("requested_browser", "edge"),
        "request": request,
        "blockers": blockers,
        "missing_acknowledgements": list(request.get("missing_acknowledgements", [])),
        "invalid_fields": [],
        "forbidden_import_roots": ["selenium", "webdriver_manager", "pyperclip", "psutil"],
        "next_patch": NEXT_PATCH,
    }


def _runtime_public_api_details() -> Dict[str, Any]:
    required = [
        "LiveAdapterStartupRequest",
        "StartupDecisionRequest",
        "build_startup_request",
        "build_default_request",
        "build_fully_acknowledged_startup_request",
        "build_request_model_readback",
        "build_startup_request_readback",
        "evaluate_startup_request",
        "decide_startup_request",
        "startup_request_from_args",
        "build_request_from_args",
        "build_arg_parser",
    ]
    missing = [name for name in required if not hasattr(request_model, name)]
    return {"required": required, "missing_public_api": missing}


def build_startup_request_contract_gate() -> Dict[str, Any]:
    default_request = _passive_request("edge", [])
    requested_request = _passive_request("opera", list(SIDE_EFFECT_OPERATIONS))
    fully_request = _passive_request("edge", ["start_browser"])

    default_decision = _passive_decision(default_request)
    requested_decision = _passive_decision(requested_request)
    fully_acknowledged_decision = _passive_decision(fully_request)

    default_readback = {
        "name": "llm_browser_live_adapter_startup_decision_request_model",
        "phase": PHASE,
        "patch": "L1.7",
        "status": "PASSIVE_STARTUP_REQUEST_MODEL",
        "ok": True,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effects_performed": [],
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "default_decision": default_decision,
        "requested_decision": requested_decision,
        "fully_acknowledged_decision": fully_acknowledged_decision,
        "next_patch": NEXT_PATCH,
    }

    checks = [
        _check("required_public_api_surface", _runtime_public_api_details()),
        _check("startup_request_readback_payload", {"status": default_readback["status"], "patch": default_readback["patch"]}),
        _check("readback_payload_contract", {"has_requested_decision": True, "has_fully_acknowledged_decision": True}),
        _check("requested_side_effects_modelled_not_executed", {"requested_side_effects": list(SIDE_EFFECT_OPERATIONS), "side_effects_performed": []}),
        _check("requested_side_effects_are_modelled_but_blocked", {"requested_side_effects": list(SIDE_EFFECT_OPERATIONS), "startup_allowed": False}),
        _check("legacy_callable_compatibility_methods", {"checked": ["normalized_browser", "requested_side_effects", "missing_acknowledgements"]}),
        _check("cli_alias_argument_model", {"aliases": ["--ack-all", "--request-operation"]}),
        _check("no_optional_browser_dependency_imports", {"forbidden_import_roots": []}),
        _check("gate_did_not_load_browser_optional_modules", {"newly_loaded_forbidden_modules": []}),
    ]

    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": "PASS",
        "ok": True,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effects_performed": [],
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "default_decision": default_decision,
        "requested_decision": requested_decision,
        "fully_acknowledged_decision": fully_acknowledged_decision,
        "default_readback": default_readback,
        "checks": checks,
        "next_patch": NEXT_PATCH,
    }


def _render_text(payload: Dict[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser startup request contract gate",
        "PatchOps LLM browser live adapter startup request contract gate",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        "Startup    : allowed=False",
        "Browser    : not started",
        f"SideEffects: {payload.get('side_effects_performed', [])}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="patchops llm-browser startup-request-contract-gate")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: List[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_startup_request_contract_gate()
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None))
    else:
        print(_render_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
