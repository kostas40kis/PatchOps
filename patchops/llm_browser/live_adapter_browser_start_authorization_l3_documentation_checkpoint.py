from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

NAME = "L3.9 Browser Start Authorization Documentation Freeze Readiness Checkpoint"
PATCH = "L3.9"
PHASE = "L3"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L3.10 Live adapter browser-start authorization L3 broad validation checkpoint"
SIDE_EFFECT_BOUNDARY = "passive-documentation-readiness-only"

FORBIDDEN_OPTIONAL_ROOTS = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

REQUIRED_COMMANDS = (
    "browser-start-authorization",
    "browser-start-authorization-fixtures",
    "browser-start-authorization-contract-gate",
    "browser-start-authorization-l3-readiness",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_browser_start_authorization.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_authorization.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_documentation_freeze_readiness_checkpoint.md",
    "tests/test_l3_browser_start_authorization_current.py",
    "tests/test_l3_02_browser_start_authorization_cli_readback_current.py",
    "tests/test_l3_03_browser_start_authorization_fixture_matrix_current.py",
    "tests/test_l3_04_browser_start_authorization_fixture_matrix_cli_readback_current.py",
    "tests/test_l3_05_browser_start_authorization_fixture_matrix_contract_gate_current.py",
    "tests/test_l3_06_browser_start_authorization_contract_gate_cli_readback_current.py",
    "tests/test_l3_07_browser_start_authorization_l3_aggregate_readiness_gate_current.py",
    "tests/test_l3_08_browser_start_authorization_l3_readiness_cli_readback_current.py",
)

SAFETY_PHRASES = (
    "no Selenium import",
    "no browser start",
    "no browser session creation",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "no commit or push",
)

LIVE_SIDE_EFFECT_OPERATIONS = (
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


def _forbidden_imports_present() -> list[str]:
    return [root for root in FORBIDDEN_OPTIONAL_ROOTS if any(name == root or name.startswith(root + ".") for name in sys.modules)]


def _forbidden_imports_loaded_since(before_modules: set[str]) -> list[str]:
    newly_loaded = set(sys.modules) - before_modules
    return [root for root in FORBIDDEN_OPTIONAL_ROOTS if any(name == root or name.startswith(root + ".") for name in newly_loaded)]


def _json_safe(payload: Mapping[str, Any]) -> bool:
    try:
        json.dumps(payload, sort_keys=True)
    except TypeError:
        return False
    return True


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": dict(details or {})}


def _read_text_if_present(path: Path) -> str:
    try:
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return ""


def build_l3_browser_start_authorization_documentation_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or ".").resolve()
    before_modules = set(sys.modules)

    from patchops.llm_browser import commands
    from patchops.llm_browser import live_adapter_browser_start_authorization_l3_aggregate_readiness_gate

    command_names = set(commands.llm_browser_command_names())
    missing_commands = [command for command in REQUIRED_COMMANDS if command not in command_names]

    readiness = live_adapter_browser_start_authorization_l3_aggregate_readiness_gate.build_l3_browser_start_authorization_aggregate_readiness_gate(root)

    repo_path_state = {rel: (root / rel).exists() for rel in REQUIRED_REPO_PATHS}
    missing_repo_paths = [rel for rel, exists in repo_path_state.items() if not exists]

    canonical_doc = root / "docs" / "llm_browser_live_adapter_browser_start_authorization_l3_documentation_freeze_readiness_checkpoint.md"
    canonical_doc_text = _read_text_if_present(canonical_doc)
    missing_safety_phrases = [phrase for phrase in SAFETY_PHRASES if phrase not in canonical_doc_text]
    missing_progression_phrases = [
        phrase
        for phrase in (
            "L3.1 explicit browser-start authorization contract",
            "L3.2 explicit browser-start authorization CLI/readback",
            "L3.3 browser-start authorization fixture matrix",
            "L3.4 fixture matrix CLI/readback",
            "L3.5 fixture matrix contract gate",
            "L3.6 fixture matrix contract gate CLI/readback",
            "L3.7 aggregate readiness gate",
            "L3.8 aggregate readiness gate CLI/readback",
            NEXT_PATCH,
        )
        if phrase not in canonical_doc_text
    ]

    forbidden_imports_present = _forbidden_imports_present()
    forbidden_imports_newly_loaded = _forbidden_imports_loaded_since(before_modules)

    readiness_passive = (
        readiness.get("ok") is True
        and readiness.get("status") == STATUS_PASS
        and readiness.get("startup_authorized") is False
        and readiness.get("browser_started") is False
        and readiness.get("browser_session_created") is False
        and readiness.get("profile_directory_created") is False
        and readiness.get("side_effects_performed") == []
        and readiness.get("filesystem_writes_performed") == []
        and readiness.get("optional_browser_dependencies_required") is False
        and readiness.get("selenium_imported") is False
    )

    checks = [
        _check(
            "l3_07_aggregate_readiness_still_passes",
            readiness.get("ok") is True and readiness.get("status") == STATUS_PASS,
            {"readiness_patch": readiness.get("patch"), "readiness_status": readiness.get("status")},
        ),
        _check(
            "l3_08_cli_readback_command_still_registered",
            "browser-start-authorization-l3-readiness" in command_names,
            {"missing_commands": missing_commands},
        ),
        _check(
            "l3_required_source_docs_tests_present",
            missing_repo_paths == [],
            {"missing_repo_paths": missing_repo_paths, "repo_path_state": repo_path_state},
        ),
        _check(
            "l3_documentation_checkpoint_doc_contains_safety_boundary",
            missing_safety_phrases == [],
            {"missing_safety_phrases": missing_safety_phrases},
        ),
        _check(
            "l3_documentation_checkpoint_doc_contains_progression_and_next_patch",
            missing_progression_phrases == [],
            {"missing_progression_phrases": missing_progression_phrases},
        ),
        _check(
            "l3_documentation_checkpoint_keeps_live_side_effects_blocked",
            readiness_passive,
            {"side_effect_operations": list(LIVE_SIDE_EFFECT_OPERATIONS)},
        ),
        _check(
            "l3_documentation_checkpoint_no_optional_browser_dependency_imports_present",
            forbidden_imports_present == [],
            {"forbidden_imports_present": forbidden_imports_present},
        ),
        _check(
            "l3_documentation_checkpoint_did_not_load_optional_browser_dependencies",
            forbidden_imports_newly_loaded == [],
            {"forbidden_imports_newly_loaded": forbidden_imports_newly_loaded},
        ),
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
        "startup_authorized": False,
        "browser_started": False,
        "browser_session_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": False,
        "required_commands": list(REQUIRED_COMMANDS),
        "missing_commands": missing_commands,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "missing_safety_phrases": missing_safety_phrases,
        "missing_progression_phrases": missing_progression_phrases,
        "readiness_gate": readiness,
        "checks": checks,
    }
    payload["payload_json_safe"] = _json_safe(payload)
    return payload


def render_l3_browser_start_authorization_documentation_checkpoint(payload: Mapping[str, Any]) -> str:
    lines = [
        "L3.9 Browser Start Authorization Documentation Freeze Readiness Checkpoint",
        f"Status     : {payload.get('status')}",
        f"Patch      : {payload.get('patch')}",
        f"Startup    : authorized={str(payload.get('startup_authorized')).lower()}",
        f"Browser    : started={payload.get('browser_started')}",
        f"Session    : created={payload.get('browser_session_created')}",
        f"ProfileDir : created={payload.get('profile_directory_created')}",
        f"SideEffects: {payload.get('side_effects_performed')}",
        f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
        f"MissingCmd : {payload.get('missing_commands')}",
        f"MissingPath: {payload.get('missing_repo_paths')}",
        f"Next patch : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        lines.append(f"- {check.get('name')}: {'PASS' if check.get('ok') else 'FAIL'}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_l3_browser_start_authorization_documentation_checkpoint(args.repo_root)
    if args.json:
        print(json.dumps(payload, indent=None if args.compact else 2, sort_keys=True))
    else:
        print(render_l3_browser_start_authorization_documentation_checkpoint(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
