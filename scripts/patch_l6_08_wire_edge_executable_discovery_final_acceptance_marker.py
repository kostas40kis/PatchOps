from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_discovery_final_acceptance_marker.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_discovery_final_acceptance_marker.md")
TEST_PATH = Path("tests/test_l6_08_edge_executable_discovery_final_acceptance_marker_current.py")
VALIDATE_PATH = Path("scripts/patch_l6_08_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L6.8 passive Microsoft Edge executable-discovery final acceptance marker.

This marker closes the passive L6 executable-discovery slice by wrapping the
accepted L6.7 broad validation checkpoint. It preserves compact JSON readback
and does not expose full nested source summaries.

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

from patchops.llm_browser import live_adapter_edge_executable_discovery_broad_validation_checkpoint as l6_07

PATCH = "L6.8"
PHASE = "L6"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L6.8 Microsoft Edge Executable Discovery Final Acceptance Marker"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-discovery-broad-validation-checkpoint"
NEXT_PATCH = "L7.1 Live adapter Microsoft Edge executable probe authorization passive contract"
SIDE_EFFECT_BOUNDARY = "edge-executable-discovery-final-acceptance-marker-only"
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
    "patchops/llm_browser/live_adapter_edge_executable_discovery_final_acceptance_marker.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_discovery_broad_validation_checkpoint.md",
    "docs/llm_browser_live_adapter_edge_executable_discovery_final_acceptance_marker.md",
    "tests/test_l6_07_edge_executable_discovery_broad_validation_checkpoint_current.py",
    "tests/test_l6_08_edge_executable_discovery_final_acceptance_marker_current.py",
    "scripts/patch_l6_07_brief_validate.py",
    "scripts/patch_l6_08_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_discovery_broad_validation_checkpoint.md": (
        "L6.7 Microsoft Edge executable discovery broad validation checkpoint",
        SOURCE_COMMAND_NAME,
        "compact JSON readback",
        "nested source summaries remain pruned",
        "L6.8 Live adapter Microsoft Edge executable discovery final acceptance marker",
    ),
    "docs/llm_browser_live_adapter_edge_executable_discovery_final_acceptance_marker.md": (
        "L6.8 Microsoft Edge executable discovery final acceptance marker",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L6 executable discovery slice accepted",
        "L6.1 executable discovery passive contract remains accepted",
        "L6.2 executable discovery CLI/readback remains accepted",
        "L6.3 executable discovery fixture matrix remains accepted",
        "L6.4 executable discovery fixture matrix CLI/readback remains accepted",
        "L6.5 executable discovery aggregate gate remains accepted",
        "L6.6 executable discovery aggregate CLI/readback remains accepted",
        "L6.7 executable discovery broad validation checkpoint remains accepted",
        "nested source summaries remain pruned",
        "source_chain_status",
        "executable discovery final acceptance marker enforced",
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
        "L7.1 Live adapter Microsoft Edge executable probe authorization passive contract",
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


def _source_l6_07_safe(summary: Mapping[str, Any]) -> bool:
    return (
        summary.get("patch") == "L6.7"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l6_01_executable_discovery_passive_contract_remains_accepted") is True
        and summary.get("l6_02_executable_discovery_cli_readback_remains_accepted") is True
        and summary.get("l6_03_executable_discovery_fixture_matrix_remains_accepted") is True
        and summary.get("l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted") is True
        and summary.get("l6_05_executable_discovery_aggregate_gate_remains_accepted") is True
        and summary.get("l6_06_executable_discovery_aggregate_cli_readback_remains_accepted") is True
        and summary.get("compact_json_readback_enabled") is True
        and summary.get("nested_source_summaries_pruned") is True
        and summary.get("edge_executable_discovery_broad_validation_checkpoint_enforced") is True
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
        and "source_l6_07_summary" not in summary
        and "source_l6_06_summary" not in summary
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
        "l6_05": bool(source.get("source_l6_06_status", {}).get("source_l6_05_status", {}).get("ok") and source.get("source_l6_06_status", {}).get("source_l6_05_status", {}).get("status") == STATUS_PASS),
        "l6_06": bool(source.get("source_l6_06_status", {}).get("ok") and source.get("source_l6_06_status", {}).get("status") == STATUS_PASS),
        "l6_07": bool(source.get("ok") is True and source.get("status") == STATUS_PASS),
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
        "source_l6_06_status": source.get("source_l6_06_status", {}),
    }


def build_edge_executable_discovery_final_acceptance_marker(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l6_07.build_edge_executable_discovery_broad_validation_checkpoint(
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
        _check("l6_07_executable_discovery_broad_checkpoint_still_passes", _source_l6_07_safe(source), _compact_source_status(source)),
        _check("l6_07_executable_discovery_broad_checkpoint_remains_passive", _source_l6_07_safe(source), {"exe_probe": source.get("edge_executable_filesystem_probe_performed"), "browser_started": source.get("browser_started")}),
        _check("l6_01_through_l6_07_chain_remains_accepted", chain_ok, acceptance),
        _check("l6_08_final_marker_command_registered", command_state.get("ok") is True, command_state),
        _check("l6_07_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l6_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l6_docs_contain_final_marker_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("executable_discovery_final_marker_is_enforced", source.get("edge_executable_discovery_broad_validation_checkpoint_enforced") is True, {}),
        _check("executable_candidates_and_fixtures_remain_modeled", source.get("edge_executable_candidate_paths_modeled") is True and source.get("edge_executable_fixture_matrix_modeled") is True, {}),
        _check("edge_executable_filesystem_probe_stays_false", source.get("edge_executable_filesystem_probe_performed") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l6_07_safe(source), {}),
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
        "l6_executable_discovery_slice_accepted": chain_ok,
        "l6_01_executable_discovery_passive_contract_remains_accepted": acceptance["l6_01"],
        "l6_02_executable_discovery_cli_readback_remains_accepted": acceptance["l6_02"],
        "l6_03_executable_discovery_fixture_matrix_remains_accepted": acceptance["l6_03"],
        "l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted": acceptance["l6_04"],
        "l6_05_executable_discovery_aggregate_gate_remains_accepted": acceptance["l6_05"],
        "l6_06_executable_discovery_aggregate_cli_readback_remains_accepted": acceptance["l6_06"],
        "l6_07_executable_discovery_broad_validation_checkpoint_remains_accepted": acceptance["l6_07"],
        "source_l6_07_status": _compact_source_status(source),
        "source_chain_status": source.get("source_chain_status", {}),
        "edge_executable_discovery_final_acceptance_marker_enforced": True,
        "edge_executable_discovery_broad_validation_checkpoint_enforced": source.get("edge_executable_discovery_broad_validation_checkpoint_enforced"),
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
        f"Slice Accepted  : {payload.get('l6_executable_discovery_slice_accepted')}",
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
    payload = build_edge_executable_discovery_final_acceptance_marker(
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
'''

DOC_CONTENT = r'''# L6.8 Microsoft Edge executable discovery final acceptance marker

L6.8 is the passive final acceptance marker for the Microsoft Edge executable-discovery slice.

Command:

`browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker`

Source command:

`browser-start-supervised-launch-edge-executable-discovery-broad-validation-checkpoint`

This patch keeps brief validation output and compact JSON readback. Nested source summaries remain pruned and exposed only as compact `source_chain_status`.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L6 executable discovery slice accepted.
- L6.1 executable discovery passive contract remains accepted.
- L6.2 executable discovery CLI/readback remains accepted.
- L6.3 executable discovery fixture matrix remains accepted.
- L6.4 executable discovery fixture matrix CLI/readback remains accepted.
- L6.5 executable discovery aggregate gate remains accepted.
- L6.6 executable discovery aggregate CLI/readback remains accepted.
- L6.7 executable discovery broad validation checkpoint remains accepted.
- nested source summaries remain pruned.
- source_chain_status is retained as the compact source-chain proof.
- executable discovery final acceptance marker enforced.
- Edge executable candidate paths remain modeled.
- fixture matrix remains modeled.
- `msedge.exe` candidates remain listed for future discovery logic.
- executable filesystem probe not performed.
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

`L7.1 Live adapter Microsoft Edge executable probe authorization passive contract`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_discovery_final_acceptance_marker as marker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-discovery-broad-validation-checkpoint"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_08_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def _assert_passive(payload: dict) -> None:
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["edge_executable_fixture_filesystem_probe_performed"] is False
    assert payload["edge_executable_fixture_path_selected"] is False
    assert payload["edge_executable_fixture_launch_attempted"] is False
    assert payload["filesystem_writes_performed"] == []
    assert payload["adapter_filesystem_writes_performed"] == []
    assert payload["side_effects_performed"] == []
    assert payload["click_download_performed"] is False
    assert payload["download_performed"] is False
    assert payload["paste_performed"] is False
    assert payload["send_or_submit_performed"] is False
    assert payload["package_run_performed_by_adapter"] is False
    assert payload["git_commit_executed"] is False
    assert payload["git_push_executed"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert "source_l6_08_summary" not in payload
    assert "source_l6_07_summary" not in payload
    assert "source_l6_06_summary" not in payload


def test_l6_08_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l6_08_final_marker_dedicated_profile_passes_passively_and_compactly() -> None:
    payload = marker.build_edge_executable_discovery_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L6.8"
    assert payload["phase"] == "L6"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l6_executable_discovery_slice_accepted"] is True
    assert payload["l6_01_executable_discovery_passive_contract_remains_accepted"] is True
    assert payload["l6_02_executable_discovery_cli_readback_remains_accepted"] is True
    assert payload["l6_03_executable_discovery_fixture_matrix_remains_accepted"] is True
    assert payload["l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["l6_05_executable_discovery_aggregate_gate_remains_accepted"] is True
    assert payload["l6_06_executable_discovery_aggregate_cli_readback_remains_accepted"] is True
    assert payload["l6_07_executable_discovery_broad_validation_checkpoint_remains_accepted"] is True
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    assert payload["edge_executable_discovery_final_acceptance_marker_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_fixture_matrix_modeled"] is True
    assert payload["next_patch"] == "L7.1 Live adapter Microsoft Edge executable probe authorization passive contract"
    assert payload["source_l6_07_status"]["patch"] == "L6.7"
    assert payload["source_l6_07_status"]["ok"] is True
    assert "source_chain_status" in payload
    _assert_passive(payload)


def test_l6_08_default_and_missing_profile_cases_are_passive() -> None:
    default_payload = marker.build_edge_executable_discovery_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEFAULT_PROFILE,
    )
    missing_payload = marker.build_edge_executable_discovery_final_acceptance_marker(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=None,
    )
    assert default_payload["ok"] is True
    assert default_payload["source_l6_07_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l6_07_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l6_08_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L6.8"
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    _assert_passive(payload)


def test_l6_08_doc_mentions_final_marker_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_discovery_final_acceptance_marker.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L6.8 Microsoft Edge executable discovery final acceptance marker",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L6 executable discovery slice accepted",
        "L6.1 executable discovery passive contract remains accepted",
        "L6.2 executable discovery CLI/readback remains accepted",
        "L6.3 executable discovery fixture matrix remains accepted",
        "L6.4 executable discovery fixture matrix CLI/readback remains accepted",
        "L6.5 executable discovery aggregate gate remains accepted",
        "L6.6 executable discovery aggregate CLI/readback remains accepted",
        "L6.7 executable discovery broad validation checkpoint remains accepted",
        "nested source summaries remain pruned",
        "source_chain_status",
        "executable discovery final acceptance marker enforced",
        "Edge executable candidate paths remain modeled",
        "fixture matrix remains modeled",
        "msedge.exe",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L7.1 Live adapter Microsoft Edge executable probe authorization passive contract",
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

from patchops.llm_browser import live_adapter_edge_executable_discovery_final_acceptance_marker as marker

COMMAND = "browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l6_08_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l6_executable_discovery_slice_accepted"] is True
    assert payload["l6_01_executable_discovery_passive_contract_remains_accepted"] is True
    assert payload["l6_02_executable_discovery_cli_readback_remains_accepted"] is True
    assert payload["l6_03_executable_discovery_fixture_matrix_remains_accepted"] is True
    assert payload["l6_04_executable_discovery_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["l6_05_executable_discovery_aggregate_gate_remains_accepted"] is True
    assert payload["l6_06_executable_discovery_aggregate_cli_readback_remains_accepted"] is True
    assert payload["l6_07_executable_discovery_broad_validation_checkpoint_remains_accepted"] is True
    assert payload["compact_json_readback_enabled"] is True
    assert payload["nested_source_summaries_pruned"] is True
    assert payload["edge_executable_discovery_final_acceptance_marker_enforced"] is True
    assert payload["edge_executable_candidate_paths_modeled"] is True
    assert payload["edge_executable_fixture_matrix_modeled"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l6_07_summary" not in payload
    assert "source_l6_06_summary" not in payload


def main() -> int:
    cases = [
        ("no_auth_dedicated", False, DEDICATED),
        ("auth_dedicated", True, DEDICATED),
        ("auth_default", True, DEFAULT),
        ("missing_profile", True, None),
    ]
    for name, allow, profile in cases:
        payload = marker.build_edge_executable_discovery_final_acceptance_marker(
            ROOT,
            allow_live_start=allow,
            profile_dir=profile,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} slice_accepted={2} compact_json={3} exe_probe={4}".format(
                name,
                payload["patch"],
                payload["l6_executable_discovery_slice_accepted"],
                payload["compact_json_readback_enabled"],
                payload["edge_executable_filesystem_probe_performed"],
            )
        )

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
    print("PASS main_cli: compact JSON parsed quickly; nested source summaries remain pruned")
    print("PASS L6.8 brief validation: executable discovery final marker accepted with no executable probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L6.8 START
# Passive Microsoft Edge executable discovery final acceptance marker.
import sys as _patchops_l6_08_sys

_PATCHOPS_L6_08_COMMAND = "browser-start-supervised-launch-edge-executable-discovery-final-acceptance-marker"

try:
    _PATCHOPS_L6_08_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L6_08_PREV_BUILD_PARSER = None

if _PATCHOPS_L6_08_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L6_08_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L6_08_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L6_08_COMMAND, help="Read back passive Edge executable discovery final acceptance marker.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_discovery_final_acceptance_marker(args) -> int:
    from . import live_adapter_edge_executable_discovery_final_acceptance_marker
    module_args = []
    repo_root = getattr(args, "repo_root", None)
    if repo_root:
        module_args.extend(["--repo-root", str(repo_root)])
    if getattr(args, "allow_live_start", False):
        module_args.append("--allow-live-start")
    profile_dir = getattr(args, "profile_dir", None)
    if profile_dir:
        module_args.extend(["--profile-dir", str(profile_dir)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_discovery_final_acceptance_marker.main(module_args)

try:
    _PATCHOPS_L6_08_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L6_08_PREV_COMMAND_NAMES = None

if _PATCHOPS_L6_08_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L6_08_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L6_08_COMMAND,) if name not in names)

_PATCHOPS_L6_08_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l6_08_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L6_08_COMMAND:
        from . import live_adapter_edge_executable_discovery_final_acceptance_marker
        return live_adapter_edge_executable_discovery_final_acceptance_marker.main(arg_list[1:])
    return _PATCHOPS_L6_08_PREV_MAIN(argv)
# PATCHOPS L6.8 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L6.8 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L6.8 command wrapper appended")
    else:
        print("L6.8 command wrapper already present")


def _append_l6_07_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_discovery_broad_validation_checkpoint.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L6.8 Live adapter Microsoft Edge executable discovery final acceptance marker"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the executable discovery broad validation checkpoint:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L6.7 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l6_07_doc_pointer()
    print("L6.8 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())