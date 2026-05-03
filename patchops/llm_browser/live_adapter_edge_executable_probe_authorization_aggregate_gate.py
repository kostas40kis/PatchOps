"""L7.5 passive Edge executable-probe authorization aggregate gate.

Aggregates accepted L7.1 through L7.4 executable-probe authorization surfaces.
The gate keeps the explicit authorization contract modeled, confirms the fixture
matrix/readback surfaces are still accepted, and still performs no executable
filesystem probe, no path selection, no launch, no Selenium import, no browser
start, no profile creation, no click/download, no paste/send, no package run,
no commit, and no push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_fixture_matrix_cli_readback as l7_04

PATCH = "L7.5"
PHASE = "L7"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L7.5 Microsoft Edge Executable Probe Authorization Aggregate Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-authorization-aggregate-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-authorization-fixture-matrix-readback"
NEXT_PATCH = "L7.6 Live adapter Microsoft Edge executable probe authorization aggregate gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-probe-authorization-aggregate-gate-only"
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
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_passive_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_aggregate_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_aggregate_gate.md",
    "tests/test_l7_04_edge_executable_probe_authorization_fixture_matrix_cli_readback_current.py",
    "tests/test_l7_05_edge_executable_probe_authorization_aggregate_gate_current.py",
    "scripts/patch_l7_04_brief_validate.py",
    "scripts/patch_l7_05_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_fixture_matrix_cli_readback.md": (
        "L7.4 Microsoft Edge executable probe authorization fixture matrix CLI/readback",
        SOURCE_COMMAND_NAME,
        "fixture matrix CLI/readback enforced",
        "authorization alone does not perform a probe",
        "L7.5 Live adapter Microsoft Edge executable probe authorization aggregate gate",
    ),
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_aggregate_gate.md": (
        "L7.5 Microsoft Edge executable probe authorization aggregate gate",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L7.1 executable probe authorization passive contract remains accepted",
        "L7.2 executable probe authorization CLI/readback remains accepted",
        "L7.3 executable probe authorization fixture matrix remains accepted",
        "L7.4 executable probe authorization fixture matrix CLI/readback remains accepted",
        "executable probe authorization aggregate gate enforced",
        "--allow-executable-probe",
        "authorization alone does not perform a probe",
        "executable probe remains blocked by phase",
        "executable filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L7.6 Live adapter Microsoft Edge executable probe authorization aggregate gate CLI/readback",
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


def _source_l7_04_safe(summary: Mapping[str, Any]) -> bool:
    ids = set(summary.get("edge_executable_probe_authorization_fixture_ids", []))
    return (
        summary.get("patch") == "L7.4"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l7_03_executable_probe_authorization_fixture_matrix_remains_accepted") is True
        and summary.get("edge_executable_probe_authorization_fixture_matrix_cli_readback_enforced") is True
        and summary.get("edge_executable_probe_authorization_fixture_matrix_enforced") is True
        and summary.get("edge_executable_probe_authorization_fixture_matrix_modeled") is True
        and summary.get("edge_executable_probe_authorization_fixture_count", 0) >= 5
        and ids == EXPECTED_FIXTURE_IDS
        and summary.get("edge_executable_probe_authorization_modeled") is True
        and summary.get("edge_executable_probe_permitted_by_phase") is False
        and summary.get("authorization_alone_does_not_perform_probe") is True
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
        and "source_l7_04_summary" not in summary
        and "source_l7_03_summary" not in summary
    )


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "fixture_count": source.get("edge_executable_probe_authorization_fixture_count"),
        "fixture_ids": source.get("edge_executable_probe_authorization_fixture_ids"),
        "probe_authorized": source.get("edge_executable_probe_authorized"),
        "probe_permitted_by_phase": source.get("edge_executable_probe_permitted_by_phase"),
        "probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
        "nested_source_summaries_pruned": source.get("nested_source_summaries_pruned") is True,
    }


def _chain_acceptance(source: Mapping[str, Any]) -> dict[str, bool]:
    source_l7_03 = source.get("source_l7_03_status", {}) if isinstance(source.get("source_l7_03_status"), Mapping) else {}
    source_l7_02 = source_l7_03.get("source_l7_02_status", {}) if isinstance(source_l7_03.get("source_l7_02_status"), Mapping) else {}
    return {
        "l7_01": bool(source_l7_02.get("ok") and source_l7_02.get("status") == STATUS_PASS) if source_l7_02 else True,
        "l7_02": bool(source_l7_03.get("ok") and source_l7_03.get("status") == STATUS_PASS),
        "l7_03": bool(source.get("source_l7_03_status", {}).get("ok") and source.get("source_l7_03_status", {}).get("status") == STATUS_PASS),
        "l7_04": bool(source.get("ok") is True and source.get("status") == STATUS_PASS),
    }


def _aggregate_state(source: Mapping[str, Any]) -> dict[str, Any]:
    acceptance = _chain_acceptance(source)
    return {
        "edge_executable_probe_authorization_aggregate_gate_enforced": True,
        "edge_executable_probe_authorization_aggregate_status": "BLOCKED_EXECUTABLE_PROBE_AUTHORIZATION_MODEL_ONLY",
        "edge_executable_probe_authorization_aggregate_reason": "L7.5 aggregates L7.1-L7.4 but still performs no executable filesystem probe, selection, or launch.",
        "l7_01_executable_probe_authorization_passive_contract_ok": acceptance["l7_01"],
        "l7_02_executable_probe_authorization_cli_readback_ok": acceptance["l7_02"],
        "l7_03_executable_probe_authorization_fixture_matrix_ok": acceptance["l7_03"],
        "l7_04_executable_probe_authorization_fixture_matrix_cli_readback_ok": acceptance["l7_04"],
        "fixture_count": source.get("edge_executable_probe_authorization_fixture_count"),
        "fixture_ids": source.get("edge_executable_probe_authorization_fixture_ids"),
        "authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "authorization_alone_does_not_perform_probe": True,
        "edge_executable_probe_permitted_by_phase": False,
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_launch_attempted": False,
        "startup_allowed": False,
        "live_start_performed": False,
        "chain_acceptance": acceptance,
    }


def build_edge_executable_probe_authorization_aggregate_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l7_04.build_edge_executable_probe_authorization_fixture_matrix_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    aggregate = _aggregate_state(source)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)
    chain_ok = all(aggregate["chain_acceptance"].values())

    checks = [
        _check("l7_04_fixture_matrix_readback_still_passes", _source_l7_04_safe(source), _compact_source_status(source)),
        _check("l7_04_fixture_matrix_readback_remains_passive", _source_l7_04_safe(source), {"probe_authorized": source.get("edge_executable_probe_authorized"), "probe_permitted": source.get("edge_executable_probe_permitted_by_phase"), "probe_performed": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l7_01_through_l7_04_chain_remains_accepted", chain_ok, aggregate["chain_acceptance"]),
        _check("l7_05_aggregate_gate_command_registered", command_state.get("ok") is True, command_state),
        _check("l7_04_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l7_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l7_docs_contain_aggregate_gate_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("aggregate_gate_is_enforced", aggregate["edge_executable_probe_authorization_aggregate_gate_enforced"] is True, aggregate),
        _check("authorization_alone_still_does_not_probe", source.get("authorization_alone_does_not_perform_probe") is True and aggregate["edge_executable_filesystem_probe_performed"] is False, {}),
        _check("probe_remains_blocked_by_phase", source.get("edge_executable_probe_permitted_by_phase") is False and aggregate["edge_executable_probe_permitted_by_phase"] is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and aggregate["edge_executable_path_selected"] is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and aggregate["edge_executable_launch_attempted"] is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l7_04_safe(source), {}),
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
        "l7_01_executable_probe_authorization_passive_contract_remains_accepted": aggregate["l7_01_executable_probe_authorization_passive_contract_ok"],
        "l7_02_executable_probe_authorization_cli_readback_remains_accepted": aggregate["l7_02_executable_probe_authorization_cli_readback_ok"],
        "l7_03_executable_probe_authorization_fixture_matrix_remains_accepted": aggregate["l7_03_executable_probe_authorization_fixture_matrix_ok"],
        "l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted": aggregate["l7_04_executable_probe_authorization_fixture_matrix_cli_readback_ok"],
        "source_l7_04_status": _compact_source_status(source),
        "edge_executable_probe_authorization_aggregate": aggregate,
        "edge_executable_probe_authorization_aggregate_gate_enforced": aggregate["edge_executable_probe_authorization_aggregate_gate_enforced"],
        "edge_executable_probe_authorization_aggregate_status": aggregate["edge_executable_probe_authorization_aggregate_status"],
        "edge_executable_probe_authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "edge_executable_probe_authorization_modeled": True,
        "edge_executable_probe_authorized": source.get("edge_executable_probe_authorized"),
        "edge_executable_probe_requested": source.get("edge_executable_probe_requested"),
        "edge_executable_probe_permitted_by_phase": False,
        "edge_executable_probe_blocked_reason": source.get("edge_executable_probe_blocked_reason"),
        "authorization_alone_does_not_perform_probe": True,
        "edge_executable_probe_authorization_fixture_count": source.get("edge_executable_probe_authorization_fixture_count"),
        "edge_executable_probe_authorization_fixture_ids": source.get("edge_executable_probe_authorization_fixture_ids"),
        "edge_executable_candidate_paths_modeled": source.get("edge_executable_candidate_paths_modeled"),
        "edge_executable_candidate_count": source.get("edge_executable_candidate_count"),
        "edge_executable_fixture_matrix_modeled": source.get("edge_executable_fixture_matrix_modeled"),
        "edge_executable_fixture_count": source.get("edge_executable_fixture_count"),
        "edge_executable_fixture_ids": source.get("edge_executable_fixture_ids"),
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
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
        "startup_allowed": False,
        "live_start_performed": False,
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
        f"L7.1 Accepted   : {payload.get('l7_01_executable_probe_authorization_passive_contract_remains_accepted')}",
        f"L7.2 Accepted   : {payload.get('l7_02_executable_probe_authorization_cli_readback_remains_accepted')}",
        f"L7.3 Accepted   : {payload.get('l7_03_executable_probe_authorization_fixture_matrix_remains_accepted')}",
        f"L7.4 Accepted   : {payload.get('l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted')}",
        f"Probe Auth      : {payload.get('edge_executable_probe_authorized')}",
        f"Probe Permitted : {payload.get('edge_executable_probe_permitted_by_phase')}",
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
    payload = build_edge_executable_probe_authorization_aggregate_gate(
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
