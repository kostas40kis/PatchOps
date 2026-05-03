
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import live_adapter_browser_profile_preflight as preflight
from . import live_adapter_browser_profile_preflight_fixtures as fixtures
from . import live_adapter_browser_profile_preflight_fixture_matrix_contract_gate as fixture_gate

NAME = "llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate"
PHASE = "L2"
PATCH = "L2.7"
NEXT_PATCH = "L2.8 Live adapter browser profile preflight L2 aggregate readiness gate CLI/readback"
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
    "playwright",
    "pyppeteer",
)
CORE_FIXTURE_CASES: tuple[str, ...] = (
    "default_edge_no_acknowledgements",
    "opera_acknowledged_start_and_profile_request",
    "edge_acknowledged_profile_only_request",
    "invalid_browser_send_request",
    "custom_profile_root_and_name",
    "opera_optional_dependency_flag",
)


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _payload_ok(payload: Mapping[str, Any]) -> bool:
    return bool(payload.get("ok") is True and str(payload.get("status")) == STATUS_PASS)


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
        return True
    except TypeError:
        return False


def _forbidden_imports_present() -> list[str]:
    present: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            present.append(root)
    return sorted(set(present))


def _new_forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(set(found))


def _surface_has_no_browser_profile_or_side_effects(payload: Mapping[str, Any]) -> bool:
    return (
        payload.get("startup_allowed") is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and payload.get("profile_directory_created") is False
        and _as_list(payload.get("side_effects_performed")) == []
        and _as_list(payload.get("filesystem_writes_performed")) == []
    )


def _case_maps(cases: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(case.get("name")): {
            "startup_allowed": bool(case.get("startup_allowed")),
            "browser_started": bool(case.get("browser_started")),
            "browser_session_created": bool(case.get("browser_session_created")),
            "profile_directory_created": bool(case.get("profile_directory_created")),
            "side_effects_performed": _as_list(case.get("side_effects_performed")),
            "filesystem_writes_performed": _as_list(case.get("filesystem_writes_performed")),
            "requested_side_effects": _as_list(case.get("requested_side_effects")),
            "invalid_fields": _as_list(case.get("invalid_fields")),
            "profile_path": str(case.get("profile_path", "")),
            "ok": bool(case.get("ok")),
        }
        for case in cases
    }


def build_browser_profile_l2_aggregate_readiness_gate(repo_root: str | Path | None = None) -> Dict[str, Any]:
    """Build the passive aggregate readiness payload for the L2 profile-preflight stack."""
    before_modules = set(sys.modules)
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()

    profile_preflight = _as_mapping(preflight.build_profile_preflight_contract(root))
    fixture_matrix = _as_mapping(fixtures.build_browser_profile_preflight_fixture_matrix(root))
    fixture_contract_gate = _as_mapping(fixture_gate.build_contract_gate(root))

    cases = [case for case in _as_list(fixture_matrix.get("cases")) if isinstance(case, Mapping)]
    case_names = [str(case.get("name")) for case in cases]
    cases_by_name = _case_maps(cases)
    missing_core_cases = [name for name in CORE_FIXTURE_CASES if name not in cases_by_name]
    invalid_cases = [name for name, case in cases_by_name.items() if _as_list(case.get("invalid_fields"))]
    requested_side_effect_cases = [name for name, case in cases_by_name.items() if _as_list(case.get("requested_side_effects"))]
    profile_paths_by_case = {name: str(case.get("profile_path", "")) for name, case in cases_by_name.items()}

    startup_allowed_by_surface = {
        "profile_preflight": profile_preflight.get("startup_allowed"),
        "fixture_matrix": fixture_matrix.get("startup_allowed"),
        "fixture_matrix_contract_gate": fixture_contract_gate.get("startup_allowed"),
    }
    startup_allowed_by_case = {name: case.get("startup_allowed") for name, case in cases_by_name.items()}
    browser_started_by_case = {name: case.get("browser_started") for name, case in cases_by_name.items()}
    browser_session_created_by_case = {name: case.get("browser_session_created") for name, case in cases_by_name.items()}
    profile_directory_created_by_case = {name: case.get("profile_directory_created") for name, case in cases_by_name.items()}
    side_effects_by_case = {name: _as_list(case.get("side_effects_performed")) for name, case in cases_by_name.items()}
    filesystem_writes_by_case = {name: _as_list(case.get("filesystem_writes_performed")) for name, case in cases_by_name.items()}

    forbidden_imports_present = _forbidden_imports_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)

    all_surfaces_pass = _payload_ok(profile_preflight) and _payload_ok(fixture_matrix) and _payload_ok(fixture_contract_gate)
    all_surfaces_no_effects = (
        _surface_has_no_browser_profile_or_side_effects(profile_preflight)
        and _surface_has_no_browser_profile_or_side_effects(fixture_matrix)
        and _surface_has_no_browser_profile_or_side_effects(fixture_contract_gate)
    )
    all_cases_no_browser = all(value is False for value in browser_started_by_case.values()) and all(value is False for value in browser_session_created_by_case.values())
    all_cases_no_profile = all(value is False for value in profile_directory_created_by_case.values()) and all(value == [] for value in filesystem_writes_by_case.values())
    all_cases_no_side_effects = all(value == [] for value in side_effects_by_case.values())
    invalid_browser_safe = invalid_cases == ["invalid_browser_send_request"] and side_effects_by_case.get("invalid_browser_send_request") == [] and startup_allowed_by_case.get("invalid_browser_send_request") is False

    checks: list[Dict[str, Any]] = [
        _check("l2_profile_preflight_contract_still_passes", _payload_ok(profile_preflight) and _surface_has_no_browser_profile_or_side_effects(profile_preflight), {"patch": profile_preflight.get("patch"), "status": profile_preflight.get("status")}),
        _check("l2_profile_fixture_matrix_still_passes", _payload_ok(fixture_matrix) and _surface_has_no_browser_profile_or_side_effects(fixture_matrix), {"patch": fixture_matrix.get("patch"), "status": fixture_matrix.get("status"), "case_count": fixture_matrix.get("case_count")}),
        _check("l2_profile_fixture_matrix_contract_gate_still_passes", _payload_ok(fixture_contract_gate) and _surface_has_no_browser_profile_or_side_effects(fixture_contract_gate), {"patch": fixture_contract_gate.get("patch"), "status": fixture_contract_gate.get("status"), "case_count": fixture_contract_gate.get("case_count")}),
        _check("l2_profile_l2_aggregate_core_cases_present", missing_core_cases == [], {"case_names": case_names, "missing_core_cases": missing_core_cases}),
        _check("l2_profile_l2_aggregate_all_upstream_surfaces_pass", all_surfaces_pass, {"upstream_statuses": {"profile_preflight": profile_preflight.get("status"), "fixture_matrix": fixture_matrix.get("status"), "fixture_matrix_contract_gate": fixture_contract_gate.get("status")}}),
        _check("l2_profile_l2_aggregate_blocks_startup", all(value is False for value in startup_allowed_by_surface.values()) and all(value is False for value in startup_allowed_by_case.values()), {"startup_allowed_by_surface": startup_allowed_by_surface, "startup_allowed_by_case": startup_allowed_by_case}),
        _check("l2_profile_l2_aggregate_creates_no_browser_session", all_surfaces_no_effects and all_cases_no_browser, {"browser_started_by_case": browser_started_by_case, "browser_session_created_by_case": browser_session_created_by_case}),
        _check("l2_profile_l2_aggregate_creates_no_profile_directory", all_surfaces_no_effects and all_cases_no_profile, {"profile_directory_created_by_case": profile_directory_created_by_case, "filesystem_writes_by_case": filesystem_writes_by_case}),
        _check("l2_profile_l2_aggregate_models_requested_side_effects_but_executes_none", requested_side_effect_cases != [] and all_cases_no_side_effects and _as_list(profile_preflight.get("side_effects_performed")) == [] and _as_list(fixture_matrix.get("side_effects_performed")) == [] and _as_list(fixture_contract_gate.get("side_effects_performed")) == [], {"requested_side_effect_cases": requested_side_effect_cases, "side_effects_performed_by_case": side_effects_by_case}),
        _check("l2_profile_l2_aggregate_invalid_browser_reported_without_side_effects", invalid_browser_safe, {"invalid_cases": invalid_cases}),
        _check("l2_profile_l2_aggregate_profile_paths_modelled_only", profile_paths_by_case != {} and all(isinstance(path, str) and path for path in profile_paths_by_case.values()) and all_cases_no_profile, {"profile_paths_by_case": profile_paths_by_case}),
        _check("l2_profile_l2_aggregate_payload_json_safe", _json_safe({"profile_preflight": profile_preflight, "fixture_matrix": fixture_matrix, "fixture_matrix_contract_gate": fixture_contract_gate, "case_maps": cases_by_name}), {"case_count": len(cases), "checks_are_json_native": True}),
        _check("no_optional_browser_dependency_imports", forbidden_imports_present == [], {"forbidden_import_roots_present": forbidden_imports_present}),
        _check("l2_profile_l2_aggregate_did_not_load_browser_optional_modules", newly_loaded_forbidden == [], {"newly_loaded_forbidden_modules": newly_loaded_forbidden}),
        _check("aggregate_profile_preflight_contract_still_passes", _payload_ok(profile_preflight), {"upstream_patch": profile_preflight.get("patch")}),
        _check("aggregate_fixture_matrix_still_passes", _payload_ok(fixture_matrix), {"upstream_patch": fixture_matrix.get("patch")}),
        _check("aggregate_fixture_matrix_contract_gate_still_passes", _payload_ok(fixture_contract_gate), {"upstream_patch": fixture_contract_gate.get("patch")}),
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
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "case_count": len(cases),
        "case_names": case_names,
        "required_core_cases": list(CORE_FIXTURE_CASES),
        "missing_core_cases": missing_core_cases,
        "invalid_cases": invalid_cases,
        "requested_side_effect_cases": requested_side_effect_cases,
        "profile_paths_by_case": profile_paths_by_case,
        "profile_preflight": dict(profile_preflight),
        "fixture_matrix": dict(fixture_matrix),
        "fixture_matrix_contract_gate": dict(fixture_contract_gate),
        "checks": checks,
    }


def build_l2_aggregate_readiness_gate(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_browser_profile_l2_aggregate_readiness_gate(repo_root)


def build_profile_preflight_l2_aggregate_readiness_gate(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_browser_profile_l2_aggregate_readiness_gate(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser profile preflight L2 aggregate readiness gate",
        "PatchOps LLM browser live adapter browser profile preflight L2 aggregate readiness gate",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Startup    : allowed={str(payload.get('startup_allowed')).lower()}",
        "BrowserRun : not started" if payload.get("browser_started") is False else "BrowserRun : started",
        f"Profile    : created={str(payload.get('profile_directory_created')).lower()}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        "Case names : " + ", ".join(_as_list(payload.get("case_names"))),
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L2 aggregate readiness gate for the browser-profile preflight stack.")
    parser.add_argument("--repo-root", default=str(_repo_root_from_here()))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_browser_profile_l2_aggregate_readiness_gate(args.repo_root)
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
