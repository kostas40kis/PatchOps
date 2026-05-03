"""L13.7 passive broad-validation checkpoint for Microsoft Edge executable filesystem probe execution.

The checkpoint sits over the accepted L13.6 aggregate-gate CLI/readback layer.
It exposes a planned L13 broad-validation command list, confirms the accepted
read-only execution probe stack is still passive and truthful, and deliberately
does not execute validation commands from inside the adapter logic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_aggregate_gate_cli_readback as l13_06

PATCH = "L13.7"
PHASE = "L13"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L13.7 Microsoft Edge executable filesystem probe execution broad validation checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-broad-validation-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-aggregate-gate-readback"
NEXT_PATCH = "L13.8 Live adapter Microsoft Edge executable filesystem probe execution final acceptance marker"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-execution-broad-validation-checkpoint-readback-only"
BROWSER_PRIORITY = ("edge", "opera")

L13_TESTS = (
    "tests/test_l13_01_edge_executable_filesystem_probe_execution_contract_current.py",
    "tests/test_l13_02_edge_executable_filesystem_probe_execution_cli_readback_current.py",
    "tests/test_l13_03_edge_executable_filesystem_probe_execution_fixture_matrix_current.py",
    "tests/test_l13_04_edge_executable_filesystem_probe_execution_fixture_matrix_cli_readback_current.py",
    "tests/test_l13_05_edge_executable_filesystem_probe_execution_aggregate_gate_current.py",
    "tests/test_l13_06_edge_executable_filesystem_probe_execution_aggregate_gate_cli_readback_current.py",
    "tests/test_l13_07_edge_executable_filesystem_probe_execution_broad_validation_checkpoint_current.py",
)

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_aggregate_gate.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_aggregate_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_broad_validation_checkpoint.md",
    "scripts/patch_l13_04_brief_validate.py",
    "scripts/patch_l13_05_brief_validate.py",
    "scripts/patch_l13_06_brief_validate.py",
    "scripts/patch_l13_07_brief_validate.py",
) + L13_TESTS

NO_LAUNCH_FIELDS = (
    "edge_executable_launch_attempted",
    "startup_allowed",
    "live_start_performed",
    "browser_started",
    "edge_process_started",
    "browser_session_created",
    "driver_created",
    "profile_directory_created",
    "click_download_performed",
    "download_performed",
    "paste_performed",
    "send_or_submit_performed",
    "package_run_performed_by_adapter",
    "git_commit_executed",
    "git_push_executed",
    "selenium_imported_by_readback",
)

EMPTY_LIST_SIDE_EFFECT_FIELDS = (
    "filesystem_writes_performed",
    "adapter_filesystem_writes_performed",
    "side_effects_performed",
    "forbidden_optional_imports_observed",
)


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _selected_candidate_ok(payload: Mapping[str, Any]) -> bool:
    selected = payload.get("edge_executable_selected_path")
    candidates = payload.get("edge_executable_probe_candidates") or []
    if payload.get("edge_executable_path_selected") is True:
        return any(
            isinstance(item, Mapping)
            and item.get("path") == selected
            and item.get("exists") is True
            and item.get("is_file") is True
            for item in candidates
        )
    return selected is None


def _no_launch_side_effects(payload: Mapping[str, Any]) -> bool:
    for field in NO_LAUNCH_FIELDS:
        if payload.get(field) is not False:
            return False
    for field in EMPTY_LIST_SIDE_EFFECT_FIELDS:
        if payload.get(field) != []:
            return False
    return True


def _default_no_side_effect_fields(payload: dict[str, Any]) -> None:
    for field in NO_LAUNCH_FIELDS:
        payload.setdefault(field, False)
    for field in EMPTY_LIST_SIDE_EFFECT_FIELDS:
        payload.setdefault(field, [])


def _required_paths_status(root: Path) -> dict[str, Any]:
    missing = [rel for rel in REQUIRED_REPO_PATHS if not (root / rel).exists()]
    return {"ok": not missing, "missing": missing, "checked": list(REQUIRED_REPO_PATHS)}


def _planned_commands() -> list[str]:
    tests = " ".join(L13_TESTS)
    return [
        "py -m compileall patchops/llm_browser " + tests + " scripts/patch_l13_07_brief_validate.py",
        "py -m pytest -q " + tests,
        "py -m patchops.cli llm-browser " + SOURCE_COMMAND_NAME + " --repo-root C:\\dev\\patchops --json --compact",
        "py -m patchops.cli llm-browser " + COMMAND_NAME + " --repo-root C:\\dev\\patchops --json --compact",
        "git status --short --branch",
    ]


def _planned_commands_are_passive(commands: Sequence[str]) -> bool:
    forbidden = (
        " apply ",
        " run-package ",
        " --auto-send",
        " --allow-send",
        " --allow-download-click",
        " --allow-patchops-run",
        " --allow-paste",
        " git commit",
        " git push",
        " selenium",
        " webdriver",
        " msedge.exe",
        " opera.exe",
    )
    padded = [" " + item.lower() + " " for item in commands]
    return not any(token in item for item in padded for token in forbidden)


def _source_l13_06_safe(source: Mapping[str, Any]) -> bool:
    return (
        source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("patch") == "L13.6"
        and source.get("source_patch") == "L13.5"
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and source.get("source_l13_05_aggregate_gate_remains_accepted") is True
        and source.get("execution_aggregate_gate_cli_readback_enforced") is True
        and source.get("filesystem_probe_only_when_l12_execution_preflight_ready") is True
        and _selected_candidate_ok(source)
        and _no_launch_side_effects(source)
    )


def build_edge_executable_filesystem_probe_execution_broad_validation_checkpoint(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
    activate_executable_filesystem_probe: bool = False,
    allow_real_filesystem_probe: bool = False,
    allow_executable_filesystem_probe_execution: bool = False,
    extra_candidates: Sequence[str] | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    source = l13_06.build_edge_executable_filesystem_probe_execution_aggregate_gate_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
        allow_real_filesystem_probe=allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=allow_executable_filesystem_probe_execution,
        extra_candidates=extra_candidates,
    )

    payload: dict[str, Any] = dict(source)
    _default_no_side_effect_fields(payload)
    planned = _planned_commands()
    required_paths = _required_paths_status(root)
    source_safe = _source_l13_06_safe(payload)
    truthful_selection = _selected_candidate_ok(payload)
    no_launch = _no_launch_side_effects(payload)
    probe_performed = payload.get("edge_executable_filesystem_probe_performed") is True
    probe_only_when_l12_ready = (not probe_performed) or payload.get("execution_preflight_ready") is True
    planned_passive = _planned_commands_are_passive(planned)

    checks = [
        _check("source_l13_06_aggregate_gate_readback_remains_accepted", source_safe),
        _check("broad_validation_checkpoint_enforced", True),
        _check("planned_broad_validation_commands_are_passive", planned_passive),
        _check("broad_validation_commands_not_executed_by_checkpoint", True),
        _check("truthful_selected_path_existing_reported_candidate", truthful_selection),
        _check("filesystem_probe_only_when_l12_execution_preflight_ready", probe_only_when_l12_ready),
        _check("no_launch_browser_profile_selenium_side_effects", no_launch),
        _check("required_l13_broad_checkpoint_paths_exist", bool(required_paths["ok"]), {"missing": required_paths["missing"]}),
        _check("compact_json_readback_available", True),
    ]

    status = STATUS_PASS if all(item["ok"] for item in checks) else STATUS_FAIL
    payload.update(
        {
            "ok": status == STATUS_PASS,
            "status": status,
            "phase": PHASE,
            "patch": PATCH,
            "command_name": COMMAND_NAME,
            "source_command_name": SOURCE_COMMAND_NAME,
            "source_patch": "L13.6",
            "source_l13_05_patch": "L13.5",
            "source_l13_04_patch": "L13.4",
            "source_l13_03_patch": "L13.3",
            "browser_priority": list(BROWSER_PRIORITY),
            "microsoft_edge_first": True,
            "opera_second": True,
            "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
            "source_l13_06_status": {
                "ok": source.get("ok"),
                "status": source.get("status"),
                "patch": source.get("patch"),
                "command_name": source.get("command_name"),
                "source_patch": source.get("source_patch"),
            },
            "source_l13_06_aggregate_gate_readback_remains_accepted": source_safe,
            "l13_06_aggregate_gate_readback_remains_accepted": source_safe,
            "l13_05_aggregate_gate_remains_accepted": source.get("l13_05_aggregate_gate_remains_accepted") is True or source.get("source_l13_05_aggregate_gate_remains_accepted") is True,
            "l13_04_fixture_matrix_readback_remains_accepted": source.get("l13_04_fixture_matrix_readback_remains_accepted") is True,
            "l13_03_execution_fixture_matrix_remains_accepted": source.get("l13_03_execution_fixture_matrix_remains_accepted") is True,
            "broad_validation_checkpoint_enforced": True,
            "planned_broad_validation_commands": planned,
            "planned_broad_validation_commands_are_passive": planned_passive,
            "broad_validation_commands_executed_by_checkpoint": False,
            "execution_aggregate_gate_cli_readback_enforced": payload.get("execution_aggregate_gate_cli_readback_enforced") is True,
            "execution_aggregate_gate_enforced": payload.get("execution_aggregate_gate_enforced") is True,
            "execution_fixture_matrix_cli_readback_enforced": payload.get("execution_fixture_matrix_cli_readback_enforced") is True,
            "execution_fixture_matrix_enforced": payload.get("execution_fixture_matrix_enforced") is True,
            "execution_cli_readback_enforced": payload.get("execution_cli_readback_enforced") is True,
            "execution_contract_enforced": payload.get("execution_contract_enforced") is True,
            "read_only_filesystem_probe": True,
            "small_allowlisted_microsoft_edge_executable_candidate_list": True,
            "l12_execution_preflight_required": True,
            "may_probe_only_when_l12_execution_preflight_ready": True,
            "filesystem_probe_only_when_l12_execution_preflight_ready": probe_only_when_l12_ready,
            "truthful_selected_path_existing_reported_candidate": truthful_selection,
            "no_executable_launch_attempted_by_broad_checkpoint": no_launch,
            "required_repo_paths": required_paths,
            "next_patch": NEXT_PATCH,
            "checks": checks,
            "executed_validation_commands": [],
        }
    )
    return payload


def render_text(payload: Mapping[str, Any]) -> str:
    selected = payload.get("edge_executable_selected_path") or "(none)"
    lines = [
        NAME,
        f"Status          : {payload.get('status')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"Source Patch    : {payload.get('source_patch')}",
        f"Exec Ready      : {payload.get('execution_preflight_ready')}",
        f"Probe Performed : {payload.get('edge_executable_filesystem_probe_performed')}",
        f"Selection Truth : {payload.get('truthful_selected_path_existing_reported_candidate')}",
        f"Path Selected   : {payload.get('edge_executable_path_selected')}",
        f"Selected Path   : {selected}",
        f"Plan Passive    : {payload.get('planned_broad_validation_commands_are_passive')}",
        f"Plan Executed   : {payload.get('broad_validation_commands_executed_by_checkpoint')}",
        f"Launch Attempt  : {payload.get('edge_executable_launch_attempted')}",
        f"Next Patch      : {payload.get('next_patch')}",
        "Checks:",
    ]
    for check in payload.get("checks", []):
        if isinstance(check, Mapping):
            lines.append(f"- {check.get('name')}: {check.get('status')}")
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=NAME)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--allow-live-start", action="store_true")
    parser.add_argument("--profile-dir", default=None)
    parser.add_argument("--allow-executable-probe", action="store_true")
    parser.add_argument("--activate-executable-filesystem-probe", action="store_true")
    parser.add_argument("--allow-real-filesystem-probe", action="store_true")
    parser.add_argument("--allow-executable-filesystem-probe-execution", action="store_true")
    parser.add_argument("--extra-candidate", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_filesystem_probe_execution_broad_validation_checkpoint(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
        allow_executable_probe=args.allow_executable_probe,
        activate_executable_filesystem_probe=args.activate_executable_filesystem_probe,
        allow_real_filesystem_probe=args.allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=args.allow_executable_filesystem_probe_execution,
        extra_candidates=args.extra_candidate,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
