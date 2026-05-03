"""Passive L5 supervised-launch handoff broad validation checkpoint.

This module performs a broad, readback-only validation of the accepted L5.1
through L5.9 supervised-launch handoff surfaces. It deliberately avoids every
live side effect: it imports no Selenium, starts no browser, creates no browser
session/profile directory, performs no adapter filesystem writes, and performs
no click/download/paste/send/package-run operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PATCH = "L5.10"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.10 Browser Start Supervised Launch Handoff L5 Broad Validation Checkpoint"
NEXT_PATCH = "L5.11 Live adapter browser-start supervised launch handoff L5 broad validation checkpoint CLI/readback"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-l5-broad-validation-checkpoint-only"

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
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint.py",
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
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint.md",
    "tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py",
    "tests/test_l5_02_browser_start_supervised_launch_handoff_cli_readback_current.py",
    "tests/test_l5_03_browser_start_supervised_launch_handoff_fixture_matrix_current.py",
    "tests/test_l5_04_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_05_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_current.py",
    "tests/test_l5_06_browser_start_supervised_launch_handoff_contract_gate_cli_readback_current.py",
    "tests/test_l5_07_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate_current.py",
    "tests/test_l5_08_browser_start_supervised_launch_handoff_l5_readiness_cli_readback_current.py",
    "tests/test_l5_09_browser_start_supervised_launch_handoff_l5_documentation_checkpoint_current.py",
    "tests/test_l5_10_supervised_launch_l5_broad_validation_checkpoint_current.py",
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
    "L5.9 documentation freeze/readiness checkpoint",
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

BROAD_VALIDATION_COMMAND_PLAN: tuple[str, ...] = (
    "python -m compileall patchops/llm_browser tests",
    "python -m pytest -q tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py tests/test_l5_02_browser_start_supervised_launch_handoff_cli_readback_current.py tests/test_l5_03_browser_start_supervised_launch_handoff_fixture_matrix_current.py tests/test_l5_04_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback_current.py tests/test_l5_05_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_current.py tests/test_l5_06_browser_start_supervised_launch_handoff_contract_gate_cli_readback_current.py tests/test_l5_07_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate_current.py tests/test_l5_08_browser_start_supervised_launch_handoff_l5_readiness_cli_readback_current.py tests/test_l5_09_browser_start_supervised_launch_handoff_l5_documentation_checkpoint_current.py tests/test_l5_10_supervised_launch_l5_broad_validation_checkpoint_current.py",
    "python -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint --repo-root C:\\dev\\patchops --json --compact",
)

FORBIDDEN_PLAN_FRAGMENTS: tuple[str, ...] = (
    "llm-browser open",
    "open --browser",
    "run-once",
    "watch-downloads",
    "selenium",
    "webdriver",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_message",
    "send_or_submit",
    "git commit",
    "git push",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


def _missing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    return [rel for rel in paths if not (root / rel).exists()]


def _read_text_if_present(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": dict(detail or {})}


def _json_safe(value: object) -> bool:
    try:
        json.dumps(value, sort_keys=True)
        return True
    except TypeError:
        return False


def _forbidden_imports_present() -> list[str]:
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in sys.modules)


def _forbidden_imports_loaded_since(before: set[str]) -> list[str]:
    after = set(sys.modules)
    return sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)


def _llm_browser_command_names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
    except Exception:
        return ()
    try:
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()


def _plan_is_passive(commands: Sequence[str]) -> bool:
    lowered = "\n".join(commands).lower()
    return not any(fragment.lower() in lowered for fragment in FORBIDDEN_PLAN_FRAGMENTS)


def build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L5.10 broad validation checkpoint payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate as readiness_gate
    from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_l5_documentation_checkpoint as documentation_checkpoint

    readiness = readiness_gate.build_l5_aggregate_readiness_gate(root)
    documentation = documentation_checkpoint.build_l5_browser_start_supervised_launch_handoff_documentation_checkpoint(root)

    command_names = _llm_browser_command_names()
    missing_commands = [name for name in REQUIRED_COMMANDS if name not in command_names]
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)

    canonical_doc = root / "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_broad_validation_checkpoint.md"
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

    documentation_passive = (
        documentation.get("ok") is True
        and documentation.get("status") == STATUS_PASS
        and documentation.get("startup_authorized") is False
        and documentation.get("startup_allowed") is False
        and documentation.get("browser_started") is False
        and documentation.get("browser_session_created") is False
        and documentation.get("driver_created") is False
        and documentation.get("profile_directory_created") is False
        and documentation.get("filesystem_writes_performed") == []
        and documentation.get("side_effects_performed") == []
        and documentation.get("optional_browser_dependencies_required") is False
        and documentation.get("selenium_imported") is False
    )

    checks = [
        _check("l5_broad_validation_required_cli_commands_present", missing_commands == [], {"missing_commands": missing_commands}),
        _check("l5_broad_validation_required_source_docs_tests_present", missing_repo_paths == [], {"missing_repo_paths": missing_repo_paths}),
        _check("l5_broad_validation_l5_aggregate_readiness_still_passive", readiness_passive, {"readiness_status": readiness.get("status"), "readiness_ok": readiness.get("ok")}),
        _check("l5_broad_validation_l5_documentation_checkpoint_still_passive", documentation_passive, {"documentation_status": documentation.get("status"), "documentation_ok": documentation.get("ok")}),
        _check("l5_broad_validation_command_plan_is_readback_only", _plan_is_passive(BROAD_VALIDATION_COMMAND_PLAN), {"planned_commands": list(BROAD_VALIDATION_COMMAND_PLAN)}),
        _check("l5_broad_validation_doc_contains_safety_boundary", missing_safety_phrases == [], {"missing_safety_phrases": missing_safety_phrases}),
        _check("l5_broad_validation_doc_contains_progression_and_next_patch", missing_progression_phrases == [], {"missing_progression_phrases": missing_progression_phrases}),
        _check("l5_broad_validation_no_optional_browser_dependency_imports_present", forbidden_imports_present == [], {"forbidden_imports_present": forbidden_imports_present}),
        _check("l5_broad_validation_did_not_load_optional_browser_dependencies", forbidden_imports_newly_loaded == [], {"forbidden_imports_newly_loaded": forbidden_imports_newly_loaded}),
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
        "source_patches": {
            "L5.1": "supervised-launch handoff contract",
            "L5.2": "supervised-launch handoff CLI/readback",
            "L5.3": "supervised-launch handoff fixture matrix",
            "L5.4": "fixture matrix CLI/readback",
            "L5.5": "fixture matrix contract gate",
            "L5.6": "contract gate CLI/readback",
            "L5.7": {"status": readiness.get("status"), "ok": readiness.get("ok")},
            "L5.8": {"cli_command": "browser-start-supervised-launch-handoff-l5-readiness", "registered": "browser-start-supervised-launch-handoff-l5-readiness" in command_names},
            "L5.9": {"status": documentation.get("status"), "ok": documentation.get("ok")},
        },
        "readiness_gate": readiness,
        "documentation_checkpoint": documentation,
        "required_commands": list(REQUIRED_COMMANDS),
        "missing_commands": missing_commands,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "missing_safety_phrases": missing_safety_phrases,
        "missing_progression_phrases": missing_progression_phrases,
        "broad_validation_command_plan": list(BROAD_VALIDATION_COMMAND_PLAN),
        "executed_validation_commands": [],
        "modelled_only": True,
        "startup_authorized": False,
        "startup_allowed": False,
        "live_driver_session_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "forbidden_imports_present": forbidden_imports_present,
        "forbidden_imports_newly_loaded": forbidden_imports_newly_loaded,
        "checks": checks,
    }
    checks.append(_check("l5_broad_validation_payload_json_safe", _json_safe(payload)))
    ok = all(check["ok"] for check in checks)
    payload["ok"] = ok
    payload["status"] = STATUS_PASS if ok else STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        "=" * len(NAME),
        f"Status          : {payload.get('status')}",
        f"Patch           : {payload.get('patch')}",
        f"Phase           : {payload.get('phase')}",
        f"Modelled Only   : {payload.get('modelled_only')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Session Created : {payload.get('browser_session_created')}",
        f"Driver Created  : {payload.get('driver_created')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"SideEffects     : {payload.get('side_effects_performed')}",
        f"Filesystem      : writes={payload.get('filesystem_writes_performed')}",
        f"Selenium Import : {payload.get('selenium_imported')}",
        f"Missing Commands: {payload.get('missing_commands')}",
        f"Missing Paths   : {payload.get('missing_repo_paths')}",
        f"Next Patch      : {payload.get('next_patch')}",
        "",
        "Source patches:",
    ]
    source_patches = payload.get("source_patches", {})
    if isinstance(source_patches, Mapping):
        for patch, state in source_patches.items():
            lines.append(f"- {patch}: {state}")
    lines.extend(["", "Checks:"])
    for check in payload.get("checks", []):
        state = "PASS" if check.get("ok") else "FAIL"
        lines.append(f"- {state}: {check.get('name')}")
    lines.extend(["", "Broad validation command plan (not executed by adapter logic):"])
    for command in payload.get("broad_validation_command_plan", []):
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_l5_browser_start_supervised_launch_handoff_broad_validation_checkpoint(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
