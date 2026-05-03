from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.md")
TEST_PATH = Path("tests/test_l10_05_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_current.py")
VALIDATE_PATH = Path("scripts/patch_l10_05_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L10.5 passive Microsoft Edge executable filesystem-probe activation aggregate gate.

Aggregates the accepted L10.1 through L10.4 explicit-activation surfaces.
Activation readiness may be true when all three gates are present, but real
filesystem probing, path selection, and launch remain blocked by phase.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback as l10_04

PATCH = "L10.5"
PHASE = "L10"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L10.5 Microsoft Edge Executable Filesystem Probe Explicit Activation Aggregate Gate"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-fixture-matrix-readback"
NEXT_PATCH = "L10.6 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-explicit-activation-aggregate-gate-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
EXECUTABLE_PROBE_ACTIVATION_FLAG = "--activate-executable-filesystem-probe"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
EXPECTED_FIXTURE_IDS = {
    "no_activation_no_auth",
    "activation_only",
    "live_and_probe_auth_without_activation",
    "all_gates_dedicated_profile",
    "all_gates_default_profile",
    "all_gates_missing_profile",
}

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_explicit_activation_contract.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_explicit_activation_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_explicit_activation_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.md",
    "tests/test_l10_04_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback_current.py",
    "tests/test_l10_05_edge_executable_filesystem_probe_explicit_activation_aggregate_gate_current.py",
    "scripts/patch_l10_04_brief_validate.py",
    "scripts/patch_l10_05_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback.md": (
        "L10.4 Microsoft Edge executable filesystem probe explicit activation fixture matrix CLI/readback",
        SOURCE_COMMAND_NAME,
        "explicit activation fixture matrix CLI/readback enforced",
        "L10.5 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.md": (
        "L10.5 Microsoft Edge executable filesystem probe explicit activation aggregate gate",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L10.1 explicit activation contract remains accepted",
        "L10.2 explicit activation CLI/readback remains accepted",
        "L10.3 explicit activation fixture matrix remains accepted",
        "L10.4 explicit activation fixture matrix CLI/readback remains accepted",
        "explicit activation aggregate gate enforced",
        "explicit activation fixture matrix CLI/readback enforced",
        "explicit activation fixture matrix enforced",
        "explicit activation modeled only",
        EXECUTABLE_PROBE_ACTIVATION_FLAG,
        EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "activation readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L10.6 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback",
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
        "fixture_count": source.get("edge_executable_filesystem_probe_activation_fixture_count"),
        "activation_requested": source.get("activation_requested"),
        "all_three_gates": source.get("filesystem_probe_activation_all_three_gates_present"),
        "activation_ready": source.get("filesystem_probe_activation_ready"),
        "activation_exec": source.get("filesystem_probe_activation_execution_allowed"),
        "fs_probe": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
    }


def _source_l10_04_safe(source: Mapping[str, Any], *, expected_ready: bool) -> bool:
    fixture_ids = set(source.get("edge_executable_filesystem_probe_activation_fixture_ids", []))
    return (
        source.get("patch") == "L10.4"
        and source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and source.get("l10_03_explicit_activation_fixture_matrix_remains_accepted") is True
        and source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback_enforced") is True
        and source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_enforced") is True
        and source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_modeled") is True
        and source.get("edge_executable_filesystem_probe_activation_fixture_count") == 6
        and fixture_ids == EXPECTED_FIXTURE_IDS
        and source.get("edge_executable_filesystem_probe_explicit_activation_cli_readback_enforced") is True
        and source.get("edge_executable_filesystem_probe_explicit_activation_contract_enforced") is True
        and source.get("filesystem_probe_activation_ready") is expected_ready
        and source.get("filesystem_probe_activation_execution_allowed") is False
        and source.get("fixture_activation_execution_allowed") is False
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
        and "source_l10_04_summary" not in source
        and "source_l10_03_summary" not in source
    )


def _aggregate_state(source: Mapping[str, Any]) -> dict[str, Any]:
    chain_acceptance = {
        "l10_01": source.get("edge_executable_filesystem_probe_explicit_activation_contract_enforced") is True,
        "l10_02": source.get("edge_executable_filesystem_probe_explicit_activation_cli_readback_enforced") is True,
        "l10_03": source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_enforced") is True,
        "l10_04": source.get("ok") is True and source.get("status") == STATUS_PASS,
    }
    return {
        "edge_executable_filesystem_probe_explicit_activation_aggregate_gate_enforced": True,
        "edge_executable_filesystem_probe_explicit_activation_aggregate_status": "MODELED_ONLY_BLOCKED_BY_PHASE",
        "edge_executable_filesystem_probe_explicit_activation_aggregate_reason": "L10.5 aggregates L10.1-L10.4 while real filesystem probing remains reserved for a later accepted phase.",
        "l10_01_explicit_activation_contract_ok": chain_acceptance["l10_01"],
        "l10_02_explicit_activation_cli_readback_ok": chain_acceptance["l10_02"],
        "l10_03_explicit_activation_fixture_matrix_ok": chain_acceptance["l10_03"],
        "l10_04_explicit_activation_fixture_matrix_cli_readback_ok": chain_acceptance["l10_04"],
        "chain_acceptance": chain_acceptance,
        "fixture_count": source.get("edge_executable_filesystem_probe_activation_fixture_count"),
        "fixture_ids": source.get("edge_executable_filesystem_probe_activation_fixture_ids"),
        "activation_requested": source.get("activation_requested"),
        "all_three_gates_present": source.get("filesystem_probe_activation_all_three_gates_present"),
        "activation_ready": source.get("filesystem_probe_activation_ready"),
        "activation_execution_allowed": False,
        "filesystem_probe_performed": False,
        "path_selected": False,
        "launch_attempted": False,
    }


def build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
    activate_executable_filesystem_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    expected_ready = bool(allow_live_start and allow_executable_probe and activate_executable_filesystem_probe)
    source = l10_04.build_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
    )
    source_safe = _source_l10_04_safe(source, expected_ready=expected_ready)
    aggregate = _aggregate_state(source)
    chain_ok = all(aggregate["chain_acceptance"].values())
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l10_04_activation_fixture_matrix_readback_still_passes", source_safe, _compact_source_status(source)),
        _check("l10_04_activation_fixture_matrix_readback_remains_passive", source_safe, {"activation_ready": source.get("filesystem_probe_activation_ready"), "activation_exec": source.get("filesystem_probe_activation_execution_allowed"), "fs_probe": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l10_01_through_l10_04_chain_remains_accepted", chain_ok, aggregate["chain_acceptance"]),
        _check("l10_05_activation_aggregate_gate_command_registered", command_state.get("ok") is True, command_state),
        _check("l10_04_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l10_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l10_docs_contain_activation_aggregate_gate_boundary", doc_state.get("ok") is True, doc_state),
        _check("activation_aggregate_gate_is_enforced", aggregate["edge_executable_filesystem_probe_explicit_activation_aggregate_gate_enforced"] is True, aggregate),
        _check("activation_fixture_ids_are_stable", set(source.get("edge_executable_filesystem_probe_activation_fixture_ids", [])) == EXPECTED_FIXTURE_IDS, {"fixture_ids": source.get("edge_executable_filesystem_probe_activation_fixture_ids")}),
        _check("activation_ready_state_matches_three_gates", source.get("filesystem_probe_activation_ready") is expected_ready, _compact_source_status(source)),
        _check("activation_execution_remains_blocked_by_phase", source.get("filesystem_probe_activation_execution_allowed") is False and aggregate["activation_execution_allowed"] is False, {}),
        _check("filesystem_probe_is_not_performed", source.get("edge_executable_filesystem_probe_performed") is False and aggregate["filesystem_probe_performed"] is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and aggregate["path_selected"] is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and aggregate["launch_attempted"] is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
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
        "l10_explicit_activation_chain_accepted": chain_ok,
        "l10_01_explicit_activation_contract_remains_accepted": aggregate["l10_01_explicit_activation_contract_ok"],
        "l10_02_explicit_activation_cli_readback_remains_accepted": aggregate["l10_02_explicit_activation_cli_readback_ok"],
        "l10_03_explicit_activation_fixture_matrix_remains_accepted": aggregate["l10_03_explicit_activation_fixture_matrix_ok"],
        "l10_04_explicit_activation_fixture_matrix_cli_readback_remains_accepted": aggregate["l10_04_explicit_activation_fixture_matrix_cli_readback_ok"],
        "source_l10_04_status": _compact_source_status(source),
        "edge_executable_filesystem_probe_explicit_activation_aggregate": aggregate,
        "edge_executable_filesystem_probe_explicit_activation_aggregate_gate_enforced": aggregate["edge_executable_filesystem_probe_explicit_activation_aggregate_gate_enforced"],
        "edge_executable_filesystem_probe_explicit_activation_aggregate_status": aggregate["edge_executable_filesystem_probe_explicit_activation_aggregate_status"],
        "edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback_enforced": source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback_enforced"),
        "edge_executable_filesystem_probe_explicit_activation_fixture_matrix_enforced": source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_enforced"),
        "edge_executable_filesystem_probe_explicit_activation_fixture_matrix_modeled": source.get("edge_executable_filesystem_probe_explicit_activation_fixture_matrix_modeled"),
        "edge_executable_filesystem_probe_activation_fixture_count": source.get("edge_executable_filesystem_probe_activation_fixture_count"),
        "edge_executable_filesystem_probe_activation_fixture_ids": source.get("edge_executable_filesystem_probe_activation_fixture_ids"),
        "edge_executable_filesystem_probe_activation_fixture_matrix": source.get("edge_executable_filesystem_probe_activation_fixture_matrix"),
        "edge_executable_filesystem_probe_explicit_activation_cli_readback_enforced": source.get("edge_executable_filesystem_probe_explicit_activation_cli_readback_enforced"),
        "edge_executable_filesystem_probe_explicit_activation_contract_enforced": source.get("edge_executable_filesystem_probe_explicit_activation_contract_enforced"),
        "edge_executable_filesystem_probe_explicit_activation_modeled": source.get("edge_executable_filesystem_probe_explicit_activation_modeled"),
        "edge_executable_filesystem_probe_activation_flag": EXECUTABLE_PROBE_ACTIVATION_FLAG,
        "edge_executable_probe_authorization_flag": EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "activation_requested": source.get("activation_requested"),
        "live_start_authorization_present": source.get("live_start_authorization_present"),
        "executable_probe_authorization_present": source.get("executable_probe_authorization_present"),
        "filesystem_probe_activation_all_three_gates_present": source.get("filesystem_probe_activation_all_three_gates_present"),
        "filesystem_probe_activation_ready": source.get("filesystem_probe_activation_ready"),
        "filesystem_probe_activation_execution_allowed": False,
        "fixture_activation_execution_allowed": False,
        "fixture_filesystem_probe_performed": False,
        "fixture_path_selected": False,
        "fixture_executable_launch_attempted": False,
        "activation_alone_does_not_probe": True,
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
        f"L10 Chain OK    : {payload.get('l10_explicit_activation_chain_accepted')}",
        f"Fixture Count   : {payload.get('edge_executable_filesystem_probe_activation_fixture_count')}",
        f"All Gates       : {payload.get('filesystem_probe_activation_all_three_gates_present')}",
        f"Activation Ready: {payload.get('filesystem_probe_activation_ready')}",
        f"Activation Exec : {payload.get('filesystem_probe_activation_execution_allowed')}",
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
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)
    payload = build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(
        args.repo_root,
        allow_live_start=args.allow_live_start,
        profile_dir=args.profile_dir,
        allow_executable_probe=args.allow_executable_probe,
        activate_executable_filesystem_probe=args.activate_executable_filesystem_probe,
    )
    if args.json:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    else:
        print(render_text(payload), end="")
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
'''

DOC_CONTENT = r'''# L10.5 Microsoft Edge executable filesystem probe explicit activation aggregate gate

L10.5 adds a passive aggregate gate for the accepted Microsoft Edge executable filesystem-probe explicit-activation stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-activation-fixture-matrix-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L10.1 explicit activation contract remains accepted.
- L10.2 explicit activation CLI/readback remains accepted.
- L10.3 explicit activation fixture matrix remains accepted.
- L10.4 explicit activation fixture matrix CLI/readback remains accepted.
- explicit activation aggregate gate enforced.
- explicit activation fixture matrix CLI/readback enforced.
- explicit activation fixture matrix enforced.
- explicit activation CLI/readback enforced.
- explicit activation contract enforced.
- explicit activation modeled only.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- activation readiness can be true while filesystem probe execution remains blocked.
- filesystem probe not performed.
- executable path not selected.
- executable launch not attempted.
- no Selenium import.
- no browser start.
- no Edge process start.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L10.6 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate as aggregate

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-fixture-matrix-readback"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l10_05_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
EXPECTED_IDS = {
    "no_activation_no_auth",
    "activation_only",
    "live_and_probe_auth_without_activation",
    "all_gates_dedicated_profile",
    "all_gates_default_profile",
    "all_gates_missing_profile",
}


def _assert_passive(payload: dict) -> None:
    assert payload["filesystem_probe_activation_execution_allowed"] is False
    assert payload["fixture_activation_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["fixture_filesystem_probe_performed"] is False
    assert payload["fixture_path_selected"] is False
    assert payload["fixture_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["selenium_imported_by_readback"] is False
    assert "source_l10_05_summary" not in payload
    assert "source_l10_04_summary" not in payload


def test_l10_05_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l10_05_activation_aggregate_not_ready_without_all_gates() -> None:
    for kwargs in [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False),
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=False),
    ]:
        payload = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(PROJECT_ROOT, **kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L10.5"
        assert payload["l10_explicit_activation_chain_accepted"] is True
        assert payload["l10_04_explicit_activation_fixture_matrix_cli_readback_remains_accepted"] is True
        assert set(payload["edge_executable_filesystem_probe_activation_fixture_ids"]) == EXPECTED_IDS
        assert payload["filesystem_probe_activation_ready"] is False
        _assert_passive(payload)


def test_l10_05_all_gates_ready_but_execution_still_blocked() -> None:
    payload = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l10_01_explicit_activation_contract_remains_accepted"] is True
    assert payload["l10_02_explicit_activation_cli_readback_remains_accepted"] is True
    assert payload["l10_03_explicit_activation_fixture_matrix_remains_accepted"] is True
    assert payload["filesystem_probe_activation_all_three_gates_present"] is True
    assert payload["filesystem_probe_activation_ready"] is True
    assert payload["filesystem_probe_activation_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L10.6 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback"
    _assert_passive(payload)


def test_l10_05_default_and_missing_profile_cases_are_passive_when_all_gates_present() -> None:
    default_payload = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True)
    missing_payload = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True, activate_executable_filesystem_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l10_04_status"]["ok"] is True
    assert default_payload["filesystem_probe_activation_ready"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l10_04_status"]["ok"] is True
    assert missing_payload["filesystem_probe_activation_ready"] is True
    _assert_passive(missing_payload)


def test_l10_05_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(PROJECT_ROOT),
            "--allow-live-start",
            "--profile-dir",
            str(DEDICATED_PROFILE),
            "--allow-executable-probe",
            "--activate-executable-filesystem-probe",
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 80000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L10.5"
    assert payload["filesystem_probe_activation_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l10_05_doc_mentions_activation_aggregate_gate_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L10.5 Microsoft Edge executable filesystem probe explicit activation aggregate gate",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L10.1 explicit activation contract remains accepted",
        "L10.2 explicit activation CLI/readback remains accepted",
        "L10.3 explicit activation fixture matrix remains accepted",
        "L10.4 explicit activation fixture matrix CLI/readback remains accepted",
        "explicit activation aggregate gate enforced",
        "explicit activation fixture matrix CLI/readback enforced",
        "explicit activation modeled only",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "activation readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L10.6 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate CLI/readback",
    ]:
        assert phrase in text
'''

VALIDATE_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate as aggregate

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l10_05_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l10_explicit_activation_chain_accepted"] is True
    assert payload["edge_executable_filesystem_probe_explicit_activation_aggregate_gate_enforced"] is True
    assert payload["filesystem_probe_activation_execution_allowed"] is False
    assert payload["fixture_activation_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l10_04_summary" not in payload


def main() -> int:
    no_activation = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False)
    assert_passive(no_activation)
    assert no_activation["filesystem_probe_activation_ready"] is False
    print("PASS no_activation: patch=L10.5 chain=True aggregate=True activation_ready=False activation_exec=False fs_probe=False path_selected=False")

    activation_only = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=True)
    assert_passive(activation_only)
    assert activation_only["filesystem_probe_activation_ready"] is False
    print("PASS activation_only: chain=True aggregate=True activation_ready=False activation_exec=False fs_probe=False path_selected=False")

    partial = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(ROOT, allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=False)
    assert_passive(partial)
    assert partial["filesystem_probe_activation_ready"] is False
    print("PASS live_and_probe_auth_without_activation: chain=True aggregate=True activation_ready=False activation_exec=False fs_probe=False path_selected=False")

    for name, profile in [("all_gates_dedicated", DEDICATED), ("all_gates_default", DEFAULT), ("all_gates_missing_profile", None)]:
        payload = aggregate.build_edge_executable_filesystem_probe_explicit_activation_aggregate_gate(
            ROOT,
            allow_live_start=True,
            profile_dir=profile,
            allow_executable_probe=True,
            activate_executable_filesystem_probe=True,
        )
        assert_passive(payload)
        assert payload["filesystem_probe_activation_ready"] is True
        print("PASS {0}: patch=L10.5 source=L10.4 fixtures=6 activation_ready=True activation_exec=False fs_probe=False path_selected=False".format(name))

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "patchops.cli",
            "llm-browser",
            COMMAND,
            "--repo-root",
            str(ROOT),
            "--allow-live-start",
            "--profile-dir",
            str(DEDICATED),
            "--allow-executable-probe",
            "--activate-executable-filesystem-probe",
            "--json",
            "--compact",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    payload = json.loads(completed.stdout)
    assert len(completed.stdout) < 80000
    assert_passive(payload)
    print("PASS main_cli: compact JSON parsed quickly; activation aggregate gate stayed passive")
    print("PASS L10.5 brief validation: activation aggregate gate accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L10.5 START
# Passive Microsoft Edge executable filesystem probe explicit activation aggregate gate.
import sys as _patchops_l10_05_sys

_PATCHOPS_L10_05_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-activation-aggregate-gate"

try:
    _PATCHOPS_L10_05_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L10_05_PREV_BUILD_PARSER = None

if _PATCHOPS_L10_05_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L10_05_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L10_05_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L10_05_COMMAND, help="Read back passive Edge executable filesystem probe activation aggregate gate.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--allow-executable-probe", action="store_true")
                        p.add_argument("--activate-executable-filesystem-probe", action="store_true")
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_filesystem_probe_activation_aggregate_gate(args) -> int:
    from . import live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "allow_live_start", False):
        module_args.append("--allow-live-start")
    profile_dir = getattr(args, "profile_dir", None)
    if profile_dir:
        module_args.extend(["--profile-dir", str(profile_dir)])
    if getattr(args, "allow_executable_probe", False):
        module_args.append("--allow-executable-probe")
    if getattr(args, "activate_executable_filesystem_probe", False):
        module_args.append("--activate-executable-filesystem-probe")
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.main(module_args)

try:
    _PATCHOPS_L10_05_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L10_05_PREV_COMMAND_NAMES = None

if _PATCHOPS_L10_05_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L10_05_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L10_05_COMMAND,) if name not in names)

_PATCHOPS_L10_05_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l10_05_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L10_05_COMMAND:
        from . import live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate
        return live_adapter_edge_executable_filesystem_probe_explicit_activation_aggregate_gate.main(arg_list[1:])
    return _PATCHOPS_L10_05_PREV_MAIN(argv)
# PATCHOPS L10.5 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L10.5 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L10.5 command wrapper appended")
    else:
        print("L10.5 command wrapper already present")


def _append_l10_04_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_explicit_activation_fixture_matrix_cli_readback.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L10.5 Live adapter Microsoft Edge executable filesystem probe explicit activation aggregate gate"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the executable filesystem probe activation fixture matrix CLI/readback:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L10.4 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l10_04_doc_pointer()
    print("L10.5 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())