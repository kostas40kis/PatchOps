
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import live_adapter_browser_profile_preflight as preflight

NAME = "llm_browser_live_adapter_browser_profile_preflight_fixture_matrix"
PHASE = "L2"
PATCH = "L2.3"
NEXT_PATCH = "L2.4 Live adapter browser profile preflight fixture matrix CLI/readback"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
REQUIRED_CORE_CASES: tuple[str, ...] = (
    "default_edge_no_acknowledgements",
    "opera_acknowledged_start_and_profile_request",
    "edge_acknowledged_profile_only_request",
    "invalid_browser_send_request",
    "custom_profile_root_and_name",
    "opera_optional_dependency_flag",
)
FORBIDDEN_IMPORT_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
)


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _payload_ok(payload: Mapping[str, Any]) -> bool:
    return bool(payload.get("ok") is True and str(payload.get("status")) == STATUS_PASS)


def _case_expected_ok(case_name: str, decision: Mapping[str, Any]) -> bool:
    """Return whether a fixture case satisfied the passive L2.3 contract.

    The fixture matrix is a validation harness, not a request approval surface.
    Some fixtures intentionally model rejected/invalid future requests, so the
    per-case success flag means the case was safely blocked and reported as
    expected, not that the request itself was allowed.
    """
    invalid_fields = _as_list(decision.get("invalid_fields"))
    expected_invalid = ["requested_browser"] if case_name == "invalid_browser_send_request" else []
    return bool(
        str(decision.get("request_status", decision.get("status"))) == "BLOCKED_PREFLIGHT_CONTRACT_ONLY"
        and invalid_fields == expected_invalid
        and bool(decision.get("startup_allowed")) is False
        and bool(decision.get("browser_started")) is False
        and bool(decision.get("browser_session_created")) is False
        and bool(decision.get("profile_directory_created")) is False
        and _as_list(decision.get("side_effects_performed")) == []
        and _as_list(decision.get("filesystem_writes_performed")) == []
        and bool(decision.get("optional_browser_dependencies_required")) is False
    )


def _checks_are_json_native(value: Any) -> bool:
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
    return sorted(present)


def _new_forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(found)


def _required_acknowledgements() -> tuple[str, ...]:
    return tuple(getattr(preflight, "REQUIRED_ACKNOWLEDGEMENTS", ()))


def _default_profile_root(repo_root: str | Path | None = None) -> str:
    if hasattr(preflight, "default_profile_root"):
        return str(preflight.default_profile_root(repo_root))
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    return str(root / "data" / "runtime" / "llm_browser_profiles")


def build_browser_profile_preflight_fixture_cases(repo_root: str | Path | None = None, profile_root: str | Path | None = None) -> list[Dict[str, Any]]:
    """Return passive fixture definitions for the L2 browser-profile preflight contract.

    The cases are data only. They model future profile/browser requests and must not
    create profile directories, start browsers, import Selenium, or write files.
    """
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    base_profile_root = str(Path(profile_root).resolve()) if profile_root is not None else _default_profile_root(root)
    custom_profile_root = str(Path(base_profile_root) / "custom-fixture-root")
    ack_all = _required_acknowledgements()
    return [
        {
            "name": "default_edge_no_acknowledgements",
            "requested_browser": "edge",
            "profile_root": base_profile_root,
            "profile_name": "patchops-llm-browser",
            "acknowledgements": [],
            "allow_browser_start": False,
            "allow_profile_directory_creation": False,
            "allow_optional_browser_dependencies": False,
            "operator_note": "default passive profile preflight fixture",
        },
        {
            "name": "opera_acknowledged_start_and_profile_request",
            "requested_browser": "opera",
            "profile_root": base_profile_root,
            "profile_name": "patchops-llm-browser",
            "acknowledgements": list(ack_all),
            "allow_browser_start": True,
            "allow_profile_directory_creation": True,
            "allow_optional_browser_dependencies": False,
            "operator_note": "fully acknowledged future startup/profile request remains blocked in L2.3",
        },
        {
            "name": "edge_acknowledged_profile_only_request",
            "requested_browser": "edge",
            "profile_root": base_profile_root,
            "profile_name": "patchops-llm-browser",
            "acknowledgements": list(ack_all),
            "allow_browser_start": False,
            "allow_profile_directory_creation": True,
            "allow_optional_browser_dependencies": False,
            "operator_note": "profile directory creation is modelled but not performed",
        },
        {
            "name": "invalid_browser_send_request",
            "requested_browser": "invalid-browser",
            "profile_root": base_profile_root,
            "profile_name": "patchops-llm-browser",
            "acknowledgements": ["operator_confirms_no_auto_send"],
            "allow_browser_start": True,
            "allow_profile_directory_creation": True,
            "allow_optional_browser_dependencies": False,
            "operator_note": "invalid browser is reported without profile creation or browser startup",
        },
        {
            "name": "custom_profile_root_and_name",
            "requested_browser": "edge",
            "profile_root": custom_profile_root,
            "profile_name": "patchops-custom-fixture-profile",
            "acknowledgements": list(ack_all),
            "allow_browser_start": False,
            "allow_profile_directory_creation": True,
            "allow_optional_browser_dependencies": False,
            "operator_note": "custom profile path is calculated as data only",
        },
        {
            "name": "opera_optional_dependency_flag",
            "requested_browser": "opera",
            "profile_root": base_profile_root,
            "profile_name": "patchops-llm-browser",
            "acknowledgements": list(ack_all),
            "allow_browser_start": True,
            "allow_profile_directory_creation": False,
            "allow_optional_browser_dependencies": True,
            "operator_note": "optional browser dependency request remains disabled in L2.3",
        },
    ]


def _evaluate_case(case: Mapping[str, Any], repo_root: Path) -> Dict[str, Any]:
    request = preflight.build_browser_profile_preflight_request(
        repo_root,
        requested_browser=str(case.get("requested_browser", "edge")),
        profile_root=case.get("profile_root"),
        profile_name=str(case.get("profile_name", "patchops-llm-browser")),
        acknowledgements=_as_list(case.get("acknowledgements")),
        allow_browser_start=bool(case.get("allow_browser_start", False)),
        allow_profile_directory_creation=bool(case.get("allow_profile_directory_creation", False)),
        allow_optional_browser_dependencies=bool(case.get("allow_optional_browser_dependencies", False)),
        operator_note=str(case.get("operator_note", "passive browser profile preflight fixture")),
    )
    decision = preflight.evaluate_browser_profile_preflight(request, repo_root)
    return {
        "name": str(case.get("name")),
        "ok": _case_expected_ok(str(case.get("name")), decision),
        "status": decision.get("request_status", decision.get("status")),
        "requested_browser": decision.get("requested_browser"),
        "normalized_browser": decision.get("normalized_browser"),
        "profile_root": decision.get("profile_root"),
        "profile_path": decision.get("profile_path"),
        "profile_name": decision.get("profile_name"),
        "requested_side_effects": _as_list(decision.get("requested_side_effects")),
        "side_effects_performed": _as_list(decision.get("side_effects_performed")),
        "filesystem_writes_performed": _as_list(decision.get("filesystem_writes_performed")),
        "startup_allowed": bool(decision.get("startup_allowed")),
        "browser_started": bool(decision.get("browser_started")),
        "browser_session_created": bool(decision.get("browser_session_created")),
        "profile_directory_created": bool(decision.get("profile_directory_created")),
        "missing_acknowledgements": _as_list(decision.get("missing_acknowledgements")),
        "invalid_fields": _as_list(decision.get("invalid_fields")),
        "manual_login_required": bool(decision.get("manual_login_required")),
        "dedicated_profile_required": bool(decision.get("dedicated_profile_required")),
        "optional_browser_dependencies_required": bool(decision.get("optional_browser_dependencies_required")),
        "decision": decision,
    }


def build_browser_profile_preflight_fixture_matrix(
    repo_root: str | Path | None = None,
    profile_root: str | Path | None = None,
) -> Dict[str, Any]:
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    before_modules = set(sys.modules)
    base_preflight = preflight.build_profile_preflight_contract(root)
    fixture_definitions = build_browser_profile_preflight_fixture_cases(root, profile_root)
    cases = [_evaluate_case(case, root) for case in fixture_definitions]

    case_names = [str(case.get("name")) for case in cases]
    missing_core_cases = [name for name in REQUIRED_CORE_CASES if name not in case_names]
    startup_allowed_by_case = {str(case.get("name")): bool(case.get("startup_allowed")) for case in cases}
    browser_started_by_case = {str(case.get("name")): bool(case.get("browser_started")) for case in cases}
    browser_session_created_by_case = {str(case.get("name")): bool(case.get("browser_session_created")) for case in cases}
    profile_directory_created_by_case = {str(case.get("name")): bool(case.get("profile_directory_created")) for case in cases}
    side_effects_performed_by_case = {str(case.get("name")): _as_list(case.get("side_effects_performed")) for case in cases}
    filesystem_writes_by_case = {str(case.get("name")): _as_list(case.get("filesystem_writes_performed")) for case in cases}
    requested_side_effect_cases = [str(case.get("name")) for case in cases if _as_list(case.get("requested_side_effects"))]
    invalid_cases = [str(case.get("name")) for case in cases if _as_list(case.get("invalid_fields"))]
    profile_paths_by_case = {str(case.get("name")): str(case.get("profile_path")) for case in cases}
    forbidden_imports_present = _forbidden_imports_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)

    checks: list[Dict[str, Any]] = [
        _check("l2_profile_preflight_contract_still_passes", _payload_ok(base_preflight), {"patch": base_preflight.get("patch"), "status": base_preflight.get("status")}),
        _check("l2_profile_fixture_matrix_has_core_cases", missing_core_cases == [], {"case_names": case_names, "missing_core_cases": missing_core_cases}),
        _check("all_profile_fixture_decisions_block_startup", all(value is False for value in startup_allowed_by_case.values()), {"startup_allowed_by_case": startup_allowed_by_case}),
        _check("all_profile_fixture_decisions_create_no_browser_session", all(value is False for value in browser_started_by_case.values()) and all(value is False for value in browser_session_created_by_case.values()), {"browser_started_by_case": browser_started_by_case, "browser_session_created_by_case": browser_session_created_by_case}),
        _check("all_profile_fixture_decisions_create_no_profile_directory", all(value is False for value in profile_directory_created_by_case.values()) and all(value == [] for value in filesystem_writes_by_case.values()), {"profile_directory_created_by_case": profile_directory_created_by_case, "filesystem_writes_by_case": filesystem_writes_by_case}),
        _check("profile_fixture_requested_side_effects_modelled_not_executed", requested_side_effect_cases != [] and all(value == [] for value in side_effects_performed_by_case.values()), {"requested_side_effect_cases": requested_side_effect_cases, "side_effects_performed_by_case": side_effects_performed_by_case}),
        _check("profile_fixture_invalid_browser_reported_without_side_effects", "invalid_browser_send_request" in invalid_cases and side_effects_performed_by_case.get("invalid_browser_send_request") == [], {"invalid_cases": invalid_cases}),
        _check("profile_fixture_paths_are_modelled_only", all(isinstance(path, str) and path for path in profile_paths_by_case.values()), {"profile_paths_by_case": profile_paths_by_case}),
        _check("profile_fixture_matrix_json_safe", _checks_are_json_native(cases), {"case_count": len(cases)}),
        _check("no_optional_browser_dependency_imports", forbidden_imports_present == [], {"forbidden_import_roots_present": forbidden_imports_present}),
        _check("l2_profile_fixture_matrix_did_not_load_browser_optional_modules", newly_loaded_forbidden == [], {"newly_loaded_forbidden_modules": newly_loaded_forbidden}),
    ]
    ok = all(check["ok"] is True for check in checks)

    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "next_patch": NEXT_PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": ok,
        "side_effect_boundary": "passive-only",
        "side_effect_operations": list(getattr(preflight, "SIDE_EFFECT_OPERATIONS", ())),
        "side_effects_performed": [],
        "filesystem_writes_performed": [],
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "optional_browser_dependencies_required": False,
        "case_count": len(cases),
        "case_names": case_names,
        "cases": cases,
        "required_core_cases": list(REQUIRED_CORE_CASES),
        "missing_core_cases": missing_core_cases,
        "requested_side_effect_cases": requested_side_effect_cases,
        "invalid_cases": invalid_cases,
        "profile_paths_by_case": profile_paths_by_case,
        "base_preflight": base_preflight,
        "checks": checks,
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser profile preflight fixture matrix",
        "PatchOps LLM browser live adapter browser profile preflight fixture matrix",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Startup    : allowed={str(payload.get('startup_allowed')).lower()}",
        "BrowserRun : not started" if not payload.get("browser_started") else "BrowserRun : started",
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
    parser = argparse.ArgumentParser(description="Passive L2 browser-profile preflight fixture matrix for the live adapter.")
    parser.add_argument("--repo-root", default=str(_repo_root_from_here()))
    parser.add_argument("--profile-root", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_browser_profile_preflight_fixture_matrix(args.repo_root, args.profile_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
