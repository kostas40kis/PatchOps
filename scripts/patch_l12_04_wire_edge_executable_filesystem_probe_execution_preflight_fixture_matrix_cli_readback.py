from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.md")
TEST_PATH = Path("tests/test_l12_04_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_current.py")
VALIDATE_PATH = Path("scripts/patch_l12_04_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L12.4 passive Microsoft Edge executable filesystem-probe execution preflight fixture-matrix CLI/readback.

Adds compact CLI/readback over the accepted L12.3 execution-preflight fixture
matrix. Execution preflight readiness may become true when all required gates
are present, but filesystem probing, path selection, and launch remain blocked
by phase.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix as l12_03

PATCH = "L12.4"
PHASE = "L12"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L12.4 Microsoft Edge Executable Filesystem Probe Execution Preflight Fixture Matrix CLI Readback"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix"
NEXT_PATCH = "L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-execution-preflight-fixture-matrix-cli-readback-only"
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
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.md",
    "tests/test_l12_03_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_current.py",
    "tests/test_l12_04_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_current.py",
    "scripts/patch_l12_03_brief_validate.py",
    "scripts/patch_l12_04_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix.md": (
        "L12.3 Microsoft Edge executable filesystem probe execution preflight fixture matrix",
        SOURCE_COMMAND_NAME,
        "execution preflight fixture matrix enforced",
        "L12.4 Live adapter Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.md": (
        "L12.4 Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L12.3 execution preflight fixture matrix remains accepted",
        "execution preflight fixture matrix CLI/readback enforced",
        "execution preflight fixture matrix enforced",
        "execution preflight CLI/readback enforced",
        "execution preflight contract enforced",
        "filesystem probe execution requires a separate explicit execution-preflight flag",
        "six execution preflight fixtures remain stable",
        "no_gates",
        "execution_flag_only",
        "real_ready_without_execution_flag",
        "execution_preflight_ready_dedicated_profile",
        "execution_preflight_ready_default_profile",
        "execution_preflight_ready_missing_profile",
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
        "L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate",
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
        "fixture_count": source.get("execution_preflight_fixture_count"),
        "real_ready": source.get("real_filesystem_probe_preflight_ready"),
        "exec_flag": source.get("execution_preflight_authorization_present"),
        "exec_ready": source.get("execution_preflight_ready"),
        "exec_allowed": source.get("execution_preflight_execution_allowed"),
        "fs_probe": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
    }


def _source_l12_03_safe(source: Mapping[str, Any], *, expected_real_ready: bool, expected_execution_ready: bool) -> bool:
    fixture_ids = set(source.get("execution_preflight_fixture_ids", []))
    return (
        source.get("patch") == "L12.3"
        and source.get("ok") is True
        and source.get("status") == STATUS_PASS
        and source.get("command_name") == SOURCE_COMMAND_NAME
        and source.get("l12_02_execution_preflight_cli_readback_remains_accepted") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced") is True
        and source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_modeled") is True
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
        and "source_l12_03_summary" not in source
        and "source_l12_02_summary" not in source
    )


def build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(
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
    source = l12_03.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
        activate_executable_filesystem_probe=activate_executable_filesystem_probe,
        allow_real_filesystem_probe=allow_real_filesystem_probe,
        allow_executable_filesystem_probe_execution=allow_executable_filesystem_probe_execution,
    )
    source_safe = _source_l12_03_safe(source, expected_real_ready=expected_real_ready, expected_execution_ready=expected_execution_ready)
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l12_03_execution_preflight_fixture_matrix_still_passes", source_safe, _compact_source_status(source)),
        _check("l12_03_execution_preflight_fixture_matrix_remains_passive", source_safe, {"exec_ready": source.get("execution_preflight_ready"), "exec_allowed": source.get("execution_preflight_execution_allowed"), "fs_probe": source.get("edge_executable_filesystem_probe_performed")}),
        _check("l12_04_execution_preflight_fixture_matrix_readback_command_registered", command_state.get("ok") is True, command_state),
        _check("l12_03_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l12_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l12_docs_contain_execution_preflight_fixture_matrix_readback_boundary", doc_state.get("ok") is True, doc_state),
        _check("execution_preflight_fixture_matrix_cli_readback_is_enforced", source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced") is True, {}),
        _check("execution_preflight_fixture_ids_are_stable", set(source.get("execution_preflight_fixture_ids", [])) == EXPECTED_FIXTURE_IDS, {"fixture_ids": source.get("execution_preflight_fixture_ids")}),
        _check("execution_preflight_ready_requires_execution_flag", source.get("execution_preflight_ready") is expected_execution_ready, _compact_source_status(source)),
        _check("execution_preflight_execution_remains_blocked_by_phase", source.get("execution_preflight_execution_allowed") is False and source.get("fixture_execution_preflight_execution_allowed") is False, {}),
        _check("filesystem_probe_is_not_performed", source.get("edge_executable_filesystem_probe_performed") is False and source.get("fixture_filesystem_probe_performed") is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and source.get("fixture_path_selected") is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and source.get("fixture_executable_launch_attempted") is False, {}),
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
        "l12_03_execution_preflight_fixture_matrix_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "l12_02_execution_preflight_cli_readback_remains_accepted": source.get("l12_02_execution_preflight_cli_readback_remains_accepted") is True,
        "l11_real_probe_preflight_stack_accepted": source.get("l11_real_probe_preflight_stack_accepted") is True,
        "source_l12_03_status": _compact_source_status(source),
        "edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_enforced": True,
        "edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced": source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_enforced"),
        "edge_executable_filesystem_probe_execution_preflight_fixture_matrix_modeled": source.get("edge_executable_filesystem_probe_execution_preflight_fixture_matrix_modeled"),
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
        f"L12.3 Accepted  : {payload.get('l12_03_execution_preflight_fixture_matrix_remains_accepted')}",
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
    payload = build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(
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
'''

DOC_CONTENT = r'''# L12.4 Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback

L12.4 adds a passive CLI/readback layer over the accepted L12.3 execution preflight fixture matrix.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L12.3 execution preflight fixture matrix remains accepted.
- execution preflight fixture matrix CLI/readback enforced.
- execution preflight fixture matrix enforced.
- execution preflight CLI/readback enforced.
- execution preflight contract enforced.
- filesystem probe execution requires a separate explicit execution-preflight flag.
- six execution preflight fixtures remain stable.
- `no_gates` fixture modeled.
- `execution_flag_only` fixture modeled.
- `real_ready_without_execution_flag` fixture modeled.
- `execution_preflight_ready_dedicated_profile` fixture modeled.
- `execution_preflight_ready_default_profile` fixture modeled.
- `execution_preflight_ready_missing_profile` fixture modeled.
- `--allow-executable-filesystem-probe-execution` is modeled but does not execute a filesystem probe yet.
- `--allow-real-filesystem-probe` remains the explicit real-probe preflight flag.
- `--activate-executable-filesystem-probe` remains the explicit activation flag.
- `--allow-executable-probe` remains the explicit executable-probe authorization flag.
- execution preflight readiness can be true while filesystem probe execution remains blocked.
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

`L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback as readback

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l12_04_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
EXPECTED_IDS = {
    "no_gates",
    "execution_flag_only",
    "real_ready_without_execution_flag",
    "execution_preflight_ready_dedicated_profile",
    "execution_preflight_ready_default_profile",
    "execution_preflight_ready_missing_profile",
}


def _assert_passive(payload: dict) -> None:
    assert payload["execution_preflight_execution_allowed"] is False
    assert payload["fixture_execution_preflight_execution_allowed"] is False
    assert payload["real_filesystem_probe_execution_allowed"] is False
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
    assert "source_l12_04_summary" not in payload
    assert "source_l12_03_summary" not in payload


def test_l12_04_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l12_04_fixture_matrix_readback_not_ready_without_all_required_gates() -> None:
    for kwargs in [
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False),
        dict(allow_live_start=False, profile_dir=DEDICATED_PROFILE, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True),
        dict(allow_live_start=True, profile_dir=DEDICATED_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False),
    ]:
        payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(PROJECT_ROOT, **kwargs)
        assert payload["ok"] is True
        assert payload["patch"] == "L12.4"
        assert payload["l12_03_execution_preflight_fixture_matrix_remains_accepted"] is True
        assert set(payload["execution_preflight_fixture_ids"]) == EXPECTED_IDS
        assert payload["execution_preflight_ready"] is False
        _assert_passive(payload)


def test_l12_04_execution_preflight_ready_but_execution_still_blocked() -> None:
    payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
        activate_executable_filesystem_probe=True,
        allow_real_filesystem_probe=True,
        allow_executable_filesystem_probe_execution=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L12"
    assert payload["execution_preflight_ready"] is True
    assert payload["execution_preflight_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["next_patch"] == "L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate"
    _assert_passive(payload)


def test_l12_04_default_and_missing_profile_cases_are_passive_when_execution_preflight_ready() -> None:
    default_payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=True)
    missing_payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l12_03_status"]["ok"] is True
    assert default_payload["execution_preflight_ready"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l12_03_status"]["ok"] is True
    assert missing_payload["execution_preflight_ready"] is True
    _assert_passive(missing_payload)


def test_l12_04_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L12.4"
    assert payload["execution_preflight_ready"] is True
    assert payload["execution_preflight_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l12_04_doc_mentions_execution_preflight_fixture_matrix_readback_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L12.4 Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L12.3 execution preflight fixture matrix remains accepted",
        "execution preflight fixture matrix CLI/readback enforced",
        "execution preflight fixture matrix enforced",
        "execution preflight CLI/readback enforced",
        "filesystem probe execution requires a separate explicit execution-preflight flag",
        "six execution preflight fixtures remain stable",
        "no_gates",
        "execution_flag_only",
        "real_ready_without_execution_flag",
        "execution_preflight_ready_dedicated_profile",
        "execution_preflight_ready_default_profile",
        "execution_preflight_ready_missing_profile",
        "--allow-executable-filesystem-probe-execution",
        "--allow-real-filesystem-probe",
        "--activate-executable-filesystem-probe",
        "--allow-executable-probe",
        "execution preflight readiness can be true while filesystem probe execution remains blocked",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L12.5 Live adapter Microsoft Edge executable filesystem probe execution preflight aggregate gate",
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

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback as readback

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l12_04_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l12_03_execution_preflight_fixture_matrix_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback_enforced"] is True
    assert payload["execution_preflight_execution_allowed"] is False
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
    assert "source_l12_03_summary" not in payload


def main() -> int:
    no_gates = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=False)
    assert_passive(no_gates)
    assert no_gates["execution_preflight_ready"] is False
    print("PASS no_gates: patch=L12.4 fixtures=6 exec_ready=False exec_allowed=False fs_probe=False path_selected=False")

    execution_flag_only = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False, activate_executable_filesystem_probe=False, allow_real_filesystem_probe=False, allow_executable_filesystem_probe_execution=True)
    assert_passive(execution_flag_only)
    assert execution_flag_only["execution_preflight_ready"] is False
    print("PASS execution_flag_only: fixtures=6 exec_ready=False exec_allowed=False fs_probe=False path_selected=False")

    real_ready_without_execution = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(ROOT, allow_live_start=True, profile_dir=DEDICATED, allow_executable_probe=True, activate_executable_filesystem_probe=True, allow_real_filesystem_probe=True, allow_executable_filesystem_probe_execution=False)
    assert_passive(real_ready_without_execution)
    assert real_ready_without_execution["real_filesystem_probe_preflight_ready"] is True
    assert real_ready_without_execution["execution_preflight_ready"] is False
    print("PASS real_ready_without_execution_flag: fixtures=6 real_ready=True exec_ready=False exec_allowed=False fs_probe=False path_selected=False")

    for name, profile in [("execution_preflight_ready_dedicated", DEDICATED), ("execution_preflight_ready_default", DEFAULT), ("execution_preflight_ready_missing_profile", None)]:
        payload = readback.build_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback(
            ROOT,
            allow_live_start=True,
            profile_dir=profile,
            allow_executable_probe=True,
            activate_executable_filesystem_probe=True,
            allow_real_filesystem_probe=True,
            allow_executable_filesystem_probe_execution=True,
        )
        assert_passive(payload)
        assert payload["execution_preflight_ready"] is True
        print("PASS {0}: patch=L12.4 source=L12.3 fixtures=6 exec_ready=True exec_allowed=False fs_probe=False path_selected=False".format(name))

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
    print("PASS main_cli: compact JSON parsed quickly; execution-preflight fixture matrix CLI/readback stayed passive")
    print("PASS L12.4 brief validation: execution-preflight fixture matrix CLI/readback accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L12.4 START
# Passive Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback.
import sys as _patchops_l12_04_sys

_PATCHOPS_L12_04_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-execution-preflight-fixture-matrix-readback"

try:
    _PATCHOPS_L12_04_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L12_04_PREV_BUILD_PARSER = None

if _PATCHOPS_L12_04_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L12_04_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L12_04_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L12_04_COMMAND, help="Read back passive Edge executable filesystem probe execution preflight fixture matrix CLI state.")
                        p.add_argument("--repo-root", default=None)
                        p.add_argument("--allow-live-start", action="store_true")
                        p.add_argument("--profile-dir", default=None)
                        p.add_argument("--allow-executable-probe", action="store_true")
                        p.add_argument("--activate-executable-filesystem-probe", action="store_true")
                        p.add_argument("--allow-real-filesystem-probe", action="store_true")
                        p.add_argument("--allow-executable-filesystem-probe-execution", action="store_true")
                        p.add_argument("--json", action="store_true")
                        p.add_argument("--compact", action="store_true")
                    break
        except Exception:
            pass
        return parser


def run_browser_start_supervised_launch_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_readback(args) -> int:
    from . import live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback
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
    if getattr(args, "json", False):
        module_args.append("--json")
    if getattr(args, "compact", False):
        module_args.append("--compact")
    return live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.main(module_args)

try:
    _PATCHOPS_L12_04_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L12_04_PREV_COMMAND_NAMES = None

if _PATCHOPS_L12_04_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L12_04_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L12_04_COMMAND,) if name not in names)

_PATCHOPS_L12_04_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l12_04_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L12_04_COMMAND:
        from . import live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback
        return live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix_cli_readback.main(arg_list[1:])
    return _PATCHOPS_L12_04_PREV_MAIN(argv)
# PATCHOPS L12.4 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L12.4 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L12.4 command wrapper appended")
    else:
        print("L12.4 command wrapper already present")


def _append_l12_03_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_execution_preflight_fixture_matrix.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L12.4 Live adapter Microsoft Edge executable filesystem probe execution preflight fixture matrix CLI/readback"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the execution preflight fixture matrix:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L12.3 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l12_03_doc_pointer()
    print("L12.4 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())