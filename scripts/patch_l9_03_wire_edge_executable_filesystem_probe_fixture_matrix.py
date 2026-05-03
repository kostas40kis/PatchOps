from __future__ import annotations

from pathlib import Path

MODULE_PATH = Path("patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_fixture_matrix.py")
DOC_PATH = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_fixture_matrix.md")
TEST_PATH = Path("tests/test_l9_03_edge_executable_filesystem_probe_fixture_matrix_current.py")
VALIDATE_PATH = Path("scripts/patch_l9_03_brief_validate.py")
COMMANDS_PATH = Path("patchops/llm_browser/commands.py")

MODULE_CONTENT = r'''"""L9.3 passive Microsoft Edge executable filesystem-probe fixture matrix.

Adds a modeled fixture matrix over the accepted L9.2 executable filesystem-probe
CLI/readback layer. The matrix covers no-authorization and authorized profile
cases, but still performs no filesystem probe, no executable path selection,
no launch, no Selenium import, no browser start, no profile creation, no
click/download, no paste/send, no package run, no commit, and no push.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_cli_readback as l9_02

PATCH = "L9.3"
PHASE = "L9"
STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
NAME = "L9.3 Microsoft Edge Executable Filesystem Probe Fixture Matrix"
COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-fixture-matrix"
SOURCE_COMMAND_NAME = "browser-start-supervised-launch-edge-executable-filesystem-probe-readback"
NEXT_PATCH = "L9.4 Live adapter Microsoft Edge executable filesystem probe fixture matrix CLI/readback"
SIDE_EFFECT_BOUNDARY = "edge-executable-filesystem-probe-fixture-matrix-only"
EXECUTABLE_PROBE_AUTHORIZATION_FLAG = "--allow-executable-probe"
BROWSER_PRIORITY = ("edge", "opera")
FORBIDDEN_OPTIONAL_ROOTS = ("selenium", "webdriver_manager", "pyperclip", "psutil", "playwright", "pyppeteer")
EDGE_EXECUTABLE_CANDIDATE_LABELS = (
    "program_files_edge_application_msedgedotexe",
    "program_files_x86_edge_application_msedgedotexe",
    "local_app_data_edge_application_msedgedotexe",
)
REPAIR_NOTE = "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok."

FIXTURE_MATRIX = (
    {"fixture_id": "no_auth_dedicated_profile", "allow_live_start": False, "allow_executable_probe": False, "profile_kind": "dedicated", "expected_readback_ok": True, "expected_preflight_passed": False, "expected_contract_ready": False, "expected_filesystem_probe_performed": False, "expected_path_selected": False},
    {"fixture_id": "live_auth_without_probe_auth", "allow_live_start": True, "allow_executable_probe": False, "profile_kind": "dedicated", "expected_readback_ok": True, "expected_preflight_passed": False, "expected_contract_ready": False, "expected_filesystem_probe_performed": False, "expected_path_selected": False},
    {"fixture_id": "probe_auth_dedicated_profile", "allow_live_start": True, "allow_executable_probe": True, "profile_kind": "dedicated", "expected_readback_ok": True, "expected_preflight_passed": True, "expected_contract_ready": True, "expected_filesystem_probe_performed": False, "expected_path_selected": False},
    {"fixture_id": "probe_auth_default_profile", "allow_live_start": True, "allow_executable_probe": True, "profile_kind": "default", "expected_readback_ok": True, "expected_preflight_passed": True, "expected_contract_ready": True, "expected_filesystem_probe_performed": False, "expected_path_selected": False},
    {"fixture_id": "probe_auth_missing_profile", "allow_live_start": True, "allow_executable_probe": True, "profile_kind": "missing", "expected_readback_ok": True, "expected_preflight_passed": True, "expected_contract_ready": True, "expected_filesystem_probe_performed": False, "expected_path_selected": False},
)
EXPECTED_FIXTURE_IDS = {item["fixture_id"] for item in FIXTURE_MATRIX}

REQUIRED_REPO_PATHS = (
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_cli_readback.py",
    "patchops/llm_browser/live_adapter_edge_executable_filesystem_probe_fixture_matrix.py",
    "patchops/llm_browser/commands.py",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_cli_readback.md",
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_fixture_matrix.md",
    "tests/test_l9_02_edge_executable_filesystem_probe_cli_readback_current.py",
    "tests/test_l9_03_edge_executable_filesystem_probe_fixture_matrix_current.py",
    "scripts/patch_l9_02_brief_validate.py",
    "scripts/patch_l9_03_brief_validate.py",
)

DOC_REQUIREMENTS = {
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_cli_readback.md": (
        "L9.2 Microsoft Edge executable filesystem probe CLI/readback",
        SOURCE_COMMAND_NAME,
        "filesystem probe CLI/readback enforced",
        "filesystem probe modeled only",
        "L9.3 Live adapter Microsoft Edge executable filesystem probe fixture matrix",
    ),
    "docs/llm_browser_live_adapter_edge_executable_filesystem_probe_fixture_matrix.md": (
        "L9.3 Microsoft Edge executable filesystem probe fixture matrix",
        COMMAND_NAME,
        SOURCE_COMMAND_NAME,
        "brief validation output",
        "compact JSON readback",
        "L9.2 executable filesystem probe CLI/readback remains accepted",
        "filesystem probe fixture matrix enforced",
        "filesystem probe modeled only",
        "no_auth_dedicated_profile",
        "live_auth_without_probe_auth",
        "probe_auth_dedicated_profile",
        "probe_auth_default_profile",
        "probe_auth_missing_profile",
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
        "L9.4 Live adapter Microsoft Edge executable filesystem probe fixture matrix CLI/readback",
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


def _source_l9_02_safe(summary: Mapping[str, Any], *, expect_contract_ready: bool, expect_preflight_passed: bool) -> bool:
    return (
        summary.get("patch") == "L9.2"
        and summary.get("ok") is True
        and summary.get("status") == STATUS_PASS
        and summary.get("command_name") == SOURCE_COMMAND_NAME
        and summary.get("l9_01_executable_filesystem_probe_passive_contract_remains_accepted") is True
        and summary.get("edge_executable_filesystem_probe_cli_readback_enforced") is True
        and summary.get("edge_executable_filesystem_probe_contract_enforced") is True
        and summary.get("edge_executable_filesystem_probe_modeled") is True
        and summary.get("edge_executable_probe_safety_preflight_passed") is expect_preflight_passed
        and summary.get("edge_executable_filesystem_probe_contract_ready") is expect_contract_ready
        and summary.get("edge_executable_filesystem_probe_execution_allowed") is False
        and summary.get("edge_executable_filesystem_probe_performed") is False
        and summary.get("edge_executable_candidate_path_labels_modeled") is True
        and summary.get("edge_executable_candidate_path_count", 0) >= 3
        and set(summary.get("edge_executable_candidate_path_labels", [])) == set(EDGE_EXECUTABLE_CANDIDATE_LABELS)
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
        and "source_l9_02_summary" not in summary
        and "source_l9_01_summary" not in summary
    )


def _compact_source_status(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "patch": source.get("patch"),
        "ok": source.get("ok") is True,
        "status": source.get("status"),
        "command_name": source.get("command_name"),
        "preflight_passed": source.get("edge_executable_probe_safety_preflight_passed"),
        "contract_ready": source.get("edge_executable_filesystem_probe_contract_ready"),
        "filesystem_probe_performed": source.get("edge_executable_filesystem_probe_performed"),
        "path_selected": source.get("edge_executable_path_selected"),
        "candidate_path_count": source.get("edge_executable_candidate_path_count"),
        "compact_json_readback_enabled": source.get("compact_json_readback_enabled") is True,
    }


def _fixture_matrix_state() -> dict[str, Any]:
    fixtures = [dict(item) for item in FIXTURE_MATRIX]
    return {
        "edge_executable_filesystem_probe_fixture_matrix_enforced": True,
        "edge_executable_filesystem_probe_fixture_matrix_modeled": True,
        "edge_executable_filesystem_probe_fixture_count": len(fixtures),
        "edge_executable_filesystem_probe_fixture_ids": [fixture["fixture_id"] for fixture in fixtures],
        "edge_executable_filesystem_probe_fixture_matrix": fixtures,
        "fixture_filesystem_probe_performed": False,
        "fixture_path_selected": False,
        "fixture_executable_launch_attempted": False,
        "fixture_contract_ready_when_authorized": True,
        "fixture_contract_not_ready_without_probe_auth": True,
    }


def build_edge_executable_filesystem_probe_fixture_matrix(
    repo_root: str | Path | None = None,
    *,
    allow_live_start: bool = False,
    profile_dir: str | Path | None = None,
    allow_executable_probe: bool = False,
) -> dict[str, Any]:
    root = _repo_root(repo_root)
    before = set(sys.modules)
    source = l9_02.build_edge_executable_filesystem_probe_cli_readback(
        root,
        allow_live_start=allow_live_start,
        profile_dir=profile_dir,
        allow_executable_probe=allow_executable_probe,
    )
    expected_contract_ready = bool(allow_executable_probe)
    expected_preflight_passed = bool(allow_executable_probe)
    source_safe = _source_l9_02_safe(source, expect_contract_ready=expected_contract_ready, expect_preflight_passed=expected_preflight_passed)
    matrix = _fixture_matrix_state()
    command_state = _command_static_presence(COMMAND_NAME)
    source_command_state = _command_static_presence(SOURCE_COMMAND_NAME)
    doc_state = _doc_state(root)
    missing_paths = _missing_paths(root, REQUIRED_REPO_PATHS)
    new_forbidden_imports = _new_forbidden_imports(before)

    checks = [
        _check("l9_02_filesystem_probe_readback_still_passes", source_safe, _compact_source_status(source)),
        _check("l9_02_filesystem_probe_readback_remains_passive", source_safe, {"contract_ready": source.get("edge_executable_filesystem_probe_contract_ready"), "fs_probe": source.get("edge_executable_filesystem_probe_performed"), "path_selected": source.get("edge_executable_path_selected")}),
        _check("l9_03_filesystem_probe_fixture_matrix_command_registered", command_state.get("ok") is True, command_state),
        _check("l9_02_source_command_still_registered", source_command_state.get("ok") is True, source_command_state),
        _check("edge_l9_required_source_docs_tests_present", not missing_paths, {"missing": missing_paths}),
        _check("edge_l9_docs_contain_filesystem_probe_fixture_matrix_boundary", doc_state.get("ok") is True, {"missing_docs": doc_state.get("missing_docs"), "missing_phrases": doc_state.get("missing_phrases")}),
        _check("filesystem_probe_fixture_matrix_is_modeled", matrix["edge_executable_filesystem_probe_fixture_matrix_modeled"] is True and matrix["edge_executable_filesystem_probe_fixture_count"] >= 5, matrix),
        _check("filesystem_probe_fixture_ids_are_stable", set(matrix["edge_executable_filesystem_probe_fixture_ids"]) == EXPECTED_FIXTURE_IDS, {"fixture_ids": matrix["edge_executable_filesystem_probe_fixture_ids"]}),
        _check("no_auth_fixtures_keep_contract_not_ready", any(f["expected_contract_ready"] is False for f in matrix["edge_executable_filesystem_probe_fixture_matrix"]), matrix),
        _check("authorized_fixtures_mark_contract_ready_but_do_not_probe", all((not f["allow_executable_probe"] or (f["expected_contract_ready"] is True and f["expected_filesystem_probe_performed"] is False)) for f in matrix["edge_executable_filesystem_probe_fixture_matrix"]), matrix),
        _check("candidate_path_labels_remain_modeled_only", source.get("edge_executable_candidate_path_labels_modeled") is True and source.get("edge_executable_candidate_path_count", 0) >= 3, _compact_source_status(source)),
        _check("filesystem_probe_execution_remains_blocked_by_phase", source.get("edge_executable_filesystem_probe_execution_allowed") is False, {}),
        _check("filesystem_probe_is_not_performed", source.get("edge_executable_filesystem_probe_performed") is False and matrix["fixture_filesystem_probe_performed"] is False, {}),
        _check("edge_executable_path_stays_unselected", source.get("edge_executable_path_selected") is False and matrix["fixture_path_selected"] is False, {}),
        _check("edge_executable_launch_stays_unattempted", source.get("edge_executable_launch_attempted") is False and matrix["fixture_executable_launch_attempted"] is False, {}),
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
        "l9_02_executable_filesystem_probe_cli_readback_remains_accepted": source.get("ok") is True and source.get("status") == STATUS_PASS,
        "source_l9_02_status": _compact_source_status(source),
        **matrix,
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
        f"L9.2 Accepted   : {payload.get('l9_02_executable_filesystem_probe_cli_readback_remains_accepted')}",
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
    payload = build_edge_executable_filesystem_probe_fixture_matrix(
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

DOC_CONTENT = r'''# L9.3 Microsoft Edge executable filesystem probe fixture matrix

L9.3 adds a passive fixture matrix for the accepted L9.2 Microsoft Edge executable filesystem-probe CLI/readback layer.

Command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-fixture-matrix`

Source command:

`browser-start-supervised-launch-edge-executable-filesystem-probe-readback`

This patch keeps brief validation output and compact JSON readback.

Boundary:

- Microsoft Edge first.
- Opera second.
- brief validation output.
- compact JSON readback.
- L9.2 executable filesystem probe CLI/readback remains accepted.
- filesystem probe fixture matrix enforced.
- filesystem probe modeled only.
- `no_auth_dedicated_profile` fixture modeled.
- `live_auth_without_probe_auth` fixture modeled.
- `probe_auth_dedicated_profile` fixture modeled.
- `probe_auth_default_profile` fixture modeled.
- `probe_auth_missing_profile` fixture modeled.
- candidate path labels modeled only.
- filesystem probe not performed.
- executable path not selected.
- executable launch not attempted.
- filesystem probe readback can report contract_ready=true while filesystem probe remains blocked.
- preflight readback can succeed while preflight_passed is false.
- Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.
- `--allow-executable-probe` remains the explicit future authorization flag.
- authorization can be present but filesystem probe execution remains blocked by phase.
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

`L9.4 Live adapter Microsoft Edge executable filesystem probe fixture matrix CLI/readback`
'''

TEST_CONTENT = r'''from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_fixture_matrix as matrix

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-fixture-matrix"
SOURCE_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-readback"
DEDICATED_PROFILE = PROJECT_ROOT / "data" / "runtime" / "browser_profiles" / "edge_l9_03_candidate"
DEFAULT_PROFILE = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"
EXPECTED_IDS = {
    "no_auth_dedicated_profile",
    "live_auth_without_probe_auth",
    "probe_auth_dedicated_profile",
    "probe_auth_default_profile",
    "probe_auth_missing_profile",
}


def _assert_passive(payload: dict) -> None:
    assert payload["startup_allowed"] is False
    assert payload["live_start_performed"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["fixture_filesystem_probe_performed"] is False
    assert payload["fixture_path_selected"] is False
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
    assert "source_l9_03_summary" not in payload
    assert "source_l9_02_summary" not in payload


def test_l9_03_command_is_registered() -> None:
    from patchops.llm_browser import commands
    names = commands.llm_browser_command_names()
    assert COMMAND in names
    assert SOURCE_COMMAND in names


def test_l9_03_no_auth_fixture_matrix_contract_not_ready_and_no_probe() -> None:
    payload = matrix.build_edge_executable_filesystem_probe_fixture_matrix(
        PROJECT_ROOT,
        allow_live_start=False,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=False,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["patch"] == "L9.3"
    assert payload["command_name"] == COMMAND
    assert payload["source_command_name"] == SOURCE_COMMAND
    assert payload["l9_02_executable_filesystem_probe_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_fixture_matrix_enforced"] is True
    assert set(payload["edge_executable_filesystem_probe_fixture_ids"]) == EXPECTED_IDS
    assert payload["edge_executable_probe_safety_preflight_passed"] is False
    assert payload["edge_executable_filesystem_probe_contract_ready"] is False
    assert any(f["expected_contract_ready"] is False for f in payload["edge_executable_filesystem_probe_fixture_matrix"])
    _assert_passive(payload)


def test_l9_03_authorized_fixture_matrix_contract_ready_but_filesystem_probe_stays_blocked() -> None:
    payload = matrix.build_edge_executable_filesystem_probe_fixture_matrix(
        PROJECT_ROOT,
        allow_live_start=True,
        profile_dir=DEDICATED_PROFILE,
        allow_executable_probe=True,
    )
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["phase"] == "L9"
    assert payload["edge_executable_probe_safety_preflight_passed"] is True
    assert payload["edge_executable_filesystem_probe_contract_ready"] is True
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert all((not f["allow_executable_probe"] or f["expected_contract_ready"] is True) for f in payload["edge_executable_filesystem_probe_fixture_matrix"])
    assert payload["next_patch"] == "L9.4 Live adapter Microsoft Edge executable filesystem probe fixture matrix CLI/readback"
    _assert_passive(payload)


def test_l9_03_default_and_missing_profile_cases_are_passive_when_authorized() -> None:
    default_payload = matrix.build_edge_executable_filesystem_probe_fixture_matrix(PROJECT_ROOT, allow_live_start=True, profile_dir=DEFAULT_PROFILE, allow_executable_probe=True)
    missing_payload = matrix.build_edge_executable_filesystem_probe_fixture_matrix(PROJECT_ROOT, allow_live_start=True, profile_dir=None, allow_executable_probe=True)
    assert default_payload["ok"] is True
    assert default_payload["source_l9_02_status"]["ok"] is True
    _assert_passive(default_payload)
    assert missing_payload["ok"] is True
    assert missing_payload["source_l9_02_status"]["ok"] is True
    _assert_passive(missing_payload)


def test_l9_03_patchops_cli_json_readback_is_parseable_compact_and_passive() -> None:
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
    assert payload["patch"] == "L9.3"
    assert payload["edge_executable_filesystem_probe_contract_ready"] is True
    assert payload["edge_executable_filesystem_probe_performed"] is False
    _assert_passive(payload)


def test_l9_03_doc_mentions_filesystem_probe_fixture_matrix_boundaries() -> None:
    doc = PROJECT_ROOT / "docs" / "llm_browser_live_adapter_edge_executable_filesystem_probe_fixture_matrix.md"
    text = doc.read_text(encoding="utf-8")
    for phrase in [
        "L9.3 Microsoft Edge executable filesystem probe fixture matrix",
        COMMAND,
        SOURCE_COMMAND,
        "brief validation output",
        "compact JSON readback",
        "L9.2 executable filesystem probe CLI/readback remains accepted",
        "filesystem probe fixture matrix enforced",
        "filesystem probe modeled only",
        "no_auth_dedicated_profile",
        "live_auth_without_probe_auth",
        "probe_auth_dedicated_profile",
        "probe_auth_default_profile",
        "probe_auth_missing_profile",
        "candidate path labels modeled only",
        "filesystem probe not performed",
        "executable path not selected",
        "executable launch not attempted",
        "filesystem probe readback can report contract_ready=true while filesystem probe remains blocked",
        "preflight readback can succeed while preflight_passed is false",
        "Missing executable-probe authorization is reported as preflight_passed=false while the passive readback itself remains ok.",
        "--allow-executable-probe",
        "authorization can be present but filesystem probe execution remains blocked by phase",
        "no Selenium import",
        "no browser start",
        "no Edge process start",
        "no click/download/paste/send/package-run side effect",
        "L9.4 Live adapter Microsoft Edge executable filesystem probe fixture matrix CLI/readback",
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

from patchops.llm_browser import live_adapter_edge_executable_filesystem_probe_fixture_matrix as matrix

COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-fixture-matrix"
DEDICATED = ROOT / "data" / "runtime" / "browser_profiles" / "edge_l9_03_candidate"
DEFAULT = r"C:\Users\kostas\AppData\Local\Microsoft\Edge\User Data\Default"


def assert_passive(payload: dict) -> None:
    assert payload["ok"] is True
    assert payload["status"] == "PASS"
    assert payload["l9_02_executable_filesystem_probe_cli_readback_remains_accepted"] is True
    assert payload["edge_executable_filesystem_probe_fixture_matrix_enforced"] is True
    assert payload["edge_executable_filesystem_probe_execution_allowed"] is False
    assert payload["edge_executable_filesystem_probe_performed"] is False
    assert payload["edge_executable_path_selected"] is False
    assert payload["edge_executable_selected_path"] is None
    assert payload["edge_executable_launch_attempted"] is False
    assert payload["fixture_filesystem_probe_performed"] is False
    assert payload["fixture_path_selected"] is False
    assert payload["browser_started"] is False
    assert payload["edge_process_started"] is False
    assert payload["browser_session_created"] is False
    assert payload["driver_created"] is False
    assert payload["profile_directory_created"] is False
    assert payload["selenium_imported_by_readback"] is False
    assert payload["side_effects_performed"] == []
    assert "source_l9_02_summary" not in payload


def main() -> int:
    no_auth = matrix.build_edge_executable_filesystem_probe_fixture_matrix(ROOT, allow_live_start=False, profile_dir=DEDICATED, allow_executable_probe=False)
    assert_passive(no_auth)
    assert no_auth["edge_executable_probe_safety_preflight_passed"] is False
    assert no_auth["edge_executable_filesystem_probe_contract_ready"] is False
    print("PASS no_probe_auth: patch=L9.3 fixtures=5 preflight_passed=False contract_ready=False fs_probe=False path_selected=False")

    cases = [
        ("probe_auth_dedicated", True, DEDICATED, True),
        ("probe_auth_default", True, DEFAULT, True),
        ("probe_auth_missing_profile", True, None, True),
    ]
    for name, live, profile, probe_auth in cases:
        payload = matrix.build_edge_executable_filesystem_probe_fixture_matrix(
            ROOT,
            allow_live_start=live,
            profile_dir=profile,
            allow_executable_probe=probe_auth,
        )
        assert_passive(payload)
        assert payload["edge_executable_probe_safety_preflight_passed"] is True
        assert payload["edge_executable_filesystem_probe_contract_ready"] is True
        print(
            "PASS {0}: patch={1} source=L9.2 fixtures={2} preflight_passed={3} contract_ready={4} fs_probe={5} path_selected={6}".format(
                name,
                payload["patch"],
                payload["edge_executable_filesystem_probe_fixture_count"],
                payload["edge_executable_probe_safety_preflight_passed"],
                payload["edge_executable_filesystem_probe_contract_ready"],
                payload["edge_executable_filesystem_probe_performed"],
                payload["edge_executable_path_selected"],
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
    print("PASS main_cli: compact JSON parsed quickly; filesystem probe fixture matrix stayed passive")
    print("PASS L9.3 brief validation: executable filesystem probe fixture matrix accepted with no filesystem probe or browser side effects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

COMMAND_BLOCK = r'''
# PATCHOPS L9.3 START
# Passive Microsoft Edge executable filesystem probe fixture matrix.
import sys as _patchops_l9_03_sys

_PATCHOPS_L9_03_COMMAND = "browser-start-supervised-launch-edge-executable-filesystem-probe-fixture-matrix"

try:
    _PATCHOPS_L9_03_PREV_BUILD_PARSER = build_parser
except NameError:  # pragma: no cover
    _PATCHOPS_L9_03_PREV_BUILD_PARSER = None

if _PATCHOPS_L9_03_PREV_BUILD_PARSER is not None:
    def build_parser():  # type: ignore[no-redef]
        parser = _PATCHOPS_L9_03_PREV_BUILD_PARSER()
        try:
            for action in getattr(parser, "_actions", []):
                if action.__class__.__name__ == "_SubParsersAction":
                    choices = getattr(action, "choices", {})
                    if _PATCHOPS_L9_03_COMMAND not in choices:
                        p = action.add_parser(_PATCHOPS_L9_03_COMMAND, help="Read back passive Edge executable filesystem probe fixture matrix.")
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


def run_browser_start_supervised_launch_edge_executable_filesystem_probe_fixture_matrix(args) -> int:
    from . import live_adapter_edge_executable_filesystem_probe_fixture_matrix
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
    return live_adapter_edge_executable_filesystem_probe_fixture_matrix.main(module_args)

try:
    _PATCHOPS_L9_03_PREV_COMMAND_NAMES = llm_browser_command_names
except NameError:  # pragma: no cover
    _PATCHOPS_L9_03_PREV_COMMAND_NAMES = None

if _PATCHOPS_L9_03_PREV_COMMAND_NAMES is not None:
    def llm_browser_command_names() -> tuple[str, ...]:  # type: ignore[no-redef]
        names = tuple(_PATCHOPS_L9_03_PREV_COMMAND_NAMES())
        return names + tuple(name for name in (_PATCHOPS_L9_03_COMMAND,) if name not in names)

_PATCHOPS_L9_03_PREV_MAIN = main

def main(argv=None):  # type: ignore[no-redef]
    arg_list = list(_patchops_l9_03_sys.argv[1:] if argv is None else argv)
    if arg_list and arg_list[0] == _PATCHOPS_L9_03_COMMAND:
        from . import live_adapter_edge_executable_filesystem_probe_fixture_matrix
        return live_adapter_edge_executable_filesystem_probe_fixture_matrix.main(arg_list[1:])
    return _PATCHOPS_L9_03_PREV_MAIN(argv)
# PATCHOPS L9.3 END
'''


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _append_command_block() -> None:
    text = COMMANDS_PATH.read_text(encoding="utf-8")
    if "# PATCHOPS L9.3 START" not in text:
        if not text.endswith("\n"):
            text += "\n"
        COMMANDS_PATH.write_text(text + "\n" + COMMAND_BLOCK.strip() + "\n", encoding="utf-8")
        print("L9.3 command wrapper appended")
    else:
        print("L9.3 command wrapper already present")


def _append_l9_02_doc_pointer() -> None:
    path = Path("docs/llm_browser_live_adapter_edge_executable_filesystem_probe_cli_readback.md")
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    phrase = "L9.3 Live adapter Microsoft Edge executable filesystem probe fixture matrix"
    if phrase not in text:
        path.write_text(text.rstrip() + "\n\nNext accepted frontier after the executable filesystem probe CLI/readback:\n\n`" + phrase + "`\n", encoding="utf-8")
        print("L9.2 doc next-frontier pointer appended")


def main() -> int:
    _write(MODULE_PATH, MODULE_CONTENT)
    _write(DOC_PATH, DOC_CONTENT)
    _write(TEST_PATH, TEST_CONTENT)
    _write(VALIDATE_PATH, VALIDATE_CONTENT)
    _append_command_block()
    _append_l9_02_doc_pointer()
    print("L9.3 files written; validation is intentionally brief and compact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())