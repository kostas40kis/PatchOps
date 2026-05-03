"""L12.8 passive Microsoft Edge executable filesystem-probe execution preflight final acceptance marker.

Closes the L12 execution-preflight stack after the accepted L12.7 broad
validation checkpoint. Execution preflight readiness may be true when all gates
are present, but filesystem probing, path selection, and launch remain blocked
by phase.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint as l12_07

PATCH = "L12.8"
PHASE = "L12"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L12.8 Microsoft Edge Executable Filesystem Probe Execution Preflight Final Acceptance Marker"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-final-acceptance-marker"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-broad-validation-checkpoint"
NEXT_PATCH = "L13.1 Live adapter Microsoft Edge executable filesystem probe execution contract"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-execution-preflight-final-acceptance-marker-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
EXECUTABLE_PROBE_ACTIVATION_FLAG = "--activate-executable-filesystem-probe"
REAL_FILESYSTEM_PROBE_FLAG = "--allow-real-filesystem-probe"
EXECUTION_PREFLIGHT_FLAG = "--allow-executable-filesystem-probe-execution"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
EXPECTED_FIXTURE_IDS = {
    "no_gates",
    "execution_flag_only",
    "real_ready_without_execution_flag",
    "execution_preflight_ready_dedicated_profile",
    "execution_preflight_ready_default_profile",
    "execution_preflight_ready_missing_profile",
}

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_aggregate_gate.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.md",
    "tests/test_l12_07_edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint_current.py",
    "tests/test_l12_08_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker_current.py",
    "scripts/patch_l12_07_brief_validate.py",
    "scripts/patch_l12_08_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint.md": (
        "L12.7 Microsoft Edge executable filesystem probe execution preflight broad validation checkpoint",
        SOURCE_COMMAND_NAME,
        "execution preflight broad validation checkpoint enforced",
        "L12.8 Live adapter Microsoft Edge executable filesystem probe execution preflight final acceptance marker",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.md": (
        "L12.8 Microsoft Edge executable filesystem probe execution preflight final acceptance marker",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L12 execution preflight stack accepted",
        "L12.1 execution preflight contract remains accepted",
        "L12.2 execution preflight CLI/readback remains accepted",
        "L12.3 execution preflight fixture matrix remains accepted",
        "L12.4 execution preflight fixture matrix CLI/readback remains accepted",
        "L12.5 execution preflight aggregate gate remains accepted",
        "L12.6 execution preflight aggregate gate CLI/readback remains accepted",
        "L12.7 execution preflight broad validation checkpoint remains accepted",
        "execution preflight final acceptance marker enforced",
        "execution preflight broad validation checkpoint enforced",
        "execution preflight aggregate gate CLI/readback enforced",
        "execution preflight aggregate gate enforced",
        "execution preflight fixture matrix CLI/readback enforced",
        "execution preflight fixture matrix enforced",
        "execution preflight CLI/readback enforced",
        "execution preflight contract enforced",
        "filesystem probe execution requires a separate explicit execution-preflight flag",
        "six execution preflight fixtures remain stable",
        EXECUTION_PREFLIGHT_FLAG,
        REAL_FILESYSTEM_PROBE_FLAG,
        EXECUTABLE_PROBE_ACTIVATION_FLAG,
        EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "execution preflight readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L13.1 Live adapter Microsoft Edge executable filesystem probe execution contract",
    ),
}


def _repo_root(repo_root: str | Path | None = None) -> Path:
    return Path.cwd().resolve() if repo_root is None else Path(repo_root).resolve()


def _missing_paths(root: Path, rel_paths: Iterable[str]) -> list[str]:
    return [rel for rel in rel_paths if not (root / rel).exists()]


def _check(name: str, ok: bool, detail: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "status": STATUS_PASS if ok else STATUS_FAIL, "ok": bool(ok), "detail": dict(detail or {})}


def _new_forbidden_imports(before: set[str]) -> list[str]:
    after = set(sys.modules)
    loaded = after - before
    found = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in loaded):
            found.append(root)
    return sorted(found)


def _command_static_presence(command_name: str) -> dict[str, Any]:
    try:
        from patchops.llm_browser import commands
        names = tuple(commands.llm_browser_command_names())
        path = Path(commands.__file__).resolve()
        text = path.read_text(encoding="utf-8")
        return {"ok": command_name in names, "command_name": command_name, "commands_path": str(path), "sentinel_present": command_name in text}
    except Exception as exc:
        return {"ok": False, "command_name": command_name, "error": f"{type(exc).__name__}: {exc}"}


def _doc_state(repo_root: Path) -> dict[str, Any]:
    missing_docs = []
    missing_phrases: dict[str, list[str]] = {}
    for rel, phrases in DOC_REQUIREMENTS.items():
        path = repo_root / rel
        if not path.exists():
            missing_docs.append(rel)
            missing_phrases[rel] = list(phrases)
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in text]
        if missing:
            missing_phrases[rel] = missing
    return {"ok": not missing_docs and not missing_phrases, "missing_docs": missing_docs, "missing_phrases": missing_phrases}


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "chain_accepted": source.get("l12_execution_preflight_chain_accepted") is True,
        "fixture_count": source.get("execution_preflight_fixture_count"),
        "real_ready": source.get("real_filesystem_probe_preflight_ready"),
        "exec_flag": source.get("execution_preflight_authorization_present"),
        "exec_ready": source.get("execution_preflight_ready"),
        "exec_allowed": source.get("execution_preflight_execution_allowed"),
        "fs_probe": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
    }


def _source_l12_07_safe(source: Mapping[str, Any], *, expected_real_ready: bool, expected_execution_ready: bool) -> bool:
    fixture_ids = set(source.get("execution_preflight_fixture_ids", []))
    return (
        source.get("patch") == "L12.7"
        and source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and source.get("l12_execution_preflight_chain_accepted") is True
        and source.get("l12_01_execution_preflight_contract_remains_accepted") is True
        and source.get("l12_02_execution_preflight_cli_readback_remains_accepted") is True
        and source.get("l12_03_execution_preflight_fixture_matrix_remains_accepted") is True
        and source.get("l12_04_execution_preflight_fixture_matrix_cli_readback_remains_accepted") is True
        and source.get("l12_05_execution_preflight_aggregate_gate_remains_accepted") is True
        and source.get("l12_06_execution_preflight_aggregate_gate_cli_readback_remains_accepted") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_aggregate_gate_cli_readback_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_aggregate_gate_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_cli_readback_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_contract_enforced") is True
        and source.get("execution_preflight_fixture_count") == 6
        and fixture_ids == EXPECTED_FIXTURE_IDS
        and source.get("execution_preflight_ready") is expected_execution_ready
        and source.get("real_filesystem_probe_preflight_ready") is expected_real_ready
        and source.get("execution_preflight_execution_allowed") is False
        and source.get("fixture_execution_preflight_execution_allowed") is False
        and source.get("real_filesystem_probe_execution_allowed") is False
        and source.get("edge_executable_filesystem_probe_execution_allowed") is False
        and source.get("edge_executable_filesystem_probe_performed") is False
        and source.get("fixture_filesystem_probe_performed") is False
        and source.get("edge_executable_path_selected") is False
        and source.get("edge_executable_selected_path") is None
        and source.get("fixture_path_selected") is False
        and source.get("edge_executable_launch_attempted") is False
        and source.get("fixture_executable_launch_attempted") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("browser_session_created") is False
        and source.get("driver_created") is False
        and source.get("profile_directory_created") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("selenium_imported_by_readback") is False
        and "source_l12_07_summary" not in source
        and "source_l12_06_summary" not in source
    )


def _chain_acceptance(source: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "l12_01": source.get("l12_01_execution_preflight_contract_remains_accepted") is True,
        "l12_02": source.get("l12_02_execution_preflight_cli_readback_remains_accepted") is True,
        "l12_03": source.get("l12_03_execution_preflight_fixture_matrix_remains_accepted") is True,
        "l12_04": source.get("l12_04_execution_preflight_fixture_matrix_cli_readback_remains_accepted") is True,
        "l12_05": source.get("l12_05_execution_preflight_aggregate_gate_remains_accepted") is True,
        "l12_06": source.get("l12_06_execution_preflight_aggregate_gate_cli_readback_remains_accepted") is True,
        "l12_07": source.get("ok") is True and source.get("status") == STATUS_PASS,
    }


def build_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
    activate_executable_filesystem_probe: bool = False,
    allow_real_filesystem_probe: bool = False,
    allow_executable_filesystem_probe_execution: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    expected_real_ready = bool(allow_live_start and allow_executable_probe and activate_executable_filesystem_probe and allow_real_filesystem_probe)
    expected_execution_ready = bool(expected_real_ready and allow_executable_filesystem_probe_execution)
    source = l12_07.build_edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
        allow_real_filesystem_probe=allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=allow_executable_filesystem_probe_execution,
    )
    source_safe = _source_l12_07_safe(source, expected_real_ready=expected_real_ready, expected_execution_ready=expected_execution_ready)
    acceptance = _chain_acceptance(source)
    stack_ok = all(acceptance.values())
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l12_07_execution_preflight_broad_checkpoint_still_passes", source_safe, _compact_source_status(source)),
        _check("l12_07_execution_preflight_broad_checkpoint_remains_passive", source_safe, {"exec_ready": source.get("execution_preflight_ready"), "exec_allowed": source.get("execution_preflight_execution_allowed"), "fs_probe": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l12_01_through_l12_07_stack_remains_accepted", stack_ok, acceptance),
        _check("l12_08_execution_preflight_final_marker_command_registered", command_state.get("ok") is True, command_state),
        _check("l12_07_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l12_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l12_docs_contain_execution_preflight_final_marker_boundary", doc_state.get("ok") is True, doc_state),
        _check("execution_preflight_final_acceptance_marker_is_enforced", stack_ok and source.get("edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint_enforced") is True, acceptance),
        _check("execution_preflight_fixture_ids_are_stable", set(source.get("execution_preflight_fixture_ids", [])) == EXPECTED_FIXTURE_IDS, {"fixture_ids": source.get("execution_preflight_fixture_ids")}),
        _check("execution_preflight_ready_requires_execution_flag", source.get("execution_preflight_ready") is expected_execution_ready, _compact_source_status(source)),
        _check("execution_preflight_execution_remains_blocked_by_phase", source.get("execution_preflight_execution_allowed") is False and source.get("fixture_execution_preflight_execution_allowed") is False, {}),
        _check("filesystem_probe_is_not_performed", source.get("edge_executable_filesystem_probe_performed") is False and source.get("fixture_filesystem_probe_performed") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and source.get("fixture_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and source.get("fixture_executable_launch_attempted") is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", source_safe, {}),
    ]
    ok = all(check["ok"] for check in checks)

    return {
        "ok": ok,
        "status": STATUS_PASS if ok else STATUS_FAIL,
        "patch": PATCH,
        "phase": PHASE,
        "name": NAME,
        "next_patch": NEXT_PATCH,
        "command_name": COMMAND_NAME,
        "source_command_name": SOURCE_COMMAND_NAME,
        "side_effect_boundary": SIDE_EFFECT_BOUNDARY,
        "repo_root": str(root),
        "browser_priority": list(BROWSER_PRIORITY),
        "edge_first": True,
        "opera_second": True,
        "brief_validation_output_enabled": True,
        "compact_json_readback_enabled": True,
        "nested_source_summaries_pruned": True,
        "l12_execution_preflight_stack_accepted": stack_ok,
        "l12_01_execution_preflight_contract_remains_accepted": acceptance["l12_01"],
        "l12_02_execution_preflight_cli_readback_remains_accepted": acceptance["l12_02"],
        "l12_03_execution_preflight_fixture_matrix_remains_accepted": acceptance["l12_03"],
        "l12_04_execution_preflight_fixture_matrix_cli_readback_remains_accepted": acceptance["l12_04"],
        "l12_05_execution_preflight_aggregate_gate_remains_accepted": acceptance["l12_05"],
        "l12_06_execution_preflight_aggregate_gate_cli_readback_remains_accepted": acceptance["l12_06"],
        "l12_07_execution_preflight_broad_validation_checkpoint_remains_accepted": acceptance["l12_07"],
        "source_l12_07_status": _compact_source_status(source),
        "edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker_enforced": True,
        "edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_broad_validation_checkpoint_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_aggregate_gate_cli_readback_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_aggregate_gate_cli_readback_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_aggregate_gate_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_aggregate_gate_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_cli_readback_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_cli_readback_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_contract_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_contract_enforced"),
        "execution_preflight_fixture_count": source.get("execution_preflight_fixture_count"),
        "execution_preflight_fixture_ids": source.get("execution_preflight_fixture_ids"),
        "execution_preflight_fixture_matrix": source.get("execution_preflight_fixture_matrix"),
        "execution_preflight_flag": EXECUTION_PREFLIGHT_FLAG,
        "execution_preflight_authorization_present": source.get("execution_preflight_authorization_present"),
        "execution_preflight_ready": source.get("execution_preflight_ready"),
        "execution_preflight_execution_allowed": False,
        "fixture_execution_preflight_execution_allowed": False,
        "fixture_filesystem_probe_performed": False,
        "fixture_path_selected": False,
        "fixture_executable_launch_attempted": False,
        "execution_preflight_does_not_probe": True,
        "real_filesystem_probe_flag": REAL_FILESYSTEM_PROBE_FLAG,
        "real_filesystem_probe_authorization_present": source.get("real_filesystem_probe_authorization_present"),
        "real_filesystem_probe_preflight_ready": source.get("real_filesystem_probe_preflight_ready"),
        "real_filesystem_probe_execution_allowed": False,
        "edge_executable_filesystem_probe_activation_flag": EXECUTABLE_PROBE_ACTIVATION_FLAG,
        "edge_executable_probe_authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "filesystem_probe_activation_ready": source.get("filesystem_probe_activation_ready"),
        "filesystem_probe_activation_execution_allowed": False,
        "edge_executable_filesystem_probe_execution_allowed": False,
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
        "startup_allowed": False,
        "live_start_performed": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "filesystem_writes_performed": [],
        "adapter_filesystem_writes_performed": [],
        "side_effects_performed": [],
        "click_download_performed": False,
        "download_performed": False,
        "paste_performed": False,
        "send_or_submit_performed": False,
        "package_run_performed_by_adapter": False,
        "git_commit_executed": False,
        "git_push_executed": False,
        "selenium_required": False,
        "selenium_imported_by_readback": False,
        "optional_browser_dependencies_required": False,
        "command_static_presence": command_state,
        "source_command_static_presence": source_command_state,
        "doc_state": doc_state,
        "missing_repo_paths": missing_paths,
        "checks": checks,
        "executed_validation_commands": [],
    }


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        NAME,
        f"Status          : {payload.get('status')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"L12 Stack OK    : {payload.get('l12_execution_preflight_stack_accepted')}",
        f"Fixture Count   : {payload.get('execution_preflight_fixture_count')}",
        f"Exec Ready      : {payload.get('execution_preflight_ready')}",
        f"Exec Allowed    : {payload.get('execution_preflight_execution_allowed')}",
        f"FS Probe        : {payload.get('edge_executable_filesystem_probe_performed')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
        allow_executable_probe=args.allow_executable_probe,
        activate_executable_filesystem_probe=args.activate_executable_filesystem_probe,
        allow_real_filesystem_probe=args.allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=args.allow_executable_filesystem_probe_execution,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
