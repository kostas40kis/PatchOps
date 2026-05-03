"""Passive L5 supervised-launch handoff documentation freeze/readiness checkpoint.

This module validates the accepted L5.1 through L5.8 supervised-launch handoff
surfaces and freezes the passive documentation boundary before the L5 broad
validation checkpoint. It is intentionally model/readback-only: it imports no
Selenium, starts no browser, creates no browser session/profile directory,
performs no adapter filesystem writes, and performs no click/download/paste/send
or package-run operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PATCH = "L5.9"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.9 Browser Start Supervised Launch Handoff Documentation Freeze Readiness Checkpoint"
NEXT_PATCH = "L5.10 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-l5-documentation-readiness-only"

FORBIDDEN_OPTIONAL_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

REQUIRED_COMMANDS: tuple[str, ...] = (
    "browser-start-supervised-launch-handoff",
    "browser-start-supervised-launch-handoff-fixtures",
    "browser-start-supervised-launch-handoff-contract-gate",
    "browser-start-supervised-launch-handoff-l5-readiness",
)

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_contract.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_documentation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_contract.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_documentation_freeze_readiness_checkpoint.md",
    "tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py",
    "tests/test_l5_02_browser_start_supervised_launch_handoff_cli_readback_current.py",
    "tests/test_l5_03_browser_start_supervised_launch_handoff_fixture_matrix_current.py",
    "tests/test_l5_04_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_05_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_current.py",
    "tests/test_l5_06_browser_start_supervised_launch_handoff_contract_gate_cli_readback_current.py",
    "tests/test_l5_07_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate_current.py",
    "tests/test_l5_08_browser_start_supervised_launch_handoff_l5_readiness_cli_readback_current.py",
    "tests/test_l5_09_browser_start_supervised_launch_handoff_l5_documentation_checkpoint_current.py",
)

SAFETY_PHRASES: tuple[str, ...] = (
    "no Selenium import",
    "no browser start",
    "no browser session creation",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "no commit or push",
)

PROGRESSION_PHRASES: tuple[str, ...] = (
    "L5.1 supervised-launch handoff contract",
    "L5.2 supervised-launch handoff CLI/readback",
    "L5.3 supervised-launch handoff fixture matrix",
    "L5.4 fixture matrix CLI/readback",
    "L5.5 fixture matrix contract gate",
    "L5.6 contract gate CLI/readback",
    "L5.7 aggregate readiness gate",
    "L5.8 aggregate readiness gate CLI/readback",
    NEXT_PATCH,
)

LIVE_SIDE_EFFECT_OPERATIONS: tuple[str, ...] = (
    "import_selenium",
    "start_browser",
    "create_browser_session",
    "create_profile_directory",
    "adapter_filesystem_write",
    "click_download",
    "paste_to_composer",
    "send_message",
    "run_downloaded_package",
    "commit",
    "push",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


def _forbidden_imports_present() -> list[str]:
    return sorted(
        root
        for root in FORBIDDEN_OPTIONAL_ROOTS
        if any(name == root or name.startswith(root + ".") for name in sys.modules)
    )


def _forbidden_imports_loaded_since(before_modules: set[str]) -> list[str]:
    newly_loaded = set(sys.modules) - before_modules
    return sorted(
        root
        for root in FORBIDDEN_OPTIONAL_ROOTS
        if any(name == root or name.startswith(root + ".") for name in newly_loaded)
    )


def _json_safe(payload: Mapping[str, Any]) -> bool:
    try:
        json.dumps(payload, sort_keys=True)
    except TypeError:
        return False
    return True


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _read_text_if_present(path: Path) -> str:
    try:
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return ""


def build_l5_browser_start_supervised_launch_handoff_documentation_checkpoint(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return the passive L5 documentation checkpoint payload."""

    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    from patchops.llm_browser import commands
    from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate

    command_names = set(commands.llm_browser_command_names())
    missing_commands = [command for command in REQUIRED_COMMANDS if command not in command_names]

    readiness = live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate.build_l5_aggregate_readiness_gate(root)

    repo_path_state = {rel: (root / rel).exists() for rel in REQUIRED_REPO_PATHS}
    missing_repo_paths = [rel for rel, exists in repo_path_state.items() if not exists]

    canonical_doc = root / "docs" / "llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_documentation_freeze_readiness_checkpoint.md"
    canonical_doc_text = _read_text_if_present(canonical_doc)
    missing_safety_phrases = [phrase for phrase in SAFETY_PHRASES if phrase not in canonical_doc_text]
    missing_progression_phrases = [phrase for phrase in PROGRESSION_PHRASES if phrase not in canonical_doc_text]

    forbidden_imports_present = _forbidden_imports_present()
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    readiness_passive = (
        readiness.get("ok") is True
        and readiness.get("status") == STATUS_PASS
        and readiness.get("startup_authorized") is False
        and readiness.get("startup_allowed") is False
        and readiness.get("browser_started") is False
        and readiness.get("browser_session_created") is False
        and readiness.get("driver_created") is False
        and readiness.get("profile_directory_created") is False
        and readiness.get("filesystem_writes_performed") == []
        and readiness.get("side_effects_performed") == []
        and readiness.get("optional_browser_dependencies_required") is False
        and readiness.get("selenium_imported") is False
    )

    checks = [
        _check("l5_documentation_checkpoint_required_cli_commands_present", missing_commands == [], {"missing_commands": missing_commands}),
        _check("l5_documentation_checkpoint_required_source_docs_tests_present", missing_repo_paths == [], {"missing_repo_paths": missing_repo_paths, "repo_path_state": repo_path_state}),
        _check("l5_documentation_checkpoint_doc_contains_safety_boundary", missing_safety_phrases == [], {"missing_safety_phrases": missing_safety_phrases}),
        _check("l5_documentation_checkpoint_doc_contains_progression_and_next_patch", missing_progression_phrases == [], {"missing_progression_phrases": missing_progression_phrases}),
        _check("l5_documentation_checkpoint_keeps_l5_aggregate_readiness_passive", readiness_passive, {"side_effect_operations": list(LIVE_SIDE_EFFECT_OPERATIONS)}),
        _check("l5_documentation_checkpoint_no_optional_browser_dependency_imports_present", forbidden_imports_present == [], {"forbidden_imports_present": forbidden_imports_present}),
        _check("l5_documentation_checkpoint_did_not_load_optional_browser_dependencies", forbidden_imports_newly_loaded == [], {"forbidden_imports_newly_loaded": forbidden_imports_newly_loaded}),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "side_effect_operations": list(LIVE_SIDE_EFFECT_OPERATIONS),
        "repo_root": str(root),
        "source_contract_patch": "L5.1",
        "source_fixture_matrix_patch": "L5.3",
        "source_contract_gate_patch": "L5.5",
        "source_aggregate_readiness_patch": "L5.7",
        "source_cli_readback_patch": "L5.8",
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "executed_validation_commands": [],
        "optional_browser_dependencies_required": False,
        "optional_browser_dependencies_imported": forbidden_imports_present,
        "forbidden_optional_imports_newly_loaded": forbidden_imports_newly_loaded,
        "selenium_imported": "selenium" in forbidden_imports_present,
        "git_commit_executed": False,
        "git_push_executed": False,
        "required_commands": list(REQUIRED_COMMANDS),
        "missing_commands": missing_commands,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "missing_safety_phrases": missing_safety_phrases,
        "missing_progression_phrases": missing_progression_phrases,
        "readiness_gate": readiness,
        "checks": checks,
    }
    checks.append(_check("l5_documentation_checkpoint_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status     : {payload.get('status')}",
        f"Patch      : {payload.get('patch')}",
        f"Repo Root  : {payload.get('repo_root')}",
        f"Startup    : authorized={payload.get('startup_authorized')} allowed={payload.get('startup_allowed')}",
        f"Browser    : started={payload.get('browser_started')} driver_created={payload.get('driver_created')}",
        f"Session    : created={payload.get('browser_session_created')}",
        f"ProfileDir : created={payload.get('profile_directory_created')}",
        f"Selenium   : imported={payload.get('selenium_imported')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"MissingCmd : {payload.get('missing_commands')}",
        f"MissingPath: {payload.get('missing_repo_paths')}",
        f"Next patch : {payload.get('next_patch')}",
        "",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_l5_browser_start_supervised_launch_handoff_documentation_checkpoint(args.repo_root)
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
