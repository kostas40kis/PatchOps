"""L8.1 passive Microsoft Edge executable-probe safety preflight contract.

L8.1 starts the safety-preflight slice after the accepted L7 executable-probe
authorization slice. It models the checks that must be true before a later
phase may perform a real executable filesystem probe, but this patch still
performs no probe, no path selection, no launch, no Selenium import, no browser
start, no profile creation, no click/download, no paste/send, no package run,
no commit, and no push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_final_acceptance_marker as l7_08

PATCH = "L8.1"
PHASE = "L8"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L8.1 Microsoft Edge Executable Probe Safety Preflight Passive Contract"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-safety-preflight-contract"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-authorization-final-acceptance-marker"
NEXT_PATCH = "L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-probe-safety-preflight-passive-contract-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
EXPECTED_FIXTURE_IDS = {
    "no_probe_auth_dedicated_profile",
    "live_auth_without_probe_auth",
    "probe_auth_dedicated_profile",
    "probe_auth_default_profile",
    "probe_auth_missing_profile",
}

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_safety_preflight_passive_contract.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md",
    "tests/test_l7_08_edge_executable_probe_authorization_final_acceptance_marker_current.py",
    "tests/test_l8_01_edge_executable_probe_safety_preflight_passive_contract_current.py",
    "scripts/patch_l7_08_brief_validate.py",
    "scripts/patch_l8_01_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_final_acceptance_marker.md": (
        "L7.8 Microsoft Edge executable probe authorization final acceptance marker",
        SOURCE_COMMAND_NAME,
        "L7 executable probe authorization slice accepted",
        "L8.1 Live adapter Microsoft Edge executable probe safety preflight passive contract",
    ),
    "docs/llm_browser_live_adapter_edge_executable_probe_safety_preflight_passive_contract.md": (
        "L8.1 Microsoft Edge executable probe safety preflight passive contract",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L7.8 executable probe authorization final marker remains accepted",
        "L7 executable probe authorization slice accepted",
        "safety preflight contract enforced",
        "safety preflight modeled only",
        "preflight alone does not perform a probe",
        "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.",
        "--allow-executable-probe",
        "authorization can be present but probe execution remains blocked by phase",
        "executable filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L8.2 Live adapter Microsoft Edge executable probe safety preflight CLI/readback",
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


def _source_l7_08_safe(summary: Mapping[str, Any]) -> bool:
    ids = set(summary.get("edge_executable_probe_authorization_fixture_ids", []))
    return (
        summary.get("patch") == "L7.8"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l7_executable_probe_authorization_slice_accepted") is True
        and summary.get("l7_01_executable_probe_authorization_passive_contract_remains_accepted") is True
        and summary.get("l7_02_executable_probe_authorization_cli_readback_remains_accepted") is True
        and summary.get("l7_03_executable_probe_authorization_fixture_matrix_remains_accepted") is True
        and summary.get("l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted") is True
        and summary.get("l7_05_executable_probe_authorization_aggregate_gate_remains_accepted") is True
        and summary.get("l7_06_executable_probe_authorization_aggregate_cli_readback_remains_accepted") is True
        and summary.get("l7_07_executable_probe_authorization_broad_validation_checkpoint_remains_accepted") is True
        and summary.get("edge_executable_probe_authorization_final_acceptance_marker_enforced") is True
        and summary.get("edge_executable_probe_authorization_modeled") is True
        and summary.get("edge_executable_probe_permitted_by_phase") is False
        and summary.get("authorization_alone_does_not_perform_probe") is True
        and ids == EXPECTED_FIXTURE_IDS
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("edge_executable_path_selected") is False
        and summary.get("edge_executable_selected_path") is None
        and summary.get("edge_executable_launch_attempted") is False
        and summary.get("fixture_probe_performed") is False
        and summary.get("fixture_executable_selected") is False
        and summary.get("fixture_executable_launch_attempted") is False
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
        and "source_l7_08_summary" not in summary
        and "source_l7_07_summary" not in summary
    )


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "slice_accepted": source.get("l7_executable_probe_authorization_slice_accepted") is True,
        "probe_authorized": source.get("edge_executable_probe_authorized"),
        "probe_permitted_by_phase": source.get("edge_executable_probe_permitted_by_phase"),
        "probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
        "nested_source_summaries_pruned": source.get("nested_source_summaries_pruned") is True,
    }


def _safety_preflight_state(source: Mapping[str, Any], allow_executable_probe: bool) -> dict[str, Any]:
    checks = {
        "l7_authorization_slice_accepted": source.get("l7_executable_probe_authorization_slice_accepted") is True,
        "explicit_probe_authorization_modeled": source.get("edge_executable_probe_authorization_modeled") is True,
        "explicit_probe_authorization_present": bool(allow_executable_probe),
        "edge_is_first_supported_browser": BROWSER_PRIORITY[0] == "edge",
        "selenium_dependency_not_required": source.get("selenium_required") is False,
        "browser_not_started": source.get("browser_started") is False,
        "profile_not_created": source.get("profile_directory_created") is False,
        "adapter_filesystem_writes_absent": source.get("adapter_filesystem_writes_performed") == [],
    }
    return {
        "edge_executable_probe_safety_preflight_contract_enforced": True,
        "edge_executable_probe_safety_preflight_modeled": True,
        "edge_executable_probe_safety_preflight_status": "MODELED_ONLY_BLOCKED_BY_PHASE",
        "edge_executable_probe_safety_preflight_checks": checks,
        "edge_executable_probe_safety_preflight_passed": all(checks.values()),
        "edge_executable_probe_preflight_allows_probe_execution": False,
        "preflight_alone_does_not_perform_probe": True,
        "preflight_authorization_present": bool(allow_executable_probe),
        "preflight_blocked_reason": "L8.1 models safety preflight only; real filesystem probing is reserved for a later accepted phase.",
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_launch_attempted": False,
        "startup_allowed": False,
        "live_start_performed": False,
    }


def build_edge_executable_probe_safety_preflight_passive_contract(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l7_08.build_edge_executable_probe_authorization_final_acceptance_marker(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    preflight = _safety_preflight_state(source, allow_executable_probe)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l7_08_authorization_final_marker_still_passes", _source_l7_08_safe(source), _compact_source_status(source)),
        _check("l7_08_authorization_final_marker_remains_passive", _source_l7_08_safe(source), {"probe_authorized": source.get("edge_executable_probe_authorized"), "probe_permitted": source.get("edge_executable_probe_permitted_by_phase"), "probe_performed": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l8_01_safety_preflight_contract_command_registered", command_state.get("ok") is True, command_state),
        _check("l7_08_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l8_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l8_docs_contain_safety_preflight_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("safety_preflight_is_modeled", preflight["edge_executable_probe_safety_preflight_modeled"] is True, preflight),
        _check("safety_preflight_checks_pass_when_authorized", preflight["edge_executable_probe_safety_preflight_passed"] is bool(allow_executable_probe), preflight),
        _check("preflight_alone_still_does_not_probe", preflight["preflight_alone_does_not_perform_probe"] is True and preflight["edge_executable_filesystem_probe_performed"] is False, preflight),
        _check("probe_execution_remains_blocked_by_phase", preflight["edge_executable_probe_preflight_allows_probe_execution"] is False, preflight),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and preflight["edge_executable_path_selected"] is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and preflight["edge_executable_launch_attempted"] is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l7_08_safe(source), {}),
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
        "l7_08_executable_probe_authorization_final_marker_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "l7_executable_probe_authorization_slice_accepted": source.get("l7_executable_probe_authorization_slice_accepted") is True,
        "source_l7_08_status": _compact_source_status(source),
        **preflight,
        "edge_executable_probe_authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "edge_executable_probe_authorization_modeled": True,
        "edge_executable_probe_authorized": source.get("edge_executable_probe_authorized"),
        "edge_executable_probe_requested": source.get("edge_executable_probe_requested"),
        "edge_executable_probe_permitted_by_phase": False,
        "edge_executable_probe_blocked_reason": source.get("edge_executable_probe_blocked_reason"),
        "authorization_alone_does_not_perform_probe": True,
        "edge_executable_candidate_paths_modeled": source.get("edge_executable_candidate_paths_modeled"),
        "edge_executable_candidate_count": source.get("edge_executable_candidate_count"),
        "edge_executable_fixture_matrix_modeled": source.get("edge_executable_fixture_matrix_modeled"),
        "edge_executable_fixture_count": source.get("edge_executable_fixture_count"),
        "edge_executable_fixture_ids": source.get("edge_executable_fixture_ids"),
        "edge_executable_selected_path": None,
        "fixture_probe_performed": False,
        "fixture_executable_selected": False,
        "fixture_executable_launch_attempted": False,
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
        f"L7.8 Accepted   : {payload.get('l7_08_executable_probe_authorization_final_marker_remains_accepted')}",
        f"Preflight OK    : {payload.get('edge_executable_probe_safety_preflight_passed')}",
        f"Probe Auth      : {payload.get('edge_executable_probe_authorized')}",
        f"Probe Permitted : {payload.get('edge_executable_probe_preflight_allows_probe_execution')}",
        f"Exe Probe       : {payload.get('edge_executable_filesystem_probe_performed')}",
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
    payload = build_edge_executable_probe_safety_preflight_passive_contract(
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
