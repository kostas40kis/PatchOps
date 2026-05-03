"""Passive L4 browser-start dry-run handoff broad validation checkpoint.

This module aggregates the accepted L4 dry-run handoff stack and verifies that
the earlier L1/L2/L3 passive live-adapter surfaces are still present. It is
readback-only: it does not import Selenium or optional browser dependencies,
start a browser, create a browser session, create profile directories, perform
adapter filesystem writes, click/download/paste/send, run downloaded packages,
or commit/push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PATCH = "L4.10"
PHASE = "L4"
NAME = "L4.10 Browser Start Dry-Run Handoff Broad Validation Checkpoint"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NEXT_PATCH = "L4.11 Live adapter browser-start dry-run handoff L4 broad validation checkpoint CLI/readback"
SIDE_EFFECT_BOUNDARY = "passive-l4-broad-validation-readback-only"

FORBIDDEN_OPTIONAL_ROOTS: tuple[str, ...] = (
    "selenium",
    "webdriver_manager",
    "pyperclip",
    "psutil",
    "playwright",
    "pyppeteer",
)

REQUIRED_L1_L2_L3_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_startup_request_l1_final_acceptance_marker.py",
    "docs/llm_browser_live_adapter_startup_request_l1_final_acceptance_marker.md",
    "tests/test_llm_browser_live_adapter_startup_request_l1_final_acceptance_marker_current.py",
    "patchops/llm_browser/live_adapter_browser_profile_l2_final_acceptance_marker.py",
    "docs/llm_browser_live_adapter_browser_profile_l2_final_acceptance_marker.md",
    "tests/test_l2_12_final_acceptance_marker_current.py",
    "patchops/llm_browser/live_adapter_browser_start_authorization_l3_final_acceptance_marker.py",
    "docs/llm_browser_live_adapter_browser_start_authorization_l3_final_acceptance_marker.md",
    "tests/test_l3_12_browser_start_authorization_l3_final_acceptance_marker_current.py",
)

REQUIRED_L4_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_contract.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_fixtures.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_l4_documentation_checkpoint.py",
    "patchops/llm_browser/live_adapter_browser_start_dry_run_handoff_l4_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_documentation_freeze_readiness_checkpoint.md",
    "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_broad_validation_checkpoint.md",
    "tests/test_l4_01_browser_start_dry_run_handoff_contract_current.py",
    "tests/test_l4_02_browser_start_dry_run_handoff_cli_readback_current.py",
    "tests/test_l4_03_browser_start_dry_run_handoff_fixture_matrix_current.py",
    "tests/test_l4_04_browser_start_dry_run_handoff_fixture_matrix_cli_readback_current.py",
    "tests/test_l4_05_browser_start_dry_run_handoff_fixture_matrix_contract_gate_current.py",
    "tests/test_l4_06_browser_start_dry_run_handoff_contract_gate_cli_readback_current.py",
    "tests/test_l4_07_browser_start_dry_run_handoff_l4_aggregate_readiness_gate_current.py",
    "tests/test_l4_08_browser_start_dry_run_handoff_l4_readiness_cli_readback_current.py",
    "tests/test_l4_09_browser_start_dry_run_handoff_l4_documentation_checkpoint_current.py",
    "tests/test_l4_10_browser_start_dry_run_handoff_l4_broad_validation_checkpoint_current.py",
)

REQUIRED_CLI_COMMANDS: tuple[str, ...] = (
    "browser-start-dry-run-handoff",
    "browser-start-dry-run-handoff-fixtures",
    "browser-start-dry-run-handoff-contract-gate",
    "browser-start-dry-run-handoff-l4-readiness",
)

COMMAND_PLAN: tuple[str, ...] = (
    "py -m compileall patchops/llm_browser tests",
    "py -m pytest -q tests/test_l4_01_browser_start_dry_run_handoff_contract_current.py tests/test_l4_02_browser_start_dry_run_handoff_cli_readback_current.py tests/test_l4_03_browser_start_dry_run_handoff_fixture_matrix_current.py tests/test_l4_04_browser_start_dry_run_handoff_fixture_matrix_cli_readback_current.py tests/test_l4_05_browser_start_dry_run_handoff_fixture_matrix_contract_gate_current.py tests/test_l4_06_browser_start_dry_run_handoff_contract_gate_cli_readback_current.py tests/test_l4_07_browser_start_dry_run_handoff_l4_aggregate_readiness_gate_current.py tests/test_l4_08_browser_start_dry_run_handoff_l4_readiness_cli_readback_current.py tests/test_l4_09_browser_start_dry_run_handoff_l4_documentation_checkpoint_current.py tests/test_l4_10_browser_start_dry_run_handoff_l4_broad_validation_checkpoint_current.py",
    "py -m patchops.llm_browser.live_adapter_browser_start_dry_run_handoff_l4_broad_validation_checkpoint --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)

FORBIDDEN_COMMAND_FRAGMENTS: tuple[str, ...] = (
    "git commit",
    "git push",
    "run-package",
    "open --browser",
    "run-once",
    "watch-downloads",
    "selenium",
    "webdriver",
    "start_browser",
    "click_download",
    "paste_to_composer",
    "send_or_submit",
)

LIVE_SIDE_EFFECT_OPERATIONS: tuple[str, ...] = (
    "import_selenium",
    "start_browser",
    "create_browser_session",
    "create_profile_directory",
    "adapter_filesystem_write",
    "read_provider_page",
    "click_download",
    "paste_to_composer",
    "send_message",
    "run_downloaded_package",
    "commit",
    "push",
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
    "L4.1 dry-run handoff contract",
    "L4.8 aggregate readiness gate CLI/readback",
    "L4.9 documentation freeze/readiness checkpoint",
    NEXT_PATCH,
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        return Path.cwd().resolve()
    candidate = Path(repo_root)
    if str(candidate) == ".":
        return Path.cwd().resolve()
    return candidate.resolve()


def _check(name: str, ok: bool, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "details": dict(details or {})}


def _missing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    return sorted(path for path in paths if not (root / path).exists())


def _read_text(root: Path, rel_path: str) -> str:
    try:
        path = root / rel_path
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8")
    except OSError:
        return ""
    return ""


def _missing_phrases(text: str, phrases: Sequence[str]) -> list[str]:
    return [phrase for phrase in phrases if phrase not in text]


def _json_safe(value: Any) -> bool:
    try:
        json.dumps(value, sort_keys=True)
    except TypeError:
        return False
    return True


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


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


def _command_plan_is_passive(commands: Sequence[str]) -> tuple[bool, list[str]]:
    lowered = "\n".join(commands).lower()
    found = [fragment for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment in lowered]
    return found == [], found


def _payload_is_passive(payload: Mapping[str, Any]) -> bool:
    return bool(
        payload.get("startup_authorized", payload.get("startup_allowed", False)) is False
        and payload.get("startup_allowed", False) is False
        and payload.get("browser_started") is False
        and payload.get("browser_session_created") is False
        and payload.get("driver_created", False) is False
        and payload.get("profile_directory_created", False) is False
        and _as_list(payload.get("filesystem_writes_performed")) == []
        and _as_list(payload.get("side_effects_performed")) == []
        and payload.get("optional_browser_dependencies_required") in (False, None)
    )


def _safe_payload(name: str, func: Any, root: Path) -> tuple[Mapping[str, Any], str | None]:
    try:
        return _as_mapping(func(root)), None
    except Exception as exc:  # pragma: no cover - operator diagnostic fallback
        return {}, f"{name}: {exc.__class__.__name__}: {exc}"


def build_l4_browser_start_dry_run_handoff_broad_validation_checkpoint(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Build a passive L4 broad-validation readback payload."""
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    from patchops.llm_browser import commands
    from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate as aggregate_gate
    from patchops.llm_browser import live_adapter_browser_start_dry_run_handoff_l4_documentation_checkpoint as documentation_checkpoint

    aggregate_payload, aggregate_error = _safe_payload(
        "l4_aggregate_readiness_gate",
        aggregate_gate.build_l4_browser_start_dry_run_handoff_aggregate_readiness_gate,
        root,
    )
    documentation_payload, documentation_error = _safe_payload(
        "l4_documentation_checkpoint",
        documentation_checkpoint.build_l4_browser_start_dry_run_handoff_documentation_checkpoint,
        root,
    )

    command_names = set(commands.llm_browser_command_names())
    missing_commands = sorted(command for command in REQUIRED_CLI_COMMANDS if command not in command_names)
    missing_previous_paths = _missing_paths(root, REQUIRED_L1_L2_L3_PATHS)
    missing_l4_paths = _missing_paths(root, REQUIRED_L4_PATHS)

    docs_text = "\n".join(
        _read_text(root, path)
        for path in (
            "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_aggregate_readiness_gate.md",
            "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_readiness_cli_readback.md",
            "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_documentation_freeze_readiness_checkpoint.md",
            "docs/llm_browser_live_adapter_browser_start_dry_run_handoff_l4_broad_validation_checkpoint.md",
        )
    )
    missing_safety_phrases = _missing_phrases(docs_text, SAFETY_PHRASES)
    missing_progression_phrases = _missing_phrases(docs_text, PROGRESSION_PHRASES)
    passive_plan_ok, forbidden_command_fragments = _command_plan_is_passive(COMMAND_PLAN)
    optional_imports_before_or_during = _forbidden_imports_present()
    optional_imports_loaded = _forbidden_imports_loaded_since(before_modules)

    checks = [
        _check("l1_l2_l3_final_surfaces_present", not missing_previous_paths, {"missing": missing_previous_paths}),
        _check("l4_surfaces_present", not missing_l4_paths, {"missing": missing_l4_paths}),
        _check("l4_cli_commands_present", not missing_commands, {"missing": missing_commands}),
        _check("aggregate_gate_passive_pass", bool(aggregate_payload.get("ok") is True and aggregate_payload.get("status") == STATUS_PASS), {"error": aggregate_error}),
        _check("aggregate_gate_has_no_live_side_effects", _payload_is_passive(aggregate_payload)),
        _check("documentation_checkpoint_passive_pass", bool(documentation_payload.get("ok") is True and documentation_payload.get("status") == STATUS_PASS), {"error": documentation_error}),
        _check("documentation_checkpoint_has_no_live_side_effects", _payload_is_passive(documentation_payload)),
        _check("command_plan_is_readback_only", passive_plan_ok, {"forbidden_fragments": forbidden_command_fragments, "commands": list(COMMAND_PLAN)}),
        _check("documentation_contains_safety_phrases", not missing_safety_phrases, {"missing": missing_safety_phrases}),
        _check("documentation_contains_progression_phrases", not missing_progression_phrases, {"missing": missing_progression_phrases}),
        _check("no_optional_browser_dependency_imported", not optional_imports_before_or_during and not optional_imports_loaded, {"present": optional_imports_before_or_during, "loaded": optional_imports_loaded}),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "ok": ok,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "startup_authorized": False,
        "startup_allowed": False,
        "browser_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "side_effects_performed": [],
        "optional_browser_dependencies_required": False,
        "selenium_imported": False,
        "adapter_filesystem_writes": False,
        "live_side_effect_operations_blocked": list(LIVE_SIDE_EFFECT_OPERATIONS),
        "command_plan": list(COMMAND_PLAN),
        "missing_previous_paths": missing_previous_paths,
        "missing_l4_paths": missing_l4_paths,
        "missing_commands": missing_commands,
        "missing_safety_phrases": missing_safety_phrases,
        "missing_progression_phrases": missing_progression_phrases,
        "forbidden_command_fragments": forbidden_command_fragments,
        "optional_imports_present": optional_imports_before_or_during,
        "optional_imports_loaded": optional_imports_loaded,
        "aggregate_gate": dict(aggregate_payload),
        "documentation_checkpoint": dict(documentation_payload),
        "checks": checks,
    }
    payload["json_safe"] = _json_safe(payload)
    if not payload["json_safe"]:
        payload["ok"] = False
        payload["status"] = STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            NAME,
            "=" * len(NAME),
            f"Status     : {payload.get('status')}",
            f"Patch      : {payload.get('patch')}",
            f"Phase      : {payload.get('phase')}",
            f"Startup    : authorized={payload.get('startup_authorized')} allowed={payload.get('startup_allowed')}",
            f"Browser    : started={payload.get('browser_started')}",
            f"Session    : created={payload.get('browser_session_created')}",
            f"Driver     : created={payload.get('driver_created')}",
            f"ProfileDir : created={payload.get('profile_directory_created')}",
            f"SideEffects: {payload.get('side_effects_performed')}",
            f"Filesystem : writes={payload.get('filesystem_writes_performed')}",
            f"Missing previous paths : {payload.get('missing_previous_paths')}",
            f"Missing L4 paths       : {payload.get('missing_l4_paths')}",
            f"Missing commands       : {payload.get('missing_commands')}",
            f"Command plan           : {payload.get('command_plan')}",
            f"Next patch : {payload.get('next_patch')}",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".", help="Repository root to validate.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON when --json is used.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    payload = build_l4_browser_start_dry_run_handoff_broad_validation_checkpoint(args.repo_root)
    if args.json:
        if args.compact:
            print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload))
    return 0 if payload.get("ok") is True else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
