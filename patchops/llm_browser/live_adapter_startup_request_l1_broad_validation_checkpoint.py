from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import live_adapter_startup_request_l1_documentation_checkpoint as docs_checkpoint

NAME = "llm_browser_live_adapter_startup_request_l1_broad_validation_checkpoint"
PHASE = "L1"
PATCH = "L1.16"
NEXT_PATCH = "L1.17 Live adapter startup request L1 final acceptance marker"
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
FOCUSED_L1_TEST_PATHS: tuple[str, ...] = (
    "tests/test_llm_browser_live_adapter_startup_request_l1_documentation_freeze_checkpoint_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_fixture_matrix_contract_gate_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_fixture_matrix_contract_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_fixture_matrix_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_fixture_matrix_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_contract_gate_l1_08k_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_contract_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_07p_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_cli_flags_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_current.py",
    "tests/test_llm_browser_live_adapter_startup_gate_current.py",
    "tests/test_llm_browser_live_adapter_passive_contract_gate_current.py",
    "tests/test_llm_browser_live_adapter_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_skeleton_current.py",
    "tests/test_llm_browser_dry_mode_release_gate_current.py",
    "tests/test_exact_cli_subcommand_set.py",
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


def _summary(payload: Mapping[str, Any]) -> Dict[str, Any]:
    checks = []
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            checks.append({"name": check.get("name"), "status": check.get("status"), "ok": check.get("ok")})
    return {
        "name": payload.get("name"),
        "patch": payload.get("patch"),
        "phase": payload.get("phase"),
        "status": payload.get("status"),
        "ok": payload.get("ok"),
        "startup_allowed": payload.get("startup_allowed"),
        "browser_started": payload.get("browser_started"),
        "browser_session_created": payload.get("browser_session_created"),
        "side_effects_performed": _as_list(payload.get("side_effects_performed")),
        "case_count": payload.get("case_count"),
        "checks": checks,
    }


def _broad_validation_commands(repo_root: Path) -> list[str]:
    root = str(repo_root)
    focused_tests = " ".join(FOCUSED_L1_TEST_PATHS)
    return [
        f'py -m patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint --repo-root "{root}" --json --compact',
        'py -m patchops.cli llm-browser startup-request-l1-readiness --json --compact',
        f'py -m patchops.cli llm-browser release-gate --repo-root "{root}" --json',
        f'py -m patchops.cli llm-browser checkpoint --repo-root "{root}" --json',
        f'py -m pytest -q {focused_tests}',
        'py -m pytest -q',
    ]


def build_l1_broad_validation_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    before_modules = set(sys.modules)
    root = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()

    documentation_payload = _as_mapping(docs_checkpoint.build_l1_documentation_freeze_readiness_checkpoint(root))
    aggregate_payload = _as_mapping(documentation_payload.get("aggregate_readiness_gate"))
    commands = _broad_validation_commands(root)

    missing_focused_tests = [path for path in FOCUSED_L1_TEST_PATHS if not (root / path).exists()]
    forbidden_present = _forbidden_imports_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)
    command_text = "\n".join(commands).lower()
    commands_are_readback_plan_only = not any(
        forbidden in command_text
        for forbidden in (
            "git commit",
            "git push",
            "run-package",
            "start_browser",
            "click_download",
            "paste_to_composer",
            "send_or_submit",
        )
    )

    checks = [
        _check(
            "l1_documentation_freeze_checkpoint_still_passes",
            _payload_ok(documentation_payload),
            {"patch": documentation_payload.get("patch"), "status": documentation_payload.get("status")},
        ),
        _check(
            "l1_aggregate_readiness_gate_still_passes",
            _payload_ok(aggregate_payload),
            {"patch": aggregate_payload.get("patch"), "status": aggregate_payload.get("status")},
        ),
        _check(
            "l1_broad_validation_focused_tests_present",
            not missing_focused_tests,
            {"missing": missing_focused_tests, "required_count": len(FOCUSED_L1_TEST_PATHS)},
        ),
        _check(
            "l1_broad_validation_command_plan_is_passive",
            commands_are_readback_plan_only,
            {"command_count": len(commands), "commands_are_not_executed_by_checkpoint": True},
        ),
        _check(
            "l1_broad_validation_keeps_no_browser_or_side_effects",
            documentation_payload.get("startup_allowed") is False
            and documentation_payload.get("browser_started") is False
            and documentation_payload.get("browser_session_created") is False
            and _as_list(documentation_payload.get("side_effects_performed")) == [],
            {
                "startup_allowed": documentation_payload.get("startup_allowed"),
                "browser_started": documentation_payload.get("browser_started"),
                "browser_session_created": documentation_payload.get("browser_session_created"),
                "side_effects_performed": _as_list(documentation_payload.get("side_effects_performed")),
            },
        ),
        _check(
            "l1_broad_validation_payload_json_safe",
            True,
            {"checks_are_json_native": True},
        ),
        _check(
            "no_optional_browser_dependency_imports",
            not forbidden_present,
            {"forbidden_import_roots_present": forbidden_present},
        ),
        _check(
            "l1_broad_validation_checkpoint_did_not_load_browser_optional_modules",
            not newly_loaded_forbidden,
            {"newly_loaded_forbidden_modules": newly_loaded_forbidden},
        ),
    ]

    ok = all(bool(check.get("ok")) for check in checks)
    payload: Dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "optional_browser_dependencies_required": False,
        "side_effect_boundary": "passive-only",
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "side_effects_performed": [],
        "case_count": documentation_payload.get("case_count"),
        "case_names": _as_list(documentation_payload.get("case_names")),
        "focused_l1_test_paths": list(FOCUSED_L1_TEST_PATHS),
        "missing_focused_l1_test_paths": missing_focused_tests,
        "broad_validation_commands": commands,
        "executed_validation_commands": [],
        "documentation_checkpoint": _summary(documentation_payload),
        "aggregate_readiness_gate": _summary(aggregate_payload),
        "checks": checks,
    }
    json.dumps(payload, sort_keys=True)
    return payload


def build_broad_validation_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l1_broad_validation_checkpoint(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser startup request L1 broad validation checkpoint",
        "PatchOps LLM browser live adapter startup request L1 broad validation checkpoint",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Startup    : allowed={payload.get('startup_allowed')}",
        f"Browser    : {'started' if payload.get('browser_started') else 'not started'}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Focused    : required={len(_as_list(payload.get('focused_l1_test_paths')))} missing={len(_as_list(payload.get('missing_focused_l1_test_paths')))}",
        f"Commands   : planned={len(_as_list(payload.get('broad_validation_commands')))} executed={len(_as_list(payload.get('executed_validation_commands')))}",
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L1 broad validation checkpoint readback.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to the installed source tree.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_l1_broad_validation_checkpoint(args.repo_root)
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
