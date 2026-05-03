from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_browser_start_authorization_l3_broad_validation_checkpoint as broad_checkpoint
from . import commands as llm_browser_commands

NAME = "L3.12 Browser Start Authorization L3 Final Acceptance Marker"
PHASE = "L3"
PATCH = "L3.12"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L4.1 Live adapter browser-start dry-run handoff contract"
SIDE_EFFECT_BOUNDARY = "passive-final-acceptance-marker-only"

FORBIDDEN_OPTIONAL_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

FINAL_ACCEPTANCE_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_authorization_l3_final_acceptance_marker --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_authorization_l3_final_acceptance_marker --repo-root C:\\dev\\patchops",
    "py -m patchops.cli llm-browser browser-start-authorization-l3-broad-validation --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "open --browser",
    "run-once",
    "watch-downloads",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_message",
    "send_or_submit",
)

REQUIRED_L3_FINAL_SOURCE_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
)

REQUIRED_L3_FINAL_DOC_PATHS: tuple[str, ...] = (
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_broad_validation_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_broad_validation_checkpoint.md",
)

REQUIRED_L3_FINAL_TEST_PATHS: tuple[str, ...] = (
    "tests/test_l3_12_browser_start_authorization_l3_final_acceptance_marker_current.py",
    "tests/test_l3_10_browser_start_authorization_l3_broad_validation_checkpoint_current.py",
    "tests/test_l3_11_browser_start_authorization_l3_broad_validation_cli_readback_current.py",
)

REQUIRED_COMMANDS: tuple[str, ...] = (
    "browser-start-authorization",
    "browser-start-authorization-fixtures",
    "browser-start-authorization-contract-gate",
    "browser-start-authorization-l3-readiness",
    "browser-start-authorization-l3-broad-validation",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L3.12 Live adapter browser-start authorization L3 final acceptance marker",
    "passive-only",
    "no Selenium import",
    "no browser start",
    "no browser session creation",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "git_commit_executed: false",
    "git_push_executed: false",
    NEXT_PATCH,
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


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _forbidden_imports_present() -> list[str]:
    return sorted({root for root in FORBIDDEN_OPTIONAL_ROOTS if any(name == root or name.startswith(root + ".") for name in sys.modules)})


def _forbidden_imports_loaded_since(before_modules: Iterable[str]) -> list[str]:
    before = set(before_modules)
    newly_loaded = set(sys.modules) - before
    return sorted({root for root in FORBIDDEN_OPTIONAL_ROOTS if any(name == root or name.startswith(root + ".") for name in newly_loaded)})


def _missing_paths(repo_root: Path, paths: Sequence[str]) -> list[str]:
    return sorted(path for path in paths if not (repo_root / path).exists())


def _read_text(repo_root: Path, rel_path: str) -> str:
    try:
        path = repo_root / rel_path
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return ""


def _missing_phrases(text: str, phrases: Sequence[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase not in text]


def _command_plan_is_passive(commands: Sequence[str]) -> tuple[bool, list[str]]:
    lowered = "\n".join(commands).lower()
    found = [fragment for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment in lowered]
    return found == [], found


def _payload_ok(payload: Mapping[str, Any]) -> bool:
    return bool(payload.get("ok") is True and str(payload.get("status")) == STATUS_PASS)


def _payload_no_live_effects(payload: Mapping[str, Any]) -> bool:
    return bool(
        payload.get("startup_authorized") is False
        and payload.get("startup_allowed") is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and payload.get("profile_directory_created") is False
        and _as_list(payload.get("filesystem_writes_performed")) == []
        and _as_list(payload.get("side_effects_performed")) == []
        and payload.get("optional_browser_dependencies_required") in (False, None)
    )


def _safe_broad_payload(repo_root: Path) -> tuple[Mapping[str, Any], str | None]:
    try:
        payload = broad_checkpoint.build_l3_browser_start_authorization_broad_validation_checkpoint(repo_root)
    except Exception as exc:  # pragma: no cover - operator diagnostic fallback
        return {}, f"{exc.__class__.__name__}: {exc}"
    return _as_mapping(payload), None


def _command_names_present() -> tuple[bool, list[str]]:
    names = set(llm_browser_commands.llm_browser_command_names())
    missing = sorted(command for command in REQUIRED_COMMANDS if command not in names)
    return missing == [], missing


def build_l3_browser_start_authorization_final_acceptance_marker(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _resolve_repo_root(repo_root)
    before_modules = set(sys.modules)

    broad_payload, broad_error = _safe_broad_payload(root)
    broad_ok = _payload_ok(broad_payload)
    broad_no_effects = _payload_no_live_effects(broad_payload) if broad_payload else False
    commands_present, missing_commands = _command_names_present()
    missing_sources = _missing_paths(root, REQUIRED_L3_FINAL_SOURCE_PATHS)
    missing_docs = _missing_paths(root, REQUIRED_L3_FINAL_DOC_PATHS)
    missing_tests = _missing_paths(root, REQUIRED_L3_FINAL_TEST_PATHS)
    doc_text = _read_text(root, "docs/llm_browser_live_adapter_browser_start_authorization_l3_final_acceptance_marker.md")
    missing_doc_phrases = _missing_phrases(doc_text, DOC_REQUIRED_PHRASES)
    command_plan_passive, forbidden_command_fragments = _command_plan_is_passive(FINAL_ACCEPTANCE_COMMANDS)
    executed_validation_commands: list[str] = []
    loaded_forbidden = _forbidden_imports_present()
    newly_loaded_forbidden = _forbidden_imports_loaded_since(before_modules)

    checks: list[dict[str, Any]] = [
        _check("l3_broad_validation_checkpoint_still_passes", broad_ok, {"patch": broad_payload.get("patch"), "status": broad_payload.get("status"), "error": broad_error}),
        _check("l3_broad_validation_checkpoint_remains_passive", broad_no_effects, {"broad_no_effects": broad_no_effects}),
        _check("l3_cli_surfaces_remain_present", commands_present, {"missing_commands": missing_commands, "required_commands": list(REQUIRED_COMMANDS)}),
        _check("l3_final_acceptance_artifacts_present", missing_sources == [] and missing_docs == [] and missing_tests == [], {"missing_sources": missing_sources, "missing_docs": missing_docs, "missing_tests": missing_tests}),
        _check("l3_final_acceptance_doc_contains_passive_boundary", missing_doc_phrases == [], {"missing_phrases": missing_doc_phrases}),
        _check("l3_final_acceptance_command_plan_is_readback_only", command_plan_passive, {"forbidden_fragments": forbidden_command_fragments, "planned_commands": list(FINAL_ACCEPTANCE_COMMANDS)}),
        _check("l3_final_acceptance_does_not_execute_planned_commands", executed_validation_commands == [], {"executed_validation_commands": executed_validation_commands}),
        _check("l3_final_acceptance_no_new_optional_browser_dependency_imports", newly_loaded_forbidden == [], {"loaded_forbidden_modules": loaded_forbidden, "newly_loaded_forbidden_modules": newly_loaded_forbidden}),
        _check("l3_final_acceptance_selenium_not_imported", "selenium" not in loaded_forbidden and "selenium" not in newly_loaded_forbidden, {"loaded_forbidden_modules": loaded_forbidden}),
    ]

    preview = {
        "broad_patch": broad_payload.get("patch"),
        "broad_status": broad_payload.get("status"),
        "missing_commands": missing_commands,
        "missing_sources": missing_sources,
        "missing_docs": missing_docs,
        "missing_tests": missing_tests,
        "final_acceptance_commands": list(FINAL_ACCEPTANCE_COMMANDS),
    }
    checks.append(_check("l3_final_acceptance_payload_json_safe", _json_safe(preview), preview))

    ok = all(check["ok"] for check in checks)
    return {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": bool(ok),
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": "selenium" in loaded_forbidden or "selenium" in newly_loaded_forbidden,
        "executed_validation_commands": executed_validation_commands,
        "final_acceptance_commands": list(FINAL_ACCEPTANCE_COMMANDS),
        "required_commands": list(REQUIRED_COMMANDS),
        "missing_commands": missing_commands,
        "required_source_paths": list(REQUIRED_L3_FINAL_SOURCE_PATHS),
        "required_doc_paths": list(REQUIRED_L3_FINAL_DOC_PATHS),
        "required_test_paths": list(REQUIRED_L3_FINAL_TEST_PATHS),
        "missing_source_paths": missing_sources,
        "missing_doc_paths": missing_docs,
        "missing_test_paths": missing_tests,
        "missing_doc_phrases": missing_doc_phrases,
        "broad_validation_checkpoint": dict(broad_payload),
        "operator_commit_recommended": True,
        "git_commit_executed": False,
        "git_push_executed": False,
        "loaded_forbidden_modules": loaded_forbidden,
        "newly_loaded_forbidden_modules": newly_loaded_forbidden,
        "checks": checks,
    }


def build_final_acceptance_marker(repo_root: str | Path | None = None) -> dict[str, Any]:
    return build_l3_browser_start_authorization_final_acceptance_marker(repo_root)


def render_text(payload: Mapping[str, Any]) -> str:
    checks = _as_list(payload.get("checks"))
    lines = [
        "PatchOps LLM browser browser-start authorization L3 final acceptance marker",
        "PatchOps LLM browser live adapter browser-start authorization L3 final acceptance marker",
        f"Name       : {payload.get('name')}",
        f"Phase      : {payload.get('phase')}",
        f"Patch      : {payload.get('patch')}",
        f"Status     : {payload.get('status')}",
        f"OK         : {payload.get('ok')}",
        f"Startup    : authorized={str(payload.get('startup_authorized')).lower()} allowed={str(payload.get('startup_allowed')).lower()}",
        f"Browser    : started={payload.get('browser_started')}",
        f"Session    : created={payload.get('browser_session_created')}",
        f"ProfileDir : created={payload.get('profile_directory_created')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Commands   : required={len(_as_list(payload.get('required_commands')))} missing={len(_as_list(payload.get('missing_commands')))} planned={len(_as_list(payload.get('final_acceptance_commands')))} executed={len(_as_list(payload.get('executed_validation_commands')))}",
        f"Commit     : recommended={str(payload.get('operator_commit_recommended')).lower()} executed={str(payload.get('git_commit_executed')).lower()} pushed={str(payload.get('git_push_executed')).lower()}",
        "Checks:",
    ]
    for check in checks:
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
            if check.get("ok") is not True:
                lines.append(f"  details: {json.dumps(check.get('details', {}), sort_keys=True)}")
    lines.append(f"Next patch : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Passive L3 final acceptance marker for browser-start authorization.")
    parser.add_argument("--repo-root", default=None, help="PatchOps repository root. Defaults to current module's repository root.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_arg_parser().parse_args(list(argv or []))
    payload = build_l3_browser_start_authorization_final_acceptance_marker(args.repo_root)
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
