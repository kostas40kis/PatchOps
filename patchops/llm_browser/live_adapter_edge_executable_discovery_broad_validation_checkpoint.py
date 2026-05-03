"""L6.7 passive Microsoft Edge executable-discovery broad validation checkpoint.

This checkpoint wraps the accepted L6.6 aggregate-gate CLI/readback surface and
keeps the compact JSON pattern introduced by L6.5a. It intentionally exposes
compact source-chain status instead of full nested summaries.

No filesystem probe, executable selection, Selenium import, browser start, Edge
process, driver/session creation, profile creation, click/download, paste/send,
package-run, commit, or push is performed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_discovery_aggregate_gate_cli_readback as l6_06

PATCH = "L6.7"
PHASE = "L6"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L6.7 Microsoft Edge Executable Discovery Broad Validation Checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-broad-validation-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-aggregate-readback"
NEXT_PATCH = "L6.8 Live adapter Microsoft Edge executable discovery final acceptance marker"
SIDE_EFFECT_BOUNDARY = "edge-executable-discovery-broad-validation-checkpoint-only"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_discovery_passive_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_aggregate_gate.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_discovery_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_discovery_aggregate_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_discovery_broad_validation_checkpoint.md",
    "tests/test_l6_06_edge_executable_discovery_aggregate_gate_cli_readback_current.py",
    "tests/test_l6_07_edge_executable_discovery_broad_validation_checkpoint_current.py",
    "scripts/patch_l6_06_brief_validate.py",
    "scripts/patch_l6_07_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_discovery_aggregate_gate_cli_readback.md": (
        "L6.6 Microsoft Edge executable discovery aggregate gate CLI/readback",
        SOURCE_COMMAND_NAME,
        "compact JSON readback",
        "nested source summaries remain pruned",
        "L6.7 Live adapter Microsoft Edge executable discovery broad validation checkpoint",
    ),
    "docs/llm_browser_live_adapter_edge_executable_discovery_broad_validation_checkpoint.md": (
        "L6.7 Microsoft Edge executable discovery broad validation checkpoint",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L6.1 executable discovery passive contract remains accepted",
        "L6.2 executable discovery CLI/readback remains accepted",
        "L6.3 executable discovery fixture matrix remains accepted",
        "L6.4 executable discovery fixture matrix CLI/readback remains accepted",
        "L6.5 executable discovery aggregate gate remains accepted",
        "L6.6 executable discovery aggregate CLI/readback remains accepted",
        "nested source summaries remain pruned",
        "source_chain_status",
        "executable discovery broad validation checkpoint enforced",
        "Edge executable candidate paths remain modeled",
        "fixture matrix remains modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L6.8 Live adapter Microsoft Edge executable discovery final acceptance marker",
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
    newly_loaded = after - before
    found = []
    for root in FORBIDDEN_OPTIONAL_ROOTS:
        if any(name == root or name.startswith(root + ".") for name in newly_loaded):
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


def _source_l6_06_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L6.6"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l6_05_executable_discovery_aggregate_gate_remains_accepted") is True
        and summary.get("compact_json_readback_enabled") is True
        and summary.get("nested_source_summaries_pruned") is True
        and summary.get("edge_executable_discovery_aggregate_readback_enforced") is True
        and summary.get("edge_executable_candidate_paths_modeled") is True
        and summary.get("edge_executable_fixture_matrix_modeled") is True
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("edge_executable_path_selected") is False
        and summary.get("edge_executable_selected_path") is None
        and summary.get("edge_executable_launch_attempted") is False
        and summary.get("edge_executable_fixture_filesystem_probe_performed") is False
        and summary.get("edge_executable_fixture_path_selected") is False
        and summary.get("edge_executable_fixture_launch_attempted") is False
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
        and "source_l6_06_summary" not in summary
        and "source_l6_05_summary" not in summary
    )


def _chain_acceptance(source: Mapping[str, Any]) -> dict[str, bool]:
    chain = source.get("source_chain_status", {})
    if not isinstance(chain, Mapping):
        chain = {}
    return {
        "l6_01": bool(chain.get("l6_01", {}).get("ok") and chain.get("l6_01", {}).get("status") == STATUS_PASS),
        "l6_02": bool(chain.get("l6_02", {}).get("ok") and chain.get("l6_02", {}).get("status") == STATUS_PASS),
        "l6_03": bool(chain.get("l6_03", {}).get("ok") and chain.get("l6_03", {}).get("status") == STATUS_PASS),
        "l6_04": bool(chain.get("l6_04", {}).get("ok") and chain.get("l6_04", {}).get("status") == STATUS_PASS),
        "l6_05": bool(source.get("source_l6_05_status", {}).get("ok") and source.get("source_l6_05_status", {}).get("status") == STATUS_PASS),
        "l6_06": bool(source.get("ok") is True and source.get("status") == STATUS_PASS),
    }


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
        "nested_source_summaries_pruned": source.get("nested_source_summaries_pruned") is True,
        "source_chain_status": source.get("source_chain_status", {}),
        "source_l6_05_status": source.get("source_l6_05_status", {}),
    }


def build_edge_executable_discovery_broad_validation_checkpoint(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l6_06.build_edge_executable_discovery_aggregate_gate_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
    )
    acceptance = _chain_acceptance(source)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)
    chain_ok = all(acceptance.values())

    checks = [
        _check("l6_06_executable_discovery_aggregate_readback_still_passes", _source_l6_06_safe(source), _compact_source_status(source)),
        _check("l6_06_executable_discovery_aggregate_readback_remains_passive", _source_l6_06_safe(source), {"exe_probe": source.get("edge_executable_filesystem_probe_performed"), "browser_started": source.get("browser_started")}),
        _check("l6_01_through_l6_06_chain_remains_accepted", chain_ok, acceptance),
        _check("l6_07_broad_checkpoint_command_registered", command_state.get("ok") is True, command_state),
        _check("l6_06_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l6_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l6_docs_contain_broad_checkpoint_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("executable_discovery_broad_checkpoint_is_enforced", source.get("edge_executable_discovery_aggregate_readback_enforced") is True, {}),
        _check("executable_candidates_and_fixtures_remain_modeled", source.get("edge_executable_candidate_paths_modeled") is True and source.get("edge_executable_fixture_matrix_modeled") is True, {}),
        _check("edge_executable_filesystem_probe_stays_false", source.get("edge_executable_filesystem_probe_performed") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l6_06_safe(source), {}),
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
        "l6_01_executable_discovery_passive_contract_remains_accepted": acceptance["l6_01"],
        "l6_02_executable_discovery_cli_readback_remains_accepted": acceptance["l6_02"],
        "l6_03_executable_discovery_fixture_matrix_remains_accepted": acceptance["l6_03"],
        "l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted": acceptance["l6_04"],
        "l6_05_executable_discovery_aggregate_gate_remains_accepted": acceptance["l6_05"],
        "l6_06_executable_discovery_aggregate_cli_readback_remains_accepted": acceptance["l6_06"],
        "source_l6_06_status": _compact_source_status(source),
        "source_chain_status": source.get("source_chain_status", {}),
        "edge_executable_discovery_broad_validation_checkpoint_enforced": True,
        "edge_executable_discovery_aggregate_readback_enforced": source.get("edge_executable_discovery_aggregate_readback_enforced"),
        "edge_executable_candidate_paths_modeled": source.get("edge_executable_candidate_paths_modeled"),
        "edge_executable_candidate_count": source.get("edge_executable_candidate_count"),
        "edge_executable_fixture_matrix_modeled": source.get("edge_executable_fixture_matrix_modeled"),
        "edge_executable_fixture_count": source.get("edge_executable_fixture_count"),
        "edge_executable_fixture_ids": source.get("edge_executable_fixture_ids"),
        "edge_executable_filesystem_probe_performed": False,
        "edge_executable_path_selected": False,
        "edge_executable_selected_path": None,
        "edge_executable_launch_attempted": False,
        "edge_executable_fixture_filesystem_probe_performed": False,
        "edge_executable_fixture_path_selected": False,
        "edge_executable_fixture_launch_attempted": False,
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
        f"L6.1 Accepted   : {payload.get('l6_01_executable_discovery_passive_contract_remains_accepted')}",
        f"L6.2 Accepted   : {payload.get('l6_02_executable_discovery_cli_readback_remains_accepted')}",
        f"L6.3 Accepted   : {payload.get('l6_03_executable_discovery_fixture_matrix_remains_accepted')}",
        f"L6.4 Accepted   : {payload.get('l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted')}",
        f"L6.5 Accepted   : {payload.get('l6_05_executable_discovery_aggregate_gate_remains_accepted')}",
        f"L6.6 Accepted   : {payload.get('l6_06_executable_discovery_aggregate_cli_readback_remains_accepted')}",
        f"Compact JSON    : {payload.get('compact_json_readback_enabled')}",
        f"Exe Probe       : {payload.get('edge_executable_filesystem_probe_performed')}",
        f"Exe Selected    : {payload.get('edge_executable_path_selected')}",
        f"Browser Started : {payload.get('browser_started')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_discovery_broad_validation_checkpoint(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
