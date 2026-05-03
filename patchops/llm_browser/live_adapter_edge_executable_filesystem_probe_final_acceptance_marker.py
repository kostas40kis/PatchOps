"""L9.8 passive Microsoft Edge executable filesystem-probe final acceptance marker.

Closes the L9 executable-filesystem-probe passive slice by wrapping the
accepted L9.7 broad validation checkpoint and proving L9.1 through L9.7 remain
accepted. The L9 stack remains model/readback only: no authorization keeps
contract_ready=false, authorized cases can report contract_ready=true, and
filesystem probing remains blocked by phase.

No filesystem probe, executable path selection, launch, Selenium import,
browser start, profile creation, click/download, paste/send, package run,
commit, or push is performed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_broad_validation_checkpoint as l9_07

PATCH = "L9.8"
PHASE = "L9"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L9.8 Microsoft Edge Executable Filesystem Probe Final Acceptance Marker"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-final-acceptance-marker"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-broad-validation-checkpoint"
NEXT_PATCH = "L10.1 Live adapter Microsoft Edge executable filesystem probe explicit activation contract"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-final-acceptance-marker-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
EXPECTED_FIXTURE_IDS = {
    "no_auth_dedicated_profile",
    "live_auth_without_probe_auth",
    "probe_auth_dedicated_profile",
    "probe_auth_default_profile",
    "probe_auth_missing_profile",
}
EDGE_EXECUTABLE_CANDIDATE_LABELS = (
    "program_files_edge_application_msedgedotexe",
    "program_files_x86_edge_application_msedgedotexe",
    "local_app_data_edge_application_msedgedotexe",
)
REPAIR_NOTE = "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok."

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_passive_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_aggregate_gate.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_broad_validation_checkpoint.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_final_acceptance_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_broad_validation_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_final_acceptance_marker.md",
    "tests/test_l9_07_edge_executable_filesystem_probe_broad_validation_checkpoint_current.py",
    "tests/test_l9_08_edge_executable_filesystem_probe_final_acceptance_marker_current.py",
    "scripts/patch_l9_07_brief_validate.py",
    "scripts/patch_l9_08_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_broad_validation_checkpoint.md": (
        "L9.7 Microsoft Edge executable filesystem probe broad validation checkpoint",
        SOURCE_COMMAND_NAME,
        "filesystem probe broad validation checkpoint enforced",
        "filesystem probe modeled only",
        "L9.8 Live adapter Microsoft Edge executable filesystem probe final acceptance marker",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_final_acceptance_marker.md": (
        "L9.8 Microsoft Edge executable filesystem probe final acceptance marker",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L9 executable filesystem probe passive slice accepted",
        "L9.1 executable filesystem probe passive contract remains accepted",
        "L9.2 executable filesystem probe CLI/readback remains accepted",
        "L9.3 executable filesystem probe fixture matrix remains accepted",
        "L9.4 executable filesystem probe fixture matrix CLI/readback remains accepted",
        "L9.5 executable filesystem probe aggregate gate remains accepted",
        "L9.6 executable filesystem probe aggregate CLI/readback remains accepted",
        "L9.7 executable filesystem probe broad validation checkpoint remains accepted",
        "filesystem probe final acceptance marker enforced",
        "filesystem probe modeled only",
        "filesystem probe fixture matrix remains modeled",
        "candidate path labels modeled only",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "filesystem probe readback can report contract_ready=true while filesystem probe remains blocked",
        "preflight readback can succeed while preflight_passed is false",
        REPAIR_NOTE,
        "--allow-executable-probe",
        "authorization can be present but filesystem probe execution remains blocked by phase",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L10.1 Live adapter Microsoft Edge executable filesystem probe explicit activation contract",
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
    state = {}
    for rel, phrases in DOC_REQUIREMENTS.items():
        path = repo_root / rel
        if not path.exists():
            missing_docs.append(rel)
            missing_phrases[rel] = list(phrases)
            state[rel] = {"exists": False, "missing_phrases": list(phrases)}
            continue
        text = path.read_text(encoding="utf-8")
        missing = [phrase for phrase in phrases if phrase not in text]
        state[rel] = {"exists": True, "missing_phrases": missing}
        if missing:
            missing_phrases[rel] = missing
    return {"ok": not missing_docs and not missing_phrases, "missing_docs": missing_docs, "missing_phrases": missing_phrases, "doc_state": state}


def _source_l9_07_safe(summary: Mapping[str, Any], *, expect_contract_ready: bool, expect_preflight_passed: bool) -> bool:
    fixture_ids = set(summary.get("edge_executable_filesystem_probe_fixture_ids", []))
    candidate_labels = set(summary.get("edge_executable_candidate_path_labels", []))
    return (
        summary.get("patch") == "L9.7"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l9_filesystem_probe_chain_accepted") is True
        and summary.get("l9_01_executable_filesystem_probe_passive_contract_remains_accepted") is True
        and summary.get("l9_02_executable_filesystem_probe_cli_readback_remains_accepted") is True
        and summary.get("l9_03_executable_filesystem_probe_fixture_matrix_remains_accepted") is True
        and summary.get("l9_04_executable_filesystem_probe_fixture_matrix_cli_readback_remains_accepted") is True
        and summary.get("l9_05_executable_filesystem_probe_aggregate_gate_remains_accepted") is True
        and summary.get("l9_06_executable_filesystem_probe_aggregate_cli_readback_remains_accepted") is True
        and summary.get("edge_executable_filesystem_probe_broad_validation_checkpoint_enforced") is True
        and summary.get("edge_executable_filesystem_probe_aggregate_gate_cli_readback_enforced") is True
        and summary.get("edge_executable_filesystem_probe_aggregate_gate_enforced") is True
        and summary.get("edge_executable_filesystem_probe_fixture_matrix_cli_readback_enforced") is True
        and summary.get("edge_executable_filesystem_probe_fixture_matrix_enforced") is True
        and summary.get("edge_executable_filesystem_probe_fixture_matrix_modeled") is True
        and summary.get("edge_executable_filesystem_probe_fixture_count", 0) >= 5
        and fixture_ids == EXPECTED_FIXTURE_IDS
        and summary.get("edge_executable_filesystem_probe_cli_readback_enforced") is True
        and summary.get("edge_executable_filesystem_probe_contract_enforced") is True
        and summary.get("edge_executable_filesystem_probe_modeled") is True
        and summary.get("edge_executable_probe_safety_preflight_passed") is expect_preflight_passed
        and summary.get("edge_executable_filesystem_probe_contract_ready") is expect_contract_ready
        and summary.get("edge_executable_filesystem_probe_execution_allowed") is False
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("fixture_filesystem_probe_performed") is False
        and summary.get("fixture_path_selected") is False
        and summary.get("fixture_executable_launch_attempted") is False
        and summary.get("edge_executable_candidate_path_labels_modeled") is True
        and summary.get("edge_executable_candidate_path_count", 0) >= 3
        and candidate_labels == set(EDGE_EXECUTABLE_CANDIDATE_LABELS)
        and summary.get("edge_executable_path_selected") is False
        and summary.get("edge_executable_selected_path") is None
        and summary.get("edge_executable_launch_attempted") is False
        and summary.get("startup_allowed") is False
        and summary.get("live_start_performed") is False
        and summary.get("browser_started") is False
        and summary.get("edge_process_started") is False
        and summary.get("browser_session_created") is False
        and summary.get("driver_created") is False
        and summary.get("profile_directory_created") is False
        and summary.get("filesystem_writes_performed") == []
        and summary.get("adapter_filesystem_writes_performed") == []
        and summary.get("side_effects_performed") == []
        and summary.get("selenium_imported_by_readback") is False
        and "source_l9_07_summary" not in summary
        and "source_l9_06_summary" not in summary
    )


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "chain_accepted": source.get("l9_filesystem_probe_chain_accepted") is True,
        "fixture_count": source.get("edge_executable_filesystem_probe_fixture_count"),
        "preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"),
        "contract_ready": source.get("edge_executable_filesystem_probe_contract_ready"),
        "filesystem_probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
        "candidate_path_count": source.get("edge_executable_candidate_path_count"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
    }


def _chain_acceptance(source: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "l9_01": source.get("l9_01_executable_filesystem_probe_passive_contract_remains_accepted") is True,
        "l9_02": source.get("l9_02_executable_filesystem_probe_cli_readback_remains_accepted") is True,
        "l9_03": source.get("l9_03_executable_filesystem_probe_fixture_matrix_remains_accepted") is True,
        "l9_04": source.get("l9_04_executable_filesystem_probe_fixture_matrix_cli_readback_remains_accepted") is True,
        "l9_05": source.get("l9_05_executable_filesystem_probe_aggregate_gate_remains_accepted") is True,
        "l9_06": source.get("l9_06_executable_filesystem_probe_aggregate_cli_readback_remains_accepted") is True,
        "l9_07": source.get("ok") is True and source.get("status") == STATUS_PASS,
    }


def build_edge_executable_filesystem_probe_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l9_07.build_edge_executable_filesystem_probe_broad_validation_checkpoint(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    expected_contract_ready = bool(allow_executable_probe)
    expected_preflight_passed = bool(allow_executable_probe)
    source_safe = _source_l9_07_safe(source, expect_contract_ready=expected_contract_ready, expect_preflight_passed=expected_preflight_passed)
    acceptance = _chain_acceptance(source)
    slice_ok = all(acceptance.values())
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l9_07_filesystem_probe_broad_checkpoint_still_passes", source_safe, _compact_source_status(source)),
        _check("l9_07_filesystem_probe_broad_checkpoint_remains_passive", source_safe, {"contract_ready": source.get("edge_executable_filesystem_probe_contract_ready"), "fs_probe": source.get("edge_executable_filesystem_probe_performed"), "path_selected": source.get("edge_executable_path_selected")}),
        _check("l9_01_through_l9_07_slice_remains_accepted", slice_ok, acceptance),
        _check("l9_08_filesystem_probe_final_marker_command_registered", command_state.get("ok") is True, command_state),
        _check("l9_07_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l9_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l9_docs_contain_filesystem_probe_final_marker_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("filesystem_probe_final_acceptance_marker_is_enforced", slice_ok and source.get("edge_executable_filesystem_probe_broad_validation_checkpoint_enforced") is True, acceptance),
        _check("fixture_ids_remain_stable", set(source.get("edge_executable_filesystem_probe_fixture_ids", [])) == EXPECTED_FIXTURE_IDS, {"fixture_ids": source.get("edge_executable_filesystem_probe_fixture_ids")}),
        _check("candidate_path_labels_remain_modeled_only", source.get("edge_executable_candidate_path_labels_modeled") is True and source.get("edge_executable_candidate_path_count", 0) >= 3, _compact_source_status(source)),
        _check("filesystem_probe_execution_remains_blocked_by_phase", source.get("edge_executable_filesystem_probe_execution_allowed") is False, {}),
        _check("filesystem_probe_is_not_performed", source.get("edge_executable_filesystem_probe_performed") is False and source.get("fixture_filesystem_probe_performed") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and source.get("fixture_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and source.get("fixture_executable_launch_attempted") is False, {}),
        _check("no_auth_readback_ok_preflight_false_contract_preserved", True if allow_executable_probe else (source.get("edge_executable_probe_safety_preflight_passed") is False and source.get("edge_executable_filesystem_probe_contract_ready") is False), _compact_source_status(source)),
        _check("authorized_contract_ready_but_filesystem_probe_stays_blocked", True if not allow_executable_probe else (source.get("edge_executable_filesystem_probe_contract_ready") is True and source.get("edge_executable_filesystem_probe_performed") is False), _compact_source_status(source)),
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
        "l9_executable_filesystem_probe_passive_slice_accepted": slice_ok,
        "l9_01_executable_filesystem_probe_passive_contract_remains_accepted": acceptance["l9_01"],
        "l9_02_executable_filesystem_probe_cli_readback_remains_accepted": acceptance["l9_02"],
        "l9_03_executable_filesystem_probe_fixture_matrix_remains_accepted": acceptance["l9_03"],
        "l9_04_executable_filesystem_probe_fixture_matrix_cli_readback_remains_accepted": acceptance["l9_04"],
        "l9_05_executable_filesystem_probe_aggregate_gate_remains_accepted": acceptance["l9_05"],
        "l9_06_executable_filesystem_probe_aggregate_cli_readback_remains_accepted": acceptance["l9_06"],
        "l9_07_executable_filesystem_probe_broad_validation_checkpoint_remains_accepted": acceptance["l9_07"],
        "source_l9_07_status": _compact_source_status(source),
        "edge_executable_filesystem_probe_final_acceptance_marker_enforced": True,
        "edge_executable_filesystem_probe_broad_validation_checkpoint_enforced": source.get("edge_executable_filesystem_probe_broad_validation_checkpoint_enforced"),
        "edge_executable_filesystem_probe_aggregate_gate_cli_readback_enforced": source.get("edge_executable_filesystem_probe_aggregate_gate_cli_readback_enforced"),
        "edge_executable_filesystem_probe_aggregate_gate_enforced": source.get("edge_executable_filesystem_probe_aggregate_gate_enforced"),
        "edge_executable_filesystem_probe_aggregate_status": source.get("edge_executable_filesystem_probe_aggregate_status"),
        "edge_executable_filesystem_probe_fixture_matrix_cli_readback_enforced": source.get("edge_executable_filesystem_probe_fixture_matrix_cli_readback_enforced"),
        "edge_executable_filesystem_probe_fixture_matrix_enforced": source.get("edge_executable_filesystem_probe_fixture_matrix_enforced"),
        "edge_executable_filesystem_probe_fixture_matrix_modeled": source.get("edge_executable_filesystem_probe_fixture_matrix_modeled"),
        "edge_executable_filesystem_probe_fixture_count": source.get("edge_executable_filesystem_probe_fixture_count"),
        "edge_executable_filesystem_probe_fixture_ids": source.get("edge_executable_filesystem_probe_fixture_ids"),
        "edge_executable_filesystem_probe_fixture_matrix": source.get("edge_executable_filesystem_probe_fixture_matrix"),
        "fixture_filesystem_probe_performed": False,
        "fixture_path_selected": False,
        "fixture_executable_launch_attempted": False,
        "fixture_contract_ready_when_authorized": True,
        "fixture_contract_not_ready_without_probe_auth": True,
        "edge_executable_filesystem_probe_cli_readback_enforced": source.get("edge_executable_filesystem_probe_cli_readback_enforced"),
        "edge_executable_filesystem_probe_contract_enforced": source.get("edge_executable_filesystem_probe_contract_enforced"),
        "edge_executable_filesystem_probe_modeled": source.get("edge_executable_filesystem_probe_modeled"),
        "edge_executable_filesystem_probe_status": source.get("edge_executable_filesystem_probe_status"),
        "edge_executable_filesystem_probe_requested": source.get("edge_executable_filesystem_probe_requested"),
        "edge_executable_filesystem_probe_contract_ready": source.get("edge_executable_filesystem_probe_contract_ready"),
        "edge_executable_filesystem_probe_execution_allowed": False,
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_filesystem_probe_blocked_reason": source.get("edge_executable_filesystem_probe_blocked_reason"),
        "edge_executable_candidate_path_labels_modeled": source.get("edge_executable_candidate_path_labels_modeled"),
        "edge_executable_candidate_path_labels": source.get("edge_executable_candidate_path_labels"),
        "edge_executable_candidate_path_count": source.get("edge_executable_candidate_path_count"),
        "edge_executable_candidate_path_results": source.get("edge_executable_candidate_path_results"),
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
        "edge_executable_probe_authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "edge_executable_probe_authorized": source.get("edge_executable_probe_authorized"),
        "edge_executable_probe_requested": source.get("edge_executable_probe_requested"),
        "edge_executable_probe_permitted_by_phase": False,
        "edge_executable_probe_preflight_allows_probe_execution": False,
        "edge_executable_probe_safety_preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"),
        "preflight_authorization_present": source.get("preflight_authorization_present"),
        "preflight_readback_can_succeed_while_preflight_passed_false": True,
        "preflight_missing_authorization_note": REPAIR_NOTE,
        "preflight_alone_does_not_perform_probe": True,
        "authorization_alone_does_not_perform_probe": True,
        "startup_allowed": False,
        "live_start_performed": False,
        "browser_started": False,
        "edge_process_started": False,
        "browser_session_created": False,
        "driver_created": False,
        "profile_directory_created": False,
        "profile_parent_directory_created": False,
        "profile_parent_filesystem_probe_performed": False,
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
        f"L9 Slice OK     : {payload.get('l9_executable_filesystem_probe_passive_slice_accepted')}",
        f"Fixture Count   : {payload.get('edge_executable_filesystem_probe_fixture_count')}",
        f"Contract Ready  : {payload.get('edge_executable_filesystem_probe_contract_ready')}",
        f"FS Probe        : {payload.get('edge_executable_filesystem_probe_performed')}",
        f"Path Selected   : {payload.get('edge_executable_path_selected')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_filesystem_probe_final_acceptance_marker(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
        allow_executable_probe=args.allow_executable_probe,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
