"""Passive L5.20 Microsoft Edge L5 documentation checkpoint.

This checkpoint reads back the accepted L5.19 Edge L5 aggregate CLI/readback
surface, verifies the Edge L5 docs/tests/source surfaces are present and still
state the passive safety boundary, and exposes a dedicated CLI command.
It does not import Selenium, start Edge, create a driver/session/profile, click
or download anything, paste/send text, run packages, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback as l5_19_readback

PATCH = "L5.20"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.20 Microsoft Edge Supervised Launch L5 Documentation Checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-l5-documentation-checkpoint"
SOURCE_COMMAND_NAME = l5_19_readback.COMMAND_NAME
NEXT_PATCH = "L5.21 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-l5-documentation-checkpoint-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*l5_19_readback.REQUIRED_COMMANDS, COMMAND_NAME)))

REQUIRED_REPO_PATHS: tuple[str, ...] = (
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_contract.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_readiness_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_documentation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_contract.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_documentation_checkpoint.md",
    "tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py",
    "tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py",
    "tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py",
    "tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py",
    "tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py",
    "tests/test_l5_17_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback_current.py",
    "tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py",
    "tests/test_l5_19_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback_current.py",
    "tests/test_l5_20_edge_supervised_launch_l5_documentation_checkpoint_current.py",
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_readiness_contract.md": (
        "Microsoft Edge",
        "manual user login",
        "dedicated profile",
        "silent auto-submit",
        "no localhost",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix.md": (
        "Microsoft Edge",
        "manual user login",
        "silent auto-submit",
        "no browser extension",
        "no localhost",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_fixture_matrix_contract_gate.md": (
        "Microsoft Edge",
        "fixture matrix",
        "contract gate",
        "passive",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate.md": (
        "Microsoft Edge",
        "L5.18",
        "L5.11",
        "L5.17",
        "no Selenium import",
        "no browser start",
        "no profile directory creation",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback.md": (
        "L5.19 Microsoft Edge supervised launch L5 aggregate readiness gate CLI/readback",
        "browser-start-supervised-launch-edge-l5-readiness-readback",
        "Microsoft Edge first",
        "Opera second",
        "no Selenium import",
        "no browser start",
        "no click/download/paste/send/package-run side effect",
        "L5.20 Live adapter Microsoft Edge supervised launch L5 documentation checkpoint",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_documentation_checkpoint.md": (
        "L5.20 Microsoft Edge supervised launch L5 documentation checkpoint",
        "browser-start-supervised-launch-edge-l5-documentation-checkpoint",
        "browser-start-supervised-launch-edge-l5-readiness-readback",
        "Microsoft Edge first",
        "Opera second",
        "dedicated profile required",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.21 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint",
    ),
}

PASSIVE_INVARIANTS: Mapping[str, Any] = {
    "startup_authorized": False,
    "startup_allowed": False,
    "browser_started": False,
    "edge_process_started": False,
    "browser_session_created": False,
    "driver_created": False,
    "profile_directory_created": False,
    "adapter_filesystem_writes_performed": [],
    "filesystem_writes_performed": [],
    "side_effects_performed": [],
    "click_download_performed": False,
    "download_performed": False,
    "paste_performed": False,
    "send_or_submit_performed": False,
    "package_run_performed_by_adapter": False,
    "git_commit_executed": False,
    "git_push_executed": False,
    "optional_browser_dependencies_required": False,
    "selenium_required": False,
    "selenium_imported_by_readback": False,
}


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()


def _missing_paths(root: Path, rel_paths: Iterable[str]) -> list[str]:
    return [rel for rel in rel_paths if not (root / rel).exists()]


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _json_safe(value: object) -> bool:
    try:
        json.dumps(value, sort_keys=True)
        return True
    except TypeError:
        return False


def _command_static_presence(root: Path, command_name: str, sentinel: str | None = None) -> dict[str, Any]:
    commands_path = root / "patchops" / "llm_browser" / "commands.py"
    if not commands_path.exists():
        return {"ok": False, "commands_path": str(commands_path), "reason": "commands.py missing", "command_name": command_name}
    text = commands_path.read_text(encoding="utf-8", errors="replace")
    payload: dict[str, Any] = {"ok": command_name in text, "commands_path": str(commands_path), "command_name": command_name}
    if sentinel is not None:
        payload["sentinel_present"] = sentinel in text
        payload["ok"] = bool(payload["ok"] and payload["sentinel_present"])
    return payload


def _required_command_state(root: Path) -> dict[str, Any]:
    command_states = {command: _command_static_presence(root, command) for command in REQUIRED_COMMANDS}
    missing_commands = [command for command, state in command_states.items() if state.get("ok") is not True]
    return {"ok": not missing_commands, "missing_commands": missing_commands, "command_states": command_states}


def _doc_phrase_state(root: Path) -> dict[str, Any]:
    state: dict[str, Any] = {}
    missing_docs: list[str] = []
    missing_phrases: dict[str, list[str]] = {}
    for rel, phrases in DOC_REQUIREMENTS.items():
        path = root / rel
        if not path.exists():
            missing_docs.append(rel)
            state[rel] = {"exists": False, "missing_phrases": list(phrases)}
            missing_phrases[rel] = list(phrases)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        missing = [phrase for phrase in phrases if phrase not in text]
        state[rel] = {"exists": True, "missing_phrases": missing}
        if missing:
            missing_phrases[rel] = missing
    return {"ok": not missing_docs and not missing_phrases, "missing_docs": missing_docs, "missing_phrases": missing_phrases, "doc_state": state}


def _l5_19_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    aggregate = payload.get("edge_l5_aggregate_readiness_summary", {})
    chain = aggregate.get("patch_status_chain", []) if isinstance(aggregate, Mapping) else []
    return {
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "source_command_name": payload.get("source_command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "aggregate_patch": aggregate.get("patch") if isinstance(aggregate, Mapping) else None,
        "aggregate_status": aggregate.get("status") if isinstance(aggregate, Mapping) else None,
        "chain_length": len(chain) if isinstance(chain, list) else 0,
        "chain": chain if isinstance(chain, list) else [],
        "startup_authorized": payload.get("startup_authorized") is True,
        "startup_allowed": payload.get("startup_allowed") is True,
        "browser_started": payload.get("browser_started") is True,
        "edge_process_started": payload.get("edge_process_started") is True,
        "browser_session_created": payload.get("browser_session_created") is True,
        "driver_created": payload.get("driver_created") is True,
        "profile_directory_created": payload.get("profile_directory_created") is True,
        "filesystem_writes_performed": payload.get("filesystem_writes_performed"),
        "adapter_filesystem_writes_performed": payload.get("adapter_filesystem_writes_performed"),
        "side_effects_performed": payload.get("side_effects_performed"),
        "selenium_imported_by_readback": payload.get("selenium_imported_by_readback") is True,
    }


def _l5_19_passive_ok(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.19"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("aggregate_patch") == "L5.18"
        and summary.get("aggregate_status") == STATUS_PASS
        and summary.get("chain_length") == 7
        and summary.get("edge_first") is True
        and summary.get("browser_priority") == list(BROWSER_PRIORITY)
        and summary.get("startup_authorized") is False
        and summary.get("startup_allowed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
    )


def build_edge_supervised_launch_l5_documentation_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_19_payload = l5_19_readback.build_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback(root)
    l5_19_summary = _l5_19_summary(l5_19_payload)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.19 START")
    checkpoint_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.20 START")
    command_state = _required_command_state(root)
    doc_state = _doc_phrase_state(root)
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)

    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    command_plan = [
        "python -m compileall patchops/llm_browser tests scripts/patch_l5_20_wire_edge_l5_documentation_checkpoint.py",
        "python -m pytest -q tests/test_l5_19_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback_current.py tests/test_l5_20_edge_supervised_launch_l5_documentation_checkpoint_current.py",
        "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_documentation_checkpoint --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-documentation-checkpoint --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]

    checks = [
        _check("l5_19_edge_l5_aggregate_cli_readback_still_passes", l5_19_summary.get("ok") is True and l5_19_summary.get("status") == STATUS_PASS, l5_19_summary),
        _check("l5_19_edge_l5_aggregate_cli_readback_remains_passive", _l5_19_passive_ok(l5_19_summary), l5_19_summary),
        _check("l5_19_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_20_documentation_checkpoint_command_registered", checkpoint_command_static.get("ok") is True, checkpoint_command_static),
        _check("edge_l5_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_safety_boundary", doc_state.get("ok") is True, doc_state),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("selenium_not_imported_by_readback", selenium_imported_by_readback is False, {"selenium_imported_by_readback": selenium_imported_by_readback}),
        _check("no_browser_or_adapter_side_effects", PASSIVE_INVARIANTS["browser_started"] is False and PASSIVE_INVARIANTS["side_effects_performed"] == [], dict(PASSIVE_INVARIANTS)),
    ]

    ok = all(check["ok"] for check in checks)
    payload: dict[str, Any] = {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "phase": PHASE,
        "patch": PATCH,
        "name": NAME,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "next_patch": NEXT_PATCH,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "repo_root": str(root),
        "required_commands": list(REQUIRED_COMMANDS),
        "required_repo_paths": list(REQUIRED_REPO_PATHS),
        "doc_requirements": {key: list(value) for key, value in DOC_REQUIREMENTS.items()},
        "l5_19_edge_l5_aggregate_readiness_gate_cli_readback": l5_19_payload,
        "l5_19_summary": l5_19_summary,
        "source_command_static_presence": source_command_static,
        "checkpoint_command_static_presence": checkpoint_command_static,
        "command_state": command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_repo_paths,
        "command_plan": command_plan,
        "checks": checks,
        "executed_validation_commands": [],
        **PASSIVE_INVARIANTS,
        "selenium_imported_by_readback": selenium_imported_by_readback,
    }
    payload["payload_json_safe"] = _json_safe(payload)
    if not payload["payload_json_safe"]:
        payload["ok"] = False
        payload["status"] = STATUS_FAIL
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "PatchOps L5.20 Microsoft Edge supervised-launch L5 documentation checkpoint",
        f"Patch           : {payload.get('patch')}",
        f"Status          : {payload.get('status')}",
        f"OK              : {payload.get('ok')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Edge First      : {payload.get('edge_first')}",
        f"Browser Priority: {payload.get('browser_priority')}",
        f"Startup Allowed : {payload.get('startup_allowed')}",
        f"Browser Started : {payload.get('browser_started')}",
        f"Edge Started    : {payload.get('edge_process_started')}",
        f"Session Created : {payload.get('browser_session_created')}",
        f"Driver Created  : {payload.get('driver_created')}",
        f"Profile Created : {payload.get('profile_directory_created')}",
        f"SideEffects     : {payload.get('side_effects_performed')}",
        f"Filesystem      : writes={payload.get('filesystem_writes_performed')}",
        f"Adapter Writes  : {payload.get('adapter_filesystem_writes_performed')}",
        f"Selenium Import : {payload.get('selenium_imported_by_readback')}",
        f"MissingPath     : {payload.get('missing_repo_paths')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    lines.append(f"Next Patch      : {payload.get('next_patch')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    payload = build_edge_supervised_launch_l5_documentation_checkpoint(args.repo_root)
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