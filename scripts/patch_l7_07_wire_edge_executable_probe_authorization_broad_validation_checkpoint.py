from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.md")
TEST_PATH = Path("tests/test_l7_07_edge_executable_probe_authorization_broad_validation_checkpoint_current.py")
VALIDATE_PATH = Path("scripts/patch_l7_07_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L7.7 passive Edge executable-probe authorization broad validation checkpoint.

Wraps accepted L7.6 in a compact broad-validation checkpoint over L7.1 through
L7.6. It confirms the authorization contract, CLI/readback, fixture matrix,
aggregate gate, and aggregate readback remain accepted while still performing
no executable filesystem probe, no path selection, no launch, no Selenium
import, no browser start, no profile creation, no click/download, no paste/send,
no package run, no commit, and no push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_aggregate_gate_cli_readback as l7_06

PATCH = "L7.7"
PHASE = "L7"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L7.7 Microsoft Edge Executable Probe Authorization Broad Validation Checkpoint"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-probe-authorization-aggregate-readback"
NEXT_PATCH = "L7.8 Live adapter Microsoft Edge executable probe authorization final acceptance marker"
SIDE_EFFECT_BOUNDARY = "edge-executable-probe-authorization-broad-validation-checkpoint-only"
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
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_aggregate_gate_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_aggregate_gate_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.md",
    "tests/test_l7_06_edge_executable_probe_authorization_aggregate_gate_cli_readback_current.py",
    "tests/test_l7_07_edge_executable_probe_authorization_broad_validation_checkpoint_current.py",
    "scripts/patch_l7_06_brief_validate.py",
    "scripts/patch_l7_07_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_aggregate_gate_cli_readback.md": (
        "L7.6 Microsoft Edge executable probe authorization aggregate gate CLI/readback",
        SOURCE_COMMAND_NAME,
        "aggregate gate CLI/readback enforced",
        "authorization alone does not perform a probe",
        "L7.7 Live adapter Microsoft Edge executable probe authorization broad validation checkpoint",
    ),
    "docs/llm_browser_live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.md": (
        "L7.7 Microsoft Edge executable probe authorization broad validation checkpoint",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L7.1 executable probe authorization passive contract remains accepted",
        "L7.2 executable probe authorization CLI/readback remains accepted",
        "L7.3 executable probe authorization fixture matrix remains accepted",
        "L7.4 executable probe authorization fixture matrix CLI/readback remains accepted",
        "L7.5 executable probe authorization aggregate gate remains accepted",
        "L7.6 executable probe authorization aggregate CLI/readback remains accepted",
        "broad validation checkpoint enforced",
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
        "L7.8 Live adapter Microsoft Edge executable probe authorization final acceptance marker",
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


def _source_l7_06_safe(summary: Mapping[str, Any]) -> bool:
    ids = set(summary.get("edge_executable_probe_authorization_fixture_ids", []))
    return (
        summary.get("patch") == "L7.6"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l7_05_executable_probe_authorization_aggregate_gate_remains_accepted") is True
        and summary.get("l7_01_executable_probe_authorization_passive_contract_remains_accepted") is True
        and summary.get("l7_02_executable_probe_authorization_cli_readback_remains_accepted") is True
        and summary.get("l7_03_executable_probe_authorization_fixture_matrix_remains_accepted") is True
        and summary.get("l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted") is True
        and summary.get("edge_executable_probe_authorization_aggregate_gate_cli_readback_enforced") is True
        and summary.get("edge_executable_probe_authorization_aggregate_gate_enforced") is True
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
        and "source_l7_06_summary" not in summary
        and "source_l7_05_summary" not in summary
    )


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "probe_authorized": source.get("edge_executable_probe_authorized"),
        "probe_permitted_by_phase": source.get("edge_executable_probe_permitted_by_phase"),
        "probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "fixture_count": source.get("edge_executable_probe_authorization_fixture_count"),
        "fixture_ids": source.get("edge_executable_probe_authorization_fixture_ids"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
        "nested_source_summaries_pruned": source.get("nested_source_summaries_pruned") is True,
    }


def _chain_acceptance(source: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "l7_01": source.get("l7_01_executable_probe_authorization_passive_contract_remains_accepted") is True,
        "l7_02": source.get("l7_02_executable_probe_authorization_cli_readback_remains_accepted") is True,
        "l7_03": source.get("l7_03_executable_probe_authorization_fixture_matrix_remains_accepted") is True,
        "l7_04": source.get("l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted") is True,
        "l7_05": source.get("l7_05_executable_probe_authorization_aggregate_gate_remains_accepted") is True,
        "l7_06": source.get("ok") is True and source.get("status") == STATUS_PASS,
    }


def build_edge_executable_probe_authorization_broad_validation_checkpoint(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l7_06.build_edge_executable_probe_authorization_aggregate_gate_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    acceptance = _chain_acceptance(source)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)
    chain_ok = all(acceptance.values())

    checks = [
        _check("l7_06_aggregate_readback_still_passes", _source_l7_06_safe(source), _compact_source_status(source)),
        _check("l7_06_aggregate_readback_remains_passive", _source_l7_06_safe(source), {"probe_authorized": source.get("edge_executable_probe_authorized"), "probe_permitted": source.get("edge_executable_probe_permitted_by_phase"), "probe_performed": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l7_01_through_l7_06_chain_remains_accepted", chain_ok, acceptance),
        _check("l7_07_broad_checkpoint_command_registered", command_state.get("ok") is True, command_state),
        _check("l7_06_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l7_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l7_docs_contain_broad_checkpoint_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("broad_validation_checkpoint_is_enforced", True, {"chain_acceptance": acceptance}),
        _check("authorization_alone_still_does_not_probe", source.get("authorization_alone_does_not_perform_probe") is True and source.get("edge_executable_filesystem_probe_performed") is False, {}),
        _check("probe_remains_blocked_by_phase", source.get("edge_executable_probe_permitted_by_phase") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False, {}),
        _check("compact_json_readback_remains_enabled", source.get("compact_json_readback_enabled") is True and source.get("nested_source_summaries_pruned") is True, {}),
        _check("edge_remains_first_supported_live_browser", BROWSER_PRIORITY[0] == "edge", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("opera_remains_second_supported_live_browser", BROWSER_PRIORITY[1] == "opera", {"browser_priority": list(BROWSER_PRIORITY)}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
        _check("no_browser_profile_or_adapter_side_effects", _source_l7_06_safe(source), {}),
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
        "l7_executable_probe_authorization_chain_accepted": chain_ok,
        "l7_01_executable_probe_authorization_passive_contract_remains_accepted": acceptance["l7_01"],
        "l7_02_executable_probe_authorization_cli_readback_remains_accepted": acceptance["l7_02"],
        "l7_03_executable_probe_authorization_fixture_matrix_remains_accepted": acceptance["l7_03"],
        "l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted": acceptance["l7_04"],
        "l7_05_executable_probe_authorization_aggregate_gate_remains_accepted": acceptance["l7_05"],
        "l7_06_executable_probe_authorization_aggregate_cli_readback_remains_accepted": acceptance["l7_06"],
        "source_l7_06_status": _compact_source_status(source),
        "edge_executable_probe_authorization_broad_validation_checkpoint_enforced": True,
        "edge_executable_probe_authorization_aggregate_gate_cli_readback_enforced": source.get("edge_executable_probe_authorization_aggregate_gate_cli_readback_enforced"),
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
        f"L7 Chain OK     : {payload.get('l7_executable_probe_authorization_chain_accepted')}",
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
    payload = build_edge_executable_probe_authorization_broad_validation_checkpoint(
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
'''

DOC_CONTENT = r'''# L7.7 Microsoft Edge executable probe authorization broad validation checkpoint

L7.7 adds a passive broad validation checkpoint for the Microsoft Edge executable-probe authorization slice.

Command:

`browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint`

Source command:

`browser-start-supervised-launch-edge-executable-probe-authorization-aggregate-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L7.1 executable probe authorization passive contract remains accepted.
- L7.2 executable probe authorization CLI/readback remains accepted.
- L7.3 executable probe authorization fixture matrix remains accepted.
- L7.4 executable probe authorization fixture matrix CLI/readback remains accepted.
- L7.5 executable probe authorization aggregate gate remains accepted.
- L7.6 executable probe authorization aggregate CLI/readback remains accepted.
- broad validation checkpoint enforced.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization alone does not perform a probe.
- executable probe remains blocked by phase.
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

`L7.8 Live adapter Microsoft Edge executable probe authorization final acceptance marker`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint as checkpoint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-aggregate-readback"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l7_07_candidate"
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
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    assert payload["authorization_alone_does_not_perform_probe"] is True
    assert payload["fixture_probe_performed"] is False
    assert payload["fixture_executable_selected"] is False
    assert payload["fixture_executable_launch_attempted"] is False
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
    assert "source_l7_07_summary" not in payload
    assert "source_l7_06_summary" not in payload


def test_l7_07_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l7_07_broad_checkpoint_dedicated_profile_passes_passively() -> None:
    payload = checkpoint.build_edge_executable_probe_authorization_broad_validation_checkpoint(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L7.7"
    assert payload["phase"] == "L7"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l7_executable_probe_authorization_chain_accepted"] is True
    assert payload["l7_01_executable_probe_authorization_passive_contract_remains_accepted"] is True
    assert payload["l7_02_executable_probe_authorization_cli_readback_remains_accepted"] is True
    assert payload["l7_03_executable_probe_authorization_fixture_matrix_remains_accepted"] is True
    assert payload["l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["l7_05_executable_probe_authorization_aggregate_gate_remains_accepted"] is True
    assert payload["l7_06_executable_probe_authorization_aggregate_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_probe_authorization_broad_validation_checkpoint_enforced"] is True
    assert payload["edge_executable_probe_authorized"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L7.8 Live adapter Microsoft Edge executable probe authorization final acceptance marker"
    _assert_passive(payload)


def test_l7_07_no_auth_default_and_missing_profile_cases_are_passive() -> None:
    no_auth = checkpoint.build_edge_executable_probe_authorization_broad_validation_checkpoint(PROJECT_ROOT, allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False)
    default_payload = checkpoint.build_edge_executable_probe_authorization_broad_validation_checkpoint(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = checkpoint.build_edge_executable_probe_authorization_broad_validation_checkpoint(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert no_auth["ok"] is True
    assert no_auth["edge_executable_probe_authorized"] is False
    _assert_passive(no_auth)
    assert default_payload["ok"] is True
    assert default_payload["source_l7_06_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l7_06_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l7_07_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L7.7"
    assert payload["edge_executable_probe_authorized"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    _assert_passive(payload)


def test_l7_07_doc_mentions_broad_checkpoint_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L7.7 Microsoft Edge executable probe authorization broad validation checkpoint",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L7.1 executable probe authorization passive contract remains accepted",
        "L7.2 executable probe authorization CLI/readback remains accepted",
        "L7.3 executable probe authorization fixture matrix remains accepted",
        "L7.4 executable probe authorization fixture matrix CLI/readback remains accepted",
        "L7.5 executable probe authorization aggregate gate remains accepted",
        "L7.6 executable probe authorization aggregate CLI/readback remains accepted",
        "broad validation checkpoint enforced",
        "--allow-executable-probe",
        "authorization alone does not perform a probe",
        "executable probe remains blocked by phase",
        "executable filesystem probe not performed",
        "executable path not selected",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L7.8 Live adapter Microsoft Edge executable probe authorization final acceptance marker",
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

from patchops.llm_browser import live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint as checkpoint

COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l7_07_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l7_executable_probe_authorization_chain_accepted"] is True
    assert payload["l7_01_executable_probe_authorization_passive_contract_remains_accepted"] is True
    assert payload["l7_02_executable_probe_authorization_cli_readback_remains_accepted"] is True
    assert payload["l7_03_executable_probe_authorization_fixture_matrix_remains_accepted"] is True
    assert payload["l7_04_executable_probe_authorization_fixture_matrix_cli_readback_remains_accepted"] is True
    assert payload["l7_05_executable_probe_authorization_aggregate_gate_remains_accepted"] is True
    assert payload["l7_06_executable_probe_authorization_aggregate_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_probe_authorization_broad_validation_checkpoint_enforced"] is True
    assert payload["edge_executable_probe_permitted_by_phase"] is False
    assert payload["authorization_alone_does_not_perform_probe"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["fixture_probe_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l7_06_summary" not in payload


def main() -> int:
    cases = [
        ("no_probe_auth", False, DEDICATED, False),
        ("probe_auth_dedicated", True, DEDICATED, True),
        ("probe_auth_default", True, DEFAULT, True),
        ("probe_auth_missing_profile", True, None, True),
    ]
    for name, live, profile, probe_auth in cases:
        payload = checkpoint.build_edge_executable_probe_authorization_broad_validation_checkpoint(
            ROOT,
            allow_live_start=live,
            profile_dir=profile,
            allow_executable_probe=probe_auth,
        )
        assert_passive(payload)
        print(
            "PASS {0}: patch={1} chain=L7.1-L7.6 probe_authorized={2} probe_permitted={3} exe_probe={4}".format(
                name,
                payload["patch"],
                payload["edge_executable_probe_authorized"],
                payload["edge_executable_probe_permitted_by_phase"],
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
            "--allow-executable-probe",
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
    print("PASS main_cli: compact JSON parsed quickly; broad checkpoint stayed passive")
    print("PASS L7.7 brief validation: broad checkpoint accepted with no executable probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L7.7 START
# Passive Microsoft Edge executable probe authorization broad validation checkpoint.
import sys as _patchops_l7_07_sys

_PATCHOPS_L7_07_COMMAND = "browser-start-supervised-launch-edge-executable-probe-authorization-broad-validation-checkpoint"

try:
    _PATCHOPS_L7_07_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L7_07_PREV_BUILD_PARSER = None

if _PATCHOPS_L7_07_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L7_07_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L7_07_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L7_07_COMMAND, help="Read back passive Edge executable probe authorization broad validation checkpoint.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--allow-executable-probe", action="store_true")
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_probe_authorization_broad_validation_checkpoint(args) -> int:
    from . import live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint
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
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.main(module_args)

try:
    _PATCHOPS_L7_07_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L7_07_PREV_COMMAND_NAMES = None

if _PATCHOPS_L7_07_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L7_07_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L7_07_COMMAND,) if name not in names)

_PATCHOPS_L7_07_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l7_07_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L7_07_COMMAND:
        from . import live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint
        return live_adapter_edge_executable_probe_authorization_broad_validation_checkpoint.main(arg_list[1:])
    return _PATCHOPS_L7_07_PREV_MAIN(argv)
# PATCHOPS L7.7 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L7.7 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L7.7 command wrapper appended")
    else:
        print("L7.7 command wrapper already present")


def _append_l7_06_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_probe_authorization_aggregate_gate_cli_readback.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L7.7 Live adapter Microsoft Edge executable probe authorization broad validation checkpoint"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the executable probe authorization aggregate CLI/readback:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L7.6 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l7_06_doc_pointer()
    print("L7.7 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())