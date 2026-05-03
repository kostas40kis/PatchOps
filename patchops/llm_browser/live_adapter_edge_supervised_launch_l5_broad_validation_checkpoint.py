"""Passive L5.21 Microsoft Edge L5 broad validation checkpoint.

This checkpoint reads back the accepted L5.20 documentation checkpoint, verifies
that the Edge L5 command/source/doc/test surfaces are still present, and exposes
a planned broad-validation command list without executing those commands from
adapter logic.

It remains fully passive: no Selenium import, no Edge process start, no browser
session, no driver, no profile directory creation, no click/download, no
paste/send, no package run, and no automatic git operation.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import live_adapter_edge_supervised_launch_l5_documentation_checkpoint as l5_20_checkpoint

PATCH = "L5.21"
PHASE = "L5"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L5.21 Microsoft Edge Supervised Launch L5 Broad Validation Checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-l5-broad-validation"
SOURCE_COMMAND_NAME = l5_20_checkpoint.COMMAND_NAME
NEXT_PATCH = "L5.22 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-supervised-launch-l5-broad-validation-checkpoint-only"
BROWSER_PRIORITY = ("edge", "opera")

REQUIRED_COMMANDS: tuple[str, ...] = tuple(dict.fromkeys((*l5_20_checkpoint.REQUIRED_COMMANDS, COMMAND_NAME)))

REQUIRED_REPO_PATHS: tuple[str, ...] = tuple(
    dict.fromkeys(
        (
            *l5_20_checkpoint.REQUIRED_REPO_PATHS,
            "patchops/llm_browser/live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint.py",
            "docs/llm_browser_live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint.md",
            "tests/test_l5_21_edge_supervised_launch_l5_broad_validation_checkpoint_current.py",
        )
    )
)

DOC_REQUIREMENTS: Mapping[str, tuple[str, ...]] = {
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_documentation_checkpoint.md": (
        "L5.20 Microsoft Edge supervised launch L5 documentation checkpoint",
        "browser-start-supervised-launch-edge-l5-documentation-checkpoint",
        "Microsoft Edge first",
        "Opera second",
        "dedicated profile required",
        "manual user login required",
        "silent auto-submit remains false",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L5.21 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint",
    ),
    "docs/llm_browser_live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint.md": (
        "L5.21 Microsoft Edge supervised launch L5 broad validation checkpoint",
        "browser-start-supervised-launch-edge-l5-broad-validation",
        "browser-start-supervised-launch-edge-l5-documentation-checkpoint",
        "Microsoft Edge first",
        "Opera second",
        "dedicated profile required",
        "manual user login required",
        "silent auto-submit remains false",
        "planned broad-validation command list",
        "adapter logic executes no validation commands",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no browser session creation",
        "no driver creation",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "no localhost PatchOps server",
        "no browser extension",
        "L5.22 Live adapter Microsoft Edge supervised launch L5 broad validation checkpoint CLI/readback",
    ),
}

BROAD_VALIDATION_COMMAND_PLAN: tuple[str, ...] = (
    "python -m compileall patchops/llm_browser tests",
    "python -m pytest -q tests/test_l5_12_edge_supervised_launch_readiness_contract_current.py tests/test_l5_13_edge_supervised_launch_readiness_cli_readback_current.py tests/test_l5_14_edge_supervised_launch_fixture_matrix_current.py tests/test_l5_15_edge_supervised_launch_fixture_matrix_cli_readback_current.py tests/test_l5_16_edge_supervised_launch_fixture_matrix_contract_gate_current.py tests/test_l5_17_edge_supervised_launch_fixture_matrix_contract_gate_cli_readback_current.py tests/test_l5_18_edge_supervised_launch_l5_aggregate_readiness_gate_current.py tests/test_l5_19_edge_supervised_launch_l5_aggregate_readiness_gate_cli_readback_current.py tests/test_l5_20_edge_supervised_launch_l5_documentation_checkpoint_current.py tests/test_l5_21_edge_supervised_launch_l5_broad_validation_checkpoint_current.py",
    "python -m patchops.llm_browser.live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint --repo-root C:\\dev\\patchops --json --compact",
    "py -m patchops.cli llm-browser browser-start-supervised-launch-edge-l5-broad-validation --repo-root C:\\dev\\patchops --json --compact",
    "git status --short --branch",
)

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

FORBIDDEN_PLAN_TOKENS: tuple[str, ...] = (
    "msedge.exe",
    "selenium",
    "webdriver",
    "click-download",
    "paste-to-composer",
    "send-message",
    "run-package-from-adapter",
)


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


def _l5_20_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    l5_19_summary = payload.get("l5_19_summary", {})
    return {
        "ok": payload.get("ok") is True,
        "status": payload.get("status"),
        "patch": payload.get("patch"),
        "command_name": payload.get("command_name"),
        "source_command_name": payload.get("source_command_name"),
        "next_patch": payload.get("next_patch"),
        "edge_first": payload.get("edge_first") is True,
        "browser_priority": payload.get("browser_priority"),
        "l5_19_patch": l5_19_summary.get("patch") if isinstance(l5_19_summary, Mapping) else None,
        "l5_19_status": l5_19_summary.get("status") if isinstance(l5_19_summary, Mapping) else None,
        "l5_19_chain_length": l5_19_summary.get("chain_length") if isinstance(l5_19_summary, Mapping) else None,
        "doc_state_ok": payload.get("doc_state", {}).get("ok") if isinstance(payload.get("doc_state"), Mapping) else None,
        "missing_repo_paths": payload.get("missing_repo_paths", []),
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


def _l5_20_passive_ok(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("patch") == "L5.20"
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l5_19_patch") == "L5.19"
        and summary.get("l5_19_status") == STATUS_PASS
        and summary.get("l5_19_chain_length") == 7
        and summary.get("doc_state_ok") is True
        and summary.get("missing_repo_paths") == []
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


def _command_plan_state() -> dict[str, Any]:
    plan = list(BROAD_VALIDATION_COMMAND_PLAN)
    joined = "\n".join(plan).lower()
    forbidden_present = [token for token in FORBIDDEN_PLAN_TOKENS if token.lower() in joined]
    expected_fragments = [
        "compileall patchops/llm_browser tests",
        "pytest -q",
        "test_l5_12_edge_supervised_launch_readiness_contract_current.py",
        "test_l5_21_edge_supervised_launch_l5_broad_validation_checkpoint_current.py",
        "live_adapter_edge_supervised_launch_l5_broad_validation_checkpoint",
        COMMAND_NAME,
        "git status --short --branch",
    ]
    missing_fragments = [fragment for fragment in expected_fragments if fragment not in joined]
    return {
        "ok": not forbidden_present and not missing_fragments and len(plan) == 5,
        "planned_commands": plan,
        "forbidden_present": forbidden_present,
        "missing_fragments": missing_fragments,
        "executed_by_adapter_logic": [],
    }


def build_edge_supervised_launch_l5_broad_validation_checkpoint(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before_modules = set(sys.modules)

    l5_20_payload = l5_20_checkpoint.build_edge_supervised_launch_l5_documentation_checkpoint(root)
    l5_20_summary = _l5_20_summary(l5_20_payload)
    source_command_static = _command_static_presence(root, SOURCE_COMMAND_NAME, "PATCHOPS L5.20 START")
    broad_command_static = _command_static_presence(root, COMMAND_NAME, "PATCHOPS L5.21 START")
    command_state = _required_command_state(root)
    doc_state = _doc_phrase_state(root)
    command_plan_state = _command_plan_state()
    missing_repo_paths = _missing_paths(root, REQUIRED_REPO_PATHS)

    after_modules = set(sys.modules)
    selenium_imported_by_readback = any(name == "selenium" or name.startswith("selenium.") for name in (after_modules - before_modules))

    checks = [
        _check("l5_20_edge_l5_documentation_checkpoint_still_passes", l5_20_summary.get("ok") is True and l5_20_summary.get("status") == STATUS_PASS, l5_20_summary),
        _check("l5_20_edge_l5_documentation_checkpoint_remains_passive", _l5_20_passive_ok(l5_20_summary), l5_20_summary),
        _check("l5_20_source_command_still_registered", source_command_static.get("ok") is True, source_command_static),
        _check("l5_21_broad_validation_command_registered", broad_command_static.get("ok") is True, broad_command_static),
        _check("edge_l5_required_command_set_registered", command_state.get("ok") is True, command_state),
        _check("edge_l5_required_source_docs_tests_present", not missing_repo_paths, {"missing": missing_repo_paths}),
        _check("edge_l5_docs_contain_safety_boundary", doc_state.get("ok") is True, doc_state),
        _check("broad_validation_command_plan_is_readback_only", command_plan_state.get("ok") is True, command_plan_state),
        _check("adapter_logic_executes_no_validation_commands", command_plan_state.get("executed_by_adapter_logic") == [], command_plan_state),
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
        "l5_20_edge_l5_documentation_checkpoint": l5_20_payload,
        "l5_20_summary": l5_20_summary,
        "source_command_static_presence": source_command_static,
        "broad_command_static_presence": broad_command_static,
        "command_state": command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_repo_paths,
        "broad_validation_command_plan": list(BROAD_VALIDATION_COMMAND_PLAN),
        "command_plan_state": command_plan_state,
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
        "PatchOps L5.21 Microsoft Edge supervised-launch L5 broad validation checkpoint",
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
        "Planned broad-validation commands:",
    ]
    for command in payload.get("broad_validation_command_plan", []):
        lines.append(f"- {command}")
    lines.append("Checks:")
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

    payload = build_edge_supervised_launch_l5_broad_validation_checkpoint(args.repo_root)
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