from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence

from . import live_adapter_startup_request_l1_readiness_gate as l1_readiness

NAME = "llm_browser_live_adapter_startup_request_l1_documentation_freeze_readiness_checkpoint"
PHASE = "L1"
PATCH = "L1.15"
NEXT_PATCH = "L1.16 Live adapter startup request L1 broad validation checkpoint"
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
REQUIRED_DOC_PATHS: tuple[str, ...] = (
    "docs/llm_browser_live_adapter_skeleton.md",
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
    "docs/llm_browser_runner.md",
)
REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter.py",
    "patchops/llm_browser/live_adapter_startup_gate.py",
    "patchops/llm_browser/live_adapter_startup_request.py",
    "patchops/llm_browser/live_adapter_startup_request_contract_gate.py",
    "patchops/llm_browser/live_adapter_startup_request_fixtures.py",
    "patchops/llm_browser/live_adapter_startup_request_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_startup_request_l1_readiness_gate.py",
    "patchops/llm_browser/live_adapter_startup_request_l1_documentation_checkpoint.py",
)
REQUIRED_TEST_PATHS: tuple[str, ...] = (
    "tests/test_llm_browser_live_adapter_skeleton_current.py",
    "tests/test_llm_browser_live_adapter_startup_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_cli_flags_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_aggregate_readiness_gate_cli_readback_current.py",
    "tests/test_llm_browser_live_adapter_startup_request_l1_documentation_freeze_checkpoint_current.py",
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


def _forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(found)


def _missing_paths(repo_root: Path, paths: Iterable[str]) -> list[str]:
    return sorted(path for path in paths if not (repo_root / path).exists())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _doc_has_all_phrases(repo_root: Path, rel_path: str, phrases: Iterable[str]) -> tuple[bool, list[str]]:
    text = _read_text(repo_root / rel_path)
    missing = [phrase for phrase in phrases if phrase not in text]
    return missing == [], missing


def build_l1_documentation_freeze_readiness_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    repo = Path(repo_root).resolve() if repo_root is not None else _repo_root_from_here()
    before_modules = set(sys.modules)
    aggregate_gate = _as_mapping(l1_readiness.build_l1_aggregate_readiness_gate())
    forbidden_imports = _forbidden_imports(before_modules)

    missing_docs = _missing_paths(repo, REQUIRED_DOC_PATHS)
    missing_sources = _missing_paths(repo, REQUIRED_SOURCE_PATHS)
    missing_tests = _missing_paths(repo, REQUIRED_TEST_PATHS)
    freeze_doc_ok, freeze_doc_missing = _doc_has_all_phrases(
        repo,
        "docs/llm_browser_live_adapter_startup_request_l1_documentation_freeze_readiness_checkpoint.md",
        (
            "L1.15",
            "documentation freeze/readiness checkpoint",
            "passive-only",
            "no Selenium import",
            "no browser start",
            "no click/download/paste/send/package-run side effect",
            "L1.16 Live adapter startup request L1 broad validation checkpoint",
        ),
    )
    runner_doc_ok, runner_doc_missing = _doc_has_all_phrases(
        repo,
        "docs/llm_browser_runner.md",
        (
            "L1.15 startup request L1 documentation freeze/readiness checkpoint",
            "py -m patchops.llm_browser.live_adapter_startup_request_l1_documentation_checkpoint",
            "passive-only",
        ),
    )

    aggregate_no_side_effects = (
        aggregate_gate.get("startup_allowed") is False
        and aggregate_gate.get("browser_started") is False
        and aggregate_gate.get("browser_session_created") is False
        and _as_list(aggregate_gate.get("side_effects_performed")) == []
    )

    checks: List[Dict[str, Any]] = [
        _check(
            "l1_aggregate_readiness_gate_still_passes",
            _payload_ok(aggregate_gate) and aggregate_no_side_effects,
            {"patch": aggregate_gate.get("patch"), "status": aggregate_gate.get("status"), "startup_allowed": aggregate_gate.get("startup_allowed")},
        ),
        _check("l1_documentation_paths_present", missing_docs == [], {"missing": missing_docs, "required_count": len(REQUIRED_DOC_PATHS)}),
        _check("l1_source_paths_present", missing_sources == [], {"missing": missing_sources, "required_count": len(REQUIRED_SOURCE_PATHS)}),
        _check("l1_focused_test_paths_present", missing_tests == [], {"missing": missing_tests, "required_count": len(REQUIRED_TEST_PATHS)}),
        _check("l1_freeze_doc_contains_passive_boundary", freeze_doc_ok, {"missing_phrases": freeze_doc_missing}),
        _check("l1_runner_doc_mentions_freeze_checkpoint", runner_doc_ok, {"missing_phrases": runner_doc_missing}),
        _check(
            "l1_documentation_freeze_keeps_no_browser_or_side_effects",
            aggregate_no_side_effects,
            {
                "startup_allowed": aggregate_gate.get("startup_allowed"),
                "browser_started": aggregate_gate.get("browser_started"),
                "browser_session_created": aggregate_gate.get("browser_session_created"),
                "side_effects_performed": aggregate_gate.get("side_effects_performed"),
            },
        ),
        _check("l1_documentation_checkpoint_payload_json_safe", True, {"checks_are_json_native": True}),
        _check("no_optional_browser_dependency_imports", forbidden_imports == [], {"forbidden_import_roots_present": forbidden_imports}),
        _check("l1_documentation_checkpoint_did_not_load_browser_optional_modules", forbidden_imports == [], {"newly_loaded_forbidden_modules": forbidden_imports}),
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
        "required_doc_paths": list(REQUIRED_DOC_PATHS),
        "required_source_paths": list(REQUIRED_SOURCE_PATHS),
        "required_test_paths": list(REQUIRED_TEST_PATHS),
        "missing_doc_paths": missing_docs,
        "missing_source_paths": missing_sources,
        "missing_test_paths": missing_tests,
        "aggregate_readiness_gate": dict(aggregate_gate),
        "case_count": aggregate_gate.get("case_count", 0),
        "case_names": list(_as_list(aggregate_gate.get("case_names"))),
        "checks": checks,
    }


def build_documentation_freeze_readiness_checkpoint(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l1_documentation_freeze_readiness_checkpoint(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser startup request L1 documentation freeze/readiness checkpoint",
        "PatchOps LLM browser live adapter startup request L1 documentation freeze/readiness checkpoint",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Cases      : {payload.get('case_count')}",
        f"Startup    : allowed={payload.get('startup_allowed')}",
        "Browser    : not started" if payload.get("browser_started") is False else "Browser    : started",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Docs       : required={len(_as_list(payload.get('required_doc_paths')))} missing={len(_as_list(payload.get('missing_doc_paths')))}",
        f"Sources    : required={len(_as_list(payload.get('required_source_paths')))} missing={len(_as_list(payload.get('missing_source_paths')))}",
        f"Tests      : required={len(_as_list(payload.get('required_test_paths')))} missing={len(_as_list(payload.get('missing_test_paths')))}",
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read back the passive L1 documentation freeze/readiness checkpoint.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to the current module's repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of operator text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l1_documentation_freeze_readiness_checkpoint(args.repo_root)
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
