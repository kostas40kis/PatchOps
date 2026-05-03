from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import live_adapter_startup_request_l1_broad_validation_checkpoint as broad_checkpoint

NAME = "llm_browser_live_adapter_startup_request_l1_final_acceptance_marker"
PHASE = "L1"
PATCH = "L1.17"
NEXT_PATCH = "L2.1 Live adapter browser profile preflight contract"
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
REQUIRED_L1_DOC_PATHS: tuple[str, ...] = (
    "docs/llm_browser_live_adapter_skeleton.md",
    "docs/llm_browser_live_adapter_startup_gate.md",
    "docs/llm_browser_live_adapter_startup_request.md",
    "docs/llm_browser_live_adapter_startup_request_cli_flags.md",
    "docs/llm_browser_live_adapter_startup_request_contract_gate.md",
    "docs/llm_browser_live_adapter_startup_request_fixture_matrix.md",
    "docs/llm_browser_live_adapter_startup_request_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_startup_request_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_startup_request_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_startup_request_l1_documentation_freeze_readiness_checkpoint.md",
    "docs/llm_browser_live_adapter_startup_request_l1_broad_validation_checkpoint.md",
    "docs/llm_browser_live_adapter_startup_request_l1_final_acceptance_marker.md",
    "docs/llm_browser_runner.md",
)
REQUIRED_L1_SOURCE_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter.py",
    "patchops/llm_browser/live_adapter_startup_gate.py",
    "patchops/llm_browser/live_adapter_startup_request.py",
    "patchops/llm_browser/live_adapter_startup_request_contract_gate.py",
    "patchops/llm_browser/live_adapter_startup_request_fixtures.py",
    "patchops/llm_browser/live_adapter_startup_request_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_startup_request_l1_readiness_gate.py",
    "patchops/llm_browser/live_adapter_startup_request_l1_documentation_checkpoint.py",
    "patchops/llm_browser/live_adapter_startup_request_l1_broad_validation_checkpoint.py",
    "patchops/llm_browser/live_adapter_startup_request_l1_final_acceptance_marker.py",
)
REQUIRED_L1_TEST_PATHS: tuple[str, ...] = (
    "tests/test_llm_browser_live_adapter_skeleton_current.py",
    "tests/test_llm_browser_live_adapter_startup_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_cli_flags_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_documentation_freeze_checkpoint_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_broad_validation_checkpoint_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_final_acceptance_marker_current.py",
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


def _missing_paths(repo_root: Path, rel_paths: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for rel in rel_paths:
        if not (repo_root / rel).exists():
            missing.append(rel)
    return missing


def _checks_are_json_native(checks: Iterable[Mapping[str, Any]]) -> bool:
    try:
        json.dumps(list(checks), sort_keys=True)
        return True
    except TypeError:
        return False


def build_l1_final_acceptance_marker(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    before_modules = set(sys.modules)

    broad_payload = broad_checkpoint.build_l1_broad_validation_checkpoint(root)
    documentation_payload = _as_mapping(broad_payload.get("documentation_checkpoint"))
    aggregate_payload = _as_mapping(broad_payload.get("aggregate_readiness_gate"))

    missing_doc_paths = _missing_paths(root, REQUIRED_L1_DOC_PATHS)
    missing_source_paths = _missing_paths(root, REQUIRED_L1_SOURCE_PATHS)
    missing_test_paths = _missing_paths(root, REQUIRED_L1_TEST_PATHS)

    startup_allowed = bool(broad_payload.get("startup_allowed"))
    browser_started = bool(broad_payload.get("browser_started"))
    browser_session_created = bool(broad_payload.get("browser_session_created"))
    side_effects_performed = _as_list(broad_payload.get("side_effects_performed"))
    executed_validation_commands = _as_list(broad_payload.get("executed_validation_commands"))
    broad_validation_commands = _as_list(broad_payload.get("broad_validation_commands"))

    forbidden_imports_present = _forbidden_imports_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)

    checks: list[Dict[str, Any]] = [
        _check("l1_broad_validation_checkpoint_still_passes", _payload_ok(broad_payload), {"patch": broad_payload.get("patch"), "status": broad_payload.get("status")}),
        _check("l1_documentation_freeze_checkpoint_still_passes", _payload_ok(documentation_payload), {"patch": documentation_payload.get("patch"), "status": documentation_payload.get("status")}),
        _check("l1_aggregate_readiness_gate_still_passes", _payload_ok(aggregate_payload), {"patch": aggregate_payload.get("patch"), "status": aggregate_payload.get("status")}),
        _check("l1_final_acceptance_required_l1_artifacts_present", not missing_doc_paths and not missing_source_paths and not missing_test_paths, {"missing_doc_paths": missing_doc_paths, "missing_source_paths": missing_source_paths, "missing_test_paths": missing_test_paths, "required_doc_count": len(REQUIRED_L1_DOC_PATHS), "required_source_count": len(REQUIRED_L1_SOURCE_PATHS), "required_test_count": len(REQUIRED_L1_TEST_PATHS)}),
        _check("l1_final_acceptance_no_browser_or_side_effects", startup_allowed is False and browser_started is False and browser_session_created is False and side_effects_performed == [], {"startup_allowed": startup_allowed, "browser_started": browser_started, "browser_session_created": browser_session_created, "side_effects_performed": side_effects_performed}),
        _check("l1_final_acceptance_does_not_execute_validation_commands", executed_validation_commands == [], {"executed_validation_commands": executed_validation_commands, "planned_command_count": len(broad_validation_commands)}),
        _check("l1_final_acceptance_payload_json_safe", _checks_are_json_native(broad_payload.get("checks", [])), {"checks_are_json_native": _checks_are_json_native(broad_payload.get("checks", []))}),
        _check("l1_final_acceptance_ready_for_operator_commit", True, {"commit_recommended": True, "commit_hint": 'git add -A; git commit -m "L1 accept startup request passive stack"', "git_commit_executed": False, "git_push_executed": False}),
        _check("no_optional_browser_dependency_imports", forbidden_imports_present == [], {"forbidden_import_roots_present": forbidden_imports_present}),
        _check("l1_final_acceptance_marker_did_not_load_browser_optional_modules", newly_loaded_forbidden == [], {"newly_loaded_forbidden_modules": newly_loaded_forbidden}),
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
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "side_effects_performed": side_effects_performed,
        "startup_allowed": startup_allowed,
        "browser_started": browser_started,
        "browser_session_created": browser_session_created,
        "optional_browser_dependencies_required": False,
        "case_count": broad_payload.get("case_count"),
        "case_names": broad_payload.get("case_names", []),
        "executed_validation_commands": executed_validation_commands,
        "broad_validation_commands": broad_validation_commands,
        "commit_recommended": True,
        "commit_hint": 'git add -A; git commit -m "L1 accept startup request passive stack"',
        "git_commit_executed": False,
        "git_push_executed": False,
        "missing_doc_paths": missing_doc_paths,
        "missing_source_paths": missing_source_paths,
        "missing_test_paths": missing_test_paths,
        "required_doc_paths": list(REQUIRED_L1_DOC_PATHS),
        "required_source_paths": list(REQUIRED_L1_SOURCE_PATHS),
        "required_test_paths": list(REQUIRED_L1_TEST_PATHS),
        "broad_validation_checkpoint": broad_payload,
        "documentation_checkpoint": documentation_payload,
        "aggregate_readiness_gate": aggregate_payload,
        "checks": checks,
    }


def build_final_acceptance_marker(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l1_final_acceptance_marker(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    missing_docs = len(_as_list(payload.get("missing_doc_paths")))
    missing_sources = len(_as_list(payload.get("missing_source_paths")))
    missing_tests = len(_as_list(payload.get("missing_test_paths")))
    lines = [
        "PatchOps LLM browser startup request L1 final acceptance marker",
        "PatchOps LLM browser live adapter startup request L1 final acceptance marker",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Startup    : allowed={str(payload.get('startup_allowed')).lower()}",
        "Browser    : not started" if not payload.get("browser_started") else "Browser    : started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Docs       : missing={missing_docs}",
        f"Sources    : missing={missing_sources}",
        f"Tests      : missing={missing_tests}",
        f"Commands   : planned={len(_as_list(payload.get('broad_validation_commands')))} executed={len(_as_list(payload.get('executed_validation_commands')))}",
        f"Commit     : recommended={str(payload.get('commit_recommended')).lower()} executed={str(payload.get('git_commit_executed')).lower()} pushed={str(payload.get('git_push_executed')).lower()}",
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L1 final acceptance marker for the live-adapter startup-request stack.")
    parser.add_argument("--repo-root", default=str(_repo_root_from_here()))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_l1_final_acceptance_marker(args.repo_root)
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
