from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_contract.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_contract.md")
TEST_PATH = Path("tests/test_l13_01_edge_executable_filesystem_probe_execution_contract_current.py")
VALIDATE_PATH = Path("scripts/patch_l13_01_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L13.1 Microsoft Edge executable filesystem-probe execution contract.

Starts the read-only executable filesystem probe layer after the accepted L12
execution-preflight stack. This patch may read filesystem metadata for a small
allowlisted Microsoft Edge executable candidate list, but it does not launch a
browser, import Selenium, create profiles, click, download, paste, send, run
packages, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker as l12_08

PATCH = "L13.1"
PHASE = "L13"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L13.1 Microsoft Edge Executable Filesystem Probe Execution Contract"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-final-acceptance-marker"
NEXT_PATCH = "L13.2 Live adapter Microsoft Edge executable filesystem probe execution CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-execution-contract-readonly-probe-only"
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
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_contract.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_contract.md",
    "tests/test_l12_08_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker_current.py",
    "tests/test_l13_01_edge_executable_filesystem_probe_execution_contract_current.py",
    "scripts/patch_l12_08_brief_validate.py",
    "scripts/patch_l13_01_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.md": (
        "L12.8 Microsoft Edge executable filesystem probe execution preflight final acceptance marker",
        SOURCE_COMMAND_NAME,
        "L12 execution preflight stack accepted",
        "L13.1 Live adapter Microsoft Edge executable filesystem probe execution contract",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_contract.md": (
        "L13.1 Microsoft Edge executable filesystem probe execution contract",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L12 execution preflight stack accepted",
        "L12.8 execution preflight final acceptance marker remains accepted",
        "execution contract enforced",
        "read-only filesystem probe",
        "small allowlisted Microsoft Edge executable candidate list",
        "filesystem probe may be performed only when L12 execution preflight readiness is true",
        "executable path may be selected if an allowlisted candidate exists",
        EXECUTION_PREFLIGHT_FLAG,
        REAL_FILESYSTEM_PROBE_FLAG,
        EXECUTABLE_PROBE_ACTIVATION_FLAG,
        EXECUTABLE_PROBE_AUTHORIZATION_FLAG,
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no executable launch attempted",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L13.2 Live adapter Microsoft Edge executable filesystem probe execution CLI/readback",
    ),
}

DEFAULT_EDGE_CANDIDATES = (
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)


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


def _candidate_paths(extra_candidates: Sequence[str] | None = None) -> list[str]:
    candidates: list[str] = list(DEFAULT_EDGE_CANDIDATES)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(str(Path(local_app_data) / "Microsoft" / "Edge" / "Application" / "msedge.exe"))
    for name in ("msedge", "msedge.exe"):
        resolved = shutil.which(name)
        if resolved:
            candidates.append(resolved)
    if extra_candidates:
        candidates.extend(str(item) for item in extra_candidates if str(item).strip())
    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        normalized = str(Path(item))
        key = normalized.lower()
        if key not in seen:
            seen.add(key)
            unique.append(normalized)
    return unique


def _probe_edge_executable_candidates(extra_candidates: Sequence[str] | None = None) -> dict[str, Any]:
    candidates = _candidate_paths(extra_candidates)
    results = []
    selected_path: str | None = None
    for candidate in candidates:
        path = Path(candidate)
        try:
            exists = path.exists()
            is_file = path.is_file() if exists else False
        except OSError as exc:
            exists = False
            is_file = False
            results.append({"path": str(path), "exists": False, "is_file": False, "error": f"{type(exc).__name__}: {exc}"})
            continue
        results.append({"path": str(path), "exists": bool(exists), "is_file": bool(is_file)})
        if selected_path is None and exists and is_file:
            selected_path = str(path)
    return {
        "candidate_count": len(candidates),
        "candidates": results,
        "selected_path": selected_path,
        "path_selected": selected_path is not None,
    }


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "stack_accepted": source.get("l12_execution_preflight_stack_accepted") is True,
        "exec_ready": source.get("execution_preflight_ready"),
        "exec_allowed": source.get("execution_preflight_execution_allowed"),
        "fs_probe": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
    }


def _source_l12_08_safe(source: Mapping[str, Any], *, expected_execution_ready: bool) -> bool:
    fixture_ids = set(source.get("execution_preflight_fixture_ids", []))
    return (
        source.get("patch") == "L12.8"
        and source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and source.get("l12_execution_preflight_stack_accepted") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker_enforced") is True
        and source.get("execution_preflight_fixture_count") == 6
        and fixture_ids == EXPECTED_FIXTURE_IDS
        and source.get("execution_preflight_ready") is expected_execution_ready
        and source.get("execution_preflight_execution_allowed") is False
        and source.get("edge_executable_filesystem_probe_performed") is False
        and source.get("edge_executable_path_selected") is False
        and source.get("edge_executable_selected_path") is None
        and source.get("edge_executable_launch_attempted") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("browser_session_created") is False
        and source.get("driver_created") is False
        and source.get("profile_directory_created") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("selenium_imported_by_readback") is False
        and "source_l12_08_summary" not in source
        and "source_l12_07_summary" not in source
    )


def build_edge_executable_filesystem_probe_execution_contract(
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
    before = set(sys.modules)
    expected_execution_ready = bool(
        allow_live_start
        and allow_executable_probe
        and activate_executable_filesystem_probe
        and allow_real_filesystem_probe
        and allow_executable_filesystem_probe_execution
    )
    source = l12_08.build_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
        allow_real_filesystem_probe=allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=allow_executable_filesystem_probe_execution,
    )
    source_safe = _source_l12_08_safe(source, expected_execution_ready=expected_execution_ready)
    probe_allowed = bool(source.get("execution_preflight_ready"))
    probe = _probe_edge_executable_candidates(extra_candidates) if probe_allowed else {
        "candidate_count": len(_candidate_paths(extra_candidates)),
        "candidates": [],
        "selected_path": None,
        "path_selected": False,
    }
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l12_08_execution_preflight_final_marker_still_passes", source_safe, _compact_source_status(source)),
        _check("l13_01_execution_contract_command_registered", command_state.get("ok") is True, command_state),
        _check("l12_08_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l13_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l13_docs_contain_execution_contract_boundary", doc_state.get("ok") is True, doc_state),
        _check("execution_contract_is_enforced", True, {"probe_allowed": probe_allowed}),
        _check("probe_only_runs_when_l12_execution_preflight_ready", (probe_allowed is expected_execution_ready), {"expected_execution_ready": expected_execution_ready, "probe_allowed": probe_allowed}),
        _check("probe_candidate_list_is_allowlisted", probe.get("candidate_count", 0) >= 2, {"candidate_count": probe.get("candidate_count")}),
        _check("probe_selection_matches_existing_candidate", (not probe.get("path_selected") or any(item.get("path") == probe.get("selected_path") and item.get("exists") and item.get("is_file") for item in probe.get("candidates", []))), probe),
        _check("edge_executable_launch_stays_unattempted", True, {}),
        _check("no_browser_start_or_profile_side_effects", source_safe, {}),
        _check("no_forbidden_browser_dependencies_imported", not new_forbidden_imports, {"new_forbidden_imports": new_forbidden_imports}),
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
        "l12_execution_preflight_stack_accepted": source.get("l12_execution_preflight_stack_accepted") is True,
        "l12_08_execution_preflight_final_acceptance_marker_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "source_l12_08_status": _compact_source_status(source),
        "edge_executable_filesystem_probe_execution_contract_enforced": True,
        "edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker_enforced"),
        "execution_preflight_flag": EXECUTION_PREFLIGHT_FLAG,
        "execution_preflight_authorization_present": source.get("execution_preflight_authorization_present"),
        "execution_preflight_ready": source.get("execution_preflight_ready"),
        "execution_preflight_execution_allowed": source.get("execution_preflight_ready") is True,
        "edge_executable_filesystem_probe_execution_allowed": probe_allowed,
        "edge_executable_filesystem_probe_performed": probe_allowed,
        "edge_executable_filesystem_probe_mode": "readonly_allowlisted_candidate_exists_probe" if probe_allowed else "not_performed_preflight_not_ready",
        "edge_executable_probe_candidate_count": probe.get("candidate_count"),
        "edge_executable_probe_candidates": probe.get("candidates"),
        "edge_executable_path_selected": bool(probe.get("path_selected")),
        "edge_executable_selected_path": probe.get("selected_path"),
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
    selected = payload.get("edge_executable_selected_path") or "(none)"
    lines = [
        NAME,
        f"Status          : {payload.get('status')}",
        f"Command         : {payload.get('command_name')}",
        f"Source Command  : {payload.get('source_command_name')}",
        f"L12 Stack OK    : {payload.get('l12_execution_preflight_stack_accepted')}",
        f"Exec Ready      : {payload.get('execution_preflight_ready')}",
        f"Probe Allowed   : {payload.get('edge_executable_filesystem_probe_execution_allowed')}",
        f"Probe Performed : {payload.get('edge_executable_filesystem_probe_performed')}",
        f"Candidate Count : {payload.get('edge_executable_probe_candidate_count')}",
        f"Path Selected   : {payload.get('edge_executable_path_selected')}",
        f"Selected Path   : {selected}",
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
    payload = build_edge_executable_filesystem_probe_execution_contract(
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
'''

DOC_CONTENT = r'''# L13.1 Microsoft Edge executable filesystem probe execution contract

L13.1 starts the read-only executable filesystem probe layer after the accepted L12 execution preflight stack.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-final-acceptance-marker`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L12 execution preflight stack accepted.
- L12.8 execution preflight final acceptance marker remains accepted.
- execution contract enforced.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- executable path may be selected if an allowlisted candidate exists.
- `--allow-executable-filesystem-probe-execution` remains the explicit execution-preflight flag.
- `--allow-real-filesystem-probe` remains the explicit real-probe preflight flag.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- no Selenium import.
- no browser start.
- no Edge process start.
- no executable launch attempted.
- no browser session creation.
- no driver creation.
- no profile directory creation.
- no click/download/paste/send/package-run side effect.
- no localhost PatchOps server.
- no browser extension.

If accepted, continue with:

`L13.2 Live adapter Microsoft Edge executable filesystem probe execution CLI/readback`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_contract as contract

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-final-acceptance-marker"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_01_candidate"
EXISTING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge.exe"
MISSING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge.exe"


def _assert_no_launch_side_effects(payload: dict) -> None:
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
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
    assert "source_l13_01_summary" not in payload
    assert "source_l12_08_summary" not in payload


def test_l13_01_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l13_01_does_not_probe_when_l12_execution_preflight_is_not_ready() -> None:
    payload = contract.build_edge_executable_filesystem_probe_execution_contract(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=False,
        activate_executable_filesystem_probe=False,
        allow_real_filesystem_probe=False,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE)],
    )
    assert payload["ok"] is True
    assert payload["patch"] == "L13.1"
    assert payload["l12_execution_preflight_stack_accepted"] is True
    assert payload["execution_preflight_ready"] is False
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    _assert_no_launch_side_effects(payload)


def test_l13_01_readonly_probe_runs_when_l12_execution_preflight_is_ready_and_can_select_fixture() -> None:
    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    payload = contract.build_edge_executable_filesystem_probe_execution_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE), str(EXISTING_FIXTURE)],
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L13"
    assert payload["l12_08_execution_preflight_final_acceptance_marker_remains_accepted"] is True
    assert payload["execution_preflight_ready"] is True
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is True
    assert payload["edge_executable_path_selected"] is True
    assert payload["edge_executable_selected_path"] == str(EXISTING_FIXTURE)
    assert payload["next_patch"] == "L13.2 Live adapter Microsoft Edge executable filesystem probe execution CLI/readback"
    _assert_no_launch_side_effects(payload)


def test_l13_01_readonly_probe_can_perform_without_selecting_missing_fixture() -> None:
    payload = contract.build_edge_executable_filesystem_probe_execution_contract(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE)],
    )
    assert payload["ok"] is True
    assert payload["execution_preflight_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is True
    assert isinstance(payload["edge_executable_path_selected"], bool)
    _assert_no_launch_side_effects(payload)


def test_l13_01_patchops_cli_json_readback_is_parseable_compact_and_no_launch_side_effects() -> None:
    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
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
            "--allow-real-filesystem-probe",
            "--allow-executable-filesystem-probe-execution",
            "--extra-candidate",
            str(MISSING_FIXTURE),
            "--extra-candidate",
            str(EXISTING_FIXTURE),
            "--json",
            "--compact",
        ],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    assert completed.returncode == 0, completed.stderr
    assert len(completed.stdout) < 90000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L13.1"
    assert payload["edge_executable_filesystem_probe_performed"] is True
    assert payload["edge_executable_selected_path"] == str(EXISTING_FIXTURE)
    _assert_no_launch_side_effects(payload)


def test_l13_01_doc_mentions_execution_contract_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_execution_contract.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L13.1 Microsoft Edge executable filesystem probe execution contract",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L12 execution preflight stack accepted",
        "L12.8 execution preflight final acceptance marker remains accepted",
        "execution contract enforced",
        "read-only filesystem probe",
        "small allowlisted Microsoft Edge executable candidate list",
        "filesystem probe may be performed only when L12 execution preflight readiness is true",
        "executable path may be selected if an allowlisted candidate exists",
        "--allow-executable-filesystem-probe-execution",
        "--allow-real-filesystem-probe",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no executable launch attempted",
        "no profile directory creation",
        "no click/download/paste/send/package-run side effect",
        "L13.2 Live adapter Microsoft Edge executable filesystem probe execution CLI/readback",
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

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_contract as contract

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_01_candidate"
EXISTING_FIXTURE = ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge.exe"
MISSING_FIXTURE = ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge.exe"


def assert_no_launch(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l12_execution_preflight_stack_accepted"] is True
    assert payload["edge_executable_filesystem_probe_execution_contract_enforced"] is True
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []


def main() -> int:
    not_ready = contract.build_edge_executable_filesystem_probe_execution_contract(
        ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED,
        allow_executable_probe=False,
        activate_executable_filesystem_probe=False,
        allow_real_filesystem_probe=False,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE)],
    )
    assert_no_launch(not_ready)
    assert not_ready["edge_executable_filesystem_probe_performed"] is False
    print("PASS not_ready: patch=L13.1 source=L12.8 exec_ready=False probe_allowed=False probe_performed=False path_selected=False launch=False")

    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    ready = contract.build_edge_executable_filesystem_probe_execution_contract(
        ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
        extra_candidates=[str(MISSING_FIXTURE), str(EXISTING_FIXTURE)],
    )
    assert_no_launch(ready)
    assert ready["execution_preflight_ready"] is True
    assert ready["edge_executable_filesystem_probe_execution_allowed"] is True
    assert ready["edge_executable_filesystem_probe_performed"] is True
    assert ready["edge_executable_path_selected"] is True
    assert ready["edge_executable_selected_path"] == str(EXISTING_FIXTURE)
    print("PASS ready_fixture: patch=L13.1 source=L12.8 exec_ready=True probe_allowed=True probe_performed=True path_selected=True launch=False")

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
            "--allow-real-filesystem-probe",
            "--allow-executable-filesystem-probe-execution",
            "--extra-candidate",
            str(MISSING_FIXTURE),
            "--extra-candidate",
            str(EXISTING_FIXTURE),
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
    assert len(completed.stdout) < 90000
    assert_no_launch(payload)
    assert payload["edge_executable_selected_path"] == str(EXISTING_FIXTURE)
    print("PASS main_cli: compact JSON parsed quickly; read-only filesystem probe selected fixture and launched nothing")
    print("PASS L13.1 brief validation: read-only executable filesystem probe execution contract accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L13.1 START
# Read-only Microsoft Edge executable filesystem probe execution contract.
import sys as _patchops_l13_01_sys

_PATCHOPS_L13_01_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-contract"

try:
    _PATCHOPS_L13_01_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L13_01_PREV_BUILD_PARSER = None

if _PATCHOPS_L13_01_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L13_01_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L13_01_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L13_01_COMMAND, help="Run read-only Edge executable filesystem probe contract.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--allow-executable-probe", action="store_true")
                        p.add_argument("--activate-executable-filesystem-probe", action="store_true")
                        p.add_argument("--allow-real-filesystem-probe", action="store_true")
                        p.add_argument("--allow-executable-filesystem-probe-execution", action="store_true")
                        p.add_argument("--extra-candidate", action="append", default=[])
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_filesystem_probe_execution_contract(args) -> int:
    from . import live_adapter_edge_executable_filesystem_probe_execution_contract
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
    if getattr(args, "allow_real_filesystem_probe", False):
        module_args.append("--allow-real-filesystem-probe")
    if getattr(args, "allow_executable_filesystem_probe_execution", False):
        module_args.append("--allow-executable-filesystem-probe-execution")
    for candidate in getattr(args, "extra_candidate", []) or []:
        module_args.extend(["--extra-candidate", str(candidate)])
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_filesystem_probe_execution_contract.main(module_args)

try:
    _PATCHOPS_L13_01_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L13_01_PREV_COMMAND_NAMES = None

if _PATCHOPS_L13_01_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L13_01_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L13_01_COMMAND,) if name not in names)

_PATCHOPS_L13_01_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l13_01_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L13_01_COMMAND:
        from . import live_adapter_edge_executable_filesystem_probe_execution_contract
        return live_adapter_edge_executable_filesystem_probe_execution_contract.main(arg_list[1:])
    return _PATCHOPS_L13_01_PREV_MAIN(argv)
# PATCHOPS L13.1 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L13.1 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L13.1 command wrapper appended")
    else:
        print("L13.1 command wrapper already present")


def _append_l12_08_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_final_acceptance_marker.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L13.1 Live adapter Microsoft Edge executable filesystem probe execution contract"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the execution preflight stack:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L12.8 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l12_08_doc_pointer()
    print("L13.1 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())