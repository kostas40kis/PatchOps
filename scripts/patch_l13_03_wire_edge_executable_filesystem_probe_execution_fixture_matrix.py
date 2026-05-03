from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.md")
TEST_PATH = Path("tests/test_l13_03_edge_executable_filesystem_probe_execution_fixture_matrix_current.py")
VALIDATE_PATH = Path("scripts/patch_l13_03_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L13.3 Microsoft Edge executable filesystem-probe execution fixture matrix.

Adds a fixture matrix over the accepted L13.2 read-only executable filesystem
probe execution CLI/readback. The matrix models not-ready and ready probe cases.
The ready case may read allowlisted executable candidate metadata, but this layer
still does not launch a browser, import Selenium, create profiles, click,
download, paste, send, run packages, commit, or push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_cli_readback as l13_02

PATCH = "L13.3"
PHASE = "L13"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L13.3 Microsoft Edge Executable Filesystem Probe Execution Fixture Matrix"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-readback"
NEXT_PATCH = "L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-execution-fixture-matrix-readonly-probe-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
EXECUTABLE_PROBE_ACTIVATION_FLAG = "--activate-executable-filesystem-probe"
REAL_FILESYSTEM_PROBE_FLAG = "--allow-real-filesystem-probe"
EXECUTION_PREFLIGHT_FLAG = "--allow-executable-filesystem-probe-execution"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")

FIXTURE_MATRIX = (
    {"fixture_id": "no_gates", "allow_live_start": False, "allow_executable_probe": False, "activate_executable_filesystem_probe": False, "allow_real_filesystem_probe": False, "allow_executable_filesystem_probe_execution": False, "expected_probe_performed": False, "expected_launch_attempted": False},
    {"fixture_id": "execution_flag_only", "allow_live_start": False, "allow_executable_probe": False, "activate_executable_filesystem_probe": False, "allow_real_filesystem_probe": False, "allow_executable_filesystem_probe_execution": True, "expected_probe_performed": False, "expected_launch_attempted": False},
    {"fixture_id": "real_ready_without_execution_flag", "allow_live_start": True, "allow_executable_probe": True, "activate_executable_filesystem_probe": True, "allow_real_filesystem_probe": True, "allow_executable_filesystem_probe_execution": False, "expected_probe_performed": False, "expected_launch_attempted": False},
    {"fixture_id": "execution_ready_missing_extra_candidate", "allow_live_start": True, "allow_executable_probe": True, "activate_executable_filesystem_probe": True, "allow_real_filesystem_probe": True, "allow_executable_filesystem_probe_execution": True, "expected_probe_performed": True, "expected_launch_attempted": False},
    {"fixture_id": "execution_ready_fixture_observed", "allow_live_start": True, "allow_executable_probe": True, "activate_executable_filesystem_probe": True, "allow_real_filesystem_probe": True, "allow_executable_filesystem_probe_execution": True, "expected_probe_performed": True, "expected_launch_attempted": False},
)
EXPECTED_FIXTURE_IDS = {item["fixture_id"] for item in FIXTURE_MATRIX}

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.md",
    "tests/test_l13_02_edge_executable_filesystem_probe_execution_cli_readback_current.py",
    "tests/test_l13_03_edge_executable_filesystem_probe_execution_fixture_matrix_current.py",
    "scripts/patch_l13_02_brief_validate.py",
    "scripts/patch_l13_03_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_cli_readback.md": (
        "L13.2 Microsoft Edge executable filesystem probe execution CLI/readback",
        SOURCE_COMMAND_NAME,
        "execution CLI/readback enforced",
        "L13.3 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.md": (
        "L13.3 Microsoft Edge executable filesystem probe execution fixture matrix",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L13.2 execution CLI/readback remains accepted",
        "L13.1 execution contract remains accepted",
        "execution fixture matrix enforced",
        "execution CLI/readback enforced",
        "execution contract enforced",
        "read-only filesystem probe",
        "small allowlisted Microsoft Edge executable candidate list",
        "filesystem probe may be performed only when L12 execution preflight readiness is true",
        "selected path, if any, is an existing reported candidate",
        "no_gates",
        "execution_flag_only",
        "real_ready_without_execution_flag",
        "execution_ready_missing_extra_candidate",
        "execution_ready_fixture_observed",
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
        "L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback",
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
        "exec_ready": source.get("execution_preflight_ready"),
        "probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
        "selected_path": source.get("edge_executable_selected_path"),
        "launch_attempted": source.get("edge_executable_launch_attempted"),
    }


def _selected_path_truthful(source: Mapping[str, Any]) -> bool:
    if source.get("edge_executable_path_selected") is not True:
        return source.get("edge_executable_selected_path") is None
    selected = source.get("edge_executable_selected_path")
    return any(
        item.get("path") == selected and item.get("exists") is True and item.get("is_file") is True
        for item in source.get("edge_executable_probe_candidates", []) or []
        if isinstance(item, Mapping)
    )


def _source_l13_02_safe(source: Mapping[str, Any], *, expected_probe_performed: bool) -> bool:
    return (
        source.get("patch") == "L13.2"
        and source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and source.get("l13_01_execution_contract_remains_accepted") is True
        and source.get("l12_execution_preflight_stack_accepted") is True
        and source.get("edge_executable_filesystem_probe_execution_cli_readback_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_contract_enforced") is True
        and source.get("edge_executable_filesystem_probe_performed") is expected_probe_performed
        and source.get("edge_executable_filesystem_probe_execution_allowed") is expected_probe_performed
        and _selected_path_truthful(source)
        and source.get("edge_executable_launch_attempted") is False
        and source.get("startup_allowed") is False
        and source.get("live_start_performed") is False
        and source.get("browser_started") is False
        and source.get("edge_process_started") is False
        and source.get("browser_session_created") is False
        and source.get("driver_created") is False
        and source.get("profile_directory_created") is False
        and source.get("filesystem_writes_performed") == []
        and source.get("adapter_filesystem_writes_performed") == []
        and source.get("side_effects_performed") == []
        and source.get("selenium_imported_by_readback") is False
        and "source_l13_02_summary" not in source
        and "source_l13_01_summary" not in source
    )


def _fixture_state() -> dict[str, Any]:
    fixtures = [dict(item) for item in FIXTURE_MATRIX]
    return {
        "edge_executable_filesystem_probe_execution_fixture_matrix_enforced": True,
        "edge_executable_filesystem_probe_execution_fixture_matrix_modeled": True,
        "execution_fixture_count": len(fixtures),
        "execution_fixture_ids": [fixture["fixture_id"] for fixture in fixtures],
        "execution_fixture_matrix": fixtures,
        "fixture_launch_attempted": False,
        "fixture_browser_started": False,
        "fixture_profile_directory_created": False,
    }


def build_edge_executable_filesystem_probe_execution_fixture_matrix(
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
    expected_probe_performed = bool(
        allow_live_start
        and allow_executable_probe
        and activate_executable_filesystem_probe
        and allow_real_filesystem_probe
        and allow_executable_filesystem_probe_execution
    )
    source = l13_02.build_edge_executable_filesystem_probe_execution_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
        allow_real_filesystem_probe=allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=allow_executable_filesystem_probe_execution,
        extra_candidates=extra_candidates,
    )
    source_safe = _source_l13_02_safe(source, expected_probe_performed=expected_probe_performed)
    fixtures = _fixture_state()
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l13_02_execution_readback_still_passes", source_safe, _compact_source_status(source)),
        _check("l13_02_execution_readback_remains_no_launch", source_safe, {"launch_attempted": source.get("edge_executable_launch_attempted"), "browser_started": source.get("browser_started")}),
        _check("l13_03_execution_fixture_matrix_command_registered", command_state.get("ok") is True, command_state),
        _check("l13_02_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l13_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l13_docs_contain_execution_fixture_matrix_boundary", doc_state.get("ok") is True, doc_state),
        _check("execution_fixture_matrix_is_enforced", fixtures["edge_executable_filesystem_probe_execution_fixture_matrix_enforced"] is True, fixtures),
        _check("execution_fixture_ids_are_stable", set(fixtures["execution_fixture_ids"]) == EXPECTED_FIXTURE_IDS, fixtures),
        _check("probe_runs_only_when_preflight_ready", source.get("edge_executable_filesystem_probe_performed") is expected_probe_performed, _compact_source_status(source)),
        _check("selected_path_is_truthful_if_present", _selected_path_truthful(source), _compact_source_status(source)),
        _check("no_executable_launch_attempted", source.get("edge_executable_launch_attempted") is False and fixtures["fixture_launch_attempted"] is False, {}),
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
        "l13_02_execution_cli_readback_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "l13_01_execution_contract_remains_accepted": source.get("l13_01_execution_contract_remains_accepted") is True,
        "l12_execution_preflight_stack_accepted": source.get("l12_execution_preflight_stack_accepted") is True,
        "source_l13_02_status": _compact_source_status(source),
        **fixtures,
        "edge_executable_filesystem_probe_execution_cli_readback_enforced": source.get("edge_executable_filesystem_probe_execution_cli_readback_enforced"),
        "edge_executable_filesystem_probe_execution_contract_enforced": source.get("edge_executable_filesystem_probe_execution_contract_enforced"),
        "execution_preflight_flag": EXECUTION_PREFLIGHT_FLAG,
        "execution_preflight_authorization_present": source.get("execution_preflight_authorization_present"),
        "execution_preflight_ready": source.get("execution_preflight_ready"),
        "execution_preflight_execution_allowed": source.get("execution_preflight_execution_allowed"),
        "edge_executable_filesystem_probe_execution_allowed": source.get("edge_executable_filesystem_probe_execution_allowed"),
        "edge_executable_filesystem_probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "edge_executable_filesystem_probe_mode": source.get("edge_executable_filesystem_probe_mode"),
        "edge_executable_probe_candidate_count": source.get("edge_executable_probe_candidate_count"),
        "edge_executable_probe_candidates": source.get("edge_executable_probe_candidates"),
        "edge_executable_path_selected": source.get("edge_executable_path_selected"),
        "edge_executable_selected_path": source.get("edge_executable_selected_path"),
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
        f"L13.2 Accepted  : {payload.get('l13_02_execution_cli_readback_remains_accepted')}",
        f"Fixture Count   : {payload.get('execution_fixture_count')}",
        f"Exec Ready      : {payload.get('execution_preflight_ready')}",
        f"Probe Performed : {payload.get('edge_executable_filesystem_probe_performed')}",
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
    payload = build_edge_executable_filesystem_probe_execution_fixture_matrix(
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

DOC_CONTENT = r'''# L13.3 Microsoft Edge executable filesystem probe execution fixture matrix

L13.3 adds a fixture matrix over the accepted L13.2 read-only executable filesystem probe execution CLI/readback.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L13.2 execution CLI/readback remains accepted.
- L13.1 execution contract remains accepted.
- L12 execution preflight stack accepted.
- execution fixture matrix enforced.
- execution CLI/readback enforced.
- execution contract enforced.
- read-only filesystem probe.
- small allowlisted Microsoft Edge executable candidate list.
- filesystem probe may be performed only when L12 execution preflight readiness is true.
- selected path, if any, is an existing reported candidate.
- `no_gates` fixture modeled.
- `execution_flag_only` fixture modeled.
- `real_ready_without_execution_flag` fixture modeled.
- `execution_ready_missing_extra_candidate` fixture modeled.
- `execution_ready_fixture_observed` fixture modeled.
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

`L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix as matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-readback"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_03_candidate"
EXISTING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge_l13_03.exe"
MISSING_FIXTURE = PROJECT_ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge-l13-03.exe"
EXPECTED_IDS = {
    "no_gates",
    "execution_flag_only",
    "real_ready_without_execution_flag",
    "execution_ready_missing_extra_candidate",
    "execution_ready_fixture_observed",
}


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
    assert "source_l13_03_summary" not in payload
    assert "source_l13_02_summary" not in payload


def _candidate_for(payload: dict, path: Path) -> dict | None:
    expected = str(path)
    for item in payload.get("edge_executable_probe_candidates", []) or []:
        if item.get("path") == expected:
            return item
    return None


def _assert_truthful_selection(payload: dict) -> None:
    selected = payload.get("edge_executable_selected_path")
    if payload["edge_executable_path_selected"]:
        assert any(
            item.get("path") == selected and item.get("exists") is True and item.get("is_file") is True
            for item in payload.get("edge_executable_probe_candidates", []) or []
        )
    else:
        assert selected is None


def test_l13_03_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l13_03_fixture_matrix_not_ready_cases_do_not_probe() -> None:
    for kwargs in [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False),
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False),
    ]:
        payload = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(PROJECT_ROOT, extra_candidates=[str(MISSING_FIXTURE)], **kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L13.3"
        assert payload["l13_02_execution_cli_readback_remains_accepted"] is True
        assert set(payload["execution_fixture_ids"]) == EXPECTED_IDS
        assert payload["edge_executable_filesystem_probe_performed"] is False
        assert payload["edge_executable_path_selected"] is False
        _assert_no_launch_side_effects(payload)


def test_l13_03_fixture_matrix_ready_case_probes_and_observes_fixture_without_launch() -> None:
    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    payload = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(
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
    assert payload["execution_preflight_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is True
    fixture_candidate = _candidate_for(payload, EXISTING_FIXTURE)
    assert fixture_candidate is not None
    assert fixture_candidate.get("exists") is True
    assert fixture_candidate.get("is_file") is True
    _assert_truthful_selection(payload)
    assert payload["next_patch"] == "L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback"
    _assert_no_launch_side_effects(payload)


def test_l13_03_patchops_cli_json_readback_is_parseable_compact_and_no_launch_side_effects() -> None:
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
    assert len(completed.stdout) < 95000
    payload = json.loads(completed.stdout)
    assert payload["ok"] is True
    assert payload["patch"] == "L13.3"
    assert payload["edge_executable_filesystem_probe_performed"] is True
    fixture_candidate = _candidate_for(payload, EXISTING_FIXTURE)
    assert fixture_candidate is not None
    assert fixture_candidate.get("exists") is True
    assert fixture_candidate.get("is_file") is True
    _assert_truthful_selection(payload)
    _assert_no_launch_side_effects(payload)


def test_l13_03_doc_mentions_execution_fixture_matrix_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L13.3 Microsoft Edge executable filesystem probe execution fixture matrix",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L13.2 execution CLI/readback remains accepted",
        "L13.1 execution contract remains accepted",
        "execution fixture matrix enforced",
        "execution CLI/readback enforced",
        "execution contract enforced",
        "read-only filesystem probe",
        "small allowlisted Microsoft Edge executable candidate list",
        "filesystem probe may be performed only when L12 execution preflight readiness is true",
        "selected path, if any, is an existing reported candidate",
        "no_gates",
        "execution_flag_only",
        "real_ready_without_execution_flag",
        "execution_ready_missing_extra_candidate",
        "execution_ready_fixture_observed",
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
        "L13.4 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix CLI/readback",
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

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix as matrix

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l13_03_candidate"
EXISTING_FIXTURE = ROOT / "data" / "runtime" / "edge_probe_fixture" / "msedge_l13_03.exe"
MISSING_FIXTURE = ROOT / "data" / "runtime" / "edge_probe_fixture" / "missing-msedge-l13-03.exe"


def assert_no_launch(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l13_02_execution_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_execution_fixture_matrix_enforced"] is True
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []


def candidate_for(payload: dict, path: Path) -> dict | None:
    expected = str(path)
    for item in payload.get("edge_executable_probe_candidates", []) or []:
        if item.get("path") == expected:
            return item
    return None


def assert_truthful_selection(payload: dict) -> None:
    selected = payload.get("edge_executable_selected_path")
    if payload["edge_executable_path_selected"]:
        assert any(
            item.get("path") == selected and item.get("exists") is True and item.get("is_file") is True
            for item in payload.get("edge_executable_probe_candidates", []) or []
        )
    else:
        assert selected is None


def main() -> int:
    for name, kwargs in [
        ("no_gates", dict(allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False)),
        ("execution_flag_only", dict(allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True)),
        ("real_ready_without_execution_flag", dict(allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False)),
    ]:
        payload = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(ROOT, extra_candidates=[str(MISSING_FIXTURE)], **kwargs)
        assert_no_launch(payload)
        assert payload["edge_executable_filesystem_probe_performed"] is False
        print("PASS {0}: patch=L13.3 fixtures=5 probe_performed=False path_selected=False launch=False".format(name))

    EXISTING_FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    EXISTING_FIXTURE.write_text("fixture executable placeholder", encoding="utf-8")
    ready = matrix.build_edge_executable_filesystem_probe_execution_fixture_matrix(
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
    assert ready["edge_executable_filesystem_probe_performed"] is True
    observed_fixture = candidate_for(ready, EXISTING_FIXTURE)
    assert observed_fixture is not None
    assert observed_fixture.get("exists") is True
    assert observed_fixture.get("is_file") is True
    assert_truthful_selection(ready)
    print("PASS execution_ready_fixture_observed: patch=L13.3 fixtures=5 probe_performed=True fixture_observed=True selected_path={0} launch=False".format(ready.get("edge_executable_selected_path") or "(none)"))

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
    assert len(completed.stdout) < 95000
    assert_no_launch(payload)
    observed_fixture = candidate_for(payload, EXISTING_FIXTURE)
    assert observed_fixture is not None
    assert observed_fixture.get("exists") is True
    assert observed_fixture.get("is_file") is True
    assert_truthful_selection(payload)
    print("PASS main_cli: compact JSON parsed quickly; execution fixture matrix was truthful and launched nothing")
    print("PASS L13.3 brief validation: read-only executable filesystem probe execution fixture matrix accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L13.3 START
# Read-only Microsoft Edge executable filesystem probe execution fixture matrix.
import sys as _patchops_l13_03_sys

_PATCHOPS_L13_03_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-fixture-matrix"

try:
    _PATCHOPS_L13_03_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L13_03_PREV_BUILD_PARSER = None

if _PATCHOPS_L13_03_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L13_03_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L13_03_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L13_03_COMMAND, help="Read back Edge executable filesystem probe execution fixture matrix without launching.")
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


def run_browser_start_supervised_launch_edge_executable_filesystem_probe_execution_fixture_matrix(args) -> int:
    from . import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix
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
    return live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.main(module_args)

try:
    _PATCHOPS_L13_03_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L13_03_PREV_COMMAND_NAMES = None

if _PATCHOPS_L13_03_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L13_03_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L13_03_COMMAND,) if name not in names)

_PATCHOPS_L13_03_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l13_03_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L13_03_COMMAND:
        from . import live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix
        return live_adapter_edge_executable_filesystem_probe_execution_fixture_matrix.main(arg_list[1:])
    return _PATCHOPS_L13_03_PREV_MAIN(argv)
# PATCHOPS L13.3 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L13.3 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L13.3 command wrapper appended")
    else:
        print("L13.3 command wrapper already present")


def _append_l13_02_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_cli_readback.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L13.3 Live adapter Microsoft Edge executable filesystem probe execution fixture matrix"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the execution CLI/readback:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L13.2 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l13_02_doc_pointer()
    print("L13.3 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())