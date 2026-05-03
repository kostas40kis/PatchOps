from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import live_adapter_browser_profile_l2_documentation_checkpoint as l2_documentation
from . import live_adapter_browser_profile_l2_readiness_gate as l2_readiness
from . import live_adapter_startup_request_l1_final_acceptance_marker as l1_final_acceptance

NAME = "llm_browser_live_adapter_browser_profile_l2_broad_validation_checkpoint"
PHASE = "L2"
PATCH = "L2.10"
NEXT_PATCH = "L2.11 Live adapter browser profile preflight L2 broad validation checkpoint CLI/readback"
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
REQUIRED_L2_DOC_PATHS: tuple[str, ...] = (
    "docs/llm_browser_live_adapter_browser_profile_preflight.md",
    "docs/llm_browser_live_adapter_browser_profile_preflight_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_profile_preflight_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_case_ok_repair.md",
    "docs/llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_profile_l2_documentation_freeze_readiness_checkpoint.md",
    "docs/llm_browser_live_adapter_browser_profile_l2_broad_validation_checkpoint.md",
    "docs/llm_browser_l2_10_broad_validation.md",
    "docs/llm_browser_runner.md",
)
REQUIRED_L2_SOURCE_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_profile_preflight.py",
    "patchops/llm_browser/live_adapter_browser_profile_preflight_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_profile_preflight_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_profile_l2_readiness_gate.py",
    "patchops/llm_browser/live_adapter_browser_profile_l2_documentation_checkpoint.py",
    "patchops/llm_browser/l2_10_broad_validation.py",
    "patchops/llm_browser/commands.py",
)
REQUIRED_L2_TEST_PATHS: tuple[str, ...] = (
    "tests/test_llm_browser_live_adapter_browser_profile_preflight_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_preflight_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_browser_profile_l2_documentation_freeze_checkpoint_current.py",
    "tests/test_l2_10_broad_validation_current.py",
    "tests/test_exact_cli_subcommand_set.py",
)
BROAD_VALIDATION_COMMANDS: tuple[str, ...] = (
    "py -m compileall patchops/llm_browser tests",
    "py -m pytest -q tests/test_llm_browser_live_adapter_browser_profile_preflight_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_current.py tests/test_llm_browser_live_adapter_browser_profile_preflight_fixture_matrix_contract_gate_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_aggregate_readiness_gate_cli_readback_current.py tests/test_llm_browser_live_adapter_browser_profile_l2_documentation_freeze_checkpoint_current.py tests/test_l2_10_broad_validation_current.py",
    "py -m patchops.cli llm-browser profile-preflight-l2-readiness --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_profile_l2_readiness_gate --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_profile_l2_documentation_checkpoint --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_startup_request_l1_final_acceptance_marker --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.l2_10_broad_validation --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)
FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_or_submit",
    "open --browser",
    "run-once",
    "watch-downloads",
)


def _repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root:
        candidate = Path(repo_root)
        if str(candidate) == ".":
            return Path.cwd().resolve()
        return candidate.resolve()
    return _repo_root_from_here()


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


def _missing_paths(repo_root: Path, paths: Iterable[str]) -> list[str]:
    return sorted(path for path in paths if not (repo_root / path).exists())


def _call_payload_builder(module: Any, names: Sequence[str], repo_root: Path) -> Mapping[str, Any]:
    for name in names:
        builder = getattr(module, name, None)
        if callable(builder):
            return _as_mapping(builder(repo_root))
    raise AttributeError(f"None of these payload builders are available: {', '.join(names)}")


def _payload_has_no_profile_or_browser_side_effects(payload: Mapping[str, Any], *, require_profile_key: bool = True) -> bool:
    if require_profile_key:
        profile_ok = payload.get("profile_directory_created") is False
    else:
        profile_ok = payload.get("profile_directory_created") in (False, None)
    return bool(
        payload.get("startup_allowed") is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and profile_ok
        and _as_list(payload.get("side_effects_performed")) == []
        and _as_list(payload.get("filesystem_writes_performed")) == []
        and payload.get("optional_browser_dependencies_required") in (False, None)
    )


def _l1_payload_has_no_browser_side_effects(payload: Mapping[str, Any]) -> bool:
    return bool(
        payload.get("startup_allowed") is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and _as_list(payload.get("side_effects_performed")) == []
        and payload.get("optional_browser_dependencies_required") in (False, None)
    )


def _ast_import_roots(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    roots: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.extend(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.append(node.module.split(".", 1)[0])
    return roots


def _source_files_import_forbidden_modules(repo_root: Path, paths: Iterable[str]) -> list[str]:
    hits: list[str] = []
    for rel in paths:
        path = repo_root / rel
        if path.suffix != ".py" or not path.exists():
            continue
        imported_roots = _ast_import_roots(path)
        for root in FORBIDDEN_IMPORT_ROOTS:
            if root in imported_roots:
                hits.append(f"{rel}:{root}")
    return sorted(set(hits))


def _command_plan_is_passive(commands: Sequence[str]) -> bool:
    lowered = "\n".join(commands).lower()
    return not any(fragment in lowered for fragment in FORBIDDEN_COMMAND_FRAGMENTS)


def build_l2_broad_validation_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = _resolve_repo_root(repo_root)
    before_modules = set(sys.modules)

    documentation_payload = _call_payload_builder(
        l2_documentation,
        ("build_l2_documentation_freeze_readiness_checkpoint", "build_documentation_freeze_readiness_checkpoint"),
        root,
    )
    aggregate_payload = _call_payload_builder(
        l2_readiness,
        (
            "build_browser_profile_l2_aggregate_readiness_gate",
            "build_l2_aggregate_readiness_gate",
            "build_l2_readiness_gate",
            "build_l2_readiness_checkpoint",
            "build_aggregate_readiness_gate",
        ),
        root,
    )
    l1_final_payload = _call_payload_builder(
        l1_final_acceptance,
        ("build_l1_final_acceptance_marker", "build_final_acceptance_marker"),
        root,
    )

    missing_l2_docs = _missing_paths(root, REQUIRED_L2_DOC_PATHS)
    missing_l2_sources = _missing_paths(root, REQUIRED_L2_SOURCE_PATHS)
    missing_l2_tests = _missing_paths(root, REQUIRED_L2_TEST_PATHS)
    l1_missing_docs = _as_list(l1_final_payload.get("missing_doc_paths"))
    l1_missing_sources = _as_list(l1_final_payload.get("missing_source_paths"))
    l1_missing_tests = _as_list(l1_final_payload.get("missing_test_paths"))
    broad_validation_commands = list(BROAD_VALIDATION_COMMANDS)
    executed_validation_commands: list[str] = []
    forbidden_imports_present = _forbidden_imports_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)
    forbidden_static_imports = _source_files_import_forbidden_modules(root, REQUIRED_L2_SOURCE_PATHS)

    l2_documentation_ok = _payload_ok(documentation_payload)
    l2_aggregate_ok = _payload_ok(aggregate_payload)
    l1_final_ok = _payload_ok(l1_final_payload)
    l2_documentation_side_effects_ok = _payload_has_no_profile_or_browser_side_effects(documentation_payload)
    l2_aggregate_side_effects_ok = _payload_has_no_profile_or_browser_side_effects(aggregate_payload)
    l1_side_effects_ok = _l1_payload_has_no_browser_side_effects(l1_final_payload)

    checks: list[Dict[str, Any]] = [
        _check("l2_documentation_checkpoint_still_passes", l2_documentation_ok, {"patch": documentation_payload.get("patch"), "status": documentation_payload.get("status")}),
        _check("l2_aggregate_readiness_gate_still_passes", l2_aggregate_ok, {"patch": aggregate_payload.get("patch"), "status": aggregate_payload.get("status")}),
        _check("l1_final_acceptance_marker_still_passes", l1_final_ok, {"patch": l1_final_payload.get("patch"), "status": l1_final_payload.get("status")}),
        _check("l2_required_docs_sources_tests_present", missing_l2_docs == [] and missing_l2_sources == [] and missing_l2_tests == [], {"missing_docs": missing_l2_docs, "missing_sources": missing_l2_sources, "missing_tests": missing_l2_tests}),
        _check("l1_accepted_surfaces_still_present", l1_missing_docs == [] and l1_missing_sources == [] and l1_missing_tests == [], {"missing_l1_docs": l1_missing_docs, "missing_l1_sources": l1_missing_sources, "missing_l1_tests": l1_missing_tests}),
        _check("l2_broad_validation_focused_tests_present", (root / "tests/test_l2_10_broad_validation_current.py").exists(), {"path": "tests/test_l2_10_broad_validation_current.py"}),
        _check("l2_broad_validation_command_plan_is_passive", _command_plan_is_passive(broad_validation_commands), {"planned_command_count": len(broad_validation_commands)}),
        _check("l2_broad_validation_does_not_execute_validation_commands", executed_validation_commands == [], {"executed_validation_commands": executed_validation_commands}),
        _check("l2_broad_validation_keeps_no_browser_profile_or_side_effects", l2_documentation_side_effects_ok and l2_aggregate_side_effects_ok and l1_side_effects_ok, {"documentation_side_effects_ok": l2_documentation_side_effects_ok, "aggregate_side_effects_ok": l2_aggregate_side_effects_ok, "l1_side_effects_ok": l1_side_effects_ok}),
        _check("l2_source_files_do_not_import_browser_optional_dependencies", forbidden_static_imports == [], {"forbidden_static_imports": forbidden_static_imports}),
        _check("no_optional_browser_dependency_imports", forbidden_imports_present == [], {"forbidden_import_roots_present": forbidden_imports_present}),
        _check("l2_broad_validation_checkpoint_did_not_load_browser_optional_modules", newly_loaded_forbidden == [], {"newly_loaded_forbidden_modules": newly_loaded_forbidden}),
    ]

    payload_preview = {
        "documentation_payload": documentation_payload,
        "aggregate_payload": aggregate_payload,
        "l1_final_payload": l1_final_payload,
        "missing_l2_docs": missing_l2_docs,
        "missing_l2_sources": missing_l2_sources,
        "missing_l2_tests": missing_l2_tests,
        "broad_validation_commands": broad_validation_commands,
    }
    checks.append(_check("l2_broad_validation_payload_json_safe", _json_safe(payload_preview), {"checks_are_json_native": True}))

    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": bool(ok),
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": "passive-only broad-validation readback; no live browser automation",
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "executed_validation_commands": executed_validation_commands,
        "broad_validation_commands": broad_validation_commands,
        "required_l2_doc_paths": list(REQUIRED_L2_DOC_PATHS),
        "required_l2_source_paths": list(REQUIRED_L2_SOURCE_PATHS),
        "required_l2_test_paths": list(REQUIRED_L2_TEST_PATHS),
        "missing_l2_doc_paths": missing_l2_docs,
        "missing_l2_source_paths": missing_l2_sources,
        "missing_l2_test_paths": missing_l2_tests,
        "l2_documentation_checkpoint": dict(documentation_payload),
        "l2_aggregate_readiness_gate": dict(aggregate_payload),
        "l1_final_acceptance_marker": dict(l1_final_payload),
        "case_count": aggregate_payload.get("case_count", 0),
        "case_names": list(_as_list(aggregate_payload.get("case_names"))),
        "checks": checks,
    }


def build_broad_validation_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l2_broad_validation_checkpoint(repo_root)


def build_profile_preflight_l2_broad_validation_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l2_broad_validation_checkpoint(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser profile preflight L2 broad validation checkpoint",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Startup    : allowed={payload.get('startup_allowed')}",
        "Browser    : not started" if payload.get("browser_started") is False else "Browser    : started",
        f"Profile    : created={payload.get('profile_directory_created')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Commands   : planned={len(_as_list(payload.get('broad_validation_commands')))} executed={len(_as_list(payload.get('executed_validation_commands')))}",
        f"Docs       : required={len(_as_list(payload.get('required_l2_doc_paths')))} missing={len(_as_list(payload.get('missing_l2_doc_paths')))}",
        f"Sources    : required={len(_as_list(payload.get('required_l2_source_paths')))} missing={len(_as_list(payload.get('missing_l2_source_paths')))}",
        f"Tests      : required={len(_as_list(payload.get('required_l2_test_paths')))} missing={len(_as_list(payload.get('missing_l2_test_paths')))}",
        f"Cases      : {payload.get('case_count')}",
        "Planned commands:",
    ]
    for command in _as_list(payload.get("broad_validation_commands")):
        lines.append(f"- {command}")
    lines.append("Checks:")
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L2 broad-validation checkpoint for the browser-profile preflight stack.")
    parser.add_argument("--repo-root", default=str(_repo_root_from_here()))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_l2_broad_validation_checkpoint(args.repo_root)
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
