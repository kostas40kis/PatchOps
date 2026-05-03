from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence

from . import l2_10_broad_validation as broad_checkpoint
from . import commands as llm_browser_commands

NAME = "llm_browser_live_adapter_browser_profile_l2_final_acceptance_marker"
PHASE = "L2"
PATCH = "L2.12"
REPAIR_PATCH = "L2.12d"
NEXT_PATCH = "L3.1 Live adapter explicit browser-start authorization contract"
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
FINAL_ACCEPTANCE_READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_profile_l2_final_acceptance_marker --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_profile_l2_final_acceptance_marker --repo-root C:\\dev\\patchops",
    "py -m patchops.cli llm-browser profile-preflight-l2-broad-validation --repo-root C:\\dev\\patchops --json --compact",
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
FINAL_DOC_PATHS: tuple[str, ...] = (
    "docs/llm_browser_live_adapter_browser_profile_l2_final_acceptance_marker.md",
    "docs/llm_browser_l2_12_final_acceptance_marker.md",
    "docs/llm_browser_runner.md",
)
FINAL_SOURCE_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_profile_l2_final_acceptance_marker.py",
    "patchops/llm_browser/l2_10_broad_validation.py",
    "patchops/llm_browser/commands.py",
)
FINAL_TEST_PATHS: tuple[str, ...] = (
    "tests/test_l2_12_final_acceptance_marker_current.py",
    "tests/test_l2_10_broad_validation_current.py",
    "tests/test_l2_11_broad_validation_cli_readback_current.py",
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


def _new_forbidden_imports(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
            found.append(root)
    return sorted(set(found))


def _loaded_forbidden_imports() -> list[str]:
    found: list[str] = []
    for root in FORBIDDEN_IMPORT_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in sys.modules):
            found.append(root)
    return sorted(set(found))


def _missing_paths(repo_root: Path, paths: Iterable[str]) -> list[str]:
    return sorted(path for path in paths if not (repo_root / path).exists())


def _read_text(repo_root: Path, relative_path: str) -> str:
    try:
        return (repo_root / relative_path).read_text(encoding="utf-8")
    except OSError:
        return ""


def _doc_has_phrases(repo_root: Path, relative_path: str, phrases: Iterable[str]) -> tuple[bool, list[str]]:
    text = _read_text(repo_root, relative_path)
    missing = [phrase for phrase in phrases if phrase not in text]
    return missing == [], missing


def _command_plan_is_passive(commands: Sequence[str]) -> bool:
    lowered = "\n".join(commands).lower()
    return not any(fragment in lowered for fragment in FORBIDDEN_COMMAND_FRAGMENTS)


def _payload_has_no_profile_or_browser_side_effects(payload: Mapping[str, Any]) -> bool:
    return bool(
        payload.get("startup_allowed") is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and payload.get("profile_directory_created") is False
        and _as_list(payload.get("filesystem_writes_performed")) == []
        and _as_list(payload.get("side_effects_performed")) == []
        and payload.get("optional_browser_dependencies_required") in (False, None)
    )


def _l2_11_cli_surface_present() -> bool:
    names = set(llm_browser_commands.llm_browser_command_names())
    return "profile-preflight-l2-broad-validation" in names


def _safe_broad_payload(repo_root: Path) -> tuple[Mapping[str, Any], str | None]:
    try:
        payload = broad_checkpoint.build_l2_broad_validation_checkpoint(repo_root)
    except Exception as exc:  # pragma: no cover - diagnostic fallback for operator reports
        return {}, f"{exc.__class__.__name__}: {exc}"
    return _as_mapping(payload), None


def build_l2_final_acceptance_marker(repo_root: str | Path | None = None) -> Dict[str, Any]:
    root = _resolve_repo_root(repo_root)
    before_modules = set(sys.modules)

    broad_payload, broad_error = _safe_broad_payload(root)
    broad_ok = _payload_ok(broad_payload)
    broad_no_effects = _payload_has_no_profile_or_browser_side_effects(broad_payload) if broad_payload else False
    command_plan = list(FINAL_ACCEPTANCE_READBACK_COMMANDS)
    executed_validation_commands: list[str] = []

    final_doc_ok, final_doc_missing = _doc_has_phrases(
        root,
        "docs/llm_browser_live_adapter_browser_profile_l2_final_acceptance_marker.md",
        (
            "L2.12",
            "final acceptance marker",
            "passive-only",
            "no Selenium import",
            "no browser start",
            "no profile directory creation",
            "git_commit_executed: false",
            "git_push_executed: false",
            NEXT_PATCH,
        ),
    )
    runner_doc_ok, runner_doc_missing = _doc_has_phrases(
        root,
        "docs/llm_browser_runner.md",
        (
            "PATCHOPS_L2_12_FINAL_ACCEPTANCE_MARKER_START",
            "L2.12 browser profile preflight L2 final acceptance marker",
            "live_adapter_browser_profile_l2_final_acceptance_marker",
            NEXT_PATCH,
        ),
    )

    missing_final_docs = _missing_paths(root, FINAL_DOC_PATHS)
    missing_final_sources = _missing_paths(root, FINAL_SOURCE_PATHS)
    missing_final_tests = _missing_paths(root, FINAL_TEST_PATHS)
    l2_11_cli_surface_present = _l2_11_cli_surface_present()
    newly_loaded_forbidden = _new_forbidden_imports(before_modules)
    loaded_forbidden = _loaded_forbidden_imports()

    checks: list[Dict[str, Any]] = [
        _check("l2_broad_validation_checkpoint_still_passes", broad_ok, {"patch": broad_payload.get("patch"), "status": broad_payload.get("status"), "error": broad_error}),
        _check("l2_broad_validation_cli_readback_surface_present", l2_11_cli_surface_present, {"command": "profile-preflight-l2-broad-validation"}),
        _check("l2_final_acceptance_artifacts_present", missing_final_docs == [] and missing_final_sources == [] and missing_final_tests == [], {"missing_docs": missing_final_docs, "missing_sources": missing_final_sources, "missing_tests": missing_final_tests}),
        _check("l2_final_acceptance_doc_contains_passive_boundary", final_doc_ok, {"missing_phrases": final_doc_missing}),
        _check("l2_runner_doc_mentions_final_acceptance_marker", runner_doc_ok, {"missing_phrases": runner_doc_missing}),
        _check("l2_final_acceptance_no_browser_profile_or_side_effects", broad_no_effects, {"broad_validation_no_effects": broad_no_effects}),
        _check("l2_final_acceptance_command_plan_is_passive", _command_plan_is_passive(command_plan), {"planned_command_count": len(command_plan)}),
        _check("l2_final_acceptance_does_not_execute_validation_commands", executed_validation_commands == [], {"executed_validation_commands": executed_validation_commands}),
        _check("l2_final_acceptance_ready_for_operator_commit", broad_ok and l2_11_cli_surface_present, {"commit_recommended": True, "commit_executed": False, "push_executed": False}),
        _check("no_new_optional_browser_dependency_imports", newly_loaded_forbidden == [], {"already_loaded_optional_browser_modules": loaded_forbidden, "newly_loaded_forbidden_modules": newly_loaded_forbidden}),
        _check("selenium_not_imported_by_final_acceptance_marker", "selenium" not in loaded_forbidden and "selenium" not in newly_loaded_forbidden, {"loaded_forbidden_modules": loaded_forbidden}),
    ]

    payload_preview = {
        "broad_validation_checkpoint": broad_payload,
        "missing_final_docs": missing_final_docs,
        "missing_final_sources": missing_final_sources,
        "missing_final_tests": missing_final_tests,
        "final_acceptance_commands": command_plan,
    }
    checks.append(_check("l2_final_acceptance_payload_json_safe", _json_safe(payload_preview), {"checks_are_json_native": True}))

    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "repair_patch": REPAIR_PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": bool(ok),
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": "passive-only final acceptance readback; no live browser automation",
        "side_effect_operations": list(SIDE_EFFECT_OPERATIONS),
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "executed_validation_commands": executed_validation_commands,
        "final_acceptance_commands": command_plan,
        "required_final_doc_paths": list(FINAL_DOC_PATHS),
        "required_final_source_paths": list(FINAL_SOURCE_PATHS),
        "required_final_test_paths": list(FINAL_TEST_PATHS),
        "missing_final_doc_paths": missing_final_docs,
        "missing_final_source_paths": missing_final_sources,
        "missing_final_test_paths": missing_final_tests,
        "broad_validation_checkpoint": dict(broad_payload),
        "case_count": broad_payload.get("case_count", 0),
        "case_names": list(_as_list(broad_payload.get("case_names"))),
        "operator_commit_recommended": True,
        "git_commit_executed": False,
        "git_push_executed": False,
        "loaded_forbidden_modules": loaded_forbidden,
        "newly_loaded_forbidden_modules": newly_loaded_forbidden,
        "checks": checks,
    }


def build_final_acceptance_marker(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l2_final_acceptance_marker(repo_root)


def build_profile_preflight_l2_final_acceptance_marker(repo_root: str | Path | None = None) -> Dict[str, Any]:
    return build_l2_final_acceptance_marker(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps LLM browser profile preflight L2 final acceptance marker",
        "PatchOps LLM browser live adapter browser profile preflight L2 final acceptance marker",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Repair     : {payload.get('repair_patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Startup    : allowed={payload.get('startup_allowed')}",
        "Browser    : not started" if payload.get("browser_started") is False else "Browser    : started",
        f"Profile    : created={payload.get('profile_directory_created')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Commands   : planned={len(_as_list(payload.get('final_acceptance_commands')))} executed={len(_as_list(payload.get('executed_validation_commands')))}",
        f"Docs       : required={len(_as_list(payload.get('required_final_doc_paths')))} missing={len(_as_list(payload.get('missing_final_doc_paths')))}",
        f"Sources    : required={len(_as_list(payload.get('required_final_source_paths')))} missing={len(_as_list(payload.get('missing_final_source_paths')))}",
        f"Tests      : required={len(_as_list(payload.get('required_final_test_paths')))} missing={len(_as_list(payload.get('missing_final_test_paths')))}",
        f"Cases      : {payload.get('case_count')}",
        f"Commit     : recommended={str(payload.get('operator_commit_recommended')).lower()} executed={str(payload.get('git_commit_executed')).lower()} pushed={str(payload.get('git_push_executed')).lower()}",
        "Checks:",
    ]
    for check in _as_list(payload.get("checks")):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
            if check.get("ok") is not True:
                lines.append(f"  details: {json.dumps(check.get('details', {}), sort_keys=True)}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L2 final acceptance marker for the browser-profile preflight stack.")
    parser.add_argument("--repo-root", default=str(_repo_root_from_here()))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    payload = build_l2_final_acceptance_marker(args.repo_root)
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
