"""Passive L5 supervised-launch handoff aggregate readiness gate.

This module aggregates the accepted L5.1 through L5.6 supervised-launch handoff
surfaces. It is intentionally model/readback-only: it imports no Selenium,
starts no browser, creates no driver/session/profile directory, writes no
adapter files, and performs no click/download/paste/send/package-run operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PATCH = "L5.7"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.7 Browser Start Supervised Launch Handoff L5 Aggregate Readiness Gate"
NEXT_PATCH = "L5.8 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "supervised-launch-handoff-l5-aggregate-readiness-gate-only"

REQUIRED_COMMANDS: tuple[str, ...] = (
    "browser-start-supervised-launch-handoff",
    "browser-start-supervised-launch-handoff-fixtures",
    "browser-start-supervised-launch-handoff-contract-gate",
)

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_contract.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_contract.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_cli_readback.md",
    "tests/test_l5_01_browser_start_supervised_launch_handoff_contract_current.py",
    "tests/test_l5_02_browser_start_supervised_launch_handoff_cli_readback_current.py",
    "tests/test_l5_03_browser_start_supervised_launch_handoff_fixture_matrix_current.py",
    "tests/test_l5_04_browser_start_supervised_launch_handoff_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_05_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate_current.py",
    "tests/test_l5_06_browser_start_supervised_launch_handoff_contract_gate_cli_readback_current.py",
)

REQUIRED_L5_07_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate.py",
    "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate.md",
    "tests/test_l5_07_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate_current.py",
)

DOC_REQUIRED_PHRASES: tuple[str, ...] = (
    "L5.7 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate",
    "L5.1",
    "L5.2",
    "L5.3",
    "L5.4",
    "L5.5",
    "L5.6",
    "no Selenium import",
    "no browser start",
    "no browser session creation",
    "no driver creation",
    "no profile directory creation",
    "no adapter filesystem writes",
    "no click/download/paste/send/package-run side effect",
    "L5.8 Live adapter browser-start supervised launch handoff L5 aggregate readiness gate CLI/readback",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
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
)

FORBIDDEN_OPTIONAL_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "playwright",
    "pyppeteer",
)

READBACK_COMMANDS: tuple[str, ...] = (
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_contract --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-handoff --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixtures --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-fixtures --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.llm_browser.live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-handoff-contract-gate --repo-root C:\\dev\\patchops --json --compact",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    return Path(repo_root).resolve()


def _missing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    return [rel for rel in paths if not (root / rel).exists()]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _json_safe(value: object) -> bool:
    try:
        json.dumps(value, sort_keys=True)
        return True
    except TypeError:
        return False


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": dict(detail or {})}


def _command_plan_is_readback_only(commands: Sequence[str]) -> bool:
    lowered = "\n".join(commands).lower()
    return not any(fragment.lower() in lowered for fragment in FORBIDDEN_COMMAND_FRAGMENTS)


def _forbidden_optional_imports_newly_loaded(before: set[str]) -> list[str]:
    after = set(sys.modules)
    loaded = sorted(root for root in FORBIDDEN_OPTIONAL_ROOTS if root in after and root not in before)
    return loaded


def _llm_browser_command_names() -> tuple[str, ...]:
    try:
        from patchops.llm_browser import commands
    except Exception:
        return ()
    try:
        return tuple(commands.llm_browser_command_names())
    except Exception:
        return ()


def build_l5_aggregate_readiness_gate(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Build the passive L5 aggregate readiness gate payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_contract as contract
    from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_fixtures as fixtures
    from patchops.llm_browser import live_adapter_browser_start_supervised_launch_handoff_fixture_matrix_contract_gate as gate

    l5_01 = contract.build_l5_browser_start_supervised_launch_handoff_contract(
        root,
        browser="edge",
        operator_decision="review_only",
    )
    l5_03 = fixtures.build_supervised_launch_handoff_fixture_matrix(root)
    l5_05 = gate.build_contract_gate(root)

    command_names = _llm_browser_command_names()
    missing_commands = [name for name in REQUIRED_COMMANDS if name not in command_names]
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    missing_l5_07_paths = _missing_paths(root, REQUIRED_L5_07_PATHS)

    doc_text = _read_text(root / "docs/llm_browser_live_adapter_browser_start_supervised_launch_handoff_l5_aggregate_readiness_gate.md")
    missing_doc_phrases = [phrase for phrase in DOC_REQUIRED_PHRASES if phrase not in doc_text]

    newly_loaded_forbidden = _forbidden_optional_imports_newly_loaded(before_modules)

    passive_invariants = {
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
        "selenium_imported": "selenium" in newly_loaded_forbidden,
        "git_commit_executed": False,
        "git_push_executed": False,
    }

    checks: list[dict[str, Any]] = [
        _check("l5_01_supervised_launch_handoff_contract_still_passes", l5_01.get("ok") is True and l5_01.get("status") == STATUS_PASS, {"patch": l5_01.get("patch"), "status": l5_01.get("status")}),
        _check("l5_02_supervised_launch_handoff_cli_command_registered", "browser-start-supervised-launch-handoff" in command_names),
        _check("l5_03_supervised_launch_handoff_fixture_matrix_still_passes", l5_03.get("ok") is True and l5_03.get("status") == STATUS_PASS, {"patch": l5_03.get("patch"), "status": l5_03.get("status"), "case_count": l5_03.get("case_count")}),
        _check("l5_04_supervised_launch_handoff_fixture_matrix_cli_command_registered", "browser-start-supervised-launch-handoff-fixtures" in command_names),
        _check("l5_05_supervised_launch_handoff_contract_gate_still_passes", l5_05.get("ok") is True and l5_05.get("status") == STATUS_PASS, {"patch": l5_05.get("patch"), "status": l5_05.get("status")}),
        _check("l5_06_supervised_launch_handoff_contract_gate_cli_command_registered", "browser-start-supervised-launch-handoff-contract-gate" in command_names),
        _check("l5_aggregate_required_command_set_registered", not missing_commands, {"missing_commands": missing_commands}),
        _check("l5_aggregate_required_repo_paths_present", not missing_repo_paths, {"missing_repo_paths": missing_repo_paths}),
        _check("l5_aggregate_l5_07_artifacts_present", not missing_l5_07_paths, {"missing_l5_07_paths": missing_l5_07_paths}),
        _check("l5_aggregate_doc_contains_boundary_and_next_patch", not missing_doc_phrases, {"missing_doc_phrases": missing_doc_phrases}),
        _check("l5_aggregate_readback_command_plan_is_passive", _command_plan_is_readback_only(READBACK_COMMANDS)),
        _check("l5_aggregate_did_not_load_optional_browser_dependencies", not newly_loaded_forbidden, {"newly_loaded": newly_loaded_forbidden}),
        _check("l5_aggregate_keeps_startup_blocked", l5_01.get("startup_allowed") is False and l5_03.get("startup_allowed") is False and l5_05.get("startup_allowed") is False),
        _check("l5_aggregate_creates_no_browser_session_or_driver", l5_01.get("browser_started") is False and l5_03.get("browser_started") is False and l5_05.get("browser_started") is False and l5_05.get("driver_created") is False),
        _check("l5_aggregate_creates_no_profile_directory_or_adapter_writes", l5_01.get("profile_directory_created") is False and l5_03.get("profile_directory_created") is False and l5_05.get("profile_directory_created") is False and l5_05.get("filesystem_writes_performed") == []),
        _check("l5_aggregate_executes_no_side_effects", l5_01.get("side_effects_performed") == [] and l5_03.get("side_effects_performed") == [] and l5_05.get("side_effects_performed") == []),
    ]

    payload: dict[str, Any] = {
        "name": NAME,
        "phase": PHASE,
        "patch": PATCH,
        "status": STATUS_PASS,
        "ok": True,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "source_patches": {
            "L5.1": {"status": l5_01.get("status"), "ok": l5_01.get("ok")},
            "L5.2": {"cli_command": "browser-start-supervised-launch-handoff", "registered": "browser-start-supervised-launch-handoff" in command_names},
            "L5.3": {"status": l5_03.get("status"), "ok": l5_03.get("ok"), "case_count": l5_03.get("case_count")},
            "L5.4": {"cli_command": "browser-start-supervised-launch-handoff-fixtures", "registered": "browser-start-supervised-launch-handoff-fixtures" in command_names},
            "L5.5": {"status": l5_05.get("status"), "ok": l5_05.get("ok")},
            "L5.6": {"cli_command": "browser-start-supervised-launch-handoff-contract-gate", "registered": "browser-start-supervised-launch-handoff-contract-gate" in command_names},
        },
        "required_commands": list(REQUIRED_COMMANDS),
        "missing_commands": missing_commands,
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "missing_repo_paths": missing_repo_paths,
        "required_l5_07_paths": list(REQUIRED_L5_07_PATHS),
        "missing_l5_07_paths": missing_l5_07_paths,
        "missing_doc_phrases": missing_doc_phrases,
        "llm_browser_command_names_checked": command_names,
        "readback_commands": list(READBACK_COMMANDS),
        "executed_validation_commands": [],
        "modelled_only": True,
        **passive_invariants,
        "forbidden_optional_imports_newly_loaded": newly_loaded_forbidden,
        "checks": checks,
    }
    checks.append(_check("l5_aggregate_payload_json_safe", _json_safe(payload)))
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
        f"Selenium Import : {payload.get('selenium_imported')}",
        f"Missing Commands: {payload.get('missing_commands')}",
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
    lines.extend(["", "Readback command plan:"])
    for command in payload.get("readback_commands", []):
        lines.append(f"- {command}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_l5_aggregate_readiness_gate(args.repo_root)
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
